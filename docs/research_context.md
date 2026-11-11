# Research context

This is a navigation summary, not an acceptance record. Consult the identified configuration, original reports and JSON audits for exact scope, assumptions and current state.

Architecture A uses protected internal fans and the `diseno_industrial_v2` sports form. A07 remains the canonical research reference; C02 is a separate 5 kg integration candidate, and C03 and later studies do not automatically replace it. Targets of 2, 5 and 10 kg require independently closed configurations. The 10 kg C03 is a geometric scaling only. Propulsion, complete mass, control, loads, transition and 600–1,000 km/h flight remain unvalidated.

The early eight-reversible-rotor, variable-pitch and deployable-surface analyses are historical alternatives. Do not transfer their maps, budgets, control authority or drag numbers to C02 without reconciling configuration and domain. The axial-propulsion study retains EDF and microturbine as research alternatives, not selections. C02 reserves an OD60 mm / ID56 mm axial corridor; the nominal Ø59.8 mm Xicoy X50/X52 examples do not fit its inside diameter, even before clearances or thermal protection.

The original master plan defines G0 requirements and traceability, G1 mass and energy, G2 installed internal module, G3 functional integration, G4 installed aerodynamics, G5 structures and actuators, G6 predictive closed-loop flight, G7 robust configuration selection, G8 autonomy and digital delivery, then physical testing. Five kilograms is an integration reference; 600 km/h is an intermediate research milestone and 1,000 km/h an unverified extension. See `plan_maestro/PLAN-MAESTRO.md`, its matrices, `ejecucion/ESTADO-TAREAS.csv`, and newer applicable evidence.

## CAD and covers

A07's 5 kg cover study uses 10 mm outward translation then 110° rotation; the poses do not prove a continuous mechanism. C02 places modules at CAD x=±160 mm, y=±76 mm, with a nominal 0.5 mm rotor-envelope clearance that is not an operating tolerance. The C03 STEP/FCStd exchange audit has unresolved discrepancies; a later partial follow-up does not establish complete equivalence.

The local segmented-cover studies are documented under `modelos_integrados/producto_C*/` and in `ESTADO-VERIFICACION-GLOBAL.md`:

- C11–C13 explored four slats and long-axis reservations; C12–C13 found interference when closed, and C13 also at 2 mm lift. C13 had no detected interference in the other sampled local poses from 5 mm.
- C14–C15 used four short test axes and eight conceptual bushings. The ideal 20 mm vertical sweep was checked locally; rotation and other interactions were sampled. No functional hinge was designed.
- C16–C18 screened rods and bushing–slat interaction. C17 found three locally passing directions per bushing in 64 candidates; C18 found no volumetric collision in 160 sampled bushing–slat pairs. Ideal coaxial geometry supports continuous reasoning only for each bushing and its own slat under nominal assumptions.
- C19 and C20 rejected the sampled straight-bar arrangements. C21 rejected one partial offset-route assembly after an interference and Boolean error, not all possible routes.
- C22 contains partial row-0 node and route checks. `COMBINACIONES.json` marks two of eight combinations as passing its limited checks; `COMBINACIONES_compuesto_v1.json` records Boolean errors and no passing combinations. Reconcile methods and errors before using either. No completed report or exported STEP was present in the inspected source.

A complete lift mechanism, structural supports, axle attachment, seals, tolerances, loads, full assembly and continuous motion remain to be established. The open pose is not approved for high-speed flight. A command-line FreeCAD startup failure led to temporary CadQuery use; it does not prove the GUI is damaged.

## Model limits

The low-speed 6DOF model uses idealized force, cone and response parameters; the high-speed video reconstructs demands from prescribed trajectories. Neither demonstrates the physical vehicle's capabilities. The installed-fan data contract in `ejecucion/G6/contrato_mapa_candidato_r1/` uses synthetic examples, rejects checked extrapolation, and is not a complete installed map or simulator integration. Separate individual ranges do not establish joint multidimensional or directional coverage.

The isolated-channel CFD and 600 km/h closed-envelope slip-wall diagnostic do not provide accepted installed fan loads or total viscous drag. The C02 fine passive-flow case at 800 iterations failed selected residual criteria. The Poiseuille and public BEM benchmarks validate specific numerical exercises, not the aircraft or installed fan. Ideal LP/SOCP allocations and free-disk power are not installed force maps or optimized electrical power. Structural section screening is not FEM or material approval. Preserve failures, raw evidence and model-specific assumptions.
