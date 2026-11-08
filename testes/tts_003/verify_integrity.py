"""Verify canonical preservation, authorized archive/delete map and privacy withdrawal."""
import ast
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
baseline=json.loads((OUT/'baseline.json').read_text())
plan=json.loads((OUT/'retirada_e_arquivo.json').read_text(encoding='utf-8-sig'))
removed={x.replace('\\','/') for group in plan['deletions'] for x in group['files']}
mapping=[(m['source'].replace('\\','/'),m['destination'].replace('\\','/')) for m in plan['moves']]
allowed_changes={'scripts/tts/generator.py','scripts/tts/config.py','scripts/tts/cli.py','AGENTS.md',
    'audio/perfis/narrador_principal.json','documentos/PIPELINE_PRODUCAO.md'}
rows=[]; errors=[];canonical=0
for row in baseline:
    rel=row['path'];p=ROOT/rel
    if rel in removed:
        if p.exists():errors.append('Withdrawal still exists: '+rel)
        rows.append(dict(path=rel,state='deleted_by_explicit_user_request'));continue
    mapped=next((dest+rel[len(source):] for source,dest in mapping if rel==source or rel.startswith(source+'/')),None)
    if mapped:
        if p.exists() or not (ROOT/mapped).is_file() or sha(ROOT/mapped)!=row['sha256']:errors.append('Archive mismatch: '+rel)
        rows.append(dict(path=rel,state='archived_unchanged',destination=mapped));continue
    if rel in allowed_changes:
        rows.append(dict(path=rel,state='intentional_authorized_update'));continue
    if not p.is_file() or sha(p)!=row['sha256']:errors.append('Unexpected change: '+rel)
    if rel.startswith(('episodios/','personagens/','cenarios/','objetos/','backups/','audio/narracoes/EP001/')) or 'manifest' in p.name.lower() or rel=='timing.json':canonical+=1
    rows.append(dict(path=rel,state='unchanged'))
for rel in ('audio/referencias_vocais/narrador_br_001','models/voice_prompts',
    'audio/narracoes/TESTES_LOCAIS_002/qwen_base_br_V1.wav'):
    if (ROOT/rel).exists():errors.append('Personal artifact still present: '+rel)
for p in (ROOT/'scripts/tts').glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
result=dict(errors=errors,canonical_and_historical_manifest_files_verified=canonical,
    states={state:sum(r['state']==state for r in rows) for state in {r['state'] for r in rows}},files=rows)
(OUT/'integrity.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
assert not errors,errors
print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
