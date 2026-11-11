# A: conductos geométricamente coherentes

Se consolidaron las cuatro camisas ilustrativas originales y los cuatro conductos del módulo vectorial en cuatro sólidos únicos, con taladro de radio 42 mm. La fuente y su huella están en `VERIFICACION.json`.

Las camisas originales tenían radio interior 41 mm, menor que el radio de un vértice de pala de aproximadamente 41,012 mm. El ensamblaje corregido deja una separación radial geométrica aproximada de 0,988 mm entre ese vértice y el taladro. Se comprobaron las intersecciones rotor/conducto por canal y la ausencia de material del conducto dentro del cilindro nominal. Los pares de volúmenes y los valores exactos están en `VERIFICACION.json`.

Se reimportó el STEP y se verificaron 101 piezas válidas. Validez de sólidos y ausencia de estas interferencias locales no equivalen a un ensamblaje funcional: faltan tolerancias, deformaciones, contención de rotor, fijaciones, rodamientos, servos/transmisiones, fabricación, masa, cargas y una revisión global de interferencias. La holgura geométrica no se declara suficiente para operación.

Este archivo es la nueva rama de integración para continuar los estudios. No acredita empuje, vuelo omnidireccional o velocidad máxima. Las simulaciones del conducto actuales excluyen rotor, motor y rejillas: esta corrección CAD no las convierte en simulación de la instalación completa.
