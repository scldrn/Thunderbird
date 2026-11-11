# Markdown source and agent-report audit

## Scope and provenance

On 2026-11-11 the user-identified research path under `Documents/ChatGPT/New project/` was absent. A research tree was found at `/Users/sam/Library/Mobile Documents/.Trash/investigacion-aeronautica/`. It was inspected in place; this audit does not establish why or when it was moved, or prove every file is identical to the tree seen earlier at the user-identified path. Nothing was restored or deleted.

`markdown_inventory_2026-11-11.json` records each source Markdown path, byte count, SHA-256 digest and same-relative-path comparison with this checkout. It was generated using:

```sh
python3 tools/audit_markdown_inventory.py \
  '/Users/sam/Library/Mobile Documents/.Trash/investigacion-aeronautica' . \
  > audits/markdown_inventory_2026-11-11.json
```

The command reads the two trees and writes only to the specified output. The source in the Trash may disappear, so the manifest is a dated snapshot, not a backup. The inventory found 489 UTF-8 Markdown files, with no source read errors: 46 had identical counterparts in the checkout and 443 had no counterpart at the same relative path. It does not compare non-Markdown files, detect renamed counterparts, verify that a file was understood, or validate its claims. The checkout also has Markdown files not present in the source; this source-oriented manifest does not enumerate them.

## Delegated review and reliability

Seven read-only review tasks were requested through Antigravity. Six returned reports; their claimed coverage was 24 root/plan files, 60 CAD files, 50 G0–G2 files, 46 G3–G8 and snapshot files, 95 agent-session files, and 213 application/third-party files. These claims overlap (in particular, G2 snapshots) and are not an independently verified count of semantic reading. The seventh task, `174a4ae8` (CFD, flight simulation, references and delivery files), timed out after 600 seconds and returned no completed audit. Earlier attempts returned empty responses. Therefore comprehensive interpretive review of all 489 files is **not accredited**.

The following spot checks compare specific assertions in the returned reports with the named source. Source statements are documented results and are not themselves independent validation of the underlying physics.

| Agent assertion | Source check | Disposition |
|---|---|---|
| `d6d42672`: 5 kg, 2 g to 600 km/h requires 1.63 kW useful power and 0.47 kg battery. | `ejecucion/G1/aceleracion_ideal_2_5_10/INFORME.md`, example table: 16.34 kW and 4.67 kg under the stated battery assumptions. | Reject agent figures; factor-of-ten discrepancy. |
| `a2453cef`: continuous-cone comparison used ECOS and recovered 693 cases, with a difference up to 3.96 N. | `ejecucion/G6/potencia_cg_ideal/INFORME-CONTRASTE-CONO-CONTINUO.md`: Clarabel 0.11.1, 6,624 saved LP/SOCP comparisons, maximum LP minus SOCP difference 0.117 N. | Reject the stated solver and numerical summary. |
| `d290a084`: the reference blade in `PALA-DE-REFERENCIA.md` is SD8020. | The document identifies NACA0012 as the geometric candidate and a synthetic polar; SD8020 is studied separately in `REVISION-CON-POLARES-EXPERIMENTALES.md`. | Reject the profile attribution. |
| `d290a084`: the 5 kg, aspect-ratio 1.5 ring has diameter 0.444 m. | `ALA-ANULAR-CONTRASTE.md`, example table: inner diameter 0.288 m and approximate outer diameter 0.333 m. | Reject the value for that example. |
| `b1ff71bb`: C11's selected open position rotates to 90°. | `modelos_integrados/producto_C11_laminas/LEEME.md` identifies 60° for the open pose; 90° is among separately sampled rotations. | Do not conflate the selected pose and the larger sampled range. |

These errors preclude treating any of the delegated reports as authoritative without checking the original evidence. Statements such as successful process exit, reimport of valid solids, or an agent's claim to have read files do not establish physical validation, complete file equivalence, or semantic coverage. Use the original project reports, inputs and audit results for future decisions. `AGENTS.md` deliberately retains only conclusions independently checked against those records or explicitly attributed to the user.
