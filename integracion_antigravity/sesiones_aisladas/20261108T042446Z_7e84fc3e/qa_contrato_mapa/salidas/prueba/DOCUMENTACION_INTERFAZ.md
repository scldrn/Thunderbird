# Documentación de Interfaz y Contrato de Datos Versionado
## Mapas Instalados de Módulo de Ventilador Interno (Fan Module)
**Versión del Contrato:** `1.0.0`  
**Fecha de Emisión:** 8 de noviembre de 2026  
**Ámbito:** Arquitectura A (ventiladores internos, referencia C02 / A07)  
**Entorno de Ejecución:** Python 3.9+ (Biblioteca estándar exclusivamente, sin dependencias externas)

---

## 1. Objeto y Alcance

Este documento especifica el **Contrato de Datos Versionado (v1.0.0)** para el almacenamiento, validación, intercambio e integración de **mapas aerodinámicos y propulsivos instalados** correspondientes a los módulos de ventilador interno de la aeronave.

### 1.1 Contexto de Ingeniería
En las fases preliminares de la arquitectura A (como en [simular.py](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_mapa_instalado/entradas/investigacion-aeronautica/simulacion_vuelo_A/simular.py)), el empuje de los ventiladores se ha modelado bajo supuestos ideales desacoplados (empuje de hasta 21 N, cono angular de 35° y retardo de primer orden $\tau = 80\,\text{ms}$). Como estipula el [PLAN-MAESTRO.md](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_mapa_instalado/entradas/investigacion-aeronautica/plan_maestro/PLAN-MAESTRO.md) (Hito G2, Sección 5.1):
> *"Sustituir el cono supuesto por una región alcanzable identificada, con incertidumbre, límites de tasa, retrasos y estados de transición. No convertir el ángulo mecánico de álabe en ángulo del empuje sin medir/calcular el conjunto... Evitar interpretar la carga sobre un álabe como reacción lateral neta instalada; cerrar balance de cantidad de movimiento."*

El presente contrato formaliza la estructura de datos que sustituirá dichos supuestos cuando se disponga de evidencia numérica (CFD) o experimental (banco de ensayos), **sin inventar mediciones inexistentes** y asegurando rigor en la trazabilidad.

---

## 2. Convención Explícita de Ejes y Punto de Aplicación

Para evitar ambigüedades en simuladores dinámicos 6DOF y algoritmos de asignación de control, el contrato define tres marcos de referencia y un punto de aplicación explícito.

```mermaid
graph LR
    subgraph Marcos de Coordenadas
        ML["MODULO_LOCAL (x_mod, y_mod, z_mod)"] -->|Rotación y Traslación| CAD["CAD_VEHICULO (x_cad, y_cad, z_cad)"]
        CAD -->|R_FLU_from_CAD = diag(-1,-1,1)| FLU["FLU_CUERPO (x_flu, y_flu, z_flu)"]
    end
```

### 2.1 Marcos de Referencia Soportados
1. **`MODULO_LOCAL` (Marco Propio del Ventilador):**
   - **Origen ($P_{app}$):** Centro geométrico del plano del disco del rotor sobre el eje axial del conducto ($z_{mod} = 0$).
   - **Eje $+x_{mod}$:** Longitudinal hacia proa relativa del módulo (paralelo al eje de vuelo $x_{FLU}$).
   - **Eje $+y_{mod}$:** Lateral hacia babor relativo del módulo (paralelo a $y_{FLU}$).
   - **Eje $+z_{mod}$:** Vertical a lo largo del eje del conducto cilíndrico, apuntando hacia arriba. Dado que el aire fluye hacia abajo ($-z_{mod}$), el empuje axial neto generado por el rotor sobre la estructura es positivo en $+z_{mod}$.
2. **`CAD_VEHICULO` (Sistema de Coordenadas CAD):**
   - Según [C02_CANDIDATA.json](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_mapa_instalado/entradas/investigacion-aeronautica/configuraciones/C02_CANDIDATA.json):
     - $x_{CAD}$: Longitudinal, con el morro del vehículo hacia $-x$.
     - $y_{CAD}$: Lateral, hacia estribor en $-y$.
     - $z_{CAD}$: Vertical hacia arriba.
3. **`FLU_CUERPO` (Forward-Left-Up de Dinámica de Vuelo):**
   - $x_{FLU}$: Longitudinal positivo hacia adelante (morro).
   - $y_{FLU}$: Lateral positivo hacia babor (izquierda).
   - $z_{FLU}$: Vertical positivo hacia arriba.
   - **Matriz de transformación CAD a FLU:**
     $$R_{FLU \leftarrow CAD} = \begin{bmatrix} -1 & 0 & 0 \\ 0 & -1 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

