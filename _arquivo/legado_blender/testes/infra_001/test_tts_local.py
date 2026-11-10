import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.tts.local import Request, QwenLocal, generate, assert_new

class Safety(unittest.TestCase):
    def test_existing_wav_and_sidecar_are_protected(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as d:
            p = Path(d)/'approved.wav'; p.write_bytes(b'protected')
            before = p.read_bytes()
            with self.assertRaises(FileExistsError): generate(Request('teste',p))
            self.assertEqual(p.read_bytes(),before)
            q = Path(d)/'pending.wav'
            Path(str(q)+'.meta.json').write_text('{"approved": true}')
            with self.assertRaises(FileExistsError): assert_new(Request('teste',q))

    def test_external_disabled_and_unknown_provider(self):
        with self.assertRaises(PermissionError): generate(Request('teste',Path('unused.wav'),provider='gemini'))
        with self.assertRaises(ValueError): generate(Request('teste',Path('unused.wav'),provider='other'))

    def test_missing_model_never_downloads(self):
        with patch('socket.socket',side_effect=AssertionError('Network forbidden')):
            with self.assertRaises(FileNotFoundError): QwenLocal(ROOT/'models/missing_fixture').load()

    def test_absent_gpu_fails_without_loading_provider(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as d:
            Path(d,'model.safetensors').touch()
            fake = SimpleNamespace(cuda=SimpleNamespace(is_available=lambda:False))
            with patch.dict(sys.modules,{'torch':fake}):
                with self.assertRaisesRegex(RuntimeError,'CUDA indisponível'): QwenLocal(d).load()

    def test_low_vram_fails_without_loading_provider(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as d:
            Path(d,'model.safetensors').touch()
            fake = SimpleNamespace(cuda=SimpleNamespace(is_available=lambda:True, mem_get_info=lambda:(1,8*1024**3)))
            with patch.dict(sys.modules,{'torch':fake}):
                with self.assertRaisesRegex(RuntimeError,'4 GiB'): QwenLocal(d).load()

    def test_style_rejected_before_loading(self):
        with self.assertRaises(ValueError): generate(Request('teste',Path('unused.wav'),style='dramatic'))

    def test_config_reproducible(self):
        from dataclasses import asdict
        a = asdict(Request('teste',Path('test.wav')))
        self.assertEqual(a,asdict(Request('teste',Path('test.wav'))))
        self.assertEqual(a['seed'],42)

    def test_truncated_wav_is_rejected(self):
        import wave
        import math
        import struct
        from scripts.tts.local import validate_local_wav
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as d:
            p=Path(d)/'truncated.wav'
            with wave.open(str(p),'wb') as w:
                w.setparams((1,2,24000,0,'NONE','not compressed'))
                w.writeframes(b''.join(struct.pack('<h',int(10000*math.sin(i*0.1))) for i in range(24000)))
            self.assertTrue(validate_local_wav(p)['valid'])
            p.write_bytes(p.read_bytes()[:-5000])
            self.assertFalse(validate_local_wav(p)['valid'])

    def test_silent_wav_and_clipped_signal_are_rejected(self):
        import wave
        import numpy as np
        from scripts.tts.local import validate_local_wav, acoustic_checks
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as d:
            p=Path(d)/'silence.wav'
            with wave.open(str(p),'wb') as w:
                w.setparams((1,2,24000,0,'NONE','not compressed'))
                w.writeframes(b'\0\0'*24000)
            self.assertFalse(validate_local_wav(p)['valid'])
        self.assertFalse(acoustic_checks(np.ones(24000,dtype=np.float32),24000)['pass'])

    def test_local_import_does_not_load_google(self):
        p = subprocess.run([sys.executable,'-c',
            "import sys; import scripts.tts.local; assert 'google.genai' not in sys.modules"],cwd=ROOT,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)

    def test_provisional_profile_cannot_generate_production(self):
        from scripts.tts.local import request_from_profile
        with self.assertRaises(PermissionError):
            request_from_profile(ROOT/'audio/perfis/narrador_principal.json','teste',Path('unused.wav'))

    def test_prior_assets_preserved(self):
        baseline = json.loads((Path(__file__).parent/'baseline.json').read_text())
        allowed = {'.gitignore','scripts/tts/__init__.py'}
        for row in baseline:
            if row['path'] in allowed: continue
            p = ROOT/row['path']
            self.assertTrue(p.is_file(),row['path'])
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),row['sha256'],row['path'])
        by_path={r['path']:r['sha256'] for r in baseline}
        for source,backup in (('.gitignore','gitignore_original.txt'),('scripts/tts/__init__.py','tts_init_original.py')):
            self.assertEqual(hashlib.sha256((ROOT/'backups/infra_001'/backup).read_bytes()).hexdigest(),by_path[source])

if __name__ == '__main__': unittest.main(verbosity=2)
