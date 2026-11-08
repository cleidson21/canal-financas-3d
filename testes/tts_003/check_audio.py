"""Read approved assets, FFmpeg decode and derive timing without rendering/muxing."""
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.tts.continuity import compare, finalizer_timing
from scripts.tts.generation_policy import read,PROFILE,sha
from scripts.pipeline_v3.audio_finalizer import resolve_ffmpeg_binaries
OUT=Path(__file__).resolve().parent
profile=read(PROFILE)
paths=[ROOT/p for p in profile['approved_assets'] if '/segmentos/' in p]
result=compare(paths)
timing=read(ROOT/'episodios/EP001_dinheiro/timing.json')
assert abs(result['reference']['duration']-timing['duracao_narracao_s'])<1e-6
for rel,expected in profile['approved_assets'].items():assert sha(ROOT/rel)==expected
ffmpeg,ffprobe=resolve_ffmpeg_binaries()
audio=ROOT/profile['approved_sample_id']
subprocess.run([ffmpeg,'-v','error','-i',str(audio),'-f','null','-'],capture_output=True,check=True)
probe=subprocess.run([ffprobe,'-v','error','-show_format','-show_streams','-of','json',str(audio)],capture_output=True,text=True,check=True)
result['ffprobe']=json.loads(probe.stdout)
result['ffmpeg_decode_pass']=True
adapted=finalizer_timing(timing)
assert len(adapted['phrases'])==sum(len(s['frases']) for s in timing['segmentos'])
assert all(0<=p['start_sec']<p['end_sec']<=102.12 for p in adapted['phrases'])
for name,value in (('audio_continuity.json',result),('timing_finalizador_EP001.json',adapted)):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,ensure_ascii=False)
print('Approved audio duration',result['reference']['duration'],'segments',len(paths),'finalizer phrases',len(adapted['phrases']))
