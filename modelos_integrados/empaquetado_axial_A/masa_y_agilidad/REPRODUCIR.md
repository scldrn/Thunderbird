# Reproducir masa, CG y perfiles ideales

Desde la raíz del proyecto:

```sh
XDG_CACHE_HOME=/tmp/codex-aero-cache .venv-cad/bin/python investigacion-aeronautica/modelos_integrados/agilidad_masa_CG_A.py
.venv-cad/bin/python investigacion-aeronautica/modelos_integrados/verificar_agilidad_CG_A.py
```

Se usan los tres STEP de reservas de estaciones y el loft cerrado de referencia. El primer script integra material e inercia bajo hipótesis explícitas, genera 36 escenarios y estudia un giro prescrito en malla temporal, refinando tres escenarios. El segundo reconstruye las tres trayectorias nominales y comprueba balances de fuerza y momento con el tensor completo en 481 instantes.

Las masas de material se asignan con densidades supuestas; los motores, los rotores y el equipo restante todavía no están dimensionados. La masa residual se calcula para completar 5 kg por definición: no es evidencia de cierre de masa. Su ubicación de balance no acredita alojamiento físico.

Los comandos guardados no incluyen dinámica o límites de tasa de actuador. La asignación LP por instante puede saltar entre soluciones equivalentes; sus diferencias finitas de fuerza/dirección no son tasas mínimas de hardware. No ejecutar estas trayectorias en un vehículo como si fueran mandos validados ni usarlas como demostración de autonomía.
