# Contraste independiente del modelo anular

3 de noviembre de 2026. Aporta evidencia a T10 del plan maestro. **Verifica ecuaciones en un caso público y contrasta un rotor aproximado con ensayos; no valida el módulo C02 instalado.**

## Comprobación numérica

Se implementó `../bem_anular.py`, con dos incógnitas por anillo: inducción axial y remolino. Emplea equilibrio de elemento de pala con cantidad de movimiento axial/angular y pérdidas de punta/raíz. A diferencia del C01 original, admite una velocidad axial de entrada positiva y geometría seccional arbitraria. No se afirma convergencia global, cobertura de vuelo invertido o identificación de la rama de molinete.

El [tutorial oficial CCBlade](https://flow.byu.edu/CCBlade.jl/stable/tutorial/) proporciona geometría y 17 ángulos interiores calculados a 5400 rpm y entrada 5 m/s. El método propio reproduce esos ángulos con diferencia máxima **5,12×10⁻¹⁰ grados**, frente al criterio previo de 0,002°. Se excluye el cero artificial del punto exacto de punta. No se ejecutó Julia: se compararon resultados publicados con nuestra resolución de dos incógnitas, usando los mismos datos de entrada.

Se comprobó además un punto de estacionario del C01 original, con sus 64 anillos, SD8020 y torsión fija. Las diferencias relativas son −2,29×10⁻¹⁰ en empuje y −1,17×10⁻¹⁰ en par. El código y los resultados históricos C01 no se modificaron. La identidad de energía se conserva en el nuevo cálculo; en el caso del tutorial su residuo absoluto máximo se sitúa en 1,71×10⁻¹³ W/m. Son comprobaciones matemáticas, no incertidumbre física.

Los archivos externos de código/datos y su licencia MIT se conservan con huellas en `PROCEDENCIA.json`; [CCBlade y sus publicaciones](https://github.com/byuflowlab/CCBlade.jl) identifican el método de referencia. El algoritmo propio no hereda por esta comparación las garantías globales del solucionador de referencia.

## Contraste experimental aproximado

Se utilizó la [cuerda/torsión UIUC](https://m-selig.ae.illinois.edu/props/volume-1/data/apce_10x5_geom.txt), radio 0,127 m, dos palas y radio de cubo supuesto 0,10R. Se integraron las cargas por trapecios, con carga cero en cubo/punta, como en el ejemplo público.

La polar NACA4412 del ejemplo es **computacional y corregida**, con Reynolds nominal informativo 50.000; se interpola en ángulo mediante Akima. Este archivo no incluye dependencia del Reynolds real de cada sección. Tampoco define el perfil exacto de una hélice comercial: [APC describe mezclas E63/perfil similar a Clark-Y](https://www.apcprop.com/technical-information/engineering/) en esa familia. No se convierte la afirmación simplificada del tutorial sobre NACA4412 en una identificación del espécimen experimental.

Comparación sin ajuste con los [16 ensayos estáticos UIUC de APC 10×5E](https://m-selig.ae.illinois.edu/props/volume-1/data/apce_10x5_static_pg0819.txt), entre 2508 y 6708 rpm:

| Magnitud | Ensayo | Modelo aproximado | Error absoluto relativo medio |
|---|---:|---:|---:|
| CT | 0,0914–0,0994 | 0,09670 | 2,12% |
| CP | 0,0366–0,0379 | 0,03364 | 9,30% |

La potencia se subestima en estos puntos. Los coeficientes del modelo permanecen constantes porque se usa una única polar sin dependencia de Re/Mach. El acuerdo en empuje no compensa esa carencia ni demuestra la fidelidad de la potencia. `COMPARACION_ESTATICA.csv` conserva todos los puntos, sin selección de los favorables; `CONTRASTE.json` conserva anillos y resultados.

Se verificó la normalización **CP=2πCQ** a partir de P=ΩQ y n=Ω/(2π). La fórmula en prosa del tutorial tiene el factor invertido; su código de comparación utiliza la multiplicación correcta. No se copió ese error a las conversiones.

## Alcance y trabajo pendiente

No se transfieren estos errores al SD8020, ocho palas, solidez elevada, Mach de punta del C01, conducto C02, reversibilidad o maniobras. Tampoco se ajusta un factor de corrección para hacer coincidir el consumo del proyecto. El archivo geométrico oficial APC 202602 volvió a devolver HTTP403; permanece sin recuperar la geometría tridimensional completa y su identidad con el espécimen histórico.

El siguiente contraste físico debe tener geometría/secciones, Reynolds/Mach y condiciones de instalación pertinentes. Siguen pendientes compresibilidad, cascada, interacción rotor–conducto–álabes, seis cargas, potencia y respuesta instalada. **T10/G2 y el objetivo global siguen abiertos.**

Reproducción desde la raíz: `.venv-cad/bin/python investigacion-aeronautica/ejecucion/G2/contrastar_bem_publico.py`. El script sobrescribe sus propios resultados de contraste, conservando los datos fuente. Se preservó un fallo inicial por retirada de `numpy.trapz`; se utiliza `numpy.trapezoid` en el entorno instalado.
