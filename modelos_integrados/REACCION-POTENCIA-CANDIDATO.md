# Reacción de rotores y potencia del candidato revisado

Se enlazan la geometría revisada, masa presupuestada 5,498 kg y tensor corregido por distribución de palas con el mapa condicional de rotor a 6000 rpm. Script: `asignacion_reaccion_potencia.py`. Salidas: `masas_distribuidas/asignacion_reaccion_potencia_{CASOS,RESUMEN,VERIFICACION}.json`.

## Modelo y muestreo

Se añade al momento de cada rotor su reacción aerodinámica según el par de eje interpolado del mapa, con el signo de giro correspondiente. Se fija el patrón de sentidos [+, +, +, +, −, −, −, −], que cancela el momento angular ideal a iguales RPM e inercias. No se optimizan todos los patrones en esta etapa. La inversión de empuje se supone por paso variable manteniendo el sentido de giro: no se cambia artificialmente el signo del par de reacción cuando el empuje cambia de signo.

Se minimiza localmente la suma de potencias eléctricas interpoladas mediante SLSQP sujeto al equilibrio no lineal. No se demuestra mínimo global. Se analizan 26 direcciones de fuerza, tres módulos de fuerza (1, 1,5 y 2 veces el peso) y siete demandas angulares: cero y ±2 rad/s² en cada eje. El cuerpo parte de velocidad angular nula; no se incluyen las cargas de giro finito de la etapa anterior. Cada nivel contiene 182 casos, no una cobertura continua de todas las direcciones.

Dominios: mapa completo de −37 a +40 N y filtro de contribución de par fuera de polar ≤5 %, de −28 a +38 N. Ambos siguen siendo mapas aerodinámicos condicionales, no mediciones del conjunto propulsor.

## Resultados

| Dominio | Módulo de fuerza/peso | Equilibrios encontrados | Potencia total entre casos resueltos |
|---|---:|---:|---:|
| Completo | 1 | 182/182 | 0,988–1,282 kW |
| Completo | 1,5 | 182/182 | 1,423–1,967 kW |
| Completo | 2 | 182/182 | 1,966–2,809 kW |
| Filtro 5 % | 1 | 182/182 | 0,988–1,282 kW |
| Filtro 5 % | 1,5 | 182/182 | 1,423–1,967 kW |
| Filtro 5 % | 2 | 122/182 | 2,035–3,393 kW |

Los 60 casos sin solución del último grupo son fallos de búsqueda de equilibrio con este método y restricciones; NO se declaran físicamente imposibles ni globalmente inviables sin una prueba adicional. A su vez, resolver todos los puntos muestreados no demuestra cobertura continua, estabilidad dinámica ni respuesta de paso suficiente. Los niveles de fuerza no equivalen a una aceleración neta única para todas las orientaciones de gravedad.

El máximo módulo de reacción resultante entre casos resueltos fue 0,607 N·m con mapa completo y 0,690 N·m con filtro. La compensación se realiza mediante el reparto de empujes: no se supone cancelación automática del par de reacción. El máximo consumo individual encontrado fue 636 W con mapa completo y 588 W con filtro. Que estas cifras aparezcan en el modelo no aprueba el motor, controlador ni su capacidad a tensión mínima.

## Energía: cociente orientativo, no autonomía validada

En los 26 casos de fuerza igual al peso y aceleración angular cero, el consumo calculado es 988–1276 W. Suponiendo 97,68 Wh nominales de batería y 80 % utilizables (78,144 Wh), el cociente energía/potencia resulta 3,68–4,74 minutos.

Este intervalo NO es una predicción de autonomía de vuelo: omite consumos auxiliares, restricciones térmicas, caída de tensión, capacidad efectiva bajo carga, transitorios y disponibilidad real de potencia del motor. No incorpora misión de alta velocidad ni consumo del reactor. La eficiencia eléctrica usada por el mapa es 85 % supuesta, no medida.

## Comprobación

Se recalcularon directamente fuerza, momento y consumo de los 1032 casos con solución utilizando los empujes guardados, sin reutilizar el residuo declarado por el optimizador. Error máximo de equilibrio: 6,73e-9 N y 4,21e-9 N·m. Esto verifica la consistencia numérica del modelo; no sustituye ensayos.

## Decisión y trabajo pendiente

La geometría revisada ya cuenta con un reparto de fuerza/par y un consumo asociados al mismo modelo de masa. Falta la respuesta temporal del paso y RPM, los límites del motor a tensión mínima y las curvas térmicas. El escalado a 10 kg no queda validado por estos resultados. Tampoco se han cerrado las masas faltantes, la retracción, la resistencia estructural real, las tomas ni el régimen transónico.


## Actualización posterior

La verificación MILP de `VERIFICACION-GLOBAL-ASIGNACION.md` resolvió los 60 fallos locales: recuperó uno y declaró 59 inviables en el modelo interpolado restringido. El balance actualizado de ese grupo es 123/182; las cifras anteriores se conservan como resultados históricos de SLSQP. No se demuestra imposibilidad física fuera de ese modelo.
