# Entregables: Presupuesto de Masa e Incertidumbre Epistemológica (C02)

Este directorio contiene los entregables del análisis de integridad másica y cuantificación de incertidumbre aeronáutica para la candidata **C02** y sus variantes hipotéticas de 2 kg, 5 kg y 10 kg.

El análisis reformula la auditoría previa de la Lista de Materiales (BOM) abandonando el supuesto simplista de "inventario cerrado" y adoptando un modelo formal de **presupuesto con intervalos de incertidumbre**, distinguiendo con rigor los datos medidos, supuestos y calculados, y preservando intactas las referencias base en `entradas/`.

---

## 1. Inventario de Archivos Generados en `salidas/`

| Archivo | Formato / Tipo | Propósito y Contenido |
|---|---|---|
| `salidas/presupuesto_incertidumbre.py` | Script Python 3 (Biblioteca Estándar) | Módulo ejecutable y librería de presupuesto. Contiene el motor dimensional `UnitChecker`, la clase `MassEntry`, agregadores de incertidumbre por intervalos, parsers de CSV y constructores de modelos. |
| `salidas/test_presupuesto_incertidumbre.py` | Suite de Pruebas (unittest) | Batería automatizada de 11 pruebas unitarias e integración que verifica inmutabilidad de referencias, distinción de desconocido vs cero, reglas de reservas, conversiones y fidelidad de datos. |
| `salidas/plantilla_presupuesto_masa.csv` | CSV Estandarizado | Plantilla oficial de presupuesto con columnas canónicas: `componente`, `masa medida`, `masa supuesta`, `intervalo inferior`, `intervalo superior`, `evidencia`, `estado`. Incluye filas guía que demuestran celdas vacías para datos desconocidos vs `0.0` para ceros explícitos. |
| `salidas/presupuesto_c02_5kg_incertidumbre.csv` | CSV Estandarizado | Presupuesto con incertidumbre de la candidata C02 (5,0 kg) integrando los 316 registros CAD, las 54 reservas volumétricas y el balance energético de G1. |
| `salidas/presupuesto_c02_roles_incertidumbre.csv` | CSV Estandarizado | Presupuesto desglosado por los 10 roles funcionales asumidos de la BOM C02, enlazando directamente con la auditoría geométrica previa. |
| `salidas/presupuesto_hipotetico_2kg.csv` | CSV Estandarizado | Presupuesto expresamente hipotético para objetivo de 2,0 kg (`pending_own_configuration`), sin inventar piezas comerciales ni pesos reales. |
| `salidas/presupuesto_hipotetico_10kg.csv` | CSV Estandarizado | Presupuesto expresamente hipotético para objetivo de 10,0 kg (`pending_own_configuration`), con escalado preliminar y márgenes AIAA S-120. |
| `salidas/REVISION_AUDITORIA_INCERTIDUMBRE.md` | Informe Técnico (Markdown) | Documento exhaustivo que profundiza en la reformulación epistemológica de la auditoría BOM, el tratamiento físico de cavidades y reservas, sensibilidades de material y desacoples energéticos. |
| `salidas/README.md` | Documentación General | Esta guía técnica de uso, verificación y advertencias normativas. |

---

## 2. Instrucciones de Ejecución y Reproducibilidad

Todo el código está desarrollado exclusivamente sobre la biblioteca estándar de Python 3 (`python3`), sin dependencias externas ni conexión a red.

### Generar o regenerar todos los presupuestos y verificar unidades:
Desde la raíz del espacio de trabajo:
```sh
python3 salidas/presupuesto_incertidumbre.py
```

### Ejecutar la suite completa de pruebas unitarias:
```sh
python3 salidas/test_presupuesto_incertidumbre.py
```
O mediante el módulo estándar `unittest`:
```sh
python3 -m unittest salidas/test_presupuesto_incertidumbre.py -v
```

---

## 3. Resumen de Pruebas Realizadas y Resultados

La suite automatizada en `salidas/test_presupuesto_incertidumbre.py` ejecutó 11 pruebas con resultado unánime de **11/11 APROBADAS (OK)**:

