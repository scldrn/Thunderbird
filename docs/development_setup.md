# Development setup

The numerical and CAD environments are separate because their dependency versions differ. On this Mac, `.venv` uses Python 3.9.6 with `requirements.txt`, and `.venv-cad` uses Python 3.12.14. Both environments are local and ignored by Git. Their Python executables depend on the installations used to create them; recreate them if moved or unavailable.

## Numerical checks

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python ejecucion/G6/contrato_mapa_candidato_r1/test_contrato_mapa.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python ejecucion/G1/aceleracion_ideal_2_5_10/verificar.py
python3 tools/check_navigation.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/check_legacy_scripts.py > /tmp/thunderbird-legacy-execution.json
```

`simulacion_vuelo_A/verificar.py` writes a JSON report next to the script. To preserve the historical report, run it in a temporary copy containing `simular.py`, `verificar.py` and `5kg_nominal.npz`. The resulting checks cover the conditional model, not physical flight.

## CAD checks

`requirements-cad.txt` is a snapshot of the separate Python 3.12 CAD environment verified on macOS arm64, not the original complete `modelos_integrados/requirements-lock.txt`. It includes CadQuery 2.8.0, OCP 7.9.3.1.1, NumPy 2.4.6 and SciPy 1.17.1. It does not include every optional application or renderer in the original lock. Availability of pinned wheels and behavior on other platforms are not established.

The current machine created this environment with `/Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`; `python3.12` was not on `PATH`. The example below assumes a working Python 3.12 is available under that name; substitute its actual path when necessary.

```sh
python3.12 -m venv .venv-cad
.venv-cad/bin/python -m pip install -r requirements-cad.txt
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 .venv-cad/bin/python modelos_integrados/producto_C14_ejes_cortos/verificar.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 .venv-cad/bin/python tools/check_c22_local.py
```

The C22 check copies its inputs into a temporary directory and compares the six local results to the recorded outcomes; it does not overwrite the study. Read the relevant study's `LEEME.md` before running its generators or audits; many write next to the historical artifacts. The C14 and C22 checks and local STEP reimports are geometric checks only. C21 is a rejected arrangement, not a mechanism approved for use.
