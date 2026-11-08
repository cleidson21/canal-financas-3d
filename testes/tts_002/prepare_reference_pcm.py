"""Local technical conversion; preserve original M4A and never overwrite WAV."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.pipeline_v3.audio_finalizer import resolve_ffmpeg_binaries
folder=ROOT/'audio/referencias_vocais/narrador_br_001'
source=folder/'referencia.wav.m4a'; dest=folder/'referencia.wav'
if dest.exists(): raise FileExistsError(dest)
before=hashlib.sha256(source.read_bytes()).hexdigest()
ffmpeg,ffprobe=resolve_ffmpeg_binaries()
original=subprocess.run([ffprobe,'-v','error','-show_streams','-show_format','-of','json',str(source)],capture_output=True,text=True,check=True)
args=[ffmpeg,'-v','error','-n','-i',str(source),'-map','0:a:0','-ac','1','-ar','24000','-c:a','pcm_s16le',str(dest)]
subprocess.run(args,capture_output=True,check=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
result=dict(source_sha256=before,source_probe=json.loads(original.stdout),command=args,
    wav_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),effects=False,
    original_preserved=True,transcript_verified=False,authorization_pending=True)
(ROOT/'testes/tts_002/reference_conversion.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
