# Malla fina RAE2822: segunda corrida terminada

3 de noviembre de 2026. La malla fina mantiene cargas casi constantes y resolución de primer punto de pared y+<1. La diferencia de arrastre respecto a la malla gruesa sigue siendo aproximadamente 3,42%. La turbulencia conserva cambios medibles; la verificación experimental y de malla no está cerrada.

Es continuación del [informe de configuración y método](INFORME-NASA-SU2.md), sobre el mismo perfil y dominio NASA convertidos. No corresponde a C02 ni al vuelo del vehículo.

## Resultado calculado

`su2_nasa_fina_r2` completa 1.800 iteraciones adicionales a las 1.200 de r1, salida 0, en 644,57 s de reloj. No altera geometría, modelos, transporte, condiciones libres ni esquemas. Conserva reinicio, campos completos y hashes.

| Magnitud | Resultado de fina r2 |
|---|---:|
| Nodos / cuadriláteros | 97.956 / 97.152 |
| CL | 0,67879834 |
| CD | 0,01259316 |
| y+ de pared, mínimo–máximo | 0,1176–0,9762 |
| Deriva entre medias de 20, CL / CD | 3,99×10⁻⁷ / 1,22×10⁻⁸ |
| RMS de Cp frente a los 103 puntos | 0,123145 |
| Diferencia de CD frente a gruesa r3 | −3,424% |
| Diferencia relativa de CL frente a gruesa r3 | +0,00706% |

La pequeña diferencia de CL cambia de signo respecto a la comparación provisional con fina r1. Esto confirma la necesidad de separar evolución iterativa de sensibilidad de malla. El cambio de CD se mantiene, pero dos mallas anisótropamente refinadas no permiten declarar independencia ni un GCI formal.

La extracción independiente de presión y tracción viscosa completa vuelve a coincidir con la fuerza nativa: error máximo de coeficiente 5,1×10⁻¹². La reconstrucción de fronteras características/Roe deja masa neta relativa a ρ∞U∞c de 9,99×10⁻⁹ y defecto de momento (−2,952×10⁻⁵;−3,329×10⁻⁵), normalizado por q∞c. Su componente axial equivale aproximadamente a 0,245% de CD. Son comprobaciones numéricas, sin identidad completa del ensamblaje ni validación física.

## Campo completo y siguiente comprobación

Entre fina r1/r2, las diferencias relativas L2 son 2,54×10⁻⁵ en densidad, 8,28×10⁻⁵ y 2,10×10⁻⁴ en momento X/Y, 2,35×10⁻⁵ en energía, 4,79×10⁻³ en k y 6,60×10⁻⁵ en ω. La mayor variación de k se encuentra en la estela, cerca de x/c=1,042; su cambio máximo es 11,95 m²/s², un 1,53% del máximo de referencia. No se ignora por observar cargas globales estables.

`su2_nasa_fina_r3_sonda` añade 600 iteraciones forzadas desde el estado más reciente. Permitirá distinguir el ajuste inicial de r1 de la evolución de un intervalo tardío. Deben inspeccionarse el proceso y el resultado reales antes de continuarlo; no reiniciar por caducidad de una observación.

El RMS experimental es ligeramente mayor que en la malla gruesa: mejorar y+ no implica mejorar automáticamente la concordancia física. Se conservan los 103 puntos, incluidas las discrepancias de borde de ataque y zona de choque. Permanecen abiertos modelo/transportes/transición, refinamiento adicional y presupuesto de incertidumbre adecuado a la magnitud que se quiera utilizar.

Evidencias: `su2_nasa_fina_r2/AUDITORIA_SU2.json`, `TRACCION_RECONSTRUIDA.json`, `DIAGNOSTICO_RESIDUOS_CP.json` y `COMPARACION_MALLAS_SU2_r2.json`. T21, G4 y el objetivo completo permanecen abiertos. No se han aprobado cargas del vehículo ni 600–1000 km/h.
