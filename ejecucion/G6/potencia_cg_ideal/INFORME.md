# Centro de masa y potencia: referencia ideal de cuatro discos

## Resultado y alcance

Este cribado enlaza el reparto de fuerzas con una comparación de potencia inducida ideal para 2, 5 y 10 kg. **No es un mapa de los ventiladores internos C02 ni demuestra vuelo.** Los cuatro discos se tratan como rotores libres, independientes e idénticos, con sus empujes paralelos; la potencia calculada no es potencia eléctrica ni una cota inferior universal de ventiladores con conducto. El modelo no incluye interacción, pérdidas, giros de rotor, reacciones de álabes, aerodinámica exterior ni dinámica de actuadores.

Datos supuestos: densidad 1,225 kg/m³, g = 9,80665 m/s² y diámetro de disco de 82 mm para 5 kg. Para 2 y 10 kg se escala el diámetro por la raíz cúbica de la masa; esto no determina la masa real de sus componentes. La referencia previa usa 82,024 mm, de ahí diferencias pequeñas por redondeo. El centro de masa y los puntos de aplicación de fuerza se sitúan en el mismo plano horizontal. Las fracciones de CG se expresan respecto a los semibrazos del rectángulo, no como fracción del largo total del vehículo.

Con aceleración nula y CG centrado, el cálculo da aproximadamente 518, 1.509 y 3.388 W para 2, 5 y 10 kg. Si el CG se desplaza al 60 % de un semibrazo, sin desplazamiento en el otro eje, la distribución óptima bajo las hipótesis del modelo es 40/40/10/10 % y las cifras pasan a 590, 1.718 y 3.857 W: **+13,84 %** respecto al reparto uniforme para el mismo empuje total. Son comparaciones ideales, no consumos previstos.

En un caso adicional de 5 kg, CG al 60 % del semibrazo longitudinal y aceleración horizontal instantánea de 0,5 g, el empuje total exigido es 54,82 N y los dos módulos más cargados requieren 21,93 N cada uno. Si se impone el límite hipotético de 20,58 N por módulo usado en el estudio G6 previo, **no existe reparto factible con todas las fuerzas paralelas**. Esto no descarta repartos con direcciones distintas ni demuestra el límite real del vehículo. La cifra sin límite es 2.031 W de referencia ideal: no debe interpretarse como potencia realizable bajo ese límite.

## Modelo y reproducibilidad

Se exige equilibrio de momentos sin aceleración angular para un empuje neto inclinado que compense el peso y produzca las aceleraciones especificadas. Para el orden de esquinas ++, +−, −+, −−, con fracciones normalizadas ξ, η y a=(1+ξ)/2, b=(1+η)/2, los pesos son (t, a−t, b−t, 1−a−b+t). Se minimiza la suma de wᵢ^(3/2) por bisección de su derivada sobre el intervalo factible; un límite por ventilador reduce ese intervalo. La comparación usa Pᵢ = Tᵢ^(3/2)/√(2ρAᵢ), fórmula de cantidad de movimiento en estacionario de discos libres ideales; véase la [teoría NDARC de NASA](https://ntrs.nasa.gov/citations/20170011656). Los factores de cono son hipótesis sobre fuerza resultante, no ángulos demostrados de álabes.

`RESULTADOS.json` contiene 800 combinaciones de masas, CG, aceleraciones y conos, junto con huellas SHA-256 del código. El límite de 20,58 N se aplica solo a los casos hipotéticos de 5 kg. Para reproducir:

```sh
python3 investigacion-aeronautica/ejecucion/G6/potencia_cg_ideal/verificar.py
python3 investigacion-aeronautica/ejecucion/G6/potencia_cg_ideal/generar.py
```

Siete pruebas pasan, incluidas una solución analítica, comparación con malla unidimensional y una prueba en la que el límite sí modifica el óptimo. Una aceleración instantánea desde el estacionario no describe una trayectoria ni una condición de vuelo rápido; los valores numéricos fuera del cono describen un contrafactual y se marcan inviables en ese modelo.

## Revisión independiente y trabajo pendiente

La sesión Antigravity `bbceeece` reprodujo correctamente el caso de desplazamiento en un solo eje y el factor 1,1384. Se rechazaron sus afirmaciones de que la región de CG factible es un rombo y de que el óptimo siempre factoriza: la envolvente de cuatro esquinas es rectangular, y para ξ=0,6 y η=0,4 la asignación factorizada no satisface la condición de optimalidad. Se rechazaron también sus umbrales aerodinámicos sin evidencia. La revisión se contrastó con el modelo y las pruebas locales.

Próximo paso: usar masas, centros de gravedad y momentos reales derivados de una configuración integrada, y sustituir estos discos libres por mapas instalados de fuerza, momento, potencia y respuesta; verificar cada modo de apertura, las interacciones y el equilibrio en transición y avance. El cono, los límites de empuje, la capacidad de aceleración y la autonomía no están demostrados.
