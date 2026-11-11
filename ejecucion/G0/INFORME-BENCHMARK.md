# Verificación numérica inicial: canal de Poiseuille

Fecha: 3 de noviembre de 2026. Tarea T05, alcance parcial.

Se ejecutaron diez casos pequeños con OpenFOAM Foundation 13, imagen `codex-aero-openfoam:13`, sin reanudar los dos solvers históricos pausados. El tutorial original era viscoelástico; se conservó en `planarPoiseuille_tutorial/` y se adaptó explícitamente a fluido newtoniano Stokes. No se utilizó su solución de Maxwell como referencia newtoniana.

## Modelo y referencia independiente

Semicanal uniforme: pared sin deslizamiento y=0, simetría y=H=1 m, periodicidad longitudinal y dirección z vacía. Velocidad inicial cero, viscosidad cinemática ν=0,1 m²/s y fuente específica de aceleración G=5 m/s². Se compara el campo a t=4 s, no el régimen estacionario.

La solución de ∂u/∂t=ν∂²u/∂y²+G es:

```
u_s = G/ν (H y − y²/2)
k_n = (n+1/2)π/H
u(y,t) = u_s − Σ [2G/(Hν k_n³)] sin(k_n y) exp(−ν k_n²t)
```

`auditar_poiseuille.py` usa 1000 términos y comprueba el mismo resultado con 2000. También compara con la solución temporal exacta del operador de difusión de volúmenes finitos mediante exponencial matricial. Revisa malla ejecutada, terminación, modelo Stokes, campos finitos y huellas de entradas/resultados. Las huellas de entradas se reconstruyeron de los archivos conservados después de ejecutar; no son una atestación inmutable previa al cálculo.

## Resultados

Error: máximo absoluto longitudinal dividido por máximo analítico en centros de celda. Los tiempos son CPU observada; no predicen costes de una malla de vehículo.

| Celdas | Δt (s) | Correctores exteriores | Error (%) | CPU (s) |
|---:|---:|---:|---:|---:|
| 20 | 0,005 | 2 | 0,492624 | 1,52 |
| 40 | 0,005 | 2 | 1,833509 | 3,52 |
| 80 | 0,005 | 2 | 4,760946 | 2,01 |
| 40 | 0,0025 | 2 | 0,708580 | 3,67 |
| 20 | 0,005 | 15 | 0,096958 | 4,01 |
| 40 | 0,005 | 15 | 0,033205 | 6,44 |
| 80 | 0,005 | 15 | 0,054932 | 9,44 |
| 40 | 0,005 | 50 | 0,033174 | 15,86 |
| 80 | 0,005 | 50 | 0,037240 | 19,05 |
| 80 | 0,0025 | 50 | 0,017932 | 36,69 |

La familia de dos correctores se rechaza como evidencia de convergencia de malla: refinar empeora el resultado. Con 50 correctores y Δt reducido, el error respecto al operador semidiscreto baja aproximadamente a la mitad. No se ha establecido convergencia formal de segundo orden espacial/temporal, aunque el diccionario especifica `backward`; no se calcula GCI ni se declara resuelta la causa del comportamiento temporal. Las velocidades transversales finales son inferiores a 2×10⁻¹⁵ m/s.

Se selecciona el último caso para comprobar integración con ParaView por su acuerdo en este instante; el umbral del auditor es una comprobación local de regresión, no un criterio universal de aceptación CFD. El proceso empleó 37 s de reloj. ParaView recuperó sus 80 celdas y produjo imagen/estado, comprobados también en la interfaz nativa.

## Alcance y paso siguiente

Esto verifica una solución simple y la cadena de datos. No valida modelos de turbulencia, choques, rotor, conducto vectorial o vehículo. Los diez campos y registros se conservan, incluidos los rechazados. `AUDITORIA-POISEUILLE.json` y `COMPARACION.csv` por caso contienen métricas reproducibles.

T05 permanece parcial: se requiere contraste experimental representativo. Se recuperó un ensayo de rotor entubado y, para la rama compresible, CAD y Cp públicos del ONERA M6; cada uno necesita identificar diferencias geométricas/modelos antes de ejecutar una campaña. No se inicia una campaña masiva a partir del coste del canal.
