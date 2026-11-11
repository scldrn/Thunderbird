# Evaluación numérica de geometría y maniobra

## Plan vigente de ejecución

El [plan maestro](../../plan_maestro/PLAN-MAESTRO.md), consolidado el 2 de noviembre de 2026, organiza las decisiones actuales, hitos, requisitos, tareas y criterios de aceptación. Los apartados anteriores de investigación se conservan como historial; sus cifras y estados no sustituyen la configuración vigente ni acreditan prestaciones del A07.


Estado: investigación activa. Leer primero [INFORME-CONSOLIDADO-VIABILIDAD.md](INFORME-CONSOLIDADO-VIABILIDAD.md), actualizado el 30 de octubre de 2026. No se ha demostrado viabilidad integral ni óptimo global. Los apartados históricos siguientes describen el cálculo inicial, no todo el conjunto actual de herramientas.

## Requisitos conservados

Masa total 2–10 kg, 600–1000 km/h, vuelo estacionario y traslaciones bruscas omnidireccionales con orientación independiente. El usuario no fija duración: se buscará una frontera viable de prestaciones, no una misión arbitraria. Comparar geometrías y cuantificar mecanismos de dirección/repliegue.

## Reproducir

`python3 calcular.py`

Python 3.9 o posterior; sin dependencias externas. Resultados CSV y JSON en resultados/. Integración de Simpson con parametrización angular para evitar singularidades en las puntas. Comprobaciones ejecutadas contra volumen analítico, superficie de esfera, isotropía de inercia esférica y refinamiento de malla.

## Modelos y límites

- Geometría: esferoide y Sears–Haack CERRADOS, volúmenes 10/25/50 litros, esbeltez 2–12. No representa todavía toma/tobera ni volumen útil después de instalar conductos.
- Atmósfera: rho=1.225 kg/m³, T=288.15 K, mu=1.7894e-5 Pa s, g=9.80665 m/s².
- Fricción: correlación turbulenta logarítmica con corrección de Mach; aproximación de anteproyecto. No se calcula transición ni separación.
- FF_A=1+1.5/f^1.5+7/f³ y FF_B=1+60/f³+0.0025f: dos hipótesis de factor de forma para estudiar sensibilidad. No son verdad de túnel para cada perfil.
- Arrastre calculado SOLO viscoso del cuerpo de referencia alineado; no se declara arrastre de onda cero. Faltan ondas, base, entradas, salidas, superficies, huecos, apéndices y trimado.
- Inercias: envolvente homogénea y núcleo esférico. Ocho módulos representados como masas puntuales en dos estaciones x=±0.2L y cuatro azimuts. Se comparan radios recogido D/2 y desplegado 1.5D/2D/2.5D. No se propone su orientación de empuje ni se verifica controlabilidad.
- Masa total constante; fracción de módulos 10/20/30 %. Resto dividido por igual entre piel y núcleo: escenario explícito, NO presupuesto real de componentes. No incluye flexibilidad de articulaciones.
- Rotación: límite ideal reposo-a-reposo bajo par constante reversible. No incluye rampa de par, momentos aerodinámicos ni giroscópicos. La traslación y la rotación no son equivalentes.
- Respuesta: sistema ideal de primer orden, sin saturación ni zona muerta; no demuestra inversión real de rotor.
- Estacionario: potencia ideal de disco equivalente y multiplicadores HIPOTÉTICOS 1.5/2/3. La superficie efectiva no es automáticamente la suma de discos inclinados. Batería a 200 Wh/kg utilizables: hipótesis energética, sin validación de potencia de descarga.
- Fuerza isotrópica: requisito suficiente mg+ma para cualquier dirección; falta reservar autoridad de momentos y demostrar asignación de actuadores.

## Primeros resultados verificables

En el caso de 10 kg y 1000 km/h, el mínimo del barrido cambia de f≈6.1 (FF_A) a f≈8.7 (FF_B), para ambas familias. Son mínimos de los modelos, no evidencia de que esas formas sean óptimas. El arrastre viscoso correspondiente está alrededor de 120–130 N; no es una predicción de vehículo completo.

Ejemplo mecánico: 10 kg, 20 % de masa en módulos, radio desplegado 2D, par supuesto 10 Nm. Iy aumenta de 0.8163 a 1.0536 kg m²; giro ideal de 90° de 0.716 a 0.814 s. Ix aumenta de 0.0911 a 0.5657 kg m². El aumento del brazo de fuerza podría aumentar el par: todavía no se ha modelado ese beneficio. Comparar a par fijo NO determina si desplegar mejora o empeora la maniobrabilidad total.

La auditoría aritmética reproduce las ecuaciones del informe aportado; no valida su aplicabilidad física.

## Evidencia externa consultada

- Fricción/arrastre preliminar: https://ntrs.nasa.gov/api/citations/20040070782/downloads/20040070782.pdf
- Correlaciones de fricción y límites de factores de forma en góndolas: https://doi.org/10.1177/0954410020922928
- Geometría Sears–Haack: https://archive.aoe.vt.edu/mason/Mason_f/CAtxtAppA.pdf
- Potencia ideal de rotor: https://ntrs.nasa.gov/api/citations/20210021872/downloads/Acree%20TM-20210021872_FINAL.pdf
- Asignación y dinámica de actuadores omnidireccionales: https://brescianini.info/wp-content/uploads/publications/breMECH18.pdf
- Dinámica de rotores y maniobras: https://arxiv.org/html/2209.10024v2
- Paso variable: https://dspace.mit.edu/entities/publication/cbf41dbd-220c-4616-b300-c116ec7841be
- Motor de referencia, ficha fabricante: https://www.jetcat.de/en/productdetails/produkte/jetcat/produkte/professionell/p250%20pro%20s%20v2

## Auditoría de finalización: pendiente

1. Presupuesto integrado de masa, volumen, potencia y energía; escenarios de autonomía máxima.
2. Matriz real de fuerzas/momentos y región alcanzable simultánea, con gravedad, reserva y saturaciones.
3. Modelos temporales de paso variable/giro reversible/orientación, datos experimentales y comparación.
4. Simulación 6-DOF de maniobras incluyendo masa/inercia de mecanismos, límites y retardos.
5. Compatibilidad cinemática de repliegue y ausencia de interferencias geométricas.
6. Aerodinámica compresible con entradas y salida, fuerza normal y momentos, trimado y transición entre modos.
7. Cargas, modos estructurales, actuadores de repliegue y aeroelasticidad.
8. Alternativas anulares/sustentadoras/achatadas comparadas a igual volumen útil y misión.
9. Optimización con incertidumbre y objetivos múltiples; no confundir mínimo de un modelo con mejor geometría posible.
10. Informe final con conclusiones de viabilidad y límites de evidencia. CFD/túnel y datos de actuadores pueden ser imprescindibles para validar prestaciones.

## Actualización: segunda etapa ejecutada

Véase ETAPA-2-CONTROL.md. Se incorporan NumPy, SciPy y Matplotlib en `.venv-aero` de la raíz del proyecto. `control.py` calcula fuerzas y momentos simultáneos; `energia_control.py` realiza un cribado condicionado de masa y energía. El análisis detecta que un escenario de propulsión dual excede los 10 kg antes de añadir combustible. No constituye una conclusión universal ni un diseño cerrado.
