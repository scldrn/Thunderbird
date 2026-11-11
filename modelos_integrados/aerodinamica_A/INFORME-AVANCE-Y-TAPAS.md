# A: envolvente, avance rápido, tapas y conducto axial

**Estado: cribado computacional; no valida vuelo, velocidad máxima, arrastre total ni estructura fabricable.** Las masas 2/5/10 kg siguen siendo objetivos supuestos. Se conserva la arquitectura A elegida.

## Geometría medida en CAD

La envolvente cerrada de referencia mide 1.340 × 0.322 × 0.194 m, encierra 40.09 litros y tiene 0.8304 m² de superficie. Su sección máxima muestreada es 0.04977 m², equivalente a un círculo de diámetro 0.2517 m; L/D equivalente=5.323. Ese cociente no predice su Mach crítico.

Se reconstruyó el loft original anterior a los recortes, insertos, detalles y puerto posterior. Es una referencia aerodinámica cerrada: no representa puertas funcionales instaladas. El conjunto visual completo mide 1,345 m por sus piezas adicionales. No se trasladan aquí coeficientes de los husos circulares anteriores.

La metrología usa integración adaptativa OCCT. Se comprobó la extracción de secciones contra un elipsoide analítico y el volumen mediante integración independiente de 135 y 269 secciones. También se compararon tres triangulaciones con el área y volumen del CAD. Los residuos numéricos no son tolerancias de fabricación. Datos: `METROLOGIA.json` y `secciones_envolvente.csv`.

Si se asignan 5 kg a esta envolvente, su densidad media respecto al volumen bruto sería 124.7 kg/m³, distinta de los 200 kg/m³ supuestos en los primeros husos. No es densidad material ni prueba de que el volumen interior esté disponible después de instalar los componentes.

## Fricción de referencia

