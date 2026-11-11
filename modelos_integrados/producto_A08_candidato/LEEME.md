# A08 candidata: correcciones nominales locales

3 de noviembre de 2026. Fuente: A07 cerrado de 5 kg objetivo, identificado por SHA-256 en `CORRECCIONES.json`. La referencia canónica continúa siendo A07.

`corregir_referencia.py` modifica siete piezas por sustracción: elimina duplicaciones de material en dos insertos laterales y dos encuentros del panel de nariz, abre envolventes nominales de asiento de tornillo y recalcula un encuentro pequeño de raíz. El diámetro supuesto de los asientos es 4,6 mm; no se aprueba una tolerancia o unión de fabricación.

`A08_cerrado_5kg_candidato.step` contiene 208 registros válidos reimportados. Las nueve parejas corregidas tienen intersección nominal cero después de reimportar. Todas las modificaciones quedaron contenidas en la geometría original. No es una nueva auditoría global completa ni un análisis bajo carga.

Permanecen decisiones de ingeniería en 48 encuentros eje–álabe, 12 encuentros de soportes y cuatro entradas de ejes en reservas de actuadores. No se los clasifica automáticamente como defectos: deben definirse uniones, taladros, retención y equipos reales.

Esta rama no incorpora materiales aprobados, hardware dimensionado, mecanismo continuo, otras poses/escalas o validez aerodinámica. No heredar resultados de masa/flujo del A07 como si pertenecieran a esta geometría modificada. No promover automáticamente a configuración funcional.
