# C01: predimensionado del rotor e integración pendiente

3 de noviembre de 2026. T10 en ejecución, arquitectura A de ventiladores internos. **No se selecciona un motor definitivo ni se acredita estacionario o agilidad.** Se dispone de un modelo anular propio, candidatos CAD calculados y restricciones concretas para el siguiente rediseño. A07 sigue siendo la referencia canónica.

## Evidencia experimental recuperada y contraste

La [base UIUC, volumen 1](https://m-selig.ae.illinois.edu/props/volume-1/propDB-volume-1.html), vinculada al trabajo AIAA 2011-1255 de Brandt y Selig, proporciona [16 puntos estáticos](https://m-selig.ae.illinois.edu/props/volume-1/data/apce_10x5_static_pg0819.txt) de la APC 10×5E y una [digitalización aproximada de cuerda/torsión](https://m-selig.ae.illinois.edu/props/volume-1/data/apce_10x5_geom.txt). Se conservaron originales y huellas en `benchmark_apc/`. Sus CT medidos van de 0,0914 a 0,0994 entre 2508 y 6708 rpm.

Se compararon sin ajuste con el [archivo APC de simulación](https://www.apcprop.com/files/PER3_10x5E.dat), interpolando únicamente dentro de su intervalo de rpm. El error absoluto medio relativo es 5,09% en CT y 3,88% en CP. El archivo identifica versión/fecha de cálculo de 2022. [APC describe esas tablas como predicciones computacionales](https://www.apcprop.com/technical-information/performance-data/), no ensayos. No se acreditó identidad de revisión con la hélice histórica. Estos errores **no son incertidumbre del rotor propio ni validación de nuestro BEM**. Véanse `contrastar_apc.py` y `benchmark_apc/CONTRASTE.json`.

La geometría digitalizada no define toda la superficie tridimensional de pala. La descarga del archivo geométrico completo del fabricante devolvió HTTP 403. El contraste de coeficientes publicado sí se completó; la reproducción CFD exacta del espécimen sigue pendiente.

## Modelo propio: qué resuelve y qué supone

`bem_hover.py` utiliza CL/CD experimentales SD8020 del programa [UIUC Low-Speed Airfoil Tests](https://m-selig.ae.illinois.edu/pd.html), *Summary of Low-Speed Airfoil Data*, volumen 1, Selig et al., 1995. No se refleja artificialmente la polar ni se oculta la extensión de extremos. Sus cuatro Reynolds y ángulos originales se comprueban contra el interpolador.

El modelo es de rotor libre aislado en estacionario. Cada anillo resuelve simultáneamente velocidad inducida axial y remolino, igualando fuerzas de elemento de pala con cantidad de movimiento. Con velocidad tangencial relativa U=Ωr−vθ y W²=U²+vi²:

```
φ = atan2(vi,U),  α = β−φ
dT/dr = B ρW²c/2 (CL cosφ−CD sinφ) = 4πρr F vi²
dQ/dr = B ρW²cr/2 (CL sinφ+CD cosφ) = 4πρr² F vi vθ
P = Ω∫dQ
```

F es el producto de correcciones de punta/raíz implementadas explícitamente. Son aproximaciones del modelo libre, sin calibración para el conducto. Se verifica la identidad energética `P=∫[vi dT + (vθ/r)dQ + D_perfil W dr]`, que detecta errores de signo o doble cuenta; no verifica por sí sola exactitud física.

Supuestos C01: ocho palas, radio de raíz 0,30R; cuerda relativa variable documentada en el script; α de diseño 6°; rotor de 82 mm frente a taladro de referencia de 84 mm en la escala 5 kg. La torsión se sintetiza para cada punto de diseño de estacionario. Las maniobras de cada candidato **reutilizan esa torsión**, variando rpm. No se rediseña la pala para aparentar seguimiento de cada demanda.

Se usan ρ=1,225 kg/m³, ν=1,46×10⁻⁵ m²/s y sonido 340,3 m/s. Se plantean κ=F_módulo_neto/T_rotor_aislado de 0,70/0,85/1,00 y eficiencia eléctrica 0,90, todos **supuestos**. κ no es una eficiencia medida, una cota universal ni un modelo de vectorización. Reparto igual entre cuatro módulos, sin reserva de momento, CG desplazado o interacción con el cuerpo.

Cinco pruebas pasan: tablas originales/interpolador, balances y energía, semejanza dimensional con coeficientes constantes, recuperación de la torsión por el solucionador directo y sensibilidad radial 64→128. Hay 15 diseños, 45 puntos de operación con perfiles anulares conservados, 243 sensibilidades de batería y 54 presupuestos parciales de misión. No hay mapa instalado ni respuesta temporal identificada.

## Resultados condicionados de estacionario

κ=0,85 y η eléctrica=0,90. Potencia total estimada de los cuatro módulos; las masas de fila son objetivos, no masas cerradas. Fuente de cálculo: `modulo_preliminar/OPERACION_CONDICIONAL.csv`.

| Masa objetivo | D rotor, referencia / ×1,25 / ×1,50 (mm) | Potencia total (kW) | Mach de punta rotacional |
|---:|---:|---:|---:|
| 2 kg | 60,4 / 75,5 / 90,6 | 1,02 / 0,82 / 0,68 | 0,488 / 0,390 / 0,325 |
| 5 kg | 82,0 / 102,5 / 123,0 | 2,97 / 2,38 / 1,98 | 0,583 / 0,467 / 0,389 |
| 10 kg | 103,3 / 129,1 / 155,0 | 6,60 / 5,28 / 4,40 | 0,655 / 0,524 / 0,437 |

En 2 kg, aproximadamente el 29,8% del par modelado de estacionario usa secciones fuera del dominio de la polar; en 5 kg, 2,03%; en 10 kg, 0,76%. La ampliación geométrica de diámetro a igual masa y carga conserva aproximadamente Reynolds en estos diseños semejantes, pero reduce Mach. **La cifra de 2 kg no acredita viabilidad.** Se requieren datos apropiados de menor Reynolds o cambiar cuerda/perfil/número de palas y volver a contrastar.

La solidez local máxima se aproxima a 1: las interacciones de cascada y tridimensionales pueden ser relevantes y no están validadas por la polar 2D. Las contribuciones con Mach relativo superior a 0,3 se registran; 0,3 es un indicador de cribado, no un límite experimental acreditado para esta polar ni una validación de las contribuciones restantes. No se aplicó una corrección compresible para fingir cobertura.

Para 5 kg, rotor de 102,5 mm: el escenario lateral de 0,5 g requiere dirección neta 26,565° y da 2,80 kW en este modelo; el escenario de aceleración vertical ascendente de 1 g da 6,66 kW. No son maniobras demostradas. Con 82 mm, los valores son 3,51 y 8,32 kW. Falta autoridad de momento, mapa de álabes, potencia transitoria y control. El modelo actual no acredita fuerzas negativas ni movimientos abruptos en todo el espacio.

## CAD de los rotores y comprobación de alojamiento

Se crearon dos rotores de referencia de 5 kg, D82 y D102,5 mm, con perfil SD8020, torsión calculada y 66 secciones de loft. Cada uno es un sólido unido con ocho palas y cubo; se exportaron cuatro STEP, dos sentidos de giro mediante geometría especular. Se reimportaron válidos. Cuatro separaciones angulares independientes, por simetría de ocho palas, no presentan intersección pala–pala. Los encuentros con el cubo se unen geométricamente; faltan filetes, retención y dimensionamiento. `modulo_preliminar/CAD/GEOMETRIA.json` identifica fuentes y resultados.

El primer cálculo de volumen con integración no adaptativa no satisfizo la identidad de unión. Se conserva el rechazo. Con cuadratura adaptativa explícita, la diferencia de la identidad de unión baja a aproximadamente 10⁻⁸ relativo; no se relajó el criterio para aceptar el resultado anterior. La estimación global de error de propiedades devuelta por OpenCascade se conserva separadamente.

La prueba de sustitución en el módulo 0, misma posición del rotor ilustrativo A07, **falla para ambos**: D82 cruza la reserva de motor y un álabe superior; D102,5 también cruza la camisa y la reserva axial. Son intersecciones nominales comprobadas. Las reservas no representan motores/tubos finales, por lo que el resultado obliga a diseñar integración; no demuestra imposibilidad de la arquitectura. No se sustituye silenciosamente el rotor del A07.

Para conservar una ruta axial OD60 mm y 2 mm de separación nominal, un conducto nuevo de ID105/OD109 mm necesitaría semiseparación lateral de ejes de al menos 86,5 mm, frente a 76 mm actuales, si ambos cilindros se cruzan a la altura de la ruta. Esa condición geométrica necesaria no garantiza compatibilidad con la piel local, tapas, soportes o mecanismos.

## Masa, inercia y misión

Sensibilidad homogénea a 1600 kg/m³; **material, estructura y rpm no aprobados**. Propiedades de los STEP mediante integración adaptativa, registradas en `CAD/INERCIA_Y_GIRO_CONDICIONAL.json`:

| Propiedad por rotor | D82 | D102,5 |
|---|---:|---:|
| Masa nominal supuesta | 16,3 g | 31,9 g |
| Inercia axial | 3,64×10⁻⁶ kg·m² | 1,11×10⁻⁵ kg·m² |
| Velocidad de diseño calculada | 46.231 rpm | 29.588 rpm |
| Momento angular | 0,0176 N·m·s | 0,0344 N·m·s |
| Energía de giro | 42,7 J | 53,4 J |
| Momento giroscópico local a 5 rad/s perpendicular | 0,088 N·m | 0,172 N·m |

La fuerza centrífuga de raíz estimada por pala es unos 269 N en ambas geometrías semejantes bajo esos supuestos. No se calcula un margen de resistencia sin material/unión. La contrarrotación puede cancelar momentos angulares agregados iguales, pero no elimina cargas locales y pierde cancelación exacta con operación desigual. El tiempo de aceleración/frenado necesita par excedente, controlador y destino de energía; no se obtiene de la potencia estacionaria.

Se acopló masa geométrica G1, cuatro rotores y batería con restricción simultánea de energía y potencia: `m_pack=max(E/e_específica,P_pico/p_específica)`. Se conserva el presupuesto de geometría de 2,679 kg y reserva provisional de 0,75 kg, sin tubo axial opcional. Para el conducto mayor se añade solo un incremento cilíndrico supuesto de cuatro paredes H180/t2 mm a 1600 kg/m³; no incluye nuevo diseño de tapas/piel/soportes. Energía útil 150 Wh/kg y potencia específica 5 kW/kg son hipótesis de pack, no propiedades seleccionadas de una batería real.

| Escenario 5 kg | Masa aún disponible, D82 | Masa aún disponible, D102,5 |
|---|---:|---:|
| Estacionario 30 s | 0,912 kg | 0,816 kg |
| Estacionario 120 s | 0,846 kg | 0,764 kg |
| 120 s, incluidos 3 s laterales de 0,5 g | 0,804 kg | 0,730 kg |
| 120 s, incluidos 3 s ascendentes de 1 g | −0,158 kg | −0,040 kg |
| Estacionario 300 s | −0,144 kg | −0,028 kg |

Ese remanente debe cubrir todavía motores, ESC, actuadores, aviónica, instalación axial y todos los cambios pendientes. Los 3 s de maniobra son un escenario de análisis. Un saldo negativo rechaza esta combinación de hipótesis; uno positivo no prueba factibilidad. No se reduce el objetivo de agilidad a los casos que caben. El ahorro de potencia del rotor mayor no lo convierte automáticamente en una solución más ligera o ágil.

## Siguiente trabajo decisivo

Diseñar la posición y envolvente de motor/cubo/eje, separar los bancos de álabes de las piezas giratorias y comparar la ampliación de conducto con otras distribuciones de área. Mantener las variantes de masa como diseños propios. Contrastar el método de rotor con un experimento reproducible, resolver compresibilidad/cascada y producir un primer mapa instalado con reacción completa de paredes. Solo después podrá aceptarse una configuración de módulo y acoplarla al control 6DOF. No se ha cerrado G2 ni el plan completo.

## Archivos y reproducción

Desde la raíz: `.venv-cad/bin/python investigacion-aeronautica/ejecucion/G2/<script.py>`.

- `contrastar_apc.py`: contraste publicado sin ajuste.
- `test_bem_hover.py`: cinco verificaciones de ecuaciones/interpolación.
- `dimensionar_modulo.py`: diseños y operación anular; puede sobrescribir sus resultados adyacentes.
- `crear_rotor_candidato.py`, `comprobar_sustitucion_rotor.py`, `medir_inercia_rotor.py`: CAD, prueba de sustitución y propiedades.
- `acoplar_masa_mision.py`, `graficar_estudio.py`: presupuesto parcial y figura.
- `renderizar_rotores_blender.py`: ejecutar con Blender, no Python ordinario. `.blend` y PNG provienen de teselación del STEP; acabado cosmético y sin aprobación de fabricación.
