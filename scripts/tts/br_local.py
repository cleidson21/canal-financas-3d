"""TTS-002: offline Base/reference and one native pt-BR Piper comparison."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import sys
import threading
import time
import wave

from .local import ROOT, Request, assert_new, validate_local_wav, acoustic_checks
from .prepare_br_models import BASE_ID, BASE_REV, PIPER_REV
from .samples_local import Monitor

REFERENCE=ROOT/'audio/referencias_vocais/narrador_br_001'
DEFAULT_TEXT=ROOT/'testes/tts_002/texto_teste.txt'
PARAMS=dict(max_new_tokens=1024,do_sample=True,top_k=50,top_p=1.0,temperature=0.9,
    repetition_penalty=1.05,subtalker_dosample=True,subtalker_top_k=50,
    subtalker_top_p=1.0,subtalker_temperature=0.9,non_streaming_mode=True)

def sha(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def dump_new(path,data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f: json.dump(data,f,indent=2,ensure_ascii=False,default=str)

def inspect_reference(directory):
    directory=Path(directory)
    audio=directory/'referencia.wav'; transcript=directory/'transcricao.txt'
    if not audio.is_file() or not transcript.is_file():
        raise FileNotFoundError('Faltam referencia.wav e/ou transcricao.txt literal; não há substituição automática')
    text=transcript.read_text(encoding='utf-8-sig').strip()
    if not text: raise ValueError('Transcrição vazia')
    digest=sha(audio)
    # The initial baseline identifies all old production/test recordings, even renamed copies.
    baseline=json.loads((ROOT/'testes/tts_002/baseline.json').read_text(encoding='utf-8'))
    forbidden={r['sha256'] for r in baseline if r['path'].startswith('audio/narracoes/') and r['path'].endswith('.wav')}
    if digest in forbidden: raise PermissionError('Áudio anterior de produção/teste recusado como referência, inclusive Puck')
    validation=validate_local_wav(audio)
    if not validation.get('valid'): raise ValueError(f'Referência inválida: {validation}')
    if validation['channels']!=1 or not 3<=validation['duration_seconds']<=30:
        raise ValueError('Referência deve ser mono PCM16, entre 3 e 30 segundos')
    import numpy as np
    with wave.open(str(audio),'rb') as w: pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
    extra=acoustic_checks(pcm,validation['sample_rate_hz'])
    if not extra['pass']: raise ValueError(f'Referência com clipping/silêncio excessivo: {extra}')
    return dict(reference_id=directory.name,audio_path=str(audio.resolve()),audio_sha256=digest,
        transcript_path=str(transcript.resolve()),transcript_sha256=sha(transcript),
        transcript=text,validation=validation,acoustic_checks=extra)

def validate_reference(directory):
    ref=inspect_reference(directory)
    path=Path(directory)/'autorizacao.json'
    if not path.is_file(): raise PermissionError('Falta autorizacao.json vinculada à gravação')
    authorization=json.loads(path.read_text(encoding='utf-8-sig'))
    for key in ('synthesis_authorized','commercial_reuse_authorized','transcript_reviewed'):
        if authorization.get(key) is not True: raise PermissionError(f'Autorização pendente: {key}')
    for key in ('audio_sha256','transcript_sha256','reference_id'):
        if authorization.get(key)!=ref[key]: raise PermissionError(f'Autorização não corresponde à referência: {key}')
    for key in ('owner','source','rights_basis','authorization_evidence','declared_at'):
        if not isinstance(authorization.get(key),str) or not authorization[key].strip(): raise PermissionError(f'Origem/autorização incompleta: {key}')
    ref['authorization_sha256']=sha(path)
    ref['authorization']=authorization
    return ref

def load_base():
    path=ROOT/'models'/BASE_REV
    if not (path/'model.safetensors').is_file(): raise FileNotFoundError('Base ausente; execute preparação explícita de modelos')
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1')
    import torch
    if not torch.cuda.is_available(): raise RuntimeError('CUDA ausente; sem fallback remoto/CPU automático')
    if torch.cuda.mem_get_info()[0]<4*1024**3: raise RuntimeError('GPU com menos de 4 GiB livres; aguarde liberação')
    from qwen_tts import Qwen3TTSModel
    model=Qwen3TTSModel.from_pretrained(str(path),local_files_only=True,device_map='cuda:0',
        dtype=torch.bfloat16,attn_implementation='sdpa')
    if model.model.tts_model_type!='base' or model.model.tts_model_size!='0b6': raise ValueError('Tipo/tamanho Base inesperado')
    return model

def clone_prompt(model,ref):
    """Safe reusable tensor-only NPZ, bound to model, runtime and authorized input."""
    import numpy as np
    import torch
    from qwen_tts.inference.qwen3_tts_model import VoiceClonePromptItem
    identity=dict(model_revision=BASE_REV,reference_sha256=ref['audio_sha256'],
        transcript_sha256=ref['transcript_sha256'],authorization_sha256=ref['authorization_sha256'],
        qwen_tts=version('qwen-tts'),torch=version('torch'))
    key=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
    cache=ROOT/'models/voice_prompts'/key
    tensor_path=cache.with_suffix('.npz'); meta_path=cache.with_suffix('.json')
    if tensor_path.exists() or meta_path.exists():
        meta=json.loads(meta_path.read_text(encoding='utf-8'))
        if meta['identity']!=identity or meta['npz_sha256']!=sha(tensor_path): raise ValueError('Cache vocal alterado/incompatível')
        with np.load(tensor_path,allow_pickle=False) as arrays:
            code=torch.from_numpy(arrays['ref_code'].copy()).to(model.device)
            embedding=torch.from_numpy(arrays['ref_spk_embedding'].copy()).to(device=model.device,dtype=getattr(torch,meta['embedding_dtype']))
        item=VoiceClonePromptItem(ref_code=code,ref_spk_embedding=embedding,
            x_vector_only_mode=False,icl_mode=True,ref_text=ref['transcript'])
        return [item],dict(cache_id=key,reused=True,identity=identity)
    items=model.create_voice_clone_prompt(ref_audio=ref['audio_path'],ref_text=ref['transcript'],x_vector_only_mode=False)
    if len(items)!=1: raise RuntimeError('Prompt inesperado')
    item=items[0]
    tensor_path.parent.mkdir(parents=True,exist_ok=True)
    with tensor_path.open('xb') as f:
        np.savez(f,ref_code=item.ref_code.detach().cpu().numpy(),
            ref_spk_embedding=item.ref_spk_embedding.detach().float().cpu().numpy())
    dump_new(meta_path,dict(identity=identity,npz_sha256=sha(tensor_path),
        embedding_dtype=str(item.ref_spk_embedding.dtype).removeprefix('torch.')))
    return items,dict(cache_id=key,reused=False,identity=identity)

def synthesize(provider,text,output,reference_dir=REFERENCE,seed=42):
    output=Path(output)
    assert_new(Request(text,output))
    if provider not in ('qwen_base_local','piper_local'): raise ValueError('Provedor não permitido')
    ref=validate_reference(reference_dir) if provider=='qwen_base_local' else None
    import numpy as np
    import soundfile as sf
    monitor=Monitor(); thread=threading.Thread(target=monitor.loop,daemon=True); thread.start()
    meta=dict(provider=provider,text=text,seed=seed,reference=ref,approved=False,
        human_approval_required=True,offline=True,generated_at=datetime.now(timezone.utc).isoformat())
    try:
        start=time.perf_counter()
        if provider=='qwen_base_local':
            import torch
            from transformers import set_seed
            set_seed(seed)
            model=load_base()
            meta.update(model=BASE_ID,revision=BASE_REV,dtype='bfloat16',attention='sdpa',language='Portuguese')
            meta['load_seconds']=time.perf_counter()-start
            torch.cuda.reset_peak_memory_stats()
            start=time.perf_counter()
            prompt,cache=clone_prompt(model,ref)
            meta['prompt_seconds']=time.perf_counter()-start
            # Exercise reconstruction of the cached prompt before the single synthesis.
            reloaded,reuse=clone_prompt(model,ref)
            meta['voice_prompt']=dict(created_or_loaded=cache,reuse_test=reuse)
            set_seed(seed); torch.cuda.synchronize(); start=time.perf_counter()
            with torch.inference_mode():
                wavs,sr=model.generate_voice_clone(text=text,language='Portuguese',voice_clone_prompt=reloaded,**PARAMS)
            torch.cuda.synchronize()
            meta['generation_seconds']=time.perf_counter()-start
            data=np.asarray(wavs[0])
            if data.size==0 or not np.isfinite(data).all() or len(data)/sr>=PARAMS['max_new_tokens']/12-0.5:
                raise RuntimeError('Áudio inválido ou possível truncamento; sem repetição automática')
            output.parent.mkdir(parents=True,exist_ok=True)
            with output.open('xb') as f: sf.write(f,data,sr,format='WAV',subtype='PCM_16')
            meta.update(settings=PARAMS,gpu_peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                gpu_peak_reserved_bytes=torch.cuda.max_memory_reserved(),runtime=version('qwen-tts'))
        else:
            from piper import PiperVoice, SynthesisConfig
            path=ROOT/'models/piper_faber'/PIPER_REV/'pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx'
            if not path.is_file(): raise FileNotFoundError('Piper Faber local ausente')
            voice=PiperVoice.load(str(path),use_cuda=False)
            meta.update(model='pt_BR-faber-medium',revision=PIPER_REV,model_sha256=sha(path),
                runtime=version('piper-tts'),device='cpu',language='pt-BR',
                model_card=str(path.parent/'MODEL_CARD'),reference=None,seed=None,
                settings=dict(length_scale=1.0,noise_scale=0.667,noise_w_scale=0.8,normalize_audio=False,volume=1.0))
            meta['load_seconds']=time.perf_counter()-start
            config=SynthesisConfig(**meta['settings'])
            output.parent.mkdir(parents=True,exist_ok=True)
            start=time.perf_counter()
            with output.open('xb') as f:
                with wave.open(f,'wb') as w: voice.synthesize_wav(text,w,syn_config=config)
            meta['generation_seconds']=time.perf_counter()-start
        validation=validate_local_wav(output)
        with wave.open(str(output),'rb') as w:
            sr=w.getframerate(); data=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
        meta.update(validation=validation,acoustic_checks=acoustic_checks(data,sr),
            sha256=sha(output),size_bytes=output.stat().st_size,
            real_time_factor=meta['generation_seconds']/(len(data)/sr))
        meta['technical_pass']=validation['valid'] and meta['acoustic_checks']['pass']
    finally:
        monitor.stop.set(); thread.join(timeout=12)
        meta['resources']=monitor.rows
        meta['memory_summary']=dict(
            sampling='approximately 0.5s plus nvidia-smi time; GPU total includes desktop',
            process_rss_peak_bytes=max((r['process_rss'] for r in monitor.rows),default=None),
            gpu_total_peak_mib_sampled=max((r['gpu_total_used_mib'] for r in monitor.rows if 'gpu_total_used_mib' in r),default=None))
    dump_new(str(output)+'.meta.json',meta)
    if not meta['technical_pass']: raise RuntimeError('Falha acústica; WAV preservado para diagnóstico, sem nova tentativa')
    return meta

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['inspect-reference','register-reference','probe-base','generate'])
    p.add_argument('--reference-dir',type=Path,default=REFERENCE)
    p.add_argument('--owner'); p.add_argument('--own-voice',action='store_true')
    p.add_argument('--allow-synthesis',action='store_true'); p.add_argument('--allow-commercial',action='store_true')
    p.add_argument('--transcript-reviewed',action='store_true')
    p.add_argument('--provider',choices=['qwen_base_local','piper_local'],default='qwen_base_local')
    p.add_argument('--text-file',type=Path,default=DEFAULT_TEXT)
    p.add_argument('--output',type=Path); p.add_argument('--seed',type=int,default=42)
    a=p.parse_args()
    try:
        if a.action=='inspect-reference': result=inspect_reference(a.reference_dir)
        elif a.action=='register-reference':
            if not (a.owner and a.own_voice and a.allow_synthesis and a.allow_commercial and a.transcript_reviewed):
                raise PermissionError('Declare titularidade, síntese, uso comercial e transcrição conferida explicitamente')
            ref=inspect_reference(a.reference_dir)
            result=dict(reference_id=ref['reference_id'],owner=a.owner,source='own_recording',rights_basis='voice_owner',
                authorization_evidence='Explicit ownership/synthesis/commercial reuse/reviewed transcript declaration recorded via registration flags',
                synthesis_authorized=True,commercial_reuse_authorized=True,transcript_reviewed=True,
                audio_sha256=ref['audio_sha256'],transcript_sha256=ref['transcript_sha256'],declared_at=datetime.now(timezone.utc).isoformat())
            dump_new(a.reference_dir/'autorizacao.json',result)
        elif a.action=='probe-base':
            start=time.perf_counter(); model=load_base()
            import torch
            result=dict(model=BASE_ID,revision=BASE_REV,type=model.model.tts_model_type,
                load_seconds=time.perf_counter()-start,cuda=torch.cuda.is_available(),device=str(model.device),
                allocated_bytes=torch.cuda.memory_allocated(),reserved_bytes=torch.cuda.memory_reserved(),
                voice_clone_tested=False,reason='No authorized reference yet')
            dump_new(ROOT/'testes/tts_002/base_probe.json',result)
        else:
            if a.output is None: raise ValueError('--output obrigatório')
            result=synthesize(a.provider,a.text_file.read_text(encoding='utf-8-sig').strip(),a.output,a.reference_dir,a.seed)
        print(json.dumps(result,indent=2,ensure_ascii=False,default=str))
    except (ValueError,PermissionError,FileNotFoundError,RuntimeError) as exc:
        print(json.dumps(dict(error=str(exc)),ensure_ascii=False),file=sys.stderr); sys.exit(2)

if __name__=='__main__':main()
