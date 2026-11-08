"""Generate only the four INFRA-001 samples. No production narration."""
import json
from pathlib import Path
import subprocess
import threading
import time
from .local import ROOT, Request, QwenLocal, generate

TEXT = 'O sapato do Nico pediu demissão. E na vila dele, ninguém usava dinheiro.\n\nSó que o sapateiro não queria batatas. Queria leite.\n\nNico... aí complicou.'
CONSISTENCY = 'Mas Nico teve uma ideia.\n\nO pescador queria batatas. Então ele conseguiu um peixe.\n\nPera aí... duas trocas seguidas dando certo?\n\nIsso tá fácil demais.'
OUT = ROOT/'audio/narracoes/TESTES_LOCAIS_001'

class Monitor:
    def __init__(self):
        self.stop = threading.Event()
        self.rows = []
    def loop(self):
        import psutil
        process = psutil.Process()
        while not self.stop.is_set():
            row = dict(time=time.time(), process_rss=process.memory_info().rss,
                system_ram_used=psutil.virtual_memory().used)
            p = subprocess.run(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=10)
            if p.returncode == 0: row['gpu_total_used_mib'] = int(p.stdout.strip())
            self.rows.append(row)
            self.stop.wait(0.5)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [('voz_A.wav','Ryan',TEXT), ('voz_B.wav','Aiden',TEXT),
            ('voz_C.wav','Uncle_Fu',TEXT), ('voz_A_consistencia.wav','Ryan',CONSISTENCY)]
    for name,voice,text in jobs:
        if (OUT/name).exists() or Path(str(OUT/name)+'.meta.json').exists():
            raise FileExistsError(OUT/name)
    monitor = Monitor()
    thread = threading.Thread(target=monitor.loop, daemon=True)
    thread.start()
    results = []
    engine = QwenLocal()
    start = time.perf_counter()
    try:
        engine.load()
        load_seconds = time.perf_counter()-start
        print('MODEL_LOADED',load_seconds,flush=True)
        for name,voice,text in jobs:
            t = time.time()
            meta = generate(Request(text=text,output=OUT/name,voice=voice), engine=engine)
            measurements = [r for r in monitor.rows if r['time']>=t]
            meta['resource_sampling'] = measurements
            meta['model_load_seconds'] = load_seconds
            if measurements:
                meta['process_rss_peak_bytes_sampled'] = max(r['process_rss'] for r in measurements)
                gpu = [r['gpu_total_used_mib'] for r in measurements if 'gpu_total_used_mib' in r]
                meta['gpu_total_peak_mib_sampled'] = max(gpu) if gpu else None
            # Update only the new metadata created by this process, never the WAV.
            Path(str(OUT/name)+'.meta.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False,default=str),encoding='utf-8')
            results.append(meta)
            print(name, 'seconds', round(meta['elapsed_seconds'],2), 'duration',
                meta['validation']['duration_seconds'], 'pass',meta['technical_pass'],flush=True)
            if not meta['technical_pass']: raise RuntimeError('Falha técnica; interrompido sem nova tentativa')
    except Exception as e:
        OUT.joinpath('failure.json').write_text(json.dumps(dict(error=repr(e),completed=len(results)),indent=2),encoding='utf-8')
        raise
    finally:
        monitor.stop.set(); thread.join(timeout=12)
        OUT.joinpath('resources.json').write_text(json.dumps(monitor.rows,indent=2),encoding='utf-8')

if __name__ == '__main__': main()
