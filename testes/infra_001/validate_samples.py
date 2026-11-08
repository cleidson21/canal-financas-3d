"""Read-only sample validation, plus metadata enrichment of this mission's files."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import wave

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from scripts.tts.local import validate_local_wav, acoustic_checks, REVISION
from scripts.tts.samples_local import TEXT, CONSISTENCY
from scripts.pipeline_v3.audio_finalizer import resolve_ffmpeg_binaries

def main():
    out=ROOT/'audio/narracoes/TESTES_LOCAIS_001'
    ffmpeg,ffprobe=resolve_ffmpeg_binaries()
    defaults=json.loads((ROOT/'models'/REVISION/'generation_config.json').read_text())
    expected=[('voz_A.wav','Ryan',TEXT),('voz_B.wav','Aiden',TEXT),
        ('voz_C.wav','Uncle_Fu',TEXT),('voz_A_consistencia.wav','Ryan',CONSISTENCY)]
    results=[]
    for filename,voice,text in expected:
        p=out/filename
        meta_path=Path(str(p)+'.meta.json')
        meta=json.loads(meta_path.read_text(encoding='utf-8'))
        assert meta['request']['text']==text and meta['request']['voice']==voice
        assert not meta['approved']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['sha256']
        acoustic=validate_local_wav(p)
        with wave.open(str(p),'rb') as w:
            sr=w.getframerate()
            waveform=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
        additional=acoustic_checks(waveform,sr)
        decode=subprocess.run([ffmpeg,'-v','error','-i',str(p),'-f','null','-'],capture_output=True)
        probe=subprocess.run([ffprobe,'-v','error','-show_streams','-of','json',str(p)],capture_output=True,text=True)
        assert acoustic['valid'] and additional['pass'] and decode.returncode==0 and probe.returncode==0
        assert len(json.loads(probe.stdout)['streams'])==1
        meta['effective_generation_settings']={**defaults,**meta['request']['synthesis'],'non_streaming_mode':True}
        meta['ffmpeg_decode_pass']=True
        meta['postwrite_validation']=dict(acoustic=acoustic,additional=additional)
        meta_path.write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf-8')
        results.append(dict(file=filename,voice=voice,pass_technical=True,duration=acoustic['duration_seconds'],
            generation_seconds=meta['elapsed_seconds'],sha256=meta['sha256']))
    resources=json.loads((out/'resources.json').read_text())
    summary=dict(samples=results,all_technical_pass=True,human_approval=False,
        resource_sampling_interval='approximately 0.5 seconds plus nvidia-smi process time',
        gpu_total_peak_mib_sampled=max(r.get('gpu_total_used_mib',0) for r in resources),
        process_rss_peak_bytes_sampled=max(r['process_rss'] for r in resources),
        system_ram_peak_used_bytes_sampled=max(r['system_ram_used'] for r in resources))
    (out/'validation_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
