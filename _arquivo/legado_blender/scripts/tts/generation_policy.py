"""Offline gates for future explicit Gemini requests; no network in this module."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
PROFILE=ROOT/'audio/perfis/narrador_principal.json'
POLICY=ROOT/'audio/perfis/politica_geracao.json'
STATE=ROOT/'audio/controle_geracao'

def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def check_identity(config):
    profile=read(PROFILE)
    if profile['approval_status']!='approved' or profile['engine']!='gemini':raise PermissionError('Perfil oficial Gemini sem aprovação')
    if (config.model,config.voice,config.language)!=(profile['model'],profile['voice_id'],profile['language']):
        raise PermissionError('Modelo/voz/idioma diferentes da identidade oficial; sem substituição automática')
    return profile

def check_reuse(path):
    profile=read(PROFILE)
    relative=Path(path).resolve().relative_to(ROOT).as_posix() if Path(path).resolve().is_relative_to(ROOT) else None
    expected=profile.get('approved_assets',{}).get(relative)
    if expected and sha(path)!=expected:raise PermissionError('Áudio aprovado alterado; reutilização bloqueada')
    return expected is not None

def request_identity(config):
    return hashlib.sha256(json.dumps(dict(model=config.model,voice=config.voice,language=config.language,
        text=config.text,style=config.style,output=str(Path(config.output_path).resolve()),sample_rate=config.sample_rate,
        speaker=config.speaker),sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def reserve_generation(config,api_key):
    profile=check_identity(config)
    policy=read(POLICY)
    if policy.get('remote_generation_enabled') is not True or profile.get('generation_enabled') is not True:
        raise PermissionError('Geração remota desativada por padrão no perfil/política')
    if policy.get('paid_generation_enabled') is not False:raise PermissionError('Este controlador aceita somente política sem geração paga')
    if not config.style.startswith(profile['style_prompt']):raise PermissionError('Usar prompt editorial oficial, seguido de direção do segmento')
    if not config.generation_permit:raise PermissionError('Falta autorização de uso único com evidência recente de cota/projeto')
    if (STATE/'quota_block.json').exists():raise PermissionError('Circuito bloqueado por cota; revisão humana necessária')
    permit=read(config.generation_permit)
    now=datetime.now(timezone.utc)
    try:
        observed=datetime.fromisoformat(permit['checked_at'])
        expires=datetime.fromisoformat(permit['expires_at'])
    except (KeyError,TypeError,ValueError) as exc:
        raise PermissionError('Datas de verificação/autorização ausentes ou inválidas') from exc
    if observed.tzinfo is None or expires.tzinfo is None or not observed<=now<expires or (now-observed).total_seconds()>3600:
        raise PermissionError('Evidência ausente/expirada; conferir projeto/cota no AI Studio novamente')
    if permit.get('billing_tier')!='free' or permit.get('billing_enabled') is not False:
        raise PermissionError('Camada gratuita não confirmada; não arriscar chamada paga')
    for field in ('human_authorized','model_available','tts_free_for_model','quota_checked'):
        if permit.get(field) is not True:raise PermissionError('Pré-verificação incompleta: '+field)
    if not permit.get('project_id') or not permit.get('evidence_reference'):
        raise PermissionError('Identificar o projeto e a evidência consultada sem incluir chave')
    if not isinstance(permit.get('remaining_requests'),int) or permit['remaining_requests']<1:
        raise PermissionError('Sem cota declarada disponível')
    fingerprint=hashlib.sha256(api_key.encode()).hexdigest()
    if permit.get('api_key_sha256')!=fingerprint or permit.get('request_sha256')!=request_identity(config):
        raise PermissionError('Autorização não corresponde à chave/projeto/requisição planejada')
    identifier=permit.get('permit_id','')
    if not re.fullmatch(r'[A-Za-z0-9_-]{8,80}',identifier):raise PermissionError('Identificador de autorização inválido')
    path=STATE/'permits'/f'{identifier}.used.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    # Atomic one-use reservation, before any network request. Errors do not auto-renew it.
    with path.open('x',encoding='utf-8') as f:json.dump(dict(permit_id=identifier,
        request_sha256=permit['request_sha256'],project_id=permit['project_id'],
        reserved_at=now.isoformat(),billing_tier_evidence='human-verified free; actual charge unverified'),f,indent=2)
    return dict(permit_id=identifier,project_id=permit['project_id'],billing_tier_declared='free',
        evidence_reference=permit['evidence_reference'],actual_charge_status='unverified',
        max_synthesis_attempts=1,automatic_retry=False)

def record_quota_block(error):
    STATE.mkdir(parents=True,exist_ok=True)
    path=STATE/'quota_block.json'
    if not path.exists():
        with path.open('x',encoding='utf-8') as f:json.dump(dict(blocked=True,
            observed_at=datetime.now(timezone.utc).isoformat(),category=error['category'],
            reset='manual quota/project review and explicit authorization; never rotate keys/projects'),f,indent=2)
