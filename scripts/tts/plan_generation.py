"""Plan a future Puck request offline; never checks API or creates a permit."""
import argparse
import hashlib
import json
from pathlib import Path
from .config import TTSRequestConfig, get_api_key_silently
from .generation_policy import read, PROFILE, POLICY, request_identity

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--text-file',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--direction',default='')
    p.add_argument('--project-id',default=None)
    a=p.parse_args()
    profile=read(PROFILE)
    text=a.text_file.read_text(encoding='utf-8-sig').strip()
    style=profile['style_prompt']+(' Direção deste trecho: '+a.direction if a.direction else '')
    config=TTSRequestConfig(text=text,style=style,output_path=a.output,
        model=profile['model'],voice=profile['voice_id'],language=profile['language'])
    key=get_api_key_silently()
    print(json.dumps(dict(model=config.model,voice=config.voice,language=config.language,style=config.style,
        text_characters=len(text),text_sha256=hashlib.sha256(text.encode()).hexdigest(),
        output=str(a.output.resolve()),request_sha256=request_identity(config),project_id_declared=a.project_id,
        api_key_sha256=hashlib.sha256(key.encode()).hexdigest() if key else None,
        remote_generation_enabled=read(POLICY)['remote_generation_enabled'],
        quota_status='unknown; review in AI Studio before any request',
        actual_billing_status='unknown; success never proves free',network_calls=0),indent=2,ensure_ascii=False))
