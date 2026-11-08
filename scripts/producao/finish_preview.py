"""Encode continuous S03 frames, mux the approved segment, and compare to V1."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.pipeline_v3.config import EP001_DELIVERIES_DIR
from scripts.pipeline_v3.audio_finalizer import resolve_ffmpeg_binaries,finalize_mp4_with_narration,probe_media_file

def main(spec):
    out=ROOT/spec['output'];cache=out/'cache/render_s03_360x640';videos=out/'videos';videos.mkdir(exist_ok=True)
    segment=next(s for s in json.loads((ROOT/spec['timing']).read_text(encoding='utf-8'))['segmentos'] if s['id']==spec['segment'])
    total=__import__('math').ceil(segment['duracao_s']*30);duration=total/30
    from PIL import Image
    import numpy as np
    hashes=[];delta=[];prev=None
    for frame in range(1,total+1):
        path=cache/f'f_{frame:04d}.png'
        with Image.open(path) as im:
            assert im.size==tuple(spec['resolution']);arr=np.asarray(im.convert('RGB'),dtype='float32')
        hashes.append(hashlib.sha256(arr.astype('uint8').tobytes()).hexdigest())
        if prev is not None:delta.append(float(np.mean(np.abs(arr-prev))))
        prev=arr
    ffmpeg,_=resolve_ffmpeg_binaries()
    def run(args,log):
        with (out/log).open('wb') as stream:subprocess.run([ffmpeg,'-v','warning','-n',*args],stderr=stream,check=True)
    silent=out/'cache/S03_IMAGEM_CONTINUA.mp4'
    if not silent.exists():run(['-framerate','30','-start_number','1','-i',str(cache/'f_%04d.png'),'-frames:v',str(total),'-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)],'encode.log')
    timing=dict(phrases=[dict(id='S03_F'+str(i+1),text=p['texto'],start_sec=p['inicio_s']-segment['inicio_global_s'],end_sec=p['fim_s']-segment['inicio_global_s']) for i,p in enumerate(segment['frases'])])
    audio=ROOT/segment['wav'];preview=videos/'EP001_S03_PROD002_COM_AUDIO_V1.mp4'
    if preview.exists():raise FileExistsError('Preserve existing preview; create a new version.')
    result=finalize_mp4_with_narration(silent,audio,preview,expected_duration_sec=duration,timing_data=timing)
    (out/'testes').mkdir(exist_ok=True)
    (out/'testes/validacao_audio.json').write_text(json.dumps(result,indent=2))
    old=EP001_DELIVERIES_DIR/'EP001_ANIMATIC_V1_SEM_LEGENDAS.mp4'
    clip=out/'cache/S03_V1_MESMO_INTERVALO.mp4'
    if not clip.exists():run(['-ss',str(segment['inicio_global_s']),'-i',str(old),'-t',str(duration),'-map','0:v:0','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p',str(clip)],'clip_V1.log')
    comparison=videos/'COMPARATIVO_V1_ESQUERDA_V2_DIREITA.mp4'
    run(['-i',str(clip),'-i',str(preview),'-filter_complex','[0:v][1:v]hstack=inputs=2[v]','-map','[v]','-map','1:a:0','-frames:v',str(total),'-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(comparison)],'comparison.log')
    runs=[];last=None;count=0
    for h in hashes:
        if last!=h and count:runs.append(count);count=0
        count+=1;last=h
    if count:runs.append(count)
    def decode_check(path):
        before=time.monotonic();r=subprocess.run([ffmpeg,'-v','error','-i',str(path),'-f','null','-'],capture_output=True)
        assert r.returncode==0 and not r.stderr,r.stderr.decode(errors='replace')
        return dict(file=path.name,seconds=time.monotonic()-before,errors=0)
    metrics=dict(rendered_frames=total,unique_pixel_frames=len(set(hashes)),longest_identical_run_frames=max(runs),mean_adjacent_pixel_delta_8bit=float(np.mean(delta)),near_identical_transitions_under_0_5=sum(d<.5 for d in delta),fps=30,duration_video=duration,duration_audio=segment['duracao_s'],preview=preview.name,comparison=comparison.name,full_decode_checks=[decode_check(preview),decode_check(old),decode_check(comparison)],probe=probe_media_file(preview),human_approval=False)
    (out/'testes/validacao_video.json').write_text(json.dumps(metrics,indent=2))
    print(json.dumps({k:v for k,v in metrics.items() if k!='probe'}))

if __name__=='__main__':main(json.loads((ROOT/sys.argv[1]).read_text()))