| ID de Prueba | Componente Auditado | Criterio de Aceptación y Verificación | Resultado |
|---|---|---|:---:|
| `test_01` | Inmutabilidad de referencias | Verifica que los 6 archivos en `entradas/` conservan exactamente sus hashes SHA-256 originales. | **OK** |
| `test_02` | Distinción desconocido vs cero | Verifica que celdas vacías y cadenas "DESCONOCIDO" devuelven `None`, mientras que "0.0" devuelve `0.0`. Garantiza que `None != 0.0`. | **OK** |
| `test_03` | Reglas de reservas volumétricas | Verifica que un volumen reservado sin hardware no puede tener masa medida asignada, y que su cota inferior puede ser 0.0 kg sin inferir que su masa real sea nula ni positiva. | **OK** |
| `test_04` | Unidades de masa | Comprueba la conversión exacta de g, mg, lb, oz a kg en `UnitChecker` y el rechazo de unidades no válidas. | **OK** |
| `test_05` | Volumen, densidad y constitutiva | Verifica conversiones de $\text{mm}^3$, $\text{cm}^3$, $\text{dm}^3$, $\text{L}$ a $\text{m}^3$, $\text{g/cm}^3$ a $\text{kg/m}^3$ y la ley física $m = V \cdot \rho$. | **OK** |
| `test_06` | Aritmética de intervalos | Comprueba que $m_{\min} \le m_{\max}$, que cotas negativas lanzan error y que la agregación por intervalos suma cotas inferior y superior. | **OK** |
| `test_07` | Fidelidad de lectura/escritura CSV | Ejecuta un ciclo completo de guardado y recarga (roundtrip) comprobando que las celdas vacías (`None`) y los ceros explícitos (`0.0`) no se degradan. | **OK** |
| `test_08` | Presupuesto C02 (5 kg) | Verifica que el presupuesto C02 tiene 0 componentes medidos, masa medida total `None`, y reservas con cota inferior en 0.0 kg. | **OK** |
| `test_09` | Modelos hipotéticos (2 kg y 10 kg) | Comprueba que las variantes de 2 kg y 10 kg declaran explícitamente estados hipotéticos, no afirman mediciones reales y no inventan componentes comerciales. | **OK** |
| `test_10` | Desglose por 10 roles funcionales | Comprueba que las sumas de las masas asignadas de los roles coinciden con los 262 registros de la BOM base ($2,783990\text{ kg}$). | **OK** |
| `test_11` | Principio de no inferencia de ausencia | Comprueba que la falta de copias locales de archivos no se interpreta como inexistencia en el repositorio, y que las reservas permanecen abiertas. | **OK** |

---

## 4. Reglas Críticas de Cumplimiento Epistemológico

1. **Distinción entre Valor Desconocido y Cero:**
   - En Python: `entry.masa_medida is None` representa un dato no medido. Nunca debe evaluarse mediante `float(val or 0.0)`, ya que falsearía el presupuesto transformando ausencia de datos en componentes de masa cero.
   - En CSV: Una celda vacía `""` representa valor desconocido. La cadena `"0.000000"` representa una verificación metrológica de masa cero.
2. **Los Volúmenes Reservados Pueden Estar Vacíos:**
   - Una reserva de espacio CAD (p.ej. el canal axial de $291.540\text{ mm}^3$ o los alojamientos de servos) es una cota geométrica de empaquetamiento.
   - **No prueba masa positiva:** El espacio puede permanecer vacío, como cavidad o conducto de paso de aire ($m = 0\text{ kg}$).
   - **No prueba masa cero:** Podría instalarse un motor o batería pesada ($m > 0\text{ kg}$).
   - Por consiguiente, su estado se define como `RESERVA_VOLUMETRICA_INCIERTA`, con intervalo $[0,000, m_{\max}]\text{ kg}$ y masa puntual `None`.
3. **No Inferencia por Archivos Ausentes:**
   - No se infiere que un archivo no copiado a este entorno de ejecución aislado no exista en el repositorio central de investigación aeronáutica.
4. **Sin Marcas, Mediciones ni Autores Inventados:**
   - Todos los ejemplos para 2 kg, 5 kg y 10 kg se identifican estrictamente como `HIPOTETICO`. No se han asignado pesos reales a componentes de catálogo ni se han inventado fabricantes comerciales.

---

## 5. Limitaciones Técnicas

1. **Inexistencia de Hardware Pesado en Báscula:** Ningún componente de la candidata C02 ni de las variantes de 2 y 10 kg ha sido sometido a pesaje real. La totalidad del hardware permanece en estado no calificado (`actual_hardware_qualified = False`).
2. **Presupuesto Físico Abierto:** Las cotas del presupuesto de 5,0 kg abarcan desde $2,446\text{ kg}$ hasta $8,776\text{ kg}$. Por tanto, la masa física del vehículo **no está cerrada**.
3. **Incompatibilidad con el Modelo de Potencia de G1:** Los $1,466\text{ kg}$ de remanente disponible en C02 son insuficientes para alojar los $3,04\text{ kg}$ a $6,40\text{ kg}$ de batería exigidos por el modelo de avance con 50 N de arrastre evaluado en el informe G1.
4. **Prohibición de Uso en Simulación Predictiva 6-DOF:** El centro de gravedad y los momentos de inercia calculados corresponden exclusivamente a sensibilidades geométricas rígidas y no deben utilizarse como modelos de planta definitiva para leyes de control de vuelo.
