# Verificación global de los casos sin solución local

Se revisaron los 60 fallos del optimizador local de la etapa anterior, todos correspondientes al dominio de empuje −28 a +38 N y fuerza solicitada de dos veces el peso. Se mantuvieron exactamente la geometría, masa 5,498 kg, tensor, sentidos de giro, par de reacción y mapa interpolado anteriores.

## Resultado

- Un caso tiene solución: el optimizador local no la había encontrado.
- Los otros 59 fueron declarados inviables por HiGHS dentro del modelo interpolado, con sus tolerancias numéricas.
- Ninguno quedó sin resolver por límite de tiempo.

Por tanto, en ese grupo de 182 demandas, el balance actualizado es 123 con equilibrio encontrado y 59 inviables dentro del sustituto matemático restringido. Los demás grupos de la etapa anterior mantienen sus resultados.

## Formulación

`verificar_asignacion_global.py` representa cada rotor mediante una selección binaria de exactamente uno de los 66 tramos entre nodos de empuje −28,…,+38 N. Una variable continua entre cero y la selección binaria interpola dentro de ese tramo. Fuerza, par de reacción y potencia usan la MISMA selección de tramo por rotor. No se utiliza la envolvente convexa de puntos no adyacentes como sustituto del mapa.

La fuerza y el momento del vehículo son lineales en esas variables, de modo que la factibilidad se resuelve mediante programación lineal entera mixta. La función objetivo es cero: se busca equilibrio, no mínimo global de consumo. Esta formulación global es exacta para las curvas lineales a tramos especificadas, sujeta a aritmética y tolerancias del solucionador. No es una prueba de exactitud aerodinámica ni de imposibilidad física.

## Control de implementación

Se reconstruyeron las variables binarias y continuas de los 486 puntos previamente resueltos en el dominio restringido. Todos satisfacen la formulación; residuo máximo de equilibrio normalizado 5,20e-9. Esto comprueba que no se excluyeron por error los puntos previamente válidos.

El caso recuperado (índice de dirección 18, caso angular 1 en el archivo original) tiene residuo 1,42e-14 y consumo calculado 2120,85 W. Ese consumo es el de una solución factible, no un óptimo. El reparto de ocho empujes se conserva en `masas_distribuidas/asignacion_global_CASOS.json`. El error entre el par reconstruido por segmentos y el interpolador original es 5,55e-17.

## Interpretación para el objetivo

Ahora puede afirmarse que la geometría y el mapa restringido actuales no cubren todas las demandas muestreadas de fuerza igual a dos veces el peso con los pares solicitados. Es una afirmación más específica que «el solucionador falló» y mucho más limitada que «el vehículo no puede realizar movimientos bruscos».

El mapa completo tiene un dominio mayor, pero depende más de las zonas de polar no cubiertas; no se puede eliminar esa incertidumbre utilizando únicamente un optimizador distinto. Sigue siendo necesario medir la inversión de empuje, la respuesta temporal y los límites eléctricos/térmicos. La prueba no abarca vuelo transónico, plegado, 2 kg, 10 kg ni óptimo global de geometría.
