"""Create mission evidence manifest after all outputs are final."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
baseline=json.loads((OUT/'baseline.json').read_text())
allowed={'.gitignore','scripts/tts/__init__.py'}
preserved=[]
changed=[]
for row in baseline:
    p=ROOT/row['path']
    same=p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    if same: preserved.append(row['path'])
    else: changed.append(row['path'])
assert set(changed)==allowed, changed
prior_wavs=[x for x in preserved if x.endswith('.wav')]
assert len(prior_wavs)==11
files=[ROOT/'.gitignore',ROOT/'AGENTS.md',ROOT/'scripts/tts/__init__.py',
       ROOT/'scripts/tts/local.py',ROOT/'scripts/tts/local_cli.py',ROOT/'scripts/tts/samples_local.py',
       ROOT/'documentos/AUDITORIA_INFRA_001.md',ROOT/'documentos/PIPELINE_PRODUCAO.md',ROOT/'documentos/RELATORIO_INFRA_001.md']
for directory in (OUT,ROOT/'audio/narracoes/TESTES_LOCAIS_001',ROOT/'audio/perfis',ROOT/'backups/infra_001'):
    files.extend(p for p in directory.rglob('*') if p.is_file() and not any(x in p.parts for x in ('pip_cache','__pycache__')) and p.name!='mission_manifest.json')
rows=[]
for p in sorted(set(files)):
    rows.append(dict(path=p.relative_to(ROOT).as_posix(),size=p.stat().st_size,
        sha256=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()))
result=dict(preserved_count=len(preserved),intentional_changes=changed,
    preserved_prior_wavs=prior_wavs,files=rows)
(OUT/'mission_manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('PRESERVED',len(preserved),'INTENTIONAL',len(changed),'PRIOR WAVS',len(prior_wavs),'EVIDENCE FILES',len(rows))
