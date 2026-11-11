"""Generate separately; never overwrite baseline CAD or presentation renders."""
import json
from pathlib import Path
import crear_modelos as base
ROOT=Path(__file__).resolve().parent
angles=json.loads((ROOT/'ejes_candidatos.json').read_text())['best']['angles_rad']
original=base.allocation
base.allocation=lambda L,D,r,theta,phi:original(L,D,r,*angles)
base.OUT=ROOT/'candidato_ejes';base.OUT.mkdir(exist_ok=True)
base.main()