Se aplica Cf=0,455 / [(log10 Re)^2,58 (1+0,144 M²)^0,65] y D_f=q Cf S. La ecuación se revisó visualmente en la página 5 del informe oficial [DLR IB 124-2010/3](https://elib.dlr.de/65162/1/DLR_IB_124-2010-3_-_BLWF_Evaluation.pdf). Se usa solo la correlación de placa lisa turbulenta; no se ha ejecutado BLWF ni se importa el factor de forma de su avión.

**Son estimaciones condicionadas a esa correlación y al área cerrada.** No incluyen onda, separación, presión de base, sustentación/trimado, interferencias, tapas, tomas o empuje instalado. Tampoco son una cota inferior rigurosa: transición, presión local y geometría pueden cambiar la fricción. No se calcula una velocidad máxima con estas cifras.

| Masa supuesta | Velocidad | Mach | Re por longitud | Fricción de referencia | D_f/peso | Potencia D_f V |
|---:|---:|---:|---:|---:|---:|---:|
| 2 kg | 600 km/h | 0.490 | 1.13e+07 | 22.1 N | 1.13 | 3.7 kW |
| 2 kg | 1000 km/h | 0.816 | 1.88e+07 | 54.6 N | 2.78 | 15.2 kW |
| 5 kg | 600 km/h | 0.490 | 1.53e+07 | 38.8 N | 0.79 | 6.5 kW |
| 5 kg | 1000 km/h | 0.816 | 2.55e+07 | 96.0 N | 1.96 | 26.7 kW |
| 10 kg | 600 km/h | 0.490 | 1.93e+07 | 59.5 N | 0.61 | 9.9 kW |
| 10 kg | 1000 km/h | 0.816 | 3.21e+07 | 147.2 N | 1.50 | 40.9 kW |

El Mach crítico y el de divergencia de arrastre permanecen sin determinar para esta forma. Se tabula Cp sónico isentrópico como criterio para futuras presiones CFD; no se calcula un Mach crítico a partir de L/D. NASA ensayó cuerpos elípticos y su equivalente circular de igual distribución de áreas a Mach 0,6, 0,9, 1,2, 1,5 y 2,0, y encontró dependencia de la sección y el ángulo de alabeo. Esto impide tratar ambas secciones como aerodinámicamente idénticas. [NASA TM-X-3129](https://ntrs.nasa.gov/citations/19750008439).

El registro NASA se pudo verificar; la descarga local del PDF no transfirió datos y el lector web rechazó su tamaño. No se han extraído números de sus figuras ni se afirma una comparación cuantitativa de arrastre basada en ellas. El contraste anterior de Sears–Haack sigue siendo de otra geometría.

## Tapas y aberturas

Se midieron cuatro pasos verticales de radio 42 mm. Hay ocho extremos que cerrar si se sellan ambas caras en avance. Los pasos abiertos añaden paredes interiores; su área total no se usa como superficie exterior de la correlación anterior.

La carga de tapa depende de Δp=p_interior−p_exterior, no de q por identidad. Se exploran |ΔCp|=0,05 / 0,1 / 0,5 / 1 con |Δp|=q|ΔCp|. Para un disco plano de radio a, F=|Δp|πa²; el momento equivalente respecto a un eje tangente es F a. Un asiento y cierre perimetral pueden transmitir esa carga sin que el servo sostenga todo ese momento. No se ha diseñado ese camino de cargas.

El cribado estructural usa discos planos isotrópicos, E=70 GPa, ν=0,33 y densidad 2700 kg/m³ SUPUESTOS. No se selecciona un metal o laminado. Se comparan bordes empotrados y simplemente apoyados. La solución de placa empotrada w0=p a⁴/(64D), D=Et³/[12(1−ν²)], se contrasta con el caso analítico de [NASA/AIAA 2014](https://ntrs.nasa.gov/api/citations/20140004248/downloads/20140004248.pdf). El cálculo reproduce el benchmark externo [Ansys STRUCT-004](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/Ansys_3D_VM/Discovery/VM_3D_Design/disco_vm/topics/r_VM_3D_disco_004.html): 0,0553 pulgadas de flecha redondeada y 5265 psi de tensión central con sus propios datos.

Se marca fuera del cribado lineal cualquier caso con w0/t>0,2, umbral conservador elegido para este estudio. Los valores lineales en esos casos se conservan como diagnósticos, no como tensiones reales ni fallo estructural demostrado. El espesor de cribado exige además tensión de flexión ≤100 MPa, límite hipotético, sin certificación de material.

| 5 kg, 1000 km/h: ΔCp supuesto | Fuerza por disco | Momento tangente equivalente | Espesor de cribado empotrado / apoyado | Masa de ocho discos, empotrado / apoyado |
|---:|---:|---:|---:|---:|
| 0.1 | 26.2 N | 1.10 N·m | 0.65 / 0.92 mm | 0.077 / 0.110 kg |
| 0.5 | 131.0 N | 5.50 N·m | 0.97 / 1.37 mm | 0.116 / 0.164 kg |
| 1.0 | 261.9 N | 11.00 N·m | 1.15 / 1.63 mm | 0.138 / 0.195 kg |

Estas masas excluyen bisagras, cierres, asientos, actuadores, sellos y refuerzos. Los discos planos no reproducen las tapas curvas del loft. Se requieren un modelo de pared/material, apoyos reales, presiones, fatiga y aeroelasticidad; una comprobación estática no acredita ausencia de flutter.

## Conflicto de espacio del conducto axial

En las estaciones de ventiladores, sus ejes verticales están en y=±65 mm, con radio interior 42 mm y exterior de camisa 44 mm. Un conducto recto coaxial con x solo deja diámetro exterior máximo 42 mm antes de intersectar esas camisas. Con pared axial SUPUESTA de 2 mm, el diámetro de aire baja a 38 mm. No se ha añadido margen de montaje.

Se contrastó la cota con intersecciones sobre las cuatro camisas del STEP integrado: los cilindros axiales exteriores de 40 y 42 mm no intersectan sus sólidos; 46, 50, 60, 80 y 100 mm sí los intersectan. El contacto límite no es holgura de montaje. Los volúmenes y la huella del STEP están en `VERIFICACION_RUTA_AXIAL.json`. Es una condición geométrica necesaria para esa ruta concreta. No demuestra una toma–motor–tobera continua, caudal suficiente o rendimiento de toma. Un motor instalado solo por detrás de los ventiladores, tomas laterales o una redistribución de estaciones pueden cambiar la restricción y deben compararse con geometría y flujo propios. El puerto posterior del diseño es representativo, no una tobera dimensionada.

## Consecuencia para continuar el objetivo completo

Hay que cerrar conjuntamente área de rotor, masa, energía y control de estacionario con la ruta de propulsión rápida y sus tapas. El próximo modelo aerodinámico debe representar una instalación única, no sumar coeficientes de cuerpos y mecanismos incompatibles. Siguen pendientes presiones y arrastre compresible verificados, rotor instalado, tomas/toberas, cierre de masa e inercias y validación estructural/dinámica. No se declara óptimo global ni imposibilidad física del concepto.

Código: `medir_aerodinamica_A.py` y `evaluar_avance_y_tapas_A.py`. Resultados: JSON y CSV de esta carpeta; los STEP son referencias de envolvente y pasos, no planos de puertas.
