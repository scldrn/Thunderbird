# Repository Guidelines

## Project Structure & Module Organization

`investigacion-aeronautica/` contains research scripts, Spanish reports, and generated `resultados/`. Within it:

- `modelos_integrados/`: CadQuery generators, geometry checks, and versioned `producto_A03`–`producto_A07` deliverables.
- `CFD/`: Gmsh meshes, OpenFOAM case preparation, solver monitoring, audits, and `solver/Dockerfile`.
- `simulacion_vuelo_A/`: conditional low-speed dynamics, verification, and video generation.
- `vuelo_rapido_visual/`: prescribed high-speed trajectories and inverse-demand visualization; not predictive flight simulation.
- `fuentes/`: scientific reference material.

Read `ESTADO-VERIFICACION-GLOBAL.md` and `modelos_integrados/DECISION-ARQUITECTURA.md` before changing assumptions. The selected architecture uses internal fans.

## Build, Test, and Development Commands

Run from the repository root:

```sh
python3 investigacion-aeronautica/calcular.py
.venv-cad/bin/python investigacion-aeronautica/simulacion_vuelo_A/simular.py
.venv-cad/bin/python investigacion-aeronautica/simulacion_vuelo_A/verificar.py
.venv-cad/bin/python investigacion-aeronautica/modelos_integrados/producto_A06/crear_A06.py
```

These generate screening results, run conditional flight scenarios, verify dynamics, and export CAD, respectively. Generators can overwrite adjacent artifacts; read their `LEEME.md` first. There is no unified build command. Core numerical dependencies and CAD dependencies are recorded separately in `requirements.txt` and `modelos_integrados/requirements-lock.txt`; do not combine their differing pins blindly.

## Coding Style & Naming Conventions

Use four-space indentation for new Python modules; preserve surrounding style in existing compact scripts. Use `snake_case` filenames/functions, uppercase constants, and explicit unit suffixes such as `_mm`, `_N`, and `_kgm2`. Resolve paths relative to `__file__`. Keep numerical routines separate from rendering where practical. No formatter or linter is currently configured.

## Testing Guidelines

Verification uses executable `verificar*.py` and audit scripts with assertions and JSON reports; no centralized pytest suite or coverage threshold exists. Run checks relevant to changed equations or geometry. Check analytic cases and timestep sensitivity for dynamics; reimport STEP files and check solid validity and relevant collisions for CAD. Preserve failed cases and logs. Numerical agreement does not establish physical validity.

## Commit & Pull Request Guidelines

Git has no commits yet, so no historical convention exists. Use short imperative subjects, for example `Fix duct clearance beneath fan covers`. Keep changes focused. PRs should describe assumptions, affected revisions, reproduction commands, verification results, and unresolved limitations; include screenshots for visual changes and link issues when applicable. Avoid staging virtual environments, caches, temporary frames, or solver dumps indiscriminately.

## Research & Runtime Constraints

Use `investigacion-aeronautica/plan_maestro/PLAN-MAESTRO.md` for execution priorities; keep historical results separate from accepted baselines.

Distinguish measured data, assumptions, calculations, and prescribed animations. Cite primary sources for scientific claims. Record changed geometry and regenerated artifacts together. Check pause records before CFD work; do not resume paused solvers without explicit authorization.
