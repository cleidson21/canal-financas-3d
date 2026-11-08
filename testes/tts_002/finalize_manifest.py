"""Freeze TTS-002 deliverable identities; model weights have a separate manifest."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
paths=[ROOT/'scripts/tts/br_local.py',ROOT/'scripts/tts/prepare_br_models.py',
    ROOT/'audio/perfis/narrador_principal.json',ROOT/'documentos/RELATORIO_TTS_002.md',
    ROOT/'documentos/TTS_002_GUIA_VOZ_BR.md',ROOT/'documentos/FICHA_AVALIACAO_TTS_002.md']
for folder in ('testes/tts_002','audio/narracoes/TESTES_LOCAIS_002',
               'audio/referencias_vocais/narrador_br_001','audio/perfis/historico/INFRA_001'):
    paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='manifest.json')
meta=json.loads((ROOT/'audio/narracoes/TESTES_LOCAIS_002/qwen_base_br_V1.wav.meta.json').read_text(encoding='utf-8'))
cache=ROOT/'models/voice_prompts'/meta['voice_prompt']['reuse_test']['cache_id']
paths.extend([cache.with_suffix('.npz'),cache.with_suffix('.json')])
rows=[]
for p in sorted(set(paths)):
    with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    rows.append(dict(path=p.relative_to(ROOT).as_posix(),size=p.stat().st_size,sha256=digest))
(ROOT/'testes/tts_002/manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print('TTS-002 manifest:',len(rows),'files; no production narrator replacement')