### 2.2 Punto de Aplicación y Reducción de Momentos
El contrato exige que todo mapa declare el punto de aplicación de la fuerza $P_{app} = [x_{app}, y_{app}, z_{app}]$ y el centro de momentos correspondiente.
Cuando una fuerza instalada $\vec{F} = [F_x, F_y, F_z]^T$ y un momento neto $\vec{M}_{app} = [M_x, M_y, M_z]^T$ expresados en $P_{app}$ se transfieren a un centro de gravedad arbitrario $P_{cg} = [x_{cg}, y_{cg}, z_{cg}]^T$, se debe aplicar rigurosamente el transporte vectorial:

$$\vec{M}_{cg} = \vec{M}_{app} + (\vec{r}_{app} - \vec{r}_{cg}) \times \vec{F}$$

Donde:
- $\vec{M}_{app}$ incluye el par de reacción de giro del rotor ($\pm Q_{rotor} \hat{z}$), momentos giroscópicos y momentos aerodinámicos de labio/conducto.
- $(\vec{r}_{app} - \vec{r}_{cg}) \times \vec{F}$ aporta el momento producido por el brazo de palanca de la fuerza instalada.

> [!IMPORTANT]
> Omitir $\vec{M}_{app}$ o calcular el momento únicamente como el producto del empuje por el brazo del CG asume erróneamente un rotor simétrico ideal sin par de torsión ni pérdidas de labio. El contrato impone la presencia de ambos términos.

---

## 3. Especificación del Contrato de Datos (Campos e Interfaces)

El contrato se implementa en formato JSON serializable y se valida formalmente mediante el validador en [contrato_mapa_ventilador.py](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_mapa_instalado/salidas/contrato_mapa_ventilador.py) y el esquema [esquema_contrato_v1.json](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_mapa_instalado/salidas/esquema_contrato_v1.json).

### 3.1 Unidades Canónicas Obligatorias
El bloque `unidades` es estrictamente mandatorio en la raíz del archivo:

| Dimensión Física | Unidad Canónica Permitida |
|---|---|
| Longitud | `"m"`, `"mm"` |
| Fuerza | `"N"`, `"kN"` |
| Momento / Torque | `"N*m"`, `"N m"`, `"Nm"` |
| Velocidad | `"m/s"`, `"m_s"` |
| Densidad | `"kg/m^3"`, `"kg/m3"`, `"kg_m3"` |
| Potencia | `"W"`, `"kW"` |
| Ángulo | `"deg"`, `"rad"` |
| Velocidad de Rotación | `"rpm"`, `"rad/s"` |
| Presión | `"Pa"`, `"kPa"`, `"bar"` |
| Temperatura | `"K"`, `"degC"` |

### 3.2 Entradas Físicas de Cada Muestra
Cada muestra en el arreglo `muestras` debe contener las siguientes variables de entrada física independientes:
1. **Flujo Local Vectorial (`flujo_local`):**
   - `velocidad_vectorial_m_s`: $[v_x, v_y, v_z]$ vector tridimensional de velocidad relativa del aire en la entrada del módulo ($m/s$).
   - `densidad_kg_m3`: Densidad del fluido local $\rho > 0$ ($kg/m^3$).
   - `temperatura_K`: Temperatura estática ambiente (opcional, por defecto 288.15 K).
   - `presion_estatica_Pa`: Presión estática local (opcional, por defecto 101325.0 Pa).
2. **Mando / Estado Cinemático (`mando_estado`):**
   - `rpm`: Velocidad de rotación del rotor ($rev/min \ge 0$).
   - `mando_normalizado`: Demanda de acelerador normalizada $u \in [0.0, 1.0]$ o $[-1.0, 1.0]$.
   - `deflexion_alabes_deg`: Deflexión vectorial de álabes orientadores $[\delta_x, \delta_y]$ en grados.
   - `estado_compuerta`: Estado de las compuertas de admisión/escape (`"abierto"`, `"cerrado"`, `"transicion"`, `"corte"`).
3. **Geometría de Referencia (`geometria_referencia`):**
   - `geometria_id`: Identificador trazable de la variante CAD (ej. `"C02_x160_5kg_MOD_FAN_01"`).
   - `modulo_id`: Identificador del alojamiento en el vehículo (ej. `"FAN_1"` a `"FAN_4"`).
   - `diametro_paso_nominal_m`: Diámetro de paso nominal del conducto (0.084 m para C02).
   - `radio_pala_nominal_m`: Radio exterior de la pala del rotor (0.041 m para C02).
   - `escala_geom`: Factor de escala frente al modelo de 5 kg (1.0 para referencia).
   - `sentido_giro`: `"CCW"` (antihorario) o `"CW"` (horario) visto desde $+z$.
   - `estados_compuertas_soportados`: Lista de estados cinemáticos compatibles.

