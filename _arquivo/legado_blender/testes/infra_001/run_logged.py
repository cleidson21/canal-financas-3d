"""Capture native return codes and UTF-8/binary streams without shell redirection."""
import json
from pathlib import Path
import subprocess
import sys
import time

if __name__=='__main__':
    directory=Path(__file__).resolve().parent
    label=sys.argv[1]
    command=sys.argv[2:]
    started=time.time()
    with (directory/(label+'_stdout.log')).open('wb') as out, (directory/(label+'_stderr.log')).open('wb') as err:
        p=subprocess.run(command,stdout=out,stderr=err)
    result=dict(command=command,returncode=p.returncode,elapsed_seconds=time.time()-started)
    (directory/(label+'_exit.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result))
    sys.exit(p.returncode)
