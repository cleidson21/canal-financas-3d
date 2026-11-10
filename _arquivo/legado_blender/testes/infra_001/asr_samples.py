"""Use the existing local Whisper small, CPU only. Never download a model."""
import difflib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'

def norm(s): return re.sub(r'[^\w\s]', '', s.lower()).split()

def main():
    import numpy as np
    from faster_whisper import WhisperModel
    from scripts.pipeline_v3.audio_finalizer import resolve_ffmpeg_binaries
    ffmpeg, ffprobe = resolve_ffmpeg_binaries()
    model = WhisperModel('small', device='cpu', compute_type='int8', local_files_only=True, cpu_threads=4)
    rows=[]
    for path in sorted((ROOT/'audio/narracoes/TESTES_LOCAIS_001').glob('*.wav')):
        meta=json.loads(Path(str(path)+'.meta.json').read_text(encoding='utf-8'))
        pcm=subprocess.run([ffmpeg,'-v','error','-i',str(path),'-ac','1','-ar','16000','-f','s16le','-'],capture_output=True,check=True).stdout
        probe=subprocess.run([ffprobe,'-v','error','-show_streams','-show_format','-of','json',str(path)],capture_output=True,check=True,text=True)
        audio=np.frombuffer(pcm,dtype=np.int16).astype(np.float32)/32768
        segments,_=model.transcribe(audio,language='pt',vad_filter=False,beam_size=5)
        text=' '.join(s.text.strip() for s in segments)
        reference=meta['request']['text']
        a,b=norm(reference),norm(text)
        diffs=[dict(kind=tag,expected=a[i:j],recognized=b[k:l]) for tag,i,j,k,l in difflib.SequenceMatcher(None,a,b).get_opcodes() if tag!='equal']
        row=dict(file=path.name,reference=reference,asr_text=text,differences=diffs,
            ffmpeg_decode_pass=True,ffprobe=json.loads(probe.stdout),
            asr_model='existing faster-whisper small',local_files_only=True,
            interpretation='ASR differences require listening; not confirmed pronunciation errors')
        rows.append(row)
        print(path.name,text,flush=True)
    (ROOT/'audio/narracoes/TESTES_LOCAIS_001/asr_validation.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')

if __name__=='__main__': main()
