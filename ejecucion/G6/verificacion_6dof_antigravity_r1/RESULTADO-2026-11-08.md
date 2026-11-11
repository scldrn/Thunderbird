# Verificación numérica del integrador 6DOF

La batería propuesta en Antigravity se ejecutó sobre una copia de `simular.py`.
El fallo previo de serialización se corrigió convirtiendo a `bool` nativo el
resultado de la comparación, sin cambiar el criterio numérico. Se conserva
`FALLO_SERIALIZACION.log` como evidencia de la ejecución anterior.

La ejecución completa terminó con código 0 y `REPORTE_PRUEBAS_SIMULAR.json`
válido. Pasaron tres casos: conservación en giro libre asimétrico con cuatro
pasos temporales, giro de 360° frente a solución analítica y pares de fuerzas
con comprobación de momento. En el giro libre, los errores máximos relativos de
energía y momento angular disminuyeron al reducir el paso de 0,02 a 0,0025 s.

Además, en una copia temporal se impuso una tolerancia angular de cero. El
programa terminó con código 1 y registró `aprobado: false` y estado `FALLIDO`;
esto comprueba que un fallo no se oculta al escribir JSON. No se cambió el
simulador original.

Son pruebas de ecuaciones e integración bajo supuestos ideales; no validan los
ventiladores, el controlador instalado ni el comportamiento del vehículo real.
