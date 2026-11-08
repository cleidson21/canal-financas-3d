import io
import json
from pathlib import Path
import socket
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import wave
from datetime import datetime,timedelta,timezone

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.tts import generation_policy as gate
from scripts.tts import generator as gen
from scripts.tts.config import TTSRequestConfig

class Guards(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.dir=Path(self.tmp.name)
        self.profile=gate.read(gate.PROFILE)
        self.profile['generation_enabled']=True
        self.policy=gate.read(gate.POLICY);self.policy['remote_generation_enabled']=True
        (self.dir/'profile.json').write_text(json.dumps(self.profile),encoding='utf-8')
        (self.dir/'policy.json').write_text(json.dumps(self.policy),encoding='utf-8')
        self.patches=[patch.object(gate,'PROFILE',self.dir/'profile.json'),patch.object(gate,'POLICY',self.dir/'policy.json'),
            patch.object(gate,'STATE',self.dir/'state'),patch.object(gen,'get_api_key_silently',return_value='synthetic-test-key'),
            patch.object(socket,'socket',side_effect=AssertionError('Network forbidden in tests'))]
        for p in self.patches:p.start()
        self.cfg=TTSRequestConfig(text='Fixture sintética; nenhuma chamada real.',style=self.profile['style_prompt'],output_path=self.dir/'new.wav')
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.tmp.cleanup()
    def permit(self,**overrides):
        now=datetime.now(timezone.utc)
        p=dict(permit_id='synthetic-permit-001',project_id='synthetic-project',api_key_sha256=__import__('hashlib').sha256(b'synthetic-test-key').hexdigest(),
            request_sha256=gate.request_identity(self.cfg),billing_tier='free',billing_enabled=False,
            checked_at=now.isoformat(),expires_at=(now+timedelta(minutes=10)).isoformat(),human_authorized=True,
            model_available=True,tts_free_for_model=True,quota_checked=True,remaining_requests=1,evidence_reference='synthetic fixture only')
        p.update(overrides); path=self.dir/'permit.json';path.write_text(json.dumps(p),encoding='utf-8')
        self.cfg.generation_permit=path
    def client(self,error=None):
        client=Mock()
        client.models.get.return_value=SimpleNamespace(name='models/'+self.cfg.model)
        if error:client.interactions.create.side_effect=error
        else:
            b=io.BytesIO()
            with wave.open(b,'wb') as w:
                w.setparams((1,2,24000,0,'NONE','not compressed'))
                w.writeframes(struct.pack('<h',4000)*12000)
            client.interactions.create.return_value=SimpleNamespace(output_audio=SimpleNamespace(data=b.getvalue(),mime_type='audio/wav',sample_rate=24000,channels=1),usage=None,id='synthetic',status='done')
        return client
    def test_defaults_block_generation_without_client(self):
        self.policy['remote_generation_enabled']=False
        (self.dir/'policy.json').write_text(json.dumps(self.policy))
        with patch.object(gen,'_create_client') as client:
            with self.assertRaises(PermissionError):gen.generate_speech(self.cfg)
            client.assert_not_called()
    def test_voice_model_language_and_style_cannot_change(self):
        for field,value in (('voice','Ryan'),('model','gemini-3.8-flash-tts'),('language','en-US'),('style','trocar estilo')):
            original=getattr(self.cfg,field);setattr(self.cfg,field,value)
            with patch.object(gen,'_create_client') as client:
                with self.assertRaises(PermissionError):gen.generate_speech(self.cfg)
                client.assert_not_called()
            setattr(self.cfg,field,original)
    def test_paid_unknown_stale_wrong_key_and_request_are_blocked(self):
        cases=[dict(billing_tier='paid',billing_enabled=True),dict(billing_tier='unknown'),dict(api_key_sha256='wrong'),
            dict(request_sha256='wrong'),dict(quota_checked=False),dict(remaining_requests=0),
            dict(checked_at=(datetime.now(timezone.utc)-timedelta(hours=2)).isoformat())]
        for overrides in cases:
            self.permit(**overrides)
            with patch.object(gen,'_create_client') as client:
                with self.assertRaises(PermissionError):gen.generate_speech(self.cfg)
                client.assert_not_called()
    def test_existing_approved_assets_reused_even_with_overwrite(self):
        self.cfg.output_path=ROOT/self.profile['approved_sample_id'];self.cfg.overwrite=True
        with patch.object(gen,'_create_client') as client:
            self.assertEqual(gen.generate_speech(self.cfg)['status'],'skipped_approved')
            client.assert_not_called()
    def test_orphan_sidecar_and_existing_unapproved_wav_protected(self):
        Path(str(self.cfg.output_path)+'.meta.json').write_text('{}')
        with self.assertRaises(FileExistsError):gen.generate_speech(self.cfg)
        self.cfg.output_path=self.dir/'existing.wav';self.cfg.output_path.write_bytes(b'untouched');self.cfg.overwrite=True
        self.assertEqual(gen.generate_speech(self.cfg)['status'],'skipped_existing')
        self.assertEqual(self.cfg.output_path.read_bytes(),b'untouched')
    def test_quota_error_trips_block_once_no_retry(self):
        self.permit()
        class Quota(Exception):code=429
        client=self.client(Quota('synthetic resource exhausted'))
        with patch.object(gen,'_create_client',return_value=client):
            self.assertEqual(gen.generate_speech(self.cfg)['status'],'error')
        self.assertEqual(client.interactions.create.call_count,1)
        self.assertTrue((self.dir/'state/quota_block.json').exists())
        with patch.object(gen,'_create_client') as factory:
            with self.assertRaises(PermissionError):gen.generate_speech(self.cfg)
            factory.assert_not_called()
    def test_single_use_and_success_never_claims_free(self):
        self.permit();client=self.client()
        with patch.object(gen,'_create_client',return_value=client):result=gen.generate_speech(self.cfg)
        self.assertEqual(result['metadata']['generation_authorization']['actual_charge_status'],'unverified')
        self.assertFalse(result['metadata']['approved'])
        with self.assertRaises(FileExistsError):gate.reserve_generation(self.cfg,'synthetic-test-key')
    def test_sdk_retry_configuration_and_remote_check_off(self):
        with patch.object(gen.genai,'Client') as constructor:
            gen._create_client()
            self.assertEqual(constructor.call_args.kwargs['http_options'].retry_options.attempts,1)
        with patch.object(gen,'_create_client') as factory:
            self.assertEqual(gen.verify_model_access()['error']['category'],'remote_checks_disabled')
            factory.assert_not_called()

if __name__=='__main__':unittest.main(verbosity=2)
