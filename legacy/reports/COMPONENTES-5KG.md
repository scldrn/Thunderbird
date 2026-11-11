# Auditoría de componentes: versión de 5 kg

Resultado: no se puede confirmar el candidato de 4,67 kg con los componentes contrastados. Esto no descarta otras arquitecturas ni otras baterías.

## Motores y hélices

La configuración previa requiere entre 33,2 y 39,2 N por rotor bajo su asignador lineal. T-Motor publica para MN4006 KV380, hélice de 13 pulgadas, 1633 g de empuje a 233 W y 24 V: insuficiente como sustitución directa. Su tabla indica masa de 68 g con cable, distinta de los 57 g publicitarios. Fuente: https://store.tmotor.com/product/mn4006-kv380-motor-antigravity-type.html

MN5008 KV170: 128 g con cable, dimensiones 55,6×32 mm; con hélice P18×6.1 alcanza 4100 g de empuje a 687 W y 46,94 V en la tabla del fabricante. La hélice tiene diámetro de 45,72 cm. Estos datos describen empuje positivo en banco: NO prueban empuje reversible simétrico. Cambiar hélice o paso invalida trasladar automáticamente la tabla. Fuente: https://store.tmotor.com/product/mn5008-kv400-motor-antigravity-type.html

No se selecciona un ESC definitivo: la compatibilidad eléctrica no acredita inversión rápida de empuje. Una solución de paso variable necesita buje, servo, control y curva medida de empuje en ambos sentidos; no hay aquí conjunto comercial validado. La viabilidad del principio se ha demostrado en investigación: https://dspace.mit.edu/entities/publication/cbf41dbd-220c-4616-b300-c116ec7841be

## Batería: referencia documentada, no selección definitiva

Molicel P50B: 18 Wh nominales, 71 g máximos por celda, 60 A continuos sujetos a corte térmico de 80 °C. Dimensiones máximas 21,55×70,15 mm. Fuente: https://www.molicel.com/wp-content/uploads/Product-Data-Sheet-of-INR-21700-P50B-80122.pdf

Se mantiene SOLO para sensibilidad la demanda previa de 5,25 kW. Con 3 V/celda bajo carga SUPUESTOS y 60 A/celda, un pack 12S3P tiene 36 celdas, 2,556 kg de celdas y aproximadamente 2,939 kg añadiendo un 15% SUPUESTO de interconexiones, soporte y protección. La potencia térmica, caída de tensión y duración admisible deben ensayarse. No se garantiza esta potencia hasta descarga completa.

A 40 A/celda, el mismo filtro exige 12S4P y una estimación de 3,919 kg de pack. Un 6S5P bajo la hipótesis de 60 A estima 2,449 kg, pero exige otro bobinado y controlador compatibles.

Reactor (1,080 kg), ocho MN5008 KV170 (1,024 kg), combustible del escenario (0,156 kg) y 36 celdas (2,556 kg) suman 4,816 kg ANTES de hélices, controladores, piel, mecanismos y demás electrónica. Esta combinación a potencia congelada no ofrece un presupuesto práctico de 5 kg.

Sustituir solo la batería anterior por el pack12S3P eleva el presupuesto previo a 6,95 kg. NO es nueva masa final convergida: cambiar diámetro, motores y masa modifica potencia e inercia. Hélices mayores podrían reducir potencia; la masa añadida puede aumentarla. No se ha demostrado que todas las opciones de LiPo o de menor demanda fallen.

## Distribución preliminar y empaquetado

El dibujo acompaña la geometría anterior: cuerpo91×23cm, dos estaciones de cuatro rotores, centros a ±18,3cm longitudinales y radio45,7cm. Muestra las envolventes de rotores mayores, no un mecanismo construido. El reactor se representa en la posición del modelo; el resto son zonas reservadas, sin validación térmica ni conductos.

Una hélice de45,7cm no cabe transversalmente dentro de23cm. El plegado de palas y brazos debe diseñarse; orientar una hélice rígida en otro plano no demuestra que ocho unidades quepan. La condición suficiente de separación de esferas envolventes entre estaciones ahora falla por9,15cm. Esto NO prueba contacto entre discos inclinados: obliga a verificar distancias reales y trayectorias de plegado en3D. La envolvente radial conservadora desplegada es1,37m.

## Decisión técnica

No comprar ni presentar estos componentes como conjunto compatible. Mantener P100 como referencia axial; comparar batería LiPo documentada frente a P50B, medir/obtener curvas bidireccionales y optimizar asignación de potencia antes de redimensionar. Un demostrador eléctrico de vuelo omnidireccional puede validar control y propulsores; no satisface por sí mismo el requisito de600–1000km/h.

Falta cerrar selección de actuadores reversibles, nueva iteración masa/potencia, CAD volumétrico y cinemático, y transición. El estado correcto es candidato condicionado, no diseño terminado.

Código: componentes_5kg.py. Datos: resultados/componentes_5kg.json. Dibujo: resultados/distribucion_5kg_preliminar.png.
