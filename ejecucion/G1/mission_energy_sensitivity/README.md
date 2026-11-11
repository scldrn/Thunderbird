# Ideal acceleration and cruise energy sensitivity

This T06 screen compares the same hypothetical two-phase mission for 2, 5 and 10 kg. The 288 cases combine the speed objectives 600/1000 km/h, prescribed accelerations 0.5/1/2/5 g, hypothetical constant drag 20/50/100/200 N and cruise durations 30/120/300 s. The same drag is applied during acceleration and cruise; constant drag down to rest is a deliberately crude hypothetical load, not a physical drag curve. Mass is constant and includes the hypothetical pack. No C02 power, dimensions, or hardware are scaled across masses.

The model assumes a simultaneous 60% overall efficiency, 150 Wh/kg usable pack energy and 5000 W/kg pack power. These are independent illustrative assumptions, not measured or qualified battery properties; their joint feasibility and peak duration are unknown. The mass associated with energy or peak power is the maximum of the two, not their sum. It is a constraint of these assumed limits, not a selected component or a general battery lower bound.

For speed V, acceleration a, mass m, constant drag D and cruise time t, acceleration distance is V²/(2a), mechanical work is `0.5*m*V² + D*V²/(2a) + D*V*t`, and the prescribed peak electrical power is `(m*a + D)*V/efficiency`. This omits static thrust power, hover, ascent, transition, support and auxiliary loads, aerodynamic lift, wind, braking, thermal limits, reserves, losses varying by operating point, and other hardware. It does not establish that speed or acceleration is attainable. Peak force and energy must be met by a real installed propulsion system, which is not identified.

For illustration, the 5 kg, 600 km/h, 1 g, 20 N and 30 s cruise case requires 91.56 Wh and 19.18 kW under these assumptions; the pack constraint is 3.84 kg, before all other components. At 1000 km/h with 120 s cruise and the other assumptions unchanged, it is 434.37 Wh and 31.96 kW, with a 6.39 kg assumed pack constraint, exceeding the entire 5 kg mass. This excludes that combination of inputs, not other energy sources, propulsion architectures, trajectories or missions.

The historical `../aceleracion_ideal_2_5_10/` screen neglects drag and cruise; `../potencia_simultanea_c02/` includes a different 5 kg mission, speed-dependent drag and a prescribed simultaneous support load. Values are not directly interchangeable. T06 remains partial: same-mission bookkeeping here is deliberately incomplete, with no valid total vehicle budget or installed map.

Run from the repository root:

```sh
.venv/bin/python ejecucion/G1/mission_energy_sensitivity/calculate.py
.venv/bin/python ejecucion/G1/mission_energy_sensitivity/test_calculate.py
```

`calculate.py` overwrites only the adjacent generated `scenarios.csv`. Tests check analytical work and peak power, duration sensitivity, and input rejection; they do not validate the physical assumptions.

## Correction to the earlier C02 mission function

`../decision_integrada_c02/calcular.py` previously used the maneuver peak instead of considering both hover and maneuver when both phases were present. If the maneuver power was lower than hover power, this understated the peak. The function now considers each phase only when it has nonzero duration. The 144 historical CSV rows were regenerated in a temporary copy and matched the preserved CSV exactly: those cases have maneuver power above hover power. The historical `METODO.json` remains untouched and records the former script hash, not the corrected script. `tests/test_mission_peak.py` covers zero, partial and full maneuver durations. This correction does not validate either mission model.
