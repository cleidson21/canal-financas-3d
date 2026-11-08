"""Baseline before TTS-003. Excludes disposable runtimes/weights, not production."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
rows=[]
for p in ROOT.rglob('*'):
    if not p.is_file() or any(x in p.parts for x in ('venvs','models','__pycache__','pip_cache','.git','tts_003')):continue
    with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    rows.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=digest,size=p.stat().st_size))
with (OUT/'baseline.json').open('x',encoding='utf-8') as f:json.dump(rows,f,indent=2)
backup=ROOT/'backups/tts_003_codigo_antes'
for rel in ('scripts/tts/generator.py','scripts/tts/config.py','scripts/tts/cli.py','AGENTS.md','audio/perfis/narrador_principal.json'):
    p=backup/rel;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write((ROOT/rel).read_bytes())
print('Baseline',len(rows),'files; production preserved before modifications')
