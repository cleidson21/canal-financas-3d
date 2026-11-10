"""Read approved WAV in a disposable process; no render/save or production edit."""
import bpy
import json
import math
from pathlib import Path
root=Path(__file__).resolve().parents[2]
audio=root/'audio/narracoes/EP001/EP001_NARRACAO_COMPLETA_V1.wav'
scene=bpy.context.scene
scene.render.fps=30
scene.render.fps_base=1
editor=scene.sequence_editor_create()
strips=getattr(editor,'strips',None)
if strips is None:strips=editor.sequences
strip=strips.new_sound(name='TTS003_APPROVED_PUCK_READONLY',filepath=str(audio),channel=1,frame_start=1)
scene.frame_start=1
scene.frame_end=math.ceil(102.12*30)
result=dict(blender=bpy.app.version_string,audio_path=str(audio),fps=30,
    frame_start=scene.frame_start,frame_end=scene.frame_end,
    strip_duration_frames=strip.frame_final_duration,strip_speed=getattr(strip,'speed_factor',1),
    render_executed=False,blend_saved=False,scene='dedicated factory process only')
assert strip.frame_final_duration>=3063
(root/'testes/tts_003/blender_audio.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
