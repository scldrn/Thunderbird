# Contrato candidato para datos de ventilador instalado

Este paquete contiene un validador y un ejemplo **sintético** de datos de un
módulo de ventilador. No contiene mediciones de C02, no interpola un mapa y no
está conectado al simulador de vuelo. Las salidas automáticas de Antigravity
utilizadas como punto de partida se conservan en
`integracion_antigravity/sesiones_aisladas/20261108T041236Z_b586a83a/contrato_mapa_instalado/`.

Se corrigió una vía de aceptación silenciosa: el candidato original permitía
la política `ADVERTIR`, pero no registraba aviso cuando una muestra excedía el
dominio. Esta revisión solo acepta `RECHAZAR`, tanto en el validador como en
el esquema JSON. Las muestras marcadas como extrapoladas o fuera de los rangos
comprobados se rechazan. Los originales no se modificaron.

Verificación ejecutada con Python estándar:

```sh
python3 test_contrato_mapa.py
```

Resultado: **27 pruebas superadas**. Entre ellas se verifican el rechazo de
`ADVERTIR` y la coincidencia del conjunto de políticas admitidas por el esquema
y por el validador. Eso no demuestra conformidad completa entre ambos.

El dominio de velocidad se expresa como módulo: no demuestra cobertura de todas
las direcciones del flujo. Estar dentro de rangos individuales tampoco
demuestra cobertura conjunta ni justifica interpolar entre muestras. Antes de
incorporarlo al 6DOF faltan datos instalados trazables, un dominio
multidimensional adecuado, tratamiento de incertidumbre y pruebas de la
integración con fuerzas, momentos y potencia.
