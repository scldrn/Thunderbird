# Candidato geométrico frente al dominio del mapa de rotor

Esta etapa utiliza el candidato de ejes revisados y su tensor corregido por distribución de palas. La masa de cálculo es 5,498 kg, no el objetivo de 5 kg. No se extrapola el mapa de 5 kg a la variante de 10 kg.

## Procedencia y naturaleza de los datos

Archivo de entrada: `../resultados/mapa_rotor_bidireccional_CONDICIONAL.csv`, generado previamente por `evaluacion_rotor_completo.py`. Rotor de dos palas, diámetro 457,2 mm, cuerda 30 mm, perfil SD8020 y 6000 rpm. Este mapa procede del modelo de elemento de pala con datos de polar limitados; NO es un ensayo del rotor ni del motor instalado. Véanse `../EVALUACION-INTEGRADA-ROTOR.md` y `../REVISION-CON-POLARES-EXPERIMENTALES.md` para hipótesis y datos originales de UIUC.

Se comparan dos intervalos continuos que contienen empuje cero:

- Mapa numéricamente resuelto: −37 a +40 N por rotor.
- Filtro de contribución de par fuera de polar no superior al 5 %: −28 a +38 N.

El umbral del 5 % es un criterio de selección arbitrario del estudio, no un error máximo, nivel de confianza o certificación. La continuidad entre puntos de 1 N se supone mediante interpolación; tampoco se ha verificado experimentalmente.

## Método

`limites_con_mapa_rotor.py` calcula la inclusión de una esfera de fuerzas y un conjunto de momentos en el conjunto convexo de fuerzas y momentos alcanzable por ocho actuadores con límites distintos de empuje positivo y negativo. Se conserva el desplazamiento del centro de ese conjunto debido a la asimetría: no se sustituye por un límite ±37 N o ±28 N.

Para velocidad angular nula se emplea la exigencia estática exacta del modelo lineal de asignación. Para velocidades no nulas se añaden las cotas conservadoras de Euler y giroscopía del informe anterior, con desajustes independientes constantes de RPM de hasta ±5 %. Se reserva simultáneamente aceleración angular de 2 rad/s² en cualquier dirección. El radio de la esfera de fuerza se expresa como aceleración adicional después de cubrir gravedad en cualquier orientación.

## Resultados condicionados

| Velocidad angular corporal | Aceleración adicional cubierta, mapa completo | Aceleración adicional cubierta, filtro 5 % |
|---|---:|---:|
| 0 rad/s | 1,035 g | 0,740 g |
| 2 rad/s | 0,928 g | 0,614 g |
| 5 rad/s | 0,281 g | No cubre toda orientación bajo esta cota |
| 10 rad/s | No cubre el conjunto de cargas acotado | No cubre el conjunto de cargas acotado |

No cubrir el conjunto conservador a velocidad angular no nula NO prueba que toda maniobra a esa velocidad sea imposible: la ampliación de cargas puede reunir máximos que no ocurren simultáneamente. La tabla tampoco constituye una envolvente de vuelo real. A velocidad angular nula, el filtro descarta la afirmación de 1 g omnidireccional con esta reserva angular dentro de ESTE modelo y dominio, sin establecer una imposibilidad física universal.

La cara limitante de los casos con radio de fuerza no negativo se comprobó mediante programación lineal; se verificó además que aumentar ese radio un 0,001 % hace inviable ese punto limitante. Esto valida el cálculo para el conjunto especificado, no sus supuestos físicos. Los 24 escenarios y residuos se guardan en `masas_distribuidas/limites_mapa_5kg.csv` y `.json`.

## Límites pendientes

El modelo todavía no incorpora el par aerodinámico de reacción del rotor en el equilibrio, respuesta dinámica del paso, variación de RPM, límites de motor/controlador, tensión mínima, calentamiento, interferencia de estelas, entrada oblicua o potencia compartida. Que un empuje aparezca en el mapa aerodinámico no demuestra que el motor pueda entregarlo. El par de reacción debe incorporarse con su curva firmada en la siguiente asignación, y el consumo debe calcularse para los mismos repartos de empuje.

Conclusión de diseño: la mejora de ejes resuelve una debilidad geométrica concreta, pero no basta para prometer movimientos abruptos omnidireccionales sin restricciones. La inversión de empuje y la cobertura experimental del rotor siguen siendo determinantes. Se mantienen abiertas las variantes 2 y 10 kg, el cierre de masa y energía, la retracción y el régimen de 600–1000 km/h.
