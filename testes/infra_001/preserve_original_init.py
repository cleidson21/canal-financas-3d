"""Recover the small original initializer from its read contents, hash checked."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
original='''"""Módulo independente de geração de voz (TTS) com Gemini 3.8 TTS API."""

from .config import (
    ALLOWED_MODELS,
    ALTERNATIVE_MODEL,
    DEFAULT_LANGUAGE,
    DEFAULT_MODEL,
    DEFAULT_VOICE,
    DOCUMENTED_VOICES,
    PROJECT_ROOT,
    TTSRequestConfig,
    check_credentials,
)
from .generator import (
    generate_speech,
    mark_as_approved,
    verify_model_access,
)
from .validator import validate_wav_file

__all__ = [
    "ALLOWED_MODELS",
    "ALTERNATIVE_MODEL",
    "DEFAULT_LANGUAGE",
    "DEFAULT_MODEL",
    "DEFAULT_VOICE",
    "DOCUMENTED_VOICES",
    "PROJECT_ROOT",
    "TTSRequestConfig",
    "check_credentials",
    "generate_speech",
    "mark_as_approved",
    "validate_wav_file",
    "verify_model_access",
]
'''
baseline={r['path']:r['sha256'] for r in json.loads((ROOT/'testes/infra_001/baseline.json').read_text())}
out=ROOT/'backups/infra_001'
out.mkdir(exist_ok=True)
texts={'scripts/tts/__init__.py':original,
       '.gitignore':(ROOT/'.gitignore').read_text(encoding='utf-8-sig').replace('# INFRA-001 isolated environments\nvenvs/\nmodels/\ntestes/infra_001/pip_cache/\n','')}
for name,text in texts.items():
    found=False
    for newline in ('\n','\r\n'):
        for count in range(6):
            for bom in (b'',b'\xef\xbb\xbf'):
                data=bom+(text.rstrip('\n').replace('\n',newline)+newline*count).encode('utf-8')
                if hashlib.sha256(data).hexdigest()==baseline[name]:
                    path=out/('tts_init_original.py' if name.endswith('.py') else 'gitignore_original.txt')
                    if not path.exists(): path.write_bytes(data)
                    print('MATCHED ORIGINAL',name,baseline[name]); found=True; break
            if found: break
        if found: break
    if not found: print('NO MATCH; no purported original backup written',name)
