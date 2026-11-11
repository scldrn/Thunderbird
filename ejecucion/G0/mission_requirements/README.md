# Mission requirements traceability

This is a working interpretation of `../../../plan_maestro/REQUISITOS.csv` and `../../../configuraciones/ESCENARIOS_INVESTIGACION.json`, not a new approval of numerical acceptance criteria. T04 remains partial until the missing decision fields and their verification conditions are agreed. Requirements and actual performance are distinct.

| Requirement | Metric and unit | Existing target or investigation scenarios | Still needed for acceptance |
|---|---|---|---|
| R02 | Takeoff mass, kg, separately for each configuration | 2, 5, 10 kg targets | Mass definition, payload, consumables, uncertainty, margins and complete BOM per variant |
| R05 | Sustained airspeed, km/h | 600 intermediate, 1000 extension; unproven | Altitude, atmosphere, duration, airspeed definition, trim, energy reserve and test conditions |
| R06 | Position error, m; attitude error, degrees; settling time, s | Hover scenarios 30, 120, 300 s | Numerical error and settling limits, initial conditions, disturbances and acceptable energy state |
| R07 | Net acceleration vector, m/s² or g; orientation, degrees | 0.5, 1, 2 g investigation; 3, 6, 10 g stress demands | Required directions, simultaneous attitude, duration, tolerances, forces and moments under gravity |
| R08 | Attitude, degrees; orientation duration, s | Attitude change tests 30 and 90 degrees | Whether inverted or arbitrary-attitude sustained flight is required and under what conditions |
| R09 | Acceleration, m/s²; jerk, m/s³; angular rate, rad/s; rotation, degrees | 30 and 90 degree turns; acceleration levels above | Initial/final states, time and overshoot limits, load and orientation conventions |
| R11 | Hover and fast-flight duration, s; energy, Wh | 30, 120, 300 s separately in each mode | Selected combined sequence, transitions, energy reserve and power source |
| R12 | Payload mass, kg; volume, m³ | No accepted value | Definition, mass, envelope and placement |
| R13 | Altitude, m; density, kg/m³; temperature, °C; wind and gust, m/s | No accepted envelope | Values, correlations and test cases |
| R14 | Exposure and operating outcome | Water, dust, ice and corrosion require domain definition | Severity, duration, permitted degradation and applicable test |
| R15 | Acoustic level and thermal limits | Noise and heat limits undefined | Measurement quantity, location, duration and numerical limits |
| R34 | Fault and recovery state | Module, door, sensor and supply faults identified as cases to define | Fault set, allowed loss of function, recovery and operating conditions |

A scenario is an input to an analysis; an acceptance criterion needs an observable, numerical or categorical limit, conditions, configuration and a verification method. The above proposed metric definitions do not settle unchosen requirements. The 3/6/10 g entries are demands, not measured capability. Source files remain authoritative and historically dated.

For T06, the companion `../../G1/mission_energy_sensitivity/` estimates one simplified acceleration-plus-cruise sequence. It is not an approved mission and deliberately leaves hover, transition, braking, reserves, hardware and installed propulsion unresolved.
