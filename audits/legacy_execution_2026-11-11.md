# Historical script execution check

All 28 Python files in `legacy/scripts/` finished with exit code zero under the separate numerical environment (`requirements.txt`) in independent temporary copies of the scripts, historical `resultados/`, and `fuentes/uiuc/`. Each run had a 45-second limit. No generated output was copied back into the checkout. Reproduce the execution check with:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tools/check_legacy_scripts.py > /tmp/thunderbird-legacy-execution.json
```

`legacy_execution_2026-11-11.json` records each script and lists pre-existing output files whose bytes differed, plus newly produced files. Exit success and matching bytes verify neither scientific accuracy nor physical flight. Reproducibility is scoped to the inputs and environment available for this check.

Nine historical outputs differed in bytes across five scripts. Three are PDF/SVG visual outputs, which were not treated as numerical comparisons. A separate JSON/CSV comparison using relative tolerance `1e-9` and absolute tolerance `1e-10` found:

- `cierre_masa.py`: two JSON outputs matched within those tolerances; 179 CSV values differed, including small numerical changes. These differences were not promoted to a new accepted result.
- `dinamica.py`: the regenerated CSV and verification JSON include the additional `estimated_tau_s` field, absent from the preserved outputs. This is a schema difference, not a verified physical improvement.
- `estructura_preliminar.py`: two reported frequency-related numerical checks differed. The outputs were not replaced or declared equivalent.

The check preserves the original data and records these differences for later analysis. Generators write into their own root-relative output locations when run directly, so inspect them before execution. This check did not run or alter paused CFD solvers.

## Detailed comparison

`tools/compare_legacy_results.py` reruns the three numerical generators in a temporary copy and compares common JSON fields and CSV rows, reporting schema additions and nonnumeric differences separately. Reproduce it with `.venv/bin/python tools/compare_legacy_results.py`; the recorded output is `legacy_numeric_comparison_2026-11-11.json`. It compares rows by their existing order and uses `math.isclose` with relative tolerance `1e-9` and absolute tolerance `1e-10`; these are comparison thresholds, not engineering acceptance limits.

- The mass-closure CSV has 179 of 2,098 numeric values outside those tolerances. The largest absolute change is 0.1885 W in `power_peak_upper_W` on zero-based row 95 (about 1.29 million W). The two mass-closure JSON files have no numeric differences outside the thresholds.
- All 132 common numeric CSV values and 12 common numeric verification JSON values for dynamics agree within those thresholds. `estimated_tau_s` is added in all 12 regenerated CSV rows and in the hover verification record. No common nonnumeric values changed.
- The structural summary has two of 63 numeric values outside the thresholds, both frequency-error checks. Its largest absolute change is approximately 4.39e-7 in the dimensionless `taper_refinement_frequency_rel` check. The generator's own assertion thresholds pass, but that does not establish equivalence of the historical and regenerated analysis.

The origin of these differences has not been established. The three changed PDF/SVG files have not been analyzed for metadata versus visual differences. Original results remain unchanged.
