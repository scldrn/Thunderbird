# Repository maintenance tools

Read-only source-comparison utilities. Run them with explicit source and checkout arguments; do not use their inventories as evidence of physical validation.

`check_c22_local.py` reruns the six recorded local-node cases in a temporary directory and compares their outcomes with the historical report. Run it with `.venv-cad/bin/python`; see `../docs/development_setup.md`. This is a sampled geometry check, not a functional mechanism test.

`check_legacy_scripts.py` runs the 28 historical root scripts in separate temporary copies of their inputs and reports changed output hashes. Run it with `.venv/bin/python`; it does not replace the original research data or validate its physics.

`compare_legacy_results.py` compares regenerated numerical outputs and schemas in a temporary copy. Run it with `.venv/bin/python`; details and limits are in `../audits/legacy_execution_2026-11-11.md`.

See [`../docs/repository_organization.md`](../docs/repository_organization.md) for placement and naming rules.
