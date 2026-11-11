# Verificación de esfuerzos y balance en campos no uniformes

3 de noviembre de 2026. Pasan las comprobaciones analíticas de los 12 estados prescritos: cuatro estados en tres mallas de 64, 128 y 256 celdas. Se ejecuta únicamente posprocesado; no son soluciones calculadas por un solver de flujo ni validación de C02.

## Parámetros y ecuaciones propias

Se usa un cubo de 1 m de lado, ρ=1,225 kg/m³ y ν=0,1 m²/s, elegido para la prueba matemática; no es la viscosidad del aire del vehículo. Las mallas tienen 4×N×2 hexaedros, N=8/16/32. Se prescriben U, presión cinemática y φ de cara en cada estado independiente. Los índices 0–3 no representan una evolución temporal.

- Couette: u(y)=2+Sy, con S=3 o 6 s⁻¹; presión cinemática constante 5 m²/s². El esfuerzo μS es constante. El signo de fuerza viscosa sobre cada frontera es el opuesto al esfuerzo sobre el fluido. La magnitud sobre cada pared horizontal es 0,3675/0,735 N; en las caras de entrada/salida aparece la componente transversal correspondiente. Las resultantes globales son cero.
- Poiseuille continuo: con η=y/H, u=Aη(1−η), A=6 m/s y H=1 m. De 0=−∂p/∂x+μ∂²u/∂y² se obtiene ∂(p/ρ)/∂x=−2νA/H²=−1,2 m/s². La fuerza de presión total es −1,47 N en X y la resistencia viscosa continua total +1,47 N.
- Poiseuille discreto: a los valores interiores de la parábola continua se suma A/(4N²), manteniendo u=0 en las dos paredes. Es la solución algebraica de la discretización ortogonal de segundo derivado y el gradiente normal de dos puntos de esta prueba. No se interpreta ese desplazamiento como un flujo continuo adicional junto a la pared.

Los perfiles de las caras laterales son condiciones matemáticas prescritas que eliminan el gradiente en Z; no representan seis paredes físicas inmóviles.

## Resultados verificados

La [condición de valor fijo](https://cpp.openfoam.org/v13/classFoam_1_1fixedValueFvPatchField.html) de pared usa el valor impuesto y la distancia al centro de la celda para el gradiente normal. Sobre la parábola continua muestreada, ese gradiente es A/H·[1−1/(2N)]. Por ello, el esfuerzo de pared reconstruido tiene un error relativo esperado 1/(2N), aunque el campo continuo satisfaga su ecuación diferencial.

| N | Celdas | Error relativo de esfuerzo, parábola continua | Defecto de CV en X, N | Defecto, parábola discreta |
|---:|---:|---:|---:|---:|
| 8 | 64 | 6,25% | −0,091875 | 0 |
| 16 | 128 | 3,125% | −0,0459375 | 0 |
| 32 | 256 | 1,5625% | −0,02296875 | 0 |

La integración de presión, las fuerzas viscosas de las seis fronteras y la partición coinciden con los valores analíticos/discretos esperados, con tolerancia absoluta 10⁻¹⁰. Se comprueban también el caudal, la cuadratura de u² y su ponderación por φ. El perfil discreto cierra el balance; el continuo presenta exactamente el defecto previsto del gradiente de pared. El error de esa reconstrucción se reduce a la mitad en cada refinamiento. Esto verifica el comportamiento del operador de pared en estos campos, no el orden global de un solver completo.

La función [forces de OpenFOAM 13](https://cpp.openfoam.org/v13/classFoam_1_1functionObjects_1_1forces.html) se contrasta con las expresiones anteriores; no se usa su propia salida como referencia matemática. `AUDITORIA.json` conserva los resultados y las huellas. Los logs y los cuatro campos de cada malla permiten repetir la inspección.

## Consecuencia para C02

Quedan comprobados signos, densidad, fuerzas viscosas no nulas, flujos y recarga de campos bajo las condiciones de esta prueba. No se demuestra equivalencia de los esfuerzos reconstruidos con todos los términos ensamblados en una malla tetraédrica, con limitadores y turbulencia. Tampoco se verifican aquí momento angular, rotor, geometría instalada o prestaciones.

`../flujo_C02_conducto/gradientes_r6_280_300/AUDITORIA.json` investiga separadamente el gradiente limitado de presión del caso real. Las dos evidencias deben interpretarse juntas antes de aprobar cargas.

Reproducción desde la raíz: `.venv-cad/bin/python investigacion-aeronautica/ejecucion/G2/verificar_cv_no_uniforme.py`. El script rechaza sobreescribir resultados y detiene su propio contenedor al terminar; para otra revisión hay que conservar la anterior y cambiar su identidad explícitamente.
