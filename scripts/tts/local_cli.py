"""Reusable offline CLI: python -m scripts.tts.local_cli --help."""
import argparse
import json
from pathlib import Path
from .local import Request, generate, MODEL_ID, request_from_profile

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--provider', choices=['qwen_local','gemini'], default='qwen_local')
    p.add_argument('--model', default=MODEL_ID)
    p.add_argument('--voice',default='Ryan')
    p.add_argument('--language',default='Portuguese')
    p.add_argument('--text-file',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--style',default='')
    p.add_argument('--seed',type=int,default=42)
    p.add_argument('--profile',type=Path,help='Perfil aprovado; parâmetros vêm integralmente do JSON')
    a = p.parse_args()
    text = a.text_file.read_text(encoding='utf-8-sig')
    if a.profile:
        import sys
        if any(x.split('=')[0] in ('--voice','--model','--language','--style','--seed','--provider') for x in sys.argv[1:]):
            p.error('Com --profile, não sobrescreva parâmetros aprovados')
        request = request_from_profile(a.profile,text,a.output)
    else:
        request = Request(text=text,output=a.output,voice=a.voice,provider=a.provider,
            model=a.model,language=a.language,style=a.style,seed=a.seed)
    result = generate(request)
    print(json.dumps(result,indent=2,ensure_ascii=False,default=str))

if __name__ == '__main__': main()
