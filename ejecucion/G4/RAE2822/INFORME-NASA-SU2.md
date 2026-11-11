# RAE2822: comparación nativa con la malla de NASA

3 de noviembre de 2026. Se dispone de una solución de referencia con cargas y campos casi estacionarios, sobre una conversión directa de la malla publicada por NASA. La extracción de fuerzas se comprobó independientemente. El contraste experimental sigue siendo provisional: faltan sensibilidad de malla/modelo, tratamiento de transición y cierre completo del presupuesto numérico de momento. No valida el vehículo ni su velocidad.

## Entradas y diferencias que permanecen

La [fuente NASA, estudio 4](https://www.grc.nasa.gov/www/wind/valid/raetaf/raetaf04/raetaf04.html) proporciona la malla C de 369 × 65, M=0,729, α=2,31°, Re=6,5 millones, temperatura de 460 R y cuerda de un pie. Su pared termina en un borde de salida afilado; la estela inferior/superior se acopla. Estas entradas no son las condiciones nominales distintas que aparecen en otros resúmenes del perfil.

`preparar_su2_nasa.py` conserva las coordenadas y los cuadriláteros, une 33 nodos coincidentes de la estela y verifica convexidad, área positiva, aristas de frontera y relectura del formato SU2. La malla original convertida tiene 23.952 nodos, 23.552 cuadriláteros, 304 aristas de pared, 368 exteriores y 128 de salida. No se importa la aprobación geométrica de OpenFOAM: SU2 usa volúmenes duales y reporta una relación máxima de áreas de cara de 561.541. La orientación nativa es correcta; esa comprobación no acredita independencia de malla.

Se emplea gas ideal con γ=1,4 y R=287,05287 J/(kg K), T∞=255,55556 K y cuerda de 0,3048 m. La constante de viscosidad de Sutherland se establece para reproducir simultáneamente Re y p∞=108.987,77 Pa; es una elección de transporte declarada, no una medición. Resultan ρ∞=1,48570 kg/m³ y U∞=233,62276 m/s.

El modelo sigue siendo SST-2003m de SU2, completamente turbulento, con I=0,1% y νt/ν=1 supuestos. No es idéntico al SST histórico de WIND ni al experimento con transición. Se conservan JST, Euler implícito, mínimos cuadrados ponderados y multigrid; el programa reduce automáticamente a dos niveles gruesos utilizables. El CFL adaptativo va de 1 a 50, empezando en 5. Las fronteras características y de presión de SU2 difieren en implementación de las de WIND.

## Convergencia observada, sin sustituirla por el mensaje de parada

Se fuerzan las iteraciones para evitar una terminación basada exclusivamente en densidad. Cada rama conserva campos, configuración, registro, identificador del binario y hashes.

| Rama y trabajo acumulado | CL calculado | CD calculado | RMS de Cp, 103 puntos |
|---|---:|---:|---:|
| NASA r1, 1.200 pasos | 0,6924411 | 0,01136997 | 0,117546 |
| NASA r2, otros 4.000 | 0,6787502 | 0,01303965 | 0,122101 |
| NASA r3, otros 1.000 | 0,6787504 | 0,01303966 | 0,122101 |

El error experimental no se utiliza para decidir cuándo detener o ajustar el solver. El primer arranque parecía concordar algo mejor, pero sus cargas aún cambiaban. Se conserva el resultado más desarrollado aunque su RMS sea mayor.

Entre r2/r3, ΔCL=2,53×10⁻⁷ y ΔCD=6,08×10⁻⁹. Las diferencias relativas L2 de todos los campos conservados son inferiores a 4,57×10⁻⁵; la mayor corresponde a k. Para k, la máxima diferencia normalizada por el máximo del campo de referencia es 1,99×10⁻⁴. Estas normas son aritméticas por nodo, no errores físicos ni normas de volumen. La mayor variación local de k se encuentra en la estela.

Los máximos log10 de residuos reportados en las últimas 20 iteraciones de r3 son −10,91/−7,85/−8,53/−5,45/−4,73/−2,50 para ρ, momento X/Y, energía, k y ω. Sus escalas dimensionales son distintas: no se exige arbitrariamente el mismo valor absoluto para todas. Se informan también los cambios reales de estado y cargas. La presión permanece entre 63,29 y 155,01 kPa; T entre 218,38 y 282,66 K; y+ de pared entre 0,750 y 3,308. La resolución de pared no está aceptada todavía.

## Fuerzas de superficie y balance exterior

`reconstruir_traccion_su2.py` reconstruye ∇U por mínimos cuadrados con pesos 1/r² y vecindad de aristas. Calcula τ=μ[∇U+∇Uᵀ−(2/3)(∇·U)I] y usa las normales duales de cada nodo. Incluye esfuerzo normal viscoso, que no contiene el coeficiente de fricción tangencial exportado.

La [implementación de fuerzas](https://github.com/su2code/SU2/blob/v8.6.0/SU2_CFD/include/solvers/CFVMFlowSolverBase.inl) utiliza precisamente la tracción completa. Una velocidad afín de referencia y una presión lineal con integral analítica verifican gradiente, orientación y pesos. En ambas mallas nativas ensayadas, la reconstrucción de las fuerzas del solver pasa el umbral de consistencia de coeficiente absoluto 10⁻⁸; en NASA r3 la mayor diferencia es 7,5×10⁻¹². El esfuerzo tangencial reconstruido también coincide con el exportado. Esta es una verificación del cálculo de cargas de superficie, no validación física.

El flujo exterior evaluado directamente con estados nodales deja un defecto de momento de norma 0,00855 en coeficientes. No corresponde al flujo numérico que realmente usa el solver. `flujo_frontera_su2.py` reconstruye por separado los estados característicos de cada marcador, conservando las normales de las esquinas, y el flujo Roe con los valores predeterminados kappa=0,5 y corrección entrópica 0,001. El [código de frontera](https://github.com/su2code/SU2/blob/v8.6.0/SU2_CFD/src/solvers/CEulerSolver.cpp) y el [flujo Roe](https://github.com/su2code/SU2/blob/v8.6.0/SU2_CFD/src/numerics/flow/convection/roe.cpp) identifican estas operaciones. Se comprueban flujo de estados iguales, antisimetría al invertir normales, contacto supersónico y estados característicos uniformes.

En r3, el flujo de masa neto reconstruido es 2,59×10⁻⁹ kg/(m s), equivalente a 2,45×10⁻¹¹ de ρ∞U∞c. El defecto de momento es (1,6625×10⁻⁴;−8,4669×10⁻⁵), norma 1,8657×10⁻⁴, normalizado por q∞c. Su componente en la dirección del arrastre es del orden de 1,25% de CD: no debe esconderse usando únicamente la escala de sustentación. Se incluyen esfuerzos viscosos en la frontera lejana; el código nativo omite el término viscoso de salida.

Los flujos Roe se reconstruyen; no se exportaron directamente del ensamblaje nativo. Persisten diferencias posibles por etapas segregadas y por la imposición fuerte de la condición de pared. No se acredita una identidad completa del residuo discreto, momento angular o energía. El siguiente contraste de malla debe comprobar también este defecto.

## Comparación completa de presiones

Se conservan los 103 puntos. El signo −Cp del archivo de NASA y el orden de extradós/intradós se verificaron con sus comandos y su curva publicada, independientemente de nuestra solución. El mayor error de r3 está en el extradós, x/c=0,0002: Cp experimental=−0,4219, SU2=+0,56997 y WIND publicado=+0,53392. No se elimina ese punto ni se atribuye su causa sin evidencia adicional.

| Región fija | Puntos | RMS SU2 r3 | RMS WIND publicado |
|---|---:|---:|---:|
| Todos | 103 | 0,12210 | 0,10683 |
| x/c<0,02 | 27 | 0,19654 | 0,18988 |
| 0,4≤x/c≤0,65 | 22 | 0,14167 | 0,08781 |
| Restantes | 54 | 0,03075 | 0,02447 |

La curva WIND publicada corresponde a Spalart–Allmaras, no a SST. Su parecido no es una tolerancia de aprobación del experimento. La incertidumbre de Cp de aproximadamente 0,0026 citada por NASA tampoco equivale al error permitido para un modelo completo. Faltan transición, resolución y sensibilidad de transporte/modelo.

## Refinamiento y reproducción

`su2_nasa_fina_r1` subdivide los intervalos tangenciales por dos, los primeros dos intervalos radiales por cuatro y los restantes por dos. Mantiene el mismo polígono del cuerpo y dominio, conservando los vértices originales. Tiene 97.956 nodos y 97.152 cuadriláteros. La semilla interpola ρ, momento, ρE, ρk y ω desde r3; comprueba positividad y divide ρk entre ρ. SST debe recalcular ω de pared para la distancia menor. Consultar el proceso real antes de cualquier continuación: una semilla interpolada no es una solución.

La corrida fina r1 terminó 1.200 pasos con salida 0 en 395,07 s. Su y+ reportado queda entre 0,117 y 0,976. La reconstrucción de fuerza completa sigue concordando con el solver, con diferencia máxima de coeficiente 3,2×10⁻¹¹. CL=0,6787052 y CD=0,01259130; el RMS de Cp de los 103 puntos es 0,123190.

`COMPARACION_MALLAS_SU2_r1_config_verificada.json` comprueba el mismo binario y opciones explícitas físicas/numéricas, admitiendo únicamente diferencias de reinicio, límite de iteraciones y salida. Cada vértice de pared fino se encuentra en el polígono grueso dentro de 1,01×10⁻¹⁷ m, y las áreas del dominio coinciden. La diferencia provisional de CD es −3,438%; ΔCL relativo=−0,00665%. El RMS de diferencia de Cp entre mallas en los 103 puntos comunes es 0,01093. Estos cambios todavía incluyen la evolución iterativa residual de la rama fina: no son una incertidumbre de discretización cerrada ni un GCI con dos mallas y refinamiento anisótropo.

En el campo fino r1, el defecto de momento con fronteras Roe es (−2,861×10⁻⁵;−3,235×10⁻⁵) en coeficientes, menor que el grueso; masa relativa=8,97×10⁻⁸. La deriva entre medias de 20 es 2,81×10⁻⁶ en CL y 6,13×10⁻⁸ en CD. Los residuos y los campos turbulentos requieren otra comprobación. `su2_nasa_fina_r2` añade 1.800 iteraciones forzadas desde ese resultado, conservando malla, modelos y opciones físicas. El multigrid efectivo difiere entre las mallas por la selección automática de niveles: deben compararse campos estabilizados, no costes por iteración como si fueran idénticos.

La primera preparación se rechazó por exigir igualdad binaria a las coordenadas del reinicio ASCII; la diferencia máxima era 8,9×10⁻¹⁶ m. Se preservó la carpeta y se aplica la tolerancia de lectura de 10⁻¹² m que ya usa la auditoría. No se arrancó ningún solver con esa preparación fallida.

Comandos desde la raíz del repositorio:

```sh
.venv-cad/bin/python investigacion-aeronautica/ejecucion/G4/RAE2822/auditar_su2.py --case investigacion-aeronautica/ejecucion/G4/RAE2822/su2_nasa_r3_sonda --reference-case investigacion-aeronautica/ejecucion/G4/RAE2822/su2_nasa_r2
.venv-cad/bin/python investigacion-aeronautica/ejecucion/G4/RAE2822/reconstruir_traccion_su2.py --case investigacion-aeronautica/ejecucion/G4/RAE2822/su2_nasa_r3_sonda
```

T21 y G4 permanecen abiertos. A07 continúa como referencia; no se modificó C02 ni se reanudaron los dos solvers históricos pausados. Esta evidencia mejora la base para calcular el vehículo; no demuestra su empuje, maniobrabilidad, autonomía, arrastre o velocidad.