### 3.3 Salidas Físicas de Cada Muestra
1. **`fuerza_vectorial_N`:** $[F_x, F_y, F_z]$ en Newtons. Vector 3D de fuerza total neta transmitida a la bancada del vehículo.
2. **`momento_vectorial_Nm`:** $[M_x, M_y, M_z]$ en Newton-metros. Vector 3D de momentos mecánicos y aerodinámicos sobre el punto $P_{app}$.
3. **`potencia_electrica_W`:** Potencia eléctrica consumida por el inversor/motor en Watts (cuando se conozca).
4. **`potencia_mecanica_W`:** Potencia mecánica al eje $P_{mec} = Q \cdot \omega$ en Watts (cuando se conozca).

---

## 4. Política Estricta de Datos Faltantes vs. Coerción a Cero

> [!CAUTION]
> En ingeniería aeronáutica, un dato no medido o desconocido **NUNCA** debe coercionarse a cero (`0.0`).
> Si la potencia eléctrica de un rotor produciendo 12 N a 26000 RPM se registrara como `0.0 W`, los optimizadores de energía y balances de batería inferirían que el módulo opera sin consumir energía (violación física de la conservación de energía).

### 4.1 Representación de Datos Faltantes
El contrato admite valores ausentes únicamente en magnitudes donde su no disponibilidad sea físicamente comprensible en campañas preliminares (ej. balances de fuerzas en bancos estáticos sin telemetría de corriente/voltaje):
- En JSON se codifica como `null`:
  ```json
  "potencia_electrica_W": null,
  "marcas_datos_faltantes": {
    "potencia_electrica_W": "NO_MEDIDO"
  }
  ```
- O alternativamente con estructura expandida:
  ```json
  "potencia_electrica_W": {
    "es_dato_faltante": true,
    "estado": "NO_MEDIDO",
    "motivo": "Banco estático de balance sin sonda de corriente instalada"
  }
  ```
- En memoria Python: El validador instancia un objeto `RegistroDatoFaltante(estado='NO_MEDIDO')` que preserva la condición `es_dato_faltante = True` y asegura que:
  `muestra.potencia_electrica_W != 0.0`.
- Cuando el motor esté deliberadamente inactivo (ej. RPM = 0 con compuerta cerrada), la potencia se registra legítimamente como `0.0 W` con `marcas_datos_faltantes: {}`.

---

## 5. Trazabilidad de Origen e Incertidumbre

### 5.1 Distinción Taxonómica del Origen
El bloque `metadatos_origen` clasifica rigurosamente la fuente de los datos:
- `"medido"`: Datos experimentales reales de túnel de viento o banco de ensayo.
- `"calculo"`: Resultados numéricos convergidos (CFD RANS/LES, BEM, vortex lattice).
- `"supuesto"`: Estimaciones analíticas ideales, modelos reducidos o datos sintéticos de prueba.

Además, el contrato incorpora el booleano obligatorio `es_sintetico`:
- Si `es_sintetico: true`, el archivo se identifica inequívocamente como muestra sintética y no se aceptará como evidencia de validación física de vuelo.

### 5.2 Estructura de Incertidumbre
Cada muestra incluye su bloque `incertidumbre`:
- `fuerza_vectorial_N`: $[u_{Fx}, u_{Fy}, u_{Fz}]$ (incertidumbres expandidas en N).
- `momento_vectorial_Nm`: $[u_{Mx}, u_{My}, u_{Mz}]$ (incertidumbres expandidas en N*m).
- `potencia_electrica_W`: $u_{Pe}$ en W (o `null` si no está medida).
- `potencia_mecanica_W`: $u_{Pm}$ en W (o `null` si no está calculada).
- `tipo_incertidumbre`: `"EXPANDIDA_K2"` (factor de cobertura $k=2$, ~95% nivel de confianza), `"ESTANDAR_1SIGMA"`, o `"INTERVALO_TOLERANCIA"`.
- `metodo_evaluacion`: Descripción del método (ej. `"GCI_Richardson_3_mallas"` para CFD, `"Propagacion_GUM_sensores"` para ensayos).

---

## 6. Dominio de Validez y Rechazo de Extrapolación

