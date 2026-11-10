# Módulo de Geração de Voz (TTS) — Canal Finanças 3D

Este documento descreve a arquitetura e o modo de uso do módulo independente de síntese de voz (`scripts/tts/`), construído sobre o SDK oficial `google-genai` e a **Interactions API** do **Gemini 3.8 TTS** (`gemini-3.8-flash-lite-tts`).

---

## 1. Visão Geral da Arquitetura

O pacote `scripts/tts/` foi projetado de forma desacoplada do pipeline 3D do Blender (`scripts/pipeline_v3/`), permitindo testar, validar e aprovar narrações antes de qualquer etapa de sincronização de animação.

```text
scripts/tts/
├── __init__.py          # Exportações públicas do pacote
├── config.py            # Parâmetros centralizados, catálogo de vozes e leitura segura de credenciais
├── generator.py         # Cliente Interactions API, síntese WAV, metadados e trava de aprovação
├── validator.py         # Validação de cabeçalho RIFF/WAVE, duração real, RMS/Pico dBFS e silêncio
├── cli.py               # Interface de linha de comando (CLI) para geração, validação e aprovação
└── run_missao_tts0.py   # Script da Missão TTS-0 (validação de acesso + Teste Curto + Narração B)
```

### Separação entre Texto e Direção Vocal (Gemini 3.8 TTS)

No Gemini 3.8 TTS, o modelo interpreta o campo `text` estritamente como **transcrição literal**. Instruções de atuação, ritmo, emoção e entonação são enviadas separadamente na anotação `speech_metadata.style` da Interactions API:

```python
input=[
    {
        "type": "user_input",
        "content": [
            {
                "type": "text",
                "text": config.text,  # Roteiro literal, sem instruções misturadas
                "annotations": [
                    {
                        "type": "speech_metadata",
                        "style": config.style,  # Direção vocal e entonação
                    }
                ],
            }
        ],
    }
]
```

---

## 2. Configuração de Credenciais

O módulo procura a chave `GEMINI_API_KEY` na seguinte ordem:

1. **Variável de ambiente do sistema** (`GEMINI_API_KEY`).
2. **Arquivo `.env` na raiz do projeto** (`C:\Users\Cleidson\Videos\canal-financas-3d\.env`).

### Configuração manual via `.env` (caso não use variável de ambiente)

1. Copie o arquivo de exemplo na raiz do projeto:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Edite `.env` e substitua `coloque_sua_chave_aqui` pela sua chave do Google AI Studio.
3. O arquivo `.env` já está protegido no `.gitignore` para nunca ser versionado.

---

## 3. Como Usar via Linha de Comando (CLI)

Execute os comandos a partir da raiz do projeto (`C:\Users\Cleidson\Videos\canal-financas-3d`):

### 3.1. Verificar credenciais, autenticação e acesso ao modelo
```powershell
python -m scripts.tts.cli check
```

### 3.2. Listar vozes predefinidas documentadas
```powershell
python -m scripts.tts.cli voices
```

### 3.3. Gerar uma nova narração em WAV
```powershell
python -m scripts.tts.cli generate `
  --text "O sapato do Nico pediu demissão. E na vila dele, ninguém usava dinheiro." `
  --style "Português brasileiro. Voz masculina adulta, natural e simpática, ritmo de conversa." `
  --voice Puck `
  --model gemini-3.8-flash-lite-tts `
  --output audio/narracoes/EP001/testes/exemplo_puck.wav
```

Você também pode carregar o roteiro a partir de um arquivo `.txt` UTF-8 usando `--text-file`:
```powershell
python -m scripts.tts.cli generate `
  --text-file roteiro_ep001.txt `
  --style "Narrador amigável e expressivo contando uma história para um amigo." `
  --voice Orus `
  --output audio/narracoes/EP001/testes/narracao_orus.wav
```

### 3.4. Validar tecnicamente um arquivo WAV existente
```powershell
python -m scripts.tts.cli validate audio/narracoes/EP001/testes/narracao_B_flash_lite_V1.wav
```

### 3.5. Proteger um arquivo aprovado contra regeneração acidental
Cada arquivo `.wav` gerado é acompanhado de um arquivo `<nome>.wav.meta.json`. Por padrão:
- O gerador **não sobrescreve** um arquivo `.wav` existente a menos que `--overwrite` seja informado.
- Quando um take é marcado como **aprovado**, nem mesmo `--overwrite` pode sobrescrevê-lo acidentalmente.

Para aprovar um arquivo:
```powershell
python -m scripts.tts.cli approve audio/narracoes/EP001/testes/narracao_B_flash_lite_V1.wav --notes "Take aprovado para animação V3.1"
```

Para remover a trava de aprovação (caso realmente deseje substituir):
```powershell
python -m scripts.tts.cli approve audio/narracoes/EP001/testes/narracao_B_flash_lite_V1.wav --unapprove
```

---

## 4. Como Comparar Novas Vozes

Para comparar timbres masculinos no mesmo trecho sem alterar o código e sem sobrescrever os testes anteriores, basta variar o parâmetro `--voice` e o nome do arquivo `--output`:

| Voz | Perfil Documentado | Comando de Teste Curto |
| :--- | :--- | :--- |
| **Puck** | Masculina, natural, simpática, ritmo de conversa e bom timing de humor | `--voice Puck --output .../teste_voz_puck.wav` |
| **Orus** | Masculina médio-grave, firme, serena e articulada | `--voice Orus --output .../teste_voz_orus.wav` |
| **Charon** | Masculina grave, calma, informativa e explicativa | `--voice Charon --output .../teste_voz_charon.wav` |
| **Iapetus** | Masculina clara, amigável e cotidiana | `--voice Iapetus --output .../teste_voz_iapetus.wav` |
| **Umbriel** | Masculina descontraída, suave e conversacional | `--voice Umbriel --output .../teste_voz_umbriel.wav` |
| **Fenrir** | Masculina expressiva, dinâmica e energética | `--voice Fenrir --output .../teste_voz_fenrir.wav` |

---

## 5. Uso Programático em Python

```python
from pathlib import Path
from scripts.tts import TTSRequestConfig, generate_speech

cfg = TTSRequestConfig(
    text="O sapato do Nico pediu demissão.",
    style="Português brasileiro, humor leve e natural.",
    output_path=Path("audio/narracoes/EP001/testes/meu_teste.wav"),
    model="gemini-3.8-flash-lite-tts",
    voice="Puck",
    overwrite=False,
)

resultado = generate_speech(cfg)
print(resultado["status"], resultado["metadata"]["validation"]["duration_seconds"])
```

