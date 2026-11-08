import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.tts import br_local as br

class Safety(unittest.TestCase):
    def test_missing_reference_fails_before_model(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as d:
            with patch.object(br,'load_base',side_effect=AssertionError('must not load')):
                with self.assertRaises(FileNotFoundError): br.synthesize('qwen_base_local','teste',Path(d)/'out.wav',Path(d))

    def test_puck_copy_is_refused(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as d:
            shutil.copyfile(ROOT/'audio/narracoes/EP001/EP001_NARRACAO_COMPLETA_V1.wav',Path(d)/'referencia.wav')
            (Path(d)/'transcricao.txt').write_text('referência proibida',encoding='utf-8')
            with self.assertRaises(PermissionError): br.inspect_reference(d)

    def test_existing_output_prevents_any_model_load(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as d:
            p=Path(d)/'approved.wav'; p.write_bytes(b'preserved')
            with self.assertRaises(FileExistsError): br.synthesize('qwen_base_local','teste',p)
            self.assertEqual(p.read_bytes(),b'preserved')

    def test_reference_authorization_is_bound_to_hashes(self):
        directory=ROOT/'audio/referencias_vocais/narrador_br_001'
        validated=br.validate_reference(directory)
        self.assertEqual(validated['audio_sha256'],br.sha(directory/'referencia.wav'))
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as d:
            auth=json.loads((directory/'autorizacao.json').read_text(encoding='utf-8'))
            fake={k:v for k,v in validated.items() if k not in ('authorization','authorization_sha256')}
            auth['audio_sha256']='altered'
            (Path(d)/'autorizacao.json').write_text(json.dumps(auth),encoding='utf-8')
            with patch.object(br,'inspect_reference',return_value=fake):
                with self.assertRaises(PermissionError): br.validate_reference(d)
            auth['audio_sha256']=validated['audio_sha256']; auth['commercial_reuse_authorized']=False
            (Path(d)/'autorizacao.json').write_text(json.dumps(auth),encoding='utf-8')
            with patch.object(br,'inspect_reference',return_value=fake):
                with self.assertRaises(PermissionError): br.validate_reference(d)

    def test_generated_audio_and_prompt_reuse(self):
        from scripts.tts.local import validate_local_wav
        folder=ROOT/'audio/narracoes/TESTES_LOCAIS_002'
        expected=(ROOT/'testes/tts_002/texto_teste.txt').read_text(encoding='utf-8').strip()
        for name in ('qwen_base_br_V1.wav','piper_faber_V1.wav'):
            p=folder/name; meta=json.loads(Path(str(p)+'.meta.json').read_text(encoding='utf-8'))
            self.assertEqual(br.sha(p),meta['sha256'])
            self.assertEqual(meta['text'],expected)
            self.assertTrue(validate_local_wav(p)['valid'])
            self.assertTrue(meta['technical_pass'])
            self.assertFalse(meta['approved'])
        meta=json.loads((folder/'qwen_base_br_V1.wav.meta.json').read_text(encoding='utf-8'))
        self.assertTrue(meta['voice_prompt']['reuse_test']['reused'])
        cache=ROOT/'models/voice_prompts'/meta['voice_prompt']['reuse_test']['cache_id']
        descriptor=json.loads(cache.with_suffix('.json').read_text())
        self.assertEqual(br.sha(cache.with_suffix('.npz')),descriptor['npz_sha256'])

    def test_prior_files_and_original_reference_preserved(self):
        baseline=json.loads((Path(__file__).parent/'baseline.json').read_text())
        for row in baseline:
            if row['path']=='audio/perfis/narrador_principal.json': continue
            p=ROOT/row['path']
            self.assertTrue(p.is_file(),row['path'])
            self.assertEqual(br.sha(p),row['sha256'],row['path'])
        profile=json.loads((ROOT/'audio/perfis/narrador_principal.json').read_text(encoding='utf-8'))
        self.assertEqual(profile['approval_status'],'rejected')
        original=ROOT/'audio/perfis/historico/INFRA_001/narrador_principal_antes_TTS_002.json'
        initial=next(x['sha256'] for x in baseline if x['path']=='audio/perfis/narrador_principal.json')
        self.assertEqual(br.sha(original),initial)
        conversion=json.loads((Path(__file__).parent/'reference_conversion.json').read_text())
        self.assertEqual(br.sha(ROOT/'audio/referencias_vocais/narrador_br_001/referencia.wav.m4a'),conversion['source_sha256'])

if __name__=='__main__': unittest.main(verbosity=2)
