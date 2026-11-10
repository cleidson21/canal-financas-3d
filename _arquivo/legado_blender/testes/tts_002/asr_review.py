"""Existing local ASR only; recognized text is a review aid, not approval."""
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
os.environ['HF_HUB_OFFLINE']='1'
from faster_whisper import WhisperModel
import numpy as np
from scripts.pipeline_v3.audio_finalizer import resolve_ffmpeg_binaries

if __name__=='__main__':
    ffmpeg,_=resolve_ffmpeg_binaries()
    model=WhisperModel('small',device='cpu',compute_type='int8',local_files_only=True,cpu_threads=4)
    rows=[]
    for file in sys.argv[2:]:
        path=Path(file)
        pcm=subprocess.run([ffmpeg,'-v','error','-i',str(path),'-ac','1','-ar','16000','-f','s16le','-'],capture_output=True,check=True).stdout
        samples=np.frombuffer(pcm,dtype='<i2').astype(np.float32)/32768
        segs,_=model.transcribe(samples,language='pt',beam_size=5,vad_filter=False)
        text=' '.join(s.text.strip() for s in segs)
        rows.append(dict(file=str(path),asr_text=text,human_review_required=True))
        print(text,flush=True)
    with Path(sys.argv[1]).open('x',encoding='utf-8') as f: json.dump(rows,f,indent=2,ensure_ascii=False)
