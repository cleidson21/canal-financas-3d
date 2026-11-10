"""Freeze TTS-003 source/config/evidence; archived weights retain prior manifests."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
paths=[ROOT/p for p in ('AGENTS.md','audio/perfis/narrador_principal.json',
    'audio/perfis/politica_geracao.json','audio/perfis/autorizacao_geracao.modelo.json',
    'scripts/tts/config.py','scripts/tts/generator.py','scripts/tts/cli.py',
    'scripts/tts/generation_policy.py','scripts/tts/continuity.py','scripts/tts/plan_generation.py',
    'documentos/RELATORIO_TTS_003.md','documentos/POLITICA_NARRACAO_E_COTAS.md',
    'documentos/PIPELINE_PRODUCAO.md','arquivo/tts_locais_rejeitados/README.md',
    'audio/perfis/historico/TTS_002/perfis_rejeitados.json')]
for folder in ('testes/tts_003','backups/tts_003_codigo_antes'):
    paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='manifest.json')
rows=[]
for p in sorted(set(paths)):
    with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    rows.append(dict(path=p.relative_to(ROOT).as_posix(),size=p.stat().st_size,sha256=digest))
with (ROOT/'testes/tts_003/manifest.json').open('x',encoding='utf-8') as f:json.dump(rows,f,indent=2)
print('TTS-003 evidence frozen:',len(rows),'files; Puck production audio unchanged')