El bloque `dominio_validez` define los intervalos continuos de interpolación segura:
```json
"dominio_validez": {
  "densidad_kg_m3": [1.0, 1.3],
  "velocidad_modulo_m_s": [0.0, 40.0],
  "rpm": [0.0, 32000.0],
  "deflexion_alabes_deg": [-35.0, 35.0],
  "politica_extrapolacion": "RECHAZAR"
}
```

### Reglas de Rechazo por Extrapolación:
1. Si una muestra tiene el atributo `es_extrapolacion: true`, el validador la **RECHAZA** inmediatamente con el código `EXTRAPOLACION_DECLARADA`.
2. Si las entradas físicas de una muestra violan cualquiera de los rangos anteriores y la política es `"RECHAZAR"`, el validador la **RECHAZA** inmediatamente.

---

## 7. Validador en Python Estándar (`contrato_mapa_ventilador.py`)

### 7.1 Arquitectura del Validador
El archivo [contrato_mapa_ventilador.py](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_mapa_instalado/salidas/contrato_mapa_ventilador.py) está escrito exclusivamente con módulos de la biblioteca estándar de Python (`json`, `math`, `dataclasses`, `enum`, `typing`, `pathlib`, `sys`). No requiere NumPy, SciPy, Pandas ni Pydantic para su funcionamiento.

### 7.2 Taxonomía de Errores de Validación

| Código de Error | Causa del Rechazo |
|---|---|
| `UNIDADES_AUSENTES` | Bloque `unidades` ausente, unidad vacía o dimensión física no admitida. |
| `VALOR_NAN_DETECTADO` | Presencia de `NaN`, `inf` o cadenas literales de punto flotante inválido. |
| `GEOMETRIA_O_EJES_DESCONOCIDOS` | Marco de referencia no registrado, geometrías no identificadas o dimensiones $\le 0$. |
| `MUESTRAS_DUPLICADAS` | Dos o más muestras coinciden en el espacio de entradas físicas ($v_x, v_y, v_z, \rho, \text{RPM}, u, \vec{\delta}, \text{compuerta}$). |
| `EXTRAPOLACION_DECLARADA` | Muestra marcada con `es_extrapolacion: true` o inputs fuera del dominio cuando la política es `RECHAZAR`. |
| `CAMPO_OBLIGATORIO_FALTANTE` | Ausencia de campos estructurales obligatorios o nulidad en campos que no admiten falta de datos. |
| `ESTRUCTURA_INVALIDA` | Malformación del esquema JSON raíz o de los tipos de datos básicos. |

### 7.3 Uso del Validador desde Línea de Comandos (CLI)
```bash
python3 salidas/contrato_mapa_ventilador.py validar salidas/ejemplo_sintetico_mapa.json
```
Salida esperada:
```text
[OK] El archivo 'salidas/ejemplo_sintetico_mapa.json' cumple rigurosamente con el contrato de datos v1.0.0.
     ID Mapa: MAP_FAN_C02_SINTETICO_001
     Geometría: C02_x160_5kg_MOD_FAN_01 (FAN_1)
     Total de muestras validadas: 4
     Muestras con potencia eléctrica no medida: 2 (preservadas como faltantes, no cero)
     Muestras con potencia mecánica no calculada: 1
```

### 7.4 Uso Programático desde Código Python
```python
from contrato_mapa_ventilador import cargar_mapa_json, RegistroDatoFaltante

mapa = cargar_mapa_json("salidas/ejemplo_sintetico_mapa.json")

for muestra in mapa.muestras:
    # Verificación segura de potencia eléctrica sin asumir cero
    if isinstance(muestra.potencia_electrica_W, RegistroDatoFaltante):
        print(f"Muestra {muestra.id_muestra}: Potencia eléctrica no disponible ({muestra.potencia_electrica_W.estado})")
    else:
        print(f"Muestra {muestra.id_muestra}: Potencia eléctrica = {muestra.potencia_electrica_W:.1f} W")
```

---

## 8. Guía de Integración con Consumidores Downstream (Simulador 6DOF)

> [!NOTE]
> De acuerdo con las instrucciones de la orden de trabajo, **el simulador original `entradas/.../simular.py` no ha sido alterado**.

Para conectar futuros mapas instalados válidos a un integrador de vuelo como `simular.py` sin alterar el código base original, se recomienda el patrón de diseño **Adaptador Propulsivo**:

