"""Independent decode, preservation and resource summary, without synthesis."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.pipeline_v3.audio_finalizer import resolve_ffmpeg_binaries

def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

if __name__=='__main__':
    ffmpeg,ffprobe=resolve_ffmpeg_binaries()
    rows=[]
    for p in sorted((ROOT/'audio/narracoes/TESTES_LOCAIS_002').glob('*.wav')):
        meta=json.loads(Path(str(p)+'.meta.json').read_text(encoding='utf-8'))
        probe=subprocess.run([ffprobe,'-v','error','-show_format','-show_streams','-of','json',str(p)],capture_output=True,text=True,check=True)
        subprocess.run([ffmpeg,'-v','error','-i',str(p),'-f','null','-'],capture_output=True,check=True)
        assert digest(p)==meta['sha256']
        rows.append(dict(file=p.name,ffmpeg_decode=True,ffprobe=json.loads(probe.stdout),
            sha256=meta['sha256'],generation_seconds=meta['generation_seconds'],
            rss_peak_bytes=max(r['process_rss'] for r in meta['resources']),
            total_gpu_peak_mib_sampled=max(r.get('gpu_total_used_mib',0) for r in meta['resources'])))
    baseline=json.loads((ROOT/'testes/tts_002/baseline.json').read_text())
    changed=[r['path'] for r in baseline if not (ROOT/r['path']).is_file() or digest(ROOT/r['path'])!=r['sha256']]
    assert changed==['audio/perfis/narrador_principal.json'] or set(changed)=={'audio/perfis/narrador_principal.json'},changed
    wavs=[r for r in baseline if r['path'].endswith('.wav')]
    for r in wavs:assert digest(ROOT/r['path'])==r['sha256']
    for p in list((ROOT/'scripts/tts').glob('*.py'))+list((ROOT/'testes/tts_002').glob('*.py')):
        ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
    old=(ROOT/'testes/infra_001/requirements-lock.txt').read_text(encoding='utf-8-sig').splitlines()
    new=(ROOT/'testes/tts_002/requirements-lock.txt').read_text(encoding='utf-8-sig').splitlines()
    old=set(filter(None,old)); new=set(filter(None,new))
    assert not old-new,old-new
    result=dict(audio=rows,prior_file_count=len(baseline),unchanged_prior_files=len(baseline)-len(changed),
        intentional_changes=changed,prior_wavs_preserved=len(wavs),removed_dependencies=sorted(old-new),added_dependencies=sorted(new-old))
    (ROOT/'testes/tts_002/validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='audio'},indent=2))
