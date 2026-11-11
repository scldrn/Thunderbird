# Reconnection progress

The 28 historical scripts were moved to `legacy/scripts/`. Eighteen scripts that computed the former repository root using `Path(__file__).resolve().parent` now resolve `parents[2]`, restoring their root-relative input and output locations. `legacy/move_manifest.json` retains hashes from before this modification; those hashes are historical and are not hashes of the edited scripts.

All 28 scripts passed Python syntax parsing. Their scientific execution has not been validated: the system Python lacks the pinned numerical packages, and the older CAD environment did not respond during the check. Historical commands, Markdown links, imports from other directories, manifests and consumers still need a complete audit and reconnection. Generators may overwrite results; no historical numerical generator or paused CFD solver was run for this change.

## Subsequent work

A local `.venv` was created from `requirements.txt`. Six CAD consumers now import the historical modules from `legacy/scripts/`. A smoke check imported `calcular`, `control` and `trimado_superficies`, checked their repository-root paths and evaluated one geometry. The low-speed 6DOF verification passed in an isolated `/tmp` copy, including timestep sensitivity. The installed-fan contract passed 27 tests and repository navigation passed three tests. The first smoke check used an incorrect English geometry key and failed; the corrected check used the documented `esferoide` key and passed. None of these checks validate physical flight or every historical script or CAD generator. Three broken Markdown links in moved historical reports were repaired. The migration remains partial and 191 original source files were unavailable at the prior inventory.

## Further verification

The historical screening generator was executed in an isolated temporary copy; its verification JSON matched the existing historical artifact byte-for-byte. The synthetic installed-fan contract passed 27 tests, acceleration screening passed four, navigation passed three, and `pip check` reported no broken requirements. The nine A07 geometry files passed the hashes specified in `configuraciones/A07_BASE.json`. Three relocated-report links and two historical command examples were corrected. Forty-eight available CAD records were recovered from the identified iCloud source; 34 CAD records and 109 execution-case records remained absent when checked. The execution-case files were not copied into solver cases because the state of historical paused containers could not be verified: Docker's local API socket was unavailable. All checks remain numerical or geometric, not flight validation.

The later final recovery attempt verified another 49 files and discarded 94 unavailable files from the active recovery inventory at the user's direction. See `recovery_attempt_2026-11-11.md` for scope; the earlier pending counts above are historical.
