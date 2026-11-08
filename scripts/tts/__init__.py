"""TTS providers with lazy legacy exports; local imports never load Gemini."""
from importlib import import_module
_CONFIG = {'ALLOWED_MODELS', 'ALTERNATIVE_MODEL', 'DEFAULT_LANGUAGE', 'DEFAULT_MODEL', 'DEFAULT_VOICE', 'DOCUMENTED_VOICES', 'PROJECT_ROOT', 'TTSRequestConfig', 'check_credentials'}
_GENERATOR = {'generate_speech', 'mark_as_approved', 'verify_model_access'}
__all__ = sorted(_CONFIG | _GENERATOR | {'validate_wav_file'})
def __getattr__(name):
    module = 'config' if name in _CONFIG else 'generator' if name in _GENERATOR else 'validator' if name == 'validate_wav_file' else None
    if module is None: raise AttributeError(name)
    value = getattr(import_module(f'.{module}', __name__), name)
    globals()[name] = value
    return value
