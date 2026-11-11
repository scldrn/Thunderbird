# Repository organization

This repository keeps the research evidence and a small English navigation layer. Historical root reports and scripts have moved to `legacy/`; their dependencies still require reconnection. CFD and solver case paths remain in place. An English navigation name does not create a second copy or a new accepted baseline.

## Navigation

| Area | Current location | Purpose |
|---|---|---|
| Project instructions | `AGENTS.md` | Short rules for contributors and agents |
| Research overview | `docs/research_context.md` | Architecture, milestones and limits |
| Research map | `docs/research_index.md` | Entry points by task and evidence |
| Configuration | `configuraciones/` | A07, C02 and frame conversion |
| Research milestones | `plan_maestro/`, `ejecucion/` | Planning, G0–G6 work and dated snapshots |
| CAD | `modelos_integrados/`, `entregas/` | Versioned geometric studies and deliveries |
| Flow | `CFD/` | Cases, solvers, audits and pause records |
| Flight | `simulacion_vuelo_A/`, `vuelo_rapido_visual/` | Conditional dynamics and prescribed visualization |
| Sources | `fuentes/` | Research references and benchmark inputs |
| Historical research | `legacy/` | Moved reports and scripts; see the move manifest and reconnection warning |
| Results | `resultados/` | Historical outputs; scripts require reconnection |
| Tool integrations | `integracion_apps/`, `integracion_antigravity/` | Tool setup and historical isolated agent sessions |
| Maintenance | `tools/`, `tests/`, `audits/` | Navigation checks, audit utilities and dated records |

## Naming and placement for new work

Use English `snake_case` names for new files and directories, preserving conventional names such as `README.md`, `AGENTS.md`, `Dockerfile` and established revision identifiers like `A07` and `C22`. Use explicit units in numerical names and fields, ISO dates (`YYYY-MM-DD`) for dated records, and a short revision suffix when needed. Do not rename existing datasets, solver dictionaries, JSON keys, CAD labels or historical revisions solely for translation.

Each new study should live in one task-specific directory under the existing relevant area. Include a short English `README.md` with purpose, source configuration and revision, inputs, reproduction and verification commands, output paths, evidence status and limitations. Keep scripts, configuration and verification adjacent; put generated artifacts in a named `results/` or `artifacts/` subdirectory for new work. Record data provenance, units and hashes where needed. Keep accepted reference, candidate, rejected study, and historical snapshot explicitly distinct.

Temporary frames, caches, environments and unreviewed third-party packages do not belong in commits. Preserve failed cases and logs when they are evidence. Do not overwrite a baseline with a generator or delete a result just because it is old. Use `.gitignore` for reproducible caches and large or third-party material; review the actual paths before staging.

## Changing legacy paths

Before relocating or renaming a legacy path, inventory code imports, `__file__`-relative paths, command lines, Markdown links, JSON/CSV keys and manifests, CAD references, case inputs, external consumers and paused processes. Prepare a reversible old-to-new mapping and update consumers and documentation together. Validate the new path and a representative reproduction, check artifact hashes and relevant geometry or numerical checks, and preserve rejected results. Do not move or modify paused solver state, or resume, restart, duplicate or destroy paused solvers, without explicit authorization. Never use a symlink as evidence that an external process or a tool resolves `__file__` correctly.

The current source recovery is incomplete: see `audits/cleanup_2026-11-11.md`. Do not treat an absent file as obsolete without checking its role and provenance. Old reports and dated audit records describe their own snapshots; the newest timestamp alone does not establish physical validity or select a baseline.
