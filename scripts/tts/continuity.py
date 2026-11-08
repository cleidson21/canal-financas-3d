"""Read-only technical continuity and canonical timing -> finalizer adapter."""
import argparse
import json
from pathlib import Path
import numpy as np
from .generation_policy import ROOT, PROFILE, read, sha
from .local import validate_local_wav
from scripts.pipeline_v3.audio_finalizer import load_wav_mono_float32, compute_audio_levels, resolve_ffmpeg_binaries
import subprocess

def inspect_audio(path):
    path=Path(path)
    validation=validate_local_wav(path)
    if not validation['valid']:raise ValueError(f'WAV inválido: {path}')
    samples,sr,channels,duration=load_wav_mono_float32(path)
    window=max(1,round(sr*0.02))
    speech=[samples[i:i+window] for i in range(0,len(samples),window)
        if np.sqrt(np.mean(samples[i:i+window]**2))>=10**(-45/20)]
    return dict(path=str(path),sha256=sha(path),validation=validation,duration=duration,
        full_levels=compute_audio_levels(samples),speech_levels=compute_audio_levels(np.concatenate(speech) if speech else samples[:0]),
        sample_rate=sr,channels=channels)

def finalizer_timing(timing):
    return dict(source='derived in memory from canonical episode timing; no source modification',
        phrases=[dict(id=f"{segment['id']}_F{phrase['indice']+1:02d}",text=phrase['texto'],
            start_sec=phrase['inicio_s'],end_sec=phrase['fim_s'])
            for segment in timing['segmentos'] for phrase in segment['frases']])

def compare(paths):
    profile=read(PROFILE)
    reference=inspect_audio(ROOT/profile['approved_sample_id'])
    results=[]
    for path in paths:
        item=inspect_audio(path)
        item['speech_rms_difference_db']=round(item['speech_levels']['rms_dbfs']-reference['speech_levels']['rms_dbfs'],2)
        item['format_matches_reference']=(item['sample_rate'],item['channels'])==(reference['sample_rate'],reference['channels'])
        item['loudness_review_flag']=abs(item['speech_rms_difference_db'])>3
        item['timbre_accent_expressiveness']='not assessed by acoustic metrics; human listening required'
        results.append(item)
    return dict(reference=reference,candidates=results,human_approval_required=True,automatic_processing=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('wav',nargs='+',type=Path)
    p.add_argument('--output',type=Path);a=p.parse_args()
    result=compare(a.wav)
    if a.output:
        with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False)
    else:print(json.dumps(result,indent=2,ensure_ascii=False))
