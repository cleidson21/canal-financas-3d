"""Provider facade: offline Qwen; Gemini requires explicit opt-in."""
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import time
import wave

ROOT = Path(__file__).resolve().parents[2]
MODEL_ID = 'Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice'
REVISION = '85e237c12c027371202489a0ec509ded67b5e4b5'

@dataclass(frozen=True)
class Request:
    text: str
    output: Path
    voice: str = 'Ryan'
    provider: str = 'qwen_local'
    model: str = MODEL_ID
    language: str = 'Portuguese'
    style: str = ''
    seed: int = 42
    synthesis: dict = field(default_factory=lambda: dict(max_new_tokens=1024, do_sample=True,
        top_k=50, top_p=1.0, temperature=0.9, repetition_penalty=1.05))

def assert_new(request):
    if not request.text.strip(): raise ValueError('Texto vazio')
    if Path(request.output).suffix.lower() != '.wav': raise ValueError('Saída deve ser WAV')
    for p in (Path(request.output), Path(str(request.output)+'.meta.json')):
        if p.exists(): raise FileExistsError(f'Arquivo preservado: {p}')

def request_from_profile(profile_path, text, output):
    """An unapproved profile cannot become production settings implicitly."""
    profile = json.loads(Path(profile_path).read_text(encoding='utf-8-sig'))
    if profile.get('approval_status') != 'approved' or not profile.get('approved_sample_id') or not profile.get('approved_on'):
        raise PermissionError('Perfil ainda depende de aprovação humana')
    if profile['model_revision'] != REVISION or profile['model'] != MODEL_ID:
        raise ValueError('Revisão aprovada diferente do adaptador; revalidação necessária')
    if profile['runtime_package'] != 'qwen-tts=='+version('qwen-tts'):
        raise ValueError('Versão do runtime diferente do perfil aprovado')
    settings = profile['synthesis']
    if settings['dtype'] != 'bfloat16' or settings['attention'] != 'sdpa':
        raise ValueError('Precisão/atenção diferente do runtime validado')
    defaults = Request(text,Path(output)).synthesis
    return Request(text=text,output=Path(output),voice=profile['voice_id'],provider=profile['engine'],
        model=profile['model'],language=profile['language'],seed=settings['seed'],
        synthesis={k:settings[k] for k in defaults})

class QwenLocal:
    def __init__(self, model_dir=None):
        self.model_dir = Path(model_dir or ROOT/'models'/REVISION)
        self.model = None

    def load(self):
        if self.model is not None: return
        if not (self.model_dir/'model.safetensors').is_file():
            raise FileNotFoundError('Modelo local ausente; download explícito necessário')
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['TRANSFORMERS_OFFLINE'] = '1'
        os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
        import torch
        if not torch.cuda.is_available(): raise RuntimeError('CUDA indisponível; sem fallback automático')
        free, _ = torch.cuda.mem_get_info()
        if free < 4*1024**3: raise RuntimeError('Menos de 4 GiB livres na GPU; geração adiada')
        from qwen_tts import Qwen3TTSModel
        self.model = Qwen3TTSModel.from_pretrained(str(self.model_dir), local_files_only=True,
            device_map='cuda:0', dtype=torch.bfloat16, attn_implementation='sdpa')

    def generate(self, request):
        assert_new(request)
        if request.model != MODEL_ID: raise ValueError('Modelo diferente do runtime fixado')
        if request.style: raise ValueError('0.6B sem instruction control; estilo recusado')
        self.load()
        import numpy as np
        import soundfile as sf
        import torch
        from transformers import set_seed
        speakers = self.model.get_supported_speakers()
        languages = self.model.get_supported_languages()
        if request.voice.lower() not in [x.lower() for x in speakers]: raise ValueError('Voz não suportada')
        if request.language.lower() not in [x.lower() for x in languages]: raise ValueError('Idioma não suportado')
        set_seed(request.seed)
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
        start = time.perf_counter()
        with torch.inference_mode():
            wavs, sr = self.model.generate_custom_voice(text=request.text, speaker=request.voice,
                language=request.language, **request.synthesis)
        torch.cuda.synchronize()
        elapsed = time.perf_counter()-start
        wav = np.asarray(wavs[0])
        if wav.size == 0 or not np.isfinite(wav).all(): raise RuntimeError('Saída vazia ou não finita')
        if len(wav)/sr >= request.synthesis['max_new_tokens']/12-0.5:
            raise RuntimeError('Possível truncamento por limite de tokens; saída recusada')
        path = Path(request.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as f:
            sf.write(f, wav, sr, format='WAV', subtype='PCM_16')
        validation = validate_local_wav(path)
        extra = acoustic_checks(wav, sr)
        meta = dict(request=asdict(request), model_revision=REVISION,
            generated_at=datetime.now(timezone.utc).isoformat(), approved=False,
            elapsed_seconds=elapsed, real_time_factor=elapsed/(len(wav)/sr),
            sample_rate=sr, size_bytes=path.stat().st_size,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(), validation=validation,
            acoustic_checks=extra, speakers=speakers, languages=languages,
            torch_version=torch.__version__, cuda=torch.version.cuda,
            package_versions={name:version(name) for name in ('qwen-tts','transformers','accelerate','soundfile','numpy','torchaudio')},
            gpu_peak_allocated_bytes=torch.cuda.max_memory_allocated(),
            gpu_peak_reserved_bytes=torch.cuda.max_memory_reserved(),
            dtype='bfloat16', attention='sdpa', offline=True, human_approval_required=True)
        meta['technical_pass'] = validation['valid'] and extra['pass']
        with Path(str(path)+'.meta.json').open('x', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False, default=str)
        return meta

def acoustic_checks(wav, sr):
    import numpy as np
    clip = float(np.mean(np.abs(wav)>=0.999))
    window = max(1, int(sr*0.02))
    silent = [np.sqrt(np.mean(wav[i:i+window]**2)) < 10**(-45/20) for i in range(0,len(wav),window)]
    longest = current = 0
    for flag in silent:
        current = current+1 if flag else 0
        longest = max(longest,current)
    return dict(clipped_fraction=clip, longest_silence_seconds=longest*0.02,
        pass_criteria='clipped fraction < 0.001, longest silence <= 3 seconds',
        **{'pass':clip<0.001 and longest*0.02<=3})

def validate_local_wav(path):
    """Preserve existing acoustic checks and additionally reject truncated PCM."""
    from .validator import validate_wav_file
    try:
        result = validate_wav_file(path)
        with wave.open(str(path),'rb') as w:
            expected = w.getnframes()*w.getnchannels()*w.getsampwidth()
            actual = len(w.readframes(w.getnframes()))
            result['pcm_integrity'] = actual==expected and w.getsampwidth()==2
        result['valid'] = result['valid'] and result['pcm_integrity']
        return result
    except (OSError,EOFError,wave.Error) as exc:
        return dict(valid=False,error=str(exc),pcm_integrity=False)

def generate(request, *, engine=None, allow_external=False):
    assert_new(request)
    if request.provider == 'qwen_local': return (engine or QwenLocal()).generate(request)
    if request.provider == 'gemini':
        if not allow_external: raise PermissionError('Gemini desativado: autorização explícita necessária')
        from .config import TTSRequestConfig
        from .generator import generate_speech
        return generate_speech(TTSRequestConfig(text=request.text, output_path=Path(request.output),
            model=request.model, voice=request.voice, language=request.language, style=request.style))
    raise ValueError('Provedor desconhecido')