```python
class AdaptadorMapaInstalado:
    """Adaptador desacoplado para alimentar simulaciones de vuelo con mapas validados."""
    def __init__(self, ruta_mapa_json: str):
        from contrato_mapa_ventilador import cargar_mapa_json, transferir_momento, rotacion_cad_a_flu
        self.mapa = cargar_mapa_json(ruta_mapa_json)
        self.p_app = self.mapa.punto_aplicacion.coordenadas_m

    def evaluar_empuje_y_momento_en_cg(self, v_local_m_s, rho_kg_m3, rpm, deflexion_deg, r_cg_modulo_m):
        # 1. Comprobar si está dentro del dominio de validez
        # 2. Interpolar fuerza vectorial [Fx, Fy, Fz] y momento [Mx, My, Mz] sobre P_app
        # 3. Transferir el momento al CG del vehículo:
        #    M_cg = transferir_momento(F, M_app, self.p_app, r_cg_modulo_m)
        # 4. Retornar fuerzas y momentos transformados al marco FLU
        pass
```

---

## 9. Ejemplo Sintético Marcado (`ejemplo_sintetico_mapa.json`)

El archivo [ejemplo_sintetico_mapa.json](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_mapa_instalado/salidas/ejemplo_sintetico_mapa.json) implementa 4 casos de prueba sintéticos:
1. `SINT_0001_ESTACIONARIO_NOMINAL`: Vuelo estacionario a 26000 RPM ($V=0$). Ambas potencias medidas ($P_{elec} = 310.5\,\text{W}$, $P_{mec} = 248.4\,\text{W}$).
2. `SINT_0002_AVANCE_POT_ELEC_NO_MEDIDA`: Flujo cruzado de 12 m/s. Potencia eléctrica señalada con marca `"NO_MEDIDO"` (conservada como `null` y objeto no nulo, sin transformar a cero).
3. `SINT_0003_VECTORIZADO_POTENCIAS_NO_DISPONIBLES`: Flujo cruzado a 5 m/s con álabes deflexionados a 15°. Ambas potencias marcadas como no disponibles (`"NO_MEDIDO"`, `"NO_CALCULADO"`).
4. `SINT_0004_COMPUERTA_CERRADA_REPOSO`: Rotor inactivo ($\text{RPM} = 0$, compuerta cerrada). Potencia registrada legítimamente como `0.0 W` correspondiente a motor desenergizado.

---

## 10. Resumen de Pruebas Realizadas y Limitaciones

### 10.1 Batería de Pruebas Automatizadas
La suite [test_contrato_mapa.py](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_mapa_instalado/salidas/test_contrato_mapa.py) ejecutó **25 pruebas unitarias** pasando el 100% con éxito (`OK` en 0.008s):
- **4 pruebas de unidades ausentes o inválidas:** Comprobación de omisión de bloque, cadenas vacías, campos ausentes y unidades no canónicas.
- **5 pruebas de detección de NaN:** En velocidad, densidad, fuerza, incertidumbre y cadenas literales `"NaN"`.
- **6 pruebas de geometrías y ejes desconocidos:** Marco desconocido, punto de aplicación inválido, ID desconocida, diámetros negativos, giros no soportados y compuertas incompatibles.
- **1 prueba de muestras duplicadas:** Detección de colisión exacta en el espacio de entradas físicas.
- **3 pruebas de extrapolación declarada:** Rechazo por flag `es_extrapolacion: true`, exceso de RPM y exceso de velocidad frente al dominio.
- **3 pruebas de manejo de datos faltantes:** Verificación de aceptación de marcas, confirmación estricta de no-coerción a cero (`!= 0.0`) y persistencia en formato JSON.
- **1 prueba de obligatoriedad:** Rechazo de `null` en magnitudes mandatorias como densidad o fuerza.
- **2 pruebas cinemáticas:** Validación de rotación CAD-a-FLU y transporte vectorial de momentos $(\vec{r} \times \vec{F})$.

### 10.2 Limitaciones Declaradas
1. **Datos Sintéticos:** Los datos incluidos en `ejemplo_sintetico_mapa.json` son estrictamente analíticos y demostrativos; no deben emplearse para cerrar hitos de certificación de vuelo ni validar márgenes de maniobra.
2. **Interpolación Espacial:** El validador se enfoca en la verificación estricta de integridad, consistencia y conformidad del contrato; los algoritmos de interpolación multivariante (ej. RBF o kriging dentro del dominio) corresponden al consumidor de los datos.
3. **Mecánica de Compuertas Transitorias:** El contrato soporta el estado `"transicion"` en compuertas, pero la cinemática continua del mecanismo (61 nodos de elevación/giro indicados en [C02_CANDIDATA.json](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_mapa_instalado/entradas/investigacion-aeronautica/configuraciones/C02_CANDIDATA.json)) requerirá mapear el ángulo de apertura como variable continua en revisiones posteriores cuando se disponga de ensayos dinámicos.
