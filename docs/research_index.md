# Research index

Start with `AGENTS.md` and `docs/research_context.md`. Open the documents below only for the task at hand; several are historical Spanish source records and must be interpreted with their date and configuration.

## Current decisions and progress

- Master plan and acceptance criteria: `plan_maestro/PLAN-MAESTRO.md`, `plan_maestro/REQUISITOS.csv`, `plan_maestro/TRABAJO.csv`, `plan_maestro/RIESGOS.csv`.
- Architecture decision: `modelos_integrados/DECISION-ARQUITECTURA.md`.
- Global verification and later updates: `ESTADO-VERIFICACION-GLOBAL.md`.
- Task status and configuration: `ejecucion/ESTADO-TAREAS.csv`, `configuraciones/A07_BASE.json`, `configuraciones/C02_CANDIDATA.json`.

## Work by discipline

- CAD reference and cover studies: `modelos_integrados/producto_A07/LEEME.md`, `ejecucion/G3/C02/INFORME-C02.md`, `modelos_integrados/producto_C03/LEEME.md`, and `modelos_integrados/producto_C11_laminas/` through `modelos_integrados/producto_C22_nudos/`. C22 has partial data, not an accepted mechanism.
- Installed fan and rotor: `ejecucion/G2/INFORME-C01.md`, `ejecucion/G2/INFORME-LEY-LOCAL-C02.md`, `ejecucion/G2/INFORME-COBERTURA-POLAR-C02.md`, `ejecucion/G2/referencia_nasa_edf/`.
- CFD status and limits: `CFD/PAUSA_SOLICITADA_USUARIO.json`, `CFD/ESTADO-CFD.md`, `CFD/ESTADO-TRANSITORIO.md`, `CFD/ESTADO-AVANCE-COMPRESIBLE.md`, `ejecucion/G2/flujo_C02_conducto/INFORME-FINA-800.md`, and `ejecucion/G4/RAE2822/`.
- Propulsion, mass and energy: `ejecucion/G3/DECISION-PROPULSION-PRELIMINAR.md`, `ejecucion/G1/decision_integrada_c02/INFORME.md`, `ejecucion/G1/potencia_simultanea_c02/INFORME.md`.
- Structure: `ejecucion/G5/rotor_C02/INFORME.md` and `legacy/reports/ESTRUCTURA-PRELIMINAR.md`; both are preliminary studies, not structural approval.
- Control and simulation: `ejecucion/G6/`, `simulacion_vuelo_A/INFORME.md`, `vuelo_rapido_visual/INFORME.md`. The installed-fan contract in `ejecucion/G6/contrato_mapa_candidato_r1/` is a synthetic candidate, not an installed map.
- Verification and recovery: `audits/markdown_review_2026-11-11.md`, `audits/cleanup_2026-11-11.md`, `tools/audit_markdown_inventory.py`, `tools/audit_recovered_files.py`.

Do not transfer performance numbers between configurations or turn CFD convergence, CAD validity, or a prescribed trajectory into physical validation.

For the historical root-level reports and scripts by topic, see [`legacy_research_index.md`](legacy_research_index.md).

For the current mission requirements traceability and a comparable 2/5/10 kg ideal energy sensitivity, see [`mission requirements`](../ejecucion/G0/mission_requirements/README.md) and [`mission energy sensitivity`](../ejecucion/G1/mission_energy_sensitivity/README.md). Both retain explicit open acceptance and physical-model limits.
