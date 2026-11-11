# Historical research

`reports/` holds historical root-level research reports and `scripts/` holds their Python scripts. These files were moved from the repository root for organization; `move_manifest.json` records their former paths and SHA-256 hashes.

**Reconnection has been execution-checked.** Eighteen scripts resolve root-relative paths from the repository root and all 28 scripts completed in isolated copies. See `../audits/legacy_execution_2026-11-11.md` for differing historical outputs and limits. Historical reports, manifests and commands may still refer to former paths; inspect them before use. The global verification audit remains at the repository root. No solver cases were moved.

The screening script `scripts/calcular.py` has been verified in an isolated copy, and representative imports now pass using `.venv`. For setup and checks see `../docs/development_setup.md`. Inspect outputs before running a generator in this checkout: historical output files may be overwritten. Other scripts remain task-specific and have not all been revalidated.
