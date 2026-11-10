"""Read-only inventory and environment evidence for INFRA-001."""
import ast
import ctypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.request
import winreg

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent

def run(args):
    try:
        p = subprocess.run(args, capture_output=True, text=True, errors='replace', timeout=60)
        return dict(command=args, code=p.returncode, stdout=p.stdout, stderr=p.stderr)
    except Exception as e:
        return dict(command=args, error=str(e))

def get(url, data=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                 headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=30))

def main():
    evidence = {}
    files = []
    for p in ROOT.rglob('*'):
        if not p.is_file() or any(x in p.parts for x in ('venvs', 'models', '__pycache__', '.git')):
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith('testes/infra_001/'):
            continue
        files.append(dict(path=rel, size=p.stat().st_size, mtime=p.stat().st_mtime,
                          sha256=hashlib.file_digest(p.open('rb'), 'sha256').hexdigest()))
    baseline = OUT / 'baseline.json'
    if not baseline.exists():
        baseline.write_text(json.dumps(files, indent=2), encoding='utf-8')
    evidence['syntax_errors'] = []
    for p in ROOT.joinpath('scripts').rglob('*.py'):
        try:
            ast.parse(p.read_text(encoding='utf-8-sig'))
        except Exception as e:
            evidence['syntax_errors'].append([str(p.relative_to(ROOT)), str(e)])
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as k:
        evidence['cpu'] = winreg.QueryValueEx(k, 'ProcessorNameString')[0]
    class Memory(ctypes.Structure):
        _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [(x, ctypes.c_ulonglong) for x in ('total','available','page','availpage','virtual','availvirtual','extended')]
    mem = Memory(); mem.length = ctypes.sizeof(mem)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
    evidence['ram'] = dict(total=mem.total, available=mem.available)
    for name, args in {'python':['python','--version'], 'gpu':['nvidia-smi'], 'ollama':['ollama','--version'], 'models':['ollama','list'], 'running':['ollama','ps']}.items():
        evidence[name] = run(args)
    for route in ('version','tags','ps'):
        try: evidence['ollama_'+route] = get('http://127.0.0.1:11434/api/'+route)
        except Exception as e: evidence['ollama_'+route] = str(e)
    try:
        evidence['ollama_qwen_show'] = get('http://127.0.0.1:11434/api/show', {'model':'jstzwhc/Qwen3-TTS'})
    except Exception as e: evidence['ollama_qwen_show'] = str(e)
    for model in ('Qwen3-TTS-12Hz-0.6B-CustomVoice','Qwen3-TTS-Tokenizer-12Hz'):
        try: evidence[model] = get('https://huggingface.co/api/models/Qwen/'+model+'?blobs=true')
        except Exception as e: evidence[model] = str(e)
    OUT.joinpath('environment.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in evidence.items() if k in ('cpu','ram','syntax_errors','ollama_version')}, indent=2))
    for model in ('Qwen3-TTS-12Hz-0.6B-CustomVoice','Qwen3-TTS-Tokenizer-12Hz'):
        m = evidence[model]
        if isinstance(m,dict): print(model, m.get('sha'), [(x['rfilename'],x.get('size')) for x in m.get('siblings',[])])

if __name__ == '__main__': main()
