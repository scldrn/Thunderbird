# Redistribución de palas y cargas durante el giro

Se continúa desde el candidato de ejes revisados. Los resultados son cálculos de sensibilidad con masas y condiciones supuestas; ninguna medición física nueva.

## Corrección del modelo de masa

El CAD asignaba 198 g por módulo en la variante objetivo de 5 kg a una envolvente cilíndrica. Se conservan los 198 g, pero se separan: motor cilíndrico uniforme de 128 g, servo y ESC como masas puntuales de 20 g cada una en el centro del motor, y dos palas de 15 g cada una situadas en el disco. Palas rectangulares uniformes, raíz a 40 mm del eje, radio exterior 228,6 mm y cuerda 30 mm. Su tensor se promedia durante una revolución. En 10 kg todas las longitudes se escalan por la raíz cúbica de dos y las masas por dos: es una extrapolación, no selección de piezas.

El procedimiento resta del tensor global la contribución original de cada módulo, incorpora las contribuciones separadas mediante ejes paralelos y recalcula CG e inercia. Conserva la masa total; el CG permanece prácticamente igual por la simetría de la redistribución. La inercia de alabeo aumenta aproximadamente 5,4 %; las otras inercias principales cambian menos de 1 %. Archivos de cálculo: `masas_rotores_distribuidas.py`, `masas_distribuidas/RESUMEN.json`.

| Variante | Inercia axial anterior kg·m² | Inercia axial corregida kg·m² | Mayor inercia principal corregida kg·m² |
|---|---:|---:|---:|
| 5 kg | 0,23010 | 0,24263 | 0,49961 |
| 10 kg | 0,73725 | 0,77705 | 1,53719 |

Estas inercias no incluyen el buje pendiente ni dimensiones reales de servo/ESC; no son una reconstrucción física definitiva. Las partidas sin ubicación se mantienen concentradas en CG para la tabla siguiente.

## Giroscopía y velocidad angular del cuerpo

Se suponen 6000 rpm en 5 kg y 4762 rpm en 10 kg, preservando la velocidad de punta bajo el escalado geométrico. No son puntos de operación seleccionados de un motor. Las palas aportan, por rotor, un momento angular de 0,3973 y 1,0010 N·m·s respectivamente. Un patrón de cuatro sentidos positivos y cuatro negativos cancela la suma ideal si los módulos son idénticos y mantienen exactamente las RPM asignadas. Esto NO cancela las cargas locales en cada soporte.

Se incluyen en la ecuación de momento el término de Euler del cuerpo y el par giroscópico de un desajuste independiente constante de RPM de hasta ±5 %. Para cubrir cualquier dirección de velocidad angular se utilizan cotas conservadoras: bola de par de Euler con radio igual a la mitad del rango de inercias principales multiplicado por la velocidad angular al cuadrado, y suma de cotas de soporte para la incertidumbre de momento angular. Las direcciones que maximizan distintos términos no tienen por qué coincidir: por ello las cifras siguientes son capacidades SUFICIENTES dentro del modelo y no mínimos necesarios exactos.

Demanda simultánea: cualquier orientación de gravedad, aceleración de traslación adicional de 1 g en cualquier dirección y aceleración angular de 2 rad/s² en cualquier dirección.

| Velocidad angular del cuerpo | Capacidad simétrica suficiente por rotor, 5 kg | Capacidad simétrica suficiente por rotor, 10 kg |
|---|---:|---:|
| 0 rad/s | ±37,85 N | ±73,71 N |
| 2 rad/s | ±39,77 N | ±79,19 N |
| 5 rad/s | ±51,12 N | ±105,34 N |
| 10 rad/s | ±88,98 N | ±193,40 N |

A 5 rad/s, el par giroscópico máximo local de un rotor, con el 5 % de desajuste y sin contar buje ni rotor del motor, es de 2,09 N·m en 5 kg y 5,26 N·m en 10 kg. Son cargas que deben transmitir los soportes cuando el giro del cuerpo es perpendicular al eje del rotor; no son pares de actuación de paso de pala.

## Verificación y límites

Se ejecutaron 72 escenarios de velocidad angular, desajuste de RPM y demanda de traslación. `verificar_cargas_giro.py` probó 864 combinaciones aleatorias de dirección de giro, aceleración angular, fuerza y desajustes, comprobando equilibrio mediante programación lineal. Residuo máximo normalizado 1,78e-13. Además se repitió el análisis estático de 108 escenarios y 1080 comprobaciones con el tensor corregido.

No se incluye variación temporal de RPM (derivada del momento angular), par aerodinámico de reacción de los rotores, perfil real de palas, buje, inercia giratoria del motor, flexión, interacción de estelas, incidencia oblicua ni dinámica de actuadores. La aproximación de tensor promediado exige que la rotación de palas sea rápida respecto al movimiento del cuerpo; no cubre vibraciones periódicas. Ninguna cota convierte al candidato en un vehículo validado ni demuestra autonomía, velocidad máxima o tiempo de reorientación.

## Implicación

Una evaluación estática desde reposo no basta para justificar movimientos bruscos. La nueva disposición mantiene su mejora estática, pero la velocidad angular del cuerpo y las diferencias entre rotores consumen autoridad de momento. Deben medirse o modelarse con fidelidad las masas giratorias y la dinámica de paso antes de fijar una envolvente de maniobra. La siguiente comparación con el mapa de rotor existente deberá respetar su dominio experimental y no extrapolarlo automáticamente a 10 kg.
