"""Explicit public downloads for TTS-002; never called during inference."""
import hashlib
import json
import os
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
BASE_ID='Qwen/Qwen3-TTS-12Hz-0.6B-Base'
BASE_REV='5d83992436eae1d760afd27aff78a71d676296fc'
PIPER_REV='e7229f7d33a10e145e109b886d661984201ac3c4'

def main():
    os.environ['HF_HOME']=str(ROOT/'models/hf_cache')
    os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
    os.environ['HF_HUB_DISABLE_XET']='1'
    from huggingface_hub import snapshot_download
    evidence=json.loads((ROOT/'testes/tts_002/environment.json').read_text())
    info=evidence[BASE_ID]
    target=ROOT/'models'/BASE_REV
    existing=ROOT/'models/85e237c12c027371202489a0ec509ded67b5e4b5/speech_tokenizer/model.safetensors'
    tokenizer=next(x for x in info['siblings'] if x['rfilename']=='speech_tokenizer/model.safetensors')
    matches=existing.is_file() and hashlib.file_digest(existing.open('rb'),'sha256').hexdigest()==tokenizer['lfs']['sha256']
    snapshot_download(BASE_ID,revision=BASE_REV,local_dir=target,max_workers=2,
        ignore_patterns=['speech_tokenizer/model.safetensors'] if matches else None)
    if matches:
        dest=target/'speech_tokenizer/model.safetensors'
        if not dest.exists(): shutil.copyfile(existing,dest)
    piper=ROOT/'models/piper_faber'/PIPER_REV
    snapshot_download('rhasspy/piper-voices',revision=PIPER_REV,local_dir=piper,max_workers=2,
        allow_patterns=['pt/pt_BR/faber/medium/MODEL_CARD','pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx*','LICENSE*'])
    rows=[]
    for model,directory,files in ((BASE_ID,target,info['siblings']),('rhasspy/piper-voices',piper,evidence['rhasspy/piper-voices']['siblings'])):
        for entry in files:
            p=directory/entry['rfilename']
            if not p.is_file():
                if model==BASE_ID: raise FileNotFoundError(p)
                continue
            digest=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
            expected=entry.get('lfs',{}).get('sha256')
            valid=p.stat().st_size==entry['size'] and (not expected or digest==expected)
            assert valid,p
            rows.append(dict(model=model,file=entry['rfilename'],sha256=digest,size=p.stat().st_size,verified=True))
    (ROOT/'testes/tts_002/model_integrity.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    print('Models downloaded and verified',len(rows))

if __name__=='__main__':main()
