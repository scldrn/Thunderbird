# Repository guidance

## Language and evidence

Communicate with the user in Spanish. Write new or updated repository documentation, comments, identifiers and user-facing text in English. Translate historical material carefully without changing technical meaning, provenance, units or reproducibility; do not silently rename paths, change machine-readable keys, or rewrite generated data, third-party material or solver outputs.

Thunderbird is conceptual research on a compact sports aircraft with protected internal fans. Masses of 2–10 kg, rapid omnidirectional maneuvering and 600–1,000 km/h are objectives, not demonstrated capabilities. Distinguish measurements, assumptions, calculations and prescribed animations; cite primary sources. Numerical agreement alone is not physical validation.

Read `ESTADO-VERIFICACION-GLOBAL.md`, `modelos_integrados/DECISION-ARQUITECTURA.md` and `plan_maestro/PLAN-MAESTRO.md` before changing assumptions. For a concise research and CAD history see `docs/research_context.md`; use the underlying reports and audits as authority. Consult `ejecucion/ESTADO-TAREAS.csv` and the identified configuration for task-specific work. Do not promote a later candidate or agent output to an accepted baseline without evidence.

## Architecture and frames

Architecture A with internal fans is selected. A07 is the canonical research reference; C02 is a separate integrated candidate and C03 and later studies do not replace it automatically. Keep results from differing geometries, masses and domains separate. The 10 kg C03 is geometric scaling, not a validated hardware or mass configuration. The opening mechanisms are conceptual; local or sampled collision checks do not prove continuous motion, flight readiness or structural integrity.

The CAD nose points toward −X while historical flight models use +X. `configuraciones/base.py` documents CAD→FLU conversion `diag(-1,-1,+1)` and mm→m; verify frame, units, moment reference and configuration before coupling models. The CAD origin is a geometric datum, not a measured CG.

## Layout and recovery

Use `docs/repository_organization.md` for naming and placement and `docs/research_index.md` to find task-specific evidence. New directories and filenames use English `snake_case`, with conventional `README.md` names and established revision IDs preserved.

Historical root-level scripts and reports are organized under `legacy/scripts/` and `legacy/reports/`; their former paths and hashes are recorded in `legacy/move_manifest.json`. All 28 scripts completed in isolated copies after reconnection; historical references and differing regenerated outputs still require review as documented in `audits/legacy_execution_2026-11-11.md`. `modelos_integrados/` contains CAD; `CFD/` contains flow cases and audits; `ejecucion/` contains G0–G6 work and snapshots; `configuraciones/` holds configuration data. `simulacion_vuelo_A/` is conditional low-speed dynamics; `vuelo_rapido_visual/` is prescribed visualization, not predictive flight. `fuentes/` contains references.

A source tree was located in `/Users/sam/Library/Mobile Documents/.Trash/investigacion-aeronautica/` on 2026-11-11 after the path originally supplied by the user disappeared. Recovery was interrupted at the user's request to remove unnecessary material; do not restore, move or delete the source without establishing intent. Availability and identity must be verified rather than assumed. `audits/markdown_review_2026-11-11.md` records the dated inventory and limitations; `audits/historical_migration_status_2026-11-11.json` and older path descriptions are historical, not current status.

Historical snapshots and failed cases can be necessary evidence even when superseded. Preserve traceability, negative results and licenses. Do not equate a third-party document or an agent report with project validation. Exact duplicate packaging, temporary frames and caches may be removed when their contents are preserved and verified; do not indiscriminately delete CFD cases or alter user work.

The unrecovered files discarded at the user's direction affect the 18 scopes listed in `audits/incomplete_case_scopes_2026-11-11.json`. Keep their historical evidence, but do not execute or treat those cases as complete unless their required inputs are re-established and checked.

## Execution and verification

There is no unified build. Historical scripts are in `legacy/scripts/`. Root-relative paths and six CAD import consumers have been reconnected; the screening generator was verified in isolation. Review each script before running it because other historical consumers and outputs may still need reconciliation. Check the relevant `LEEME.md`, environment and paths before running generators: they may overwrite artifacts. Numerical and CAD dependencies have separate pins; see `docs/development_setup.md` for the verified environments and checks. Use `verificar*.py` and audit scripts appropriate to the change; preserve failures and logs. Check analytical cases and timestep sensitivity for dynamics; reimport STEP and check solid validity, relevant collisions and continuous versus sampled motion for CAD. CFD requires convergence, conservation, mesh, domain and model sensitivity; a solver exit alone is not acceptance.

Before CFD work, inspect `CFD/PAUSA_SOLICITADA_USUARIO.json`, later dated records and actual process state. Do not resume, restart, duplicate or destroy paused solvers without explicit authorization. For blade-element coupling do not add BEM induction to CFD disk velocity that already includes it, or equate fluid force work with shaft power. Mark polar extrapolation and preserve distinct experimental branches.

Use four-space indentation in new Python, preserve surrounding style, prefer `snake_case`, uppercase constants and unit suffixes such as `_mm`, `_N`, `_kgm2`; resolve paths relative to `__file__`. Keep numerical and rendering code separate where practical. No unified formatter or test suite is configured. Report assumptions, commands, results and remaining limits. Do not stage environments, caches, temporary frames, solver dumps or third-party code indiscriminately. Use short imperative commit subjects.
