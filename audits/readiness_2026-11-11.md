# Development readiness check

This record covers environment setup and selected numerical/CAD checks. It is not physical validation and does not establish that every historical script, case, or missing source artifact is runnable.

- `.venv`: Python 3.9.6 with `requirements.txt`; `pip check` passed. Navigation, installed-fan contract and ideal-acceleration tests passed in the preceding reconnection audit. Conditional 6DOF verification passed in an isolated temporary copy.
- `.venv-cad`: Python 3.12.14, CadQuery 2.8.0, OCP 7.9.3.1.1, NumPy 2.4.6 and SciPy 1.17.1; `pip check` passed. The installed snapshot is recorded in `requirements-cad.txt`, not the full historical CAD/renderer lock. The C14 sweep unit test passed all three cases.
- STEP reimport with CadQuery: C14 closed 13, C18 open 29 and C21 rejected 32 records; each imported record had a valid shape with solids. C21 remains rejected; these checks are not full assembly, collision or flight validation.
- C22 `RESULTADOS.json` identifies the recovered C17 candidate STEP by the correct SHA-256. Both C22 combination reports identify the current C22 node-results file by the correct SHA-256. Their conflicting results and Boolean errors remain unresolved; no completed mechanism is implied.
- C22 node screening was rerun in an isolated temporary copy using the separate CAD environment. All six local cases reproduced the recorded pass/fail states, errors, sampled check counts and overlap volumes within 1e-7 mm³. Five passed and the 0.75 mm node on leaf 2 lacked the intended connection. `tools/check_c22_local.py` repeats that comparison without changing the study. This verifies only those sampled local checks, not continuous motion or a functional joint.
- A07 geometry and C02 candidate STEP hashes were checked in the preceding reconnection audit. Ninety-four unavailable historical source files were excluded at the user's direction; the 18 affected case or study scopes are listed in `incomplete_case_scopes_2026-11-11.json` and must not be assumed complete.
- CFD paused-solver restrictions remain in effect. This check did not start, resume or restart a solver.
- A local Markdown-link scan covered 161 files in the principal research areas, excluding snapshot paths. It found five unresolved links, all in the vendored CCBlade tutorial (`howto.md` and four `@ref` references); these were preserved as upstream documentation rather than presented as project links. This scan does not verify command examples, backtick paths or other references.

See `docs/development_setup.md` for setup and read-only check commands. Historical generators may overwrite outputs: inspect their `LEEME.md` and use an isolated copy where appropriate.
