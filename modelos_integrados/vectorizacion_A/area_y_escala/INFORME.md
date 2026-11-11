# Arquitectura A: área, escala y referencia de potencia de estacionario

**Estimaciones de cribado; no son prestaciones verificadas ni selección de motor.** Se conserva el diseño A aprobado. Masa de referencia 5 kg supuesta; cuatro rotores ilustrativos de diámetro de barrido calculado 82,024 mm a partir de sus vértices en el script CAD. Las escalas de 2 y 10 kg son operaciones algebraicas a densidad media constante, no presupuestos de masa cerrados.

La referencia usa cuatro rotores libres ideales con carga igual, aire de 1,225 kg/m³, g=9,80665 m/s² y P=(mg)^(3/2)/√(2ρA_total). No incluye pérdidas ni maniobra. Un conducto puede contribuir al empuje y cambiar el flujo: esta referencia no se presenta como cota inferior universal del sistema con conductos ni como potencia eléctrica instalada. NASA NDARC diferencia explícitamente el rotor libre y el ventilador carenado.

| Masa supuesta | Escala | Envolvente algebraica L × ancho × alto, mm | Ø de cada rotor, mm | Área total, m² | Potencia inducida ideal de referencia, W | Energía de referencia en 120 s, Wh |
|---:|---:|---|---:|---:|---:|---:|
| 2 kg | 0.737 | 991 × 237 × 143 | 60.4 | 0.01147 | 518 | 17.3 |
| 5 kg | 1.000 | 1345 × 322 × 194 | 82.0 | 0.02114 | 1509 | 50.3 |
| 10 kg | 1.260 | 1695 × 406 × 245 | 103.3 | 0.03355 | 3387 | 112.9 |

Las energías no equivalen a capacidad de batería ni autonomía: faltan potencia real, energía utilizable, reserva, refrigeración y masa de esa batería. A semejanza geométrica, área ∝ m^(2/3), carga de disco ∝ m^(1/3) y esta potencia de referencia ∝ m^(7/6). No se infiere que el mismo ventilador o mapa escale sin cambiar Reynolds, velocidad de punta y límites térmicos.

| Ø rotor para 5 kg, mm | Potencia ideal de referencia, W | Separación entre discos al mantener el paso lateral original de 130 mm, mm |
|---:|---:|---:|
| 82.0 | 1509 | 48.0 |
| 100.0 | 1238 | 30.0 |
| 120.0 | 1031 | 10.0 |
| 160.0 | 773 | -30.0 |
| 200.0 | 619 | -70.0 |

Una separación negativa implica solapamiento geométrico de los discos coplanares a los centros actuales. Una separación positiva no demuestra alojamiento: faltan camisas, holguras, espesores, estructura, conductos, motores y secciones locales de la carrocería. La tabla permite estudiar más área sin prometer que quepa dentro de la envolvente elegida.

El CAD de estilo original tiene radio de taladro de camisa de 41 mm, frente a un vértice de hélice a √(41²+1²)=41,012 mm: no tenía holgura funcional definida. La rama preliminar retenía esas camisas. Se corrigió en `../CAD_integracion_coherente/A_integracion_conductos_coherentes.step`: cuatro conductos consolidados con radio interior de 42 mm y separación radial geométrica aproximada de 0,988 mm. Las comprobaciones locales están en su `VERIFICACION.json`; no declaran suficiente la holgura de operación ni cierran deformaciones o tolerancias.

La CFD de entrada impuesta de 40 m/s solo ensaya un conducto sin rotor: no garantiza que el ventilador genere ese caudal o presión, ni demuestra el empuje útil exigido por el análisis de control. El dimensionamiento siguiente requiere una curva presión–caudal–potencia y un balance integrado de entrada/salida/carcasa.

Fuentes primarias: [NASA NDARC Theory 2017](https://ntrs.nasa.gov/api/citations/20170011656/downloads/20170011656.pdf) y [NASA NDARC, apéndice teórico](https://ntrs.nasa.gov/api/citations/20230003601/downloads/NASA%20TP-20220000355%20appxA.pdf). Las cifras de las tablas proceden de `CALCULOS.json`, regenerable con `escala_area_potencia_A.py`.
