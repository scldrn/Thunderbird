# Familia escalable: evaluación independiente de 2, 5 y 10 kg

**Revisión posterior:** los candidatos de este barrido optimista no son configuraciones integradas cerradas. La auditoría posterior de 5 kg y las limitaciones del conjunto están en `INFORME-CONSOLIDADO-VIABILIDAD.md`.

Se calcularon 324 escenarios: tres límites de masa, tres reactores de referencia, dos hipótesis eléctricas, tres alargamientos (4,6,8), tres diámetros de rotor (20,30,40 cm) y dos aceleraciones garantizadas estáticas (0,5 y 1 g). Ocho rotores reversibles; asignador lineal y orientación de ejes heredados del estudio previo. No se optimizaron número de rotores ni nuevas arquitecturas: no es un óptimo global.

## Datos de motores

| Referencia | Masa publicada | Empuje máximo publicado | Consumo máximo |
|---|---:|---:|---:|
| P20-SX, descatalogado | 0,350 kg | 24 N | 90 ml/min |
| P100-RX-BL | 1,080 kg | 100 N | 390 ml/min |
| P250 de la etapa anterior | 2,155 kg | 250 N | 820 ml/min |

La masa del motor no equivale a instalación completa. Los empujes publicados no son curvas instaladas a Mach 0,49–0,82. Densidad de combustible supuesta: 0,8 kg/l.

Fuentes primarias:
- https://www.jetcat.de/en/productdetails/produkte/jetcat/produkte/Eingestellte%20Produkte%20Zubehoer/p20_sx
- https://www.jetcat.de/de/productdetails/produkte/jetcat/produkte/RC%20ENGINES/Engines/p100_rx-bl
- https://www.jetcat.de/en/productdetails/produkte/jetcat/produkte/Professionell/p250%20pro%20s%20v2

## Hipótesis comunes

Volumen exterior de referencia = límite de masa / 200 kg/m³. La masa calculada puede quedar por debajo del límite: no se añade carga útil para rellenar el presupuesto (excepto mínimo de 2 kg heredado). Cuerpo esferoidal cerrado usado como referencia; requiere rediseño al introducir toma y escape.

30 s de uso eléctrico (90% estacionario, 10% maniobra) y combustible para 30 s al consumo máximo. No es duración demostrada de misión: faltan arranque, transición y reserva operacional.

Se añadió una asignación de masa del 10% del límite para integración, además de brazos, piel y aviónica del modelo. Esta asignación se coloca al centro para calcular inercia; no demuestra que mecanismos reales cumplan su peso o distribución. Reserva angular: 2 rad/s². Se verifican envolventes de discos desplegados y un cilindro motor en el fuselaje con 10 mm radiales de espacio supuesto; no se valida refrigeración, conductos, depósito, batería ni retracción.

Hipótesis optimista: módulos 200 N/kg, eficiencia efectiva de disco 0,8, batería 8 kW/kg y 220 Wh/kg utilizables, piel 1 kg/m². Ningún conjunto de componentes ha sido verificado con esas prestaciones simultáneas. La hipótesis de referencia extrapolada no pasó los filtros para híbridos en esta malla: no implica imposibilidad física.

## Candidatos para continuar, no diseños aprobados

Todos los siguientes usan la hipótesis optimista y el requisito estático de 1 g adicional en cualquier dirección, considerando gravedad.

| Límite | Motor | Masa calculada | Cuerpo largo × diámetro | Rotores | Cota de potencia pico eléctrica |
|---|---|---:|---|---|---:|
| 2 kg | P20-SX de referencia | 2,00 kg | 0,883 × 0,147 m | 8 × 30 cm | 1,62 kW |
| 5 kg | P100-RX-BL | 4,67 kg | 0,914 × 0,229 m | 8 × 30 cm | 5,25 kW |
| 10 kg | P100-RX-BL | 7,34 kg | 1,509 × 0,252 m | 8 × 40 cm | 8,76 kW |
| 10 kg, mayor empuje axial | P250 | 9,15 kg | 1,152 × 0,288 m | 8 × 40 cm | 10,93 kW |

Estas potencias son cotas del asignador con discos aislados; no cotas físicas certificadas. Las dimensiones describen solo el cuerpo. La extensión radial conservadora desplegada es 4D + diámetro del rotor: aproximadamente 0,89; 1,21; 1,41 y 1,55 m respectivamente. La geometría compacta de las opciones L/D4 favorece este presupuesto de masa, pero NO queda validada para transónico.

## Velocidad: filtro separado

| Candidato anterior | Arrastre viscoso modelo a 600 km/h | A 1000 km/h | Empuje estático publicado |
|---|---:|---:|---:|
| 2 kg | 20,9 N | 51,7 N | 24 N |
| 5 kg | 51,1 N | 126,3 N | 100 N |
| 10 kg / P100 | 56,2 N | 139,2 N | 100 N |
| 10 kg / P250 | 78,3 N | 193,4 N | 250 N |

Cálculo de fricción turbulenta y máximo de dos factores de forma hipotéticos usados en etapas anteriores. Excluye arrastre de onda, sustentación, compensación, toma, base e interferencia. Estos números NO predicen velocidad máxima. La comparación con empuje estático es solo un indicador de margen, no equilibrio de vuelo. En particular, no se puede afirmar que el P250 alcance 1000 km/h porque 250 sea mayor que 193.

La selección automática en el JSON usa como filtro exploratorio empuje estático >=1,5 veces arrastre viscoso a600, y minimiza masa entre los casos que pasan. El factor1,5 es arbitrario y no sustituye pérdidas instaladas. La tabla humana también incluye 2kg y P250 para mostrar los compromisos que ese filtro omite.

## Conclusión y siguiente decisión

No se necesita fijar toda la familia en 10 kg. La versión de 5 kg merece continuar con un reactor menor y una geometría propia. La de 2 kg requiere especial atención al empuje de vuelo rápido; la de 10 kg permite comparar masa menor frente a reactor mayor. Ninguna está validada para la misión completa. Faltan motores intermedios, hardware eléctrico real, optimización de distribución y topología, reserva estructural y térmica, y mapa de empuje instalado antes de seleccionar una arquitectura ganadora.

## Reproducción

Ejecutar `familia.py` desde el entorno `.venv-aero`. Resultados completos en `resultados/familia_ESCENARIOS.csv`; selección exploratoria en `resultados/familia_SELECCION_CONDICIONAL.json`. `cierre_masa.py` admite ahora especificaciones de motor, alargamiento y masa adicional, manteniendo los valores anteriores por defecto.
