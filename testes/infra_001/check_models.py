"""Verify all downloaded files with sizes and SHA256 LFS identities from HF API."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
env = json.loads((ROOT/'testes/infra_001/environment.json').read_text())
m = env['Qwen3-TTS-12Hz-0.6B-CustomVoice']
rows = []
for info in m['siblings']:
    p = ROOT/'models'/m['sha']/info['rfilename']
    row = dict(path=info['rfilename'], exists=p.is_file())
    if p.is_file():
        row['size'] = p.stat().st_size
        row['expected_size'] = info.get('size')
        row['sha256'] = hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
        row['expected_sha256'] = info.get('lfs',{}).get('sha256')
        row['pass'] = row['size']==row['expected_size'] and (not row['expected_sha256'] or row['sha256']==row['expected_sha256'])
    rows.append(row)
(ROOT/'testes/infra_001/model_integrity.json').write_text(json.dumps(rows,indent=2))
assert all(r.get('pass') for r in rows), rows
print('PASS',len(rows),'model files')
