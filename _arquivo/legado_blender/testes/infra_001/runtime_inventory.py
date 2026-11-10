"""Record runtime, installed license metadata and direct dependency versions."""
import importlib.metadata as md
import json
from pathlib import Path
import platform
import subprocess
import sys
import torch

OUT=Path(__file__).resolve().parent
rows=[]
for package in md.distributions():
    m=package.metadata
    rows.append(dict(name=m['Name'],version=package.version,
        license_expression=m.get('License-Expression'),license=m.get('License'),
        license_classifiers=[x for x in m.get_all('Classifier',[]) if x.startswith('License')],
        license_files=m.get_all('License-File',[])))
(OUT/'dependency_licenses.json').write_text(json.dumps(sorted(rows,key=lambda x:x['name'].lower()),indent=2),encoding='utf-8')
result=dict(python=sys.version,executable=sys.executable,os=platform.platform(),
    torch=torch.__version__,cuda_runtime=torch.version.cuda,cuda_available=torch.cuda.is_available(),
    gpu=torch.cuda.get_device_name(),compute_capability=torch.cuda.get_device_capability(),
    supported_arches=torch.cuda.get_arch_list(),cuda_operation=(torch.ones(4,device='cuda')*2).tolist())
(OUT/'runtime.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
