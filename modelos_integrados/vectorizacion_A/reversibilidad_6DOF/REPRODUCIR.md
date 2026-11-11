# Reproducir esta etapa

Ejecutar desde `/Users/sam/Documents/ChatGPT/New project`, usando el entorno existente `.venv-cad`. No se requiere una instalación adicional para reproducir lo ejecutado en esta sesión.

Los scripts regeneran sus propias salidas. No lanzan ni modifican simulaciones CFD. Conservar los archivos de las ejecuciones rechazadas como evidencia histórica; el contenido de `auditoria_error_centro_original` no debe reutilizarse como resultado actual.

```sh
.venv-cad/bin/python investigacion-aeronautica/modelos_integrados/reversibilidad_6dof_A.py

XDG_CACHE_HOME=/tmp/codex-aero-cache .venv-cad/bin/python investigacion-aeronautica/modelos_integrados/doble_flujo_A.py

.venv-cad/bin/python investigacion-aeronautica/modelos_integrados/transitorios_ideales_A.py --case base_horizontal_5kg
.venv-cad/bin/python investigacion-aeronautica/modelos_integrados/transitorios_ideales_A.py
.venv-cad/bin/python investigacion-aeronautica/modelos_integrados/transitorios_ideales_A.py --preload 3
.venv-cad/bin/python investigacion-aeronautica/modelos_integrados/transitorios_ideales_A.py --preload 5

XDG_CACHE_HOME=/tmp/codex-aero-cache .venv-cad/bin/python investigacion-aeronautica/modelos_integrados/verificar_dominio_doble_flujo_A.py
MPLCONFIGDIR=/tmp/codex-aero-mpl .venv-cad/bin/python investigacion-aeronautica/modelos_integrados/generar_informe_control_A.py
```

La auditoría comprueba los archivos actuales y marca el informe como pendiente al comenzar. Si falla, resolver la causa antes de volver a generar el informe; no interpretar un archivo antiguo como verificación de un cálculo nuevo. La revisión reconstruye facetas, targets, equilibrio y restricciones de las trayectorias, además de contrastar coordenadas con el CAD.

Las optimizaciones de referencia ideal de potencia incluyen comprobación numérica de KKT; los LP de cambio de componentes incluyen comprobación de dualidad. Son verificaciones del modelo ideal declarado. No convierten las cifras en datos de empuje, potencia instalada, respuesta de servo o vuelo.
