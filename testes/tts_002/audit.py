"""Read-only snapshot, dependency/GPU checks and public model metadata."""
import hashlib
import importlib.metadata as md
import json
from pathlib import Path
import shutil
import subprocess
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent

def main():
    baseline=OUT/'baseline.json'
    if not baseline.exists():
        rows=[]
        for p in ROOT.rglob('*'):
            if not p.is_file() or any(x in p.parts for x in ('venvs','models','__pycache__','pip_cache','.git')) or 'tts_002' in p.parts: continue
            rows.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()))
        baseline.write_text(json.dumps(rows,indent=2),encoding='utf-8')
    result={'disk':shutil.disk_usage(ROOT)._asdict()}
    for key,cmd in {'gpu':['nvidia-smi'],'ollama':['ollama','ps'],'pip_check':[str(ROOT/'venvs/tts_local/Scripts/python.exe'),'-m','pip','check']}.items():
        r=subprocess.run(cmd,capture_output=True,text=True,errors='replace')
        result[key]=dict(code=r.returncode,stdout=r.stdout,stderr=r.stderr)
    for model in ('Qwen/Qwen3-TTS-12Hz-0.6B-Base','Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign','rhasspy/piper-voices'):
        url='https://huggingface.co/api/models/'+model+'?blobs=true'
        result[model]=json.load(urllib.request.urlopen(url,timeout=30))
    for name in ('faber','cadu'):
        url=f'https://huggingface.co/rhasspy/piper-voices/raw/main/pt/pt_BR/{name}/medium/MODEL_CARD'
        result['piper_'+name+'_card']=urllib.request.urlopen(url,timeout=30).read().decode()
    (OUT/'environment.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('disk',result['disk'])
    for key in ('Qwen/Qwen3-TTS-12Hz-0.6B-Base','Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign'):
        m=result[key]; print(key,m['sha'],sum(x.get('size',0) for x in m['siblings']),[(x['rfilename'],x.get('size')) for x in m['siblings'] if x.get('size',0)>100000000])
    print(result['piper_faber_card']); print(result['piper_cadu_card'])

if __name__=='__main__':main()
