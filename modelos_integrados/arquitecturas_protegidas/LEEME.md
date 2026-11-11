# Tres arquitecturas protegidas: CAD de alojamiento

Modelos paramétricos CadQuery, STEP en milímetros, renders Mitsuba CPU. Fuente: `../arquitecturas_protegidas.py`. Fuselaje común de 1400 mm de longitud y 420 mm de diámetro máximo para comparar a la misma escala. Son propuestas NUEVAS de alojamiento; no equivalen al candidato anterior de 5 kg ni heredan sus resultados de control o empuje.

- **A_internos_seccion:** ocho ventiladores radiales internos de diámetro de rotor 130 mm, con pasos abiertos en la carcasa. Se oculta un cuadrante de la carcasa para ver el interior. Los discos azules separados son tapas abiertas esquemáticas: no hay todavía bisagras, accionamiento, sellos ni apoyo calculados. El corte es solo para inspección, no una forma de vuelo.
- **B_retractiles_guardado / B_retractiles_desplegado:** cuatro casetes con rotor de 160 mm; centros guardados en y=±90 mm y desplegados en y=±340 mm, con estaciones x=±300 mm. Se muestran guías y tapas como volúmenes conceptuales. Son dos estados de alojamiento, NO una cinemática de retracción continua comprobada. Faltan cierres, refuerzos y adaptación de tapas a la superficie curva. Los motores son cilíndricos ilustrativos y las palas no tienen un perfil aerodinámico dimensionado.
- **C_conductos_exteriores:** cuatro rotores de 180 mm rodeados de conductos y sujetos con uniones cortas. Protegen periféricamente las puntas; las caras abiertas aún requieren resolver flujo, exposición frontal y posibles compuertas.

## Qué se ha verificado

Los sólidos se comprueban con el núcleo CAD antes de exportar. Los renders usan los mismos sólidos exportados, con materiales de presentación. Las dimensiones nominales y los estados se guardan en `dimensiones.json`. Los STEP contienen piezas separadas para revisión.

## Límites de estos conceptos

No se han dimensionado para una masa final ni para potencia, resistencia estructural, control en seis grados de libertad, enfriamiento, sellado o arrastre a Mach 0,82. En particular, la disposición radial de A y los cuatro rotores paralelos de B/C NO demuestran omnidireccionalidad con orientación fija: hacen falta estudiar vectorización, canales axiales y autoridad de momento. No deben presentarse como sistemas de vuelo completos.

Los números y diámetros de módulos se eligieron para explorar alojamiento; no constituyen una selección de propulsión. Área geométrica total de discos: A 0,1062 m²; B 0,0804 m²; C 0,1018 m². Son mucho menores que los 1,3134 m² de ocho rotores de 457,2 mm del candidato anterior. Esta comparación de área NO equivale a área efectiva de sustentación ni permite transferir empuje o potencia del modelo anterior. La reducción debe evaluarse antes de elegir arquitectura.

Estos modelos muestran el espacio necesario y el aspecto de cada alternativa. La siguiente etapa debe integrar rutas de flujo/vectorización y comprobar conjuntamente masa, fuerza, momento, cargas sobre compuertas e interferencias durante el movimiento.
