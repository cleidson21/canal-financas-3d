# Guia de Produção — Como Criar e Renderizar Episódios no Canal 3D

Este guia descreve o fluxo de trabalho completo para abrir, inspecionar, re-executar ou criar novos episódios (`EP002`, `EP003`, etc.) no **Blender 5.2.3 LTS** utilizando a arquitetura modular **V3**.

---

## 1. Abrir o EP001

O [índice do EP001](../episodios/EP001_dinheiro/00_ABRIR_EP001.md) reúne o animatic integral, a prova da Cena 3 e os editáveis. O piloto de 15 segundos está em [arquivo/EP001/piloto](../arquivo/EP001/piloto/).

Os comandos V2/V3/V3.1 abaixo reproduzem o piloto e gravam novas saídas em `.cache/EP001/`. Para a prova da Cena 3, veja a [API 3D](../scripts/producao/README.md).

## 2. Como Executar o Pipeline pela Linha de Comando (Headless CLI)

A partir da raiz do projeto (`c:\Users\Cleidson\Videos\canal-financas-3d`), utilize o executável do Blender 5.2 com o orquestrador [`scripts/build_scene.py`](file:///c:/Users/Cleidson/Videos/canal-financas-3d/scripts/build_scene.py):

### 2.1. Reconstruir Apenas a Cena Principal (`.blend`)
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P "scripts/build_scene.py" -- --mode build
```

### 2.2. Gerar cópias de trabalho das bibliotecas em `.cache/EP001/piloto_V3/bibliotecas/`
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P "scripts/build_scene.py" -- --mode libraries
```

### 2.3. Renderizar Frames de Auditoria, Close-ups e Prancha Comparativa V2 × V3
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P "scripts/build_scene.py" -- --mode audit-stills
```

### 2.4. Testar as Duas Aberturas de 3 Segundos (Abertura A vs. Abertura B)
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P "scripts/build_scene.py" -- --mode openings-test
```

### 2.5. Renderizar Vídeo Preview Rápido (50% Resolução, 16 Samples)
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P "scripts/build_scene.py" -- --mode video-preview
```

### 2.6. Renderizar Vídeo Final Full HD Vertical (`1080×1920`, 30 FPS, H.264)
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P "scripts/build_scene.py" -- --mode video-final
```

### 2.7. Executar a Suíte Automatizada de Testes Técnicos
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P "testes/test_pipeline_v3.py"
```

---

## 3. Passo a Passo para Criar um Novo Episódio (`EP002_moeda`, etc.)

1. **Criar a Pasta do Episódio**:
   Crie a estrutura `episodios/EP002_moeda/` contendo as subpastas `cenas/`, `previews/`, `renders/` e `videos/`, além dos arquivos `roteiro.md` e `storyboard.md`.
2. **Importar Ativos Base**:
   No script do novo episódio, importe os construtores de `pipeline_v3`:
   - `character_nico.build_character_nico(col_nico, mats)` para instanciar o **Nico V3** com `Nico_Armature_V3` e controles de expressão facial.
   - `environment_fair.build_village_and_fair(cols, mats)` para montar a vila e a feira (ou vincule `cenarios/vila.blend` e `personagens/nico_base.blend`).
3. **Definir Beats e Posições**:
   Configure o dicionário de `BEATS` (em quadros a `30 FPS`) e os cortes de câmera com `scene_setup.set_camera_cut_holds(cam_obj, cut_frames)` para garantir cortes secos entre planos sem interpolação indesejada.
4. **Inspecionar Stills Antes do Vídeo Final**:
   Sempre execute a renderização dos quadros-chave (*keyframes* de cada plano) e verifique visualmente silhueta, ausência de intersecções e margem de segurança `9:16` antes de disparar o render MP4 final.

---

## 4. Procedimento de Exportação e Finalização Audiovisual (V3.1+ com FFmpeg e FFprobe)

Quando o Blender renderiza a cena 3D diretamente (`scene.render.use_sequencer = False`), a faixa de áudio AAC gerada pelo codificador interno do Blender pode sair silenciosa (`0.0` linear / `-240 dBFS`), mesmo que haja uma `SoundStrip` no VSE. Por isso, toda exportação audiovisual narrada utiliza a etapa obrigatória de finalização e auditoria em [`scripts/pipeline_v3/audio_finalizer.py`](file:///c:/Users/Cleidson/Videos/canal-financas-3d/scripts/pipeline_v3/audio_finalizer.py).

### 4.1. As 10 Etapas Automáticas da Finalização Audiovisual (`finalize_mp4_with_narration`)
1. **Entrada validada:** Recebe o vídeo `.mp4` (H.264) renderizado pelo Blender e o arquivo `.wav` de narração (verificando antes se o próprio WAV possui RMS e pico válidos).
2. **Remoção de áudio inválido:** Descarta qualquer faixa de áudio silenciosa ou incorreta do vídeo original via `-map 0:v:0`.
3. **Muxing sem recodificação de vídeo:** Incorpora o WAV como AAC (`-c:a aac -b:a 192k -ar 24000 -ac 1`) preservando o fluxo de vídeo H.264 intacto via `-c:v copy`.
4. **Ancoragem no tempo zero:** Mantém o início da narração em `t = 0.000s` (`aresample=async=1:first_pts=0`), respeitando integralmente o silêncio inicial (`0,00s – 0,41s`).
5. **Preenchimento exclusivo da cauda (*tail padding*):** Completa com silêncio apenas o intervalo final restante (`apad=whole_dur=<duração_cena>,atrim=0:<duração_cena>`) quando a cena (`19,20s`) é mais longa que a narração (`18,72s`).
6. **Preservação da duração planejada:** Garante que vídeo e áudio terminem exatamente na duração planejada da cena (`19,20s` / `576 quadros` a `30 FPS`).
7. **Validação estrutural via FFprobe:** Inspeciona os fluxos `video` (`h264`, `576 frames`, `19.20s`, `start_time=0.0`) e `audio` (`aac`, `24000 Hz`, `19.20s`, `start_time=0.0`, bitrate real `> 80 kbps`).
8. **Auditoria de audibilidade PCM (RMS e Pico):** Decodifica a faixa AAC do MP4 final para PCM `16-bit` em memória e verifica se o RMS ativo (`> -35 dBFS`) e o pico (`> -15 dBFS`) comprovam áudio audível, rejeitando imediatamente faixas silenciosas.
9. **Comparação com o WAV de origem:** Calcula a correlação cruzada por FFT para medir deslocamento temporal (`|lag| <= 20 ms`, obtendo `0.0 ms`), correlação de forma de onda (`>= 0.95`, obtendo `0.999938`), correlação de envelope RMS de 10 ms (`>= 0.98`, obtendo `0.999995`), silêncio da cauda (`< -50 dBFS`) e integridade individual de todas as 6 frases de `timing.json`.
10. **Interrupção imediata em caso de falha (*Fail-Fast*):** Lança `AudioVerificationError` e interrompe o pipeline se qualquer verificação falhar.

### 4.2. Comandos de Finalização e Teste Audiovisual

- **Finalizar os vídeos V3.1 existentes sem re-renderizar no Blender:**
  ```powershell
  & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P "scripts/finalize_audio_v3_1.py"
  ```
- **Finalizar um arquivo MP4 específico com um WAV específico:**
  ```powershell
  & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P "scripts/finalize_audio_v3_1.py" -- --video "caminho/video_blender.mp4" --audio "caminho/narracao.wav" --output "caminho/video_finalizado.mp4"
  ```
- **Executar a suíte de testes automatizados V3.1/V3.1.1 (incluindo teste de falha para áudio silencioso):**
  ```powershell
  & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P "testes/test_pipeline_v3_1.py"
  ```


