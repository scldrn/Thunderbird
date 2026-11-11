# Candidatos concretos y decisión de selección provisional

**Revisión posterior:** este presupuesto es histórico. Al integrar superficies, el margen de 5 kg cambia; consultar `INFORME-CONSOLIDADO-VIABILIDAD.md` y `masa_consolidada_5kg_RESUMEN.json` en `resultados`. Las autonomías de abajo usan un modelo eléctrico anterior y no constituyen prestaciones actuales.

## Batería candidata principal

GNB22006S120A: 6S1P,22,2V,2200mAh,357g±10g,110×34×50mm,conectorXT60. Son especificaciones comerciales del fabricante, no medidas propias. Fuente: https://www.gaoneng.shop/products/gaoneng-gnb-6s-22.2v-2200mah-120c-xt60-lipo-battery

Dos packs en serie forman12S/2200mAh:714g publicados,97,68Wh nominales. Se asignan40g adicionales para integración:754g estimados, con al menos±20g de tolerancia de packs. No se interpreta la etiqueta120C como corriente garantizada. Falta curva de descarga y ensayo de conectores, temperatura y tensión. Cualquier accesorio de integración que exceda40g reduce el margen.

Con presupuesto previo de3,46kg para reactor, motores, combustible, estructura asignada, electrónica, instalación y reserva, quedan786g para ocho conjuntos ESC+hélice+buje+servo:98,25g por estación. El motor de128g ya se contó. Esto abre margen respecto a P50B, pero no demuestra cierre de5kg ni valida las asignaciones estructurales.

Cuatro packs en12S2P pesan1,468kg con la misma asignación adicional, y dejan solo9g por estación para esos conjuntos. Se descarta esta variante bajo el presupuesto actual, no por imposibilidad universal.

## Energía y potencia: escenarios separados

Usando exclusivamente las potencias muestreadas del modelo anterior (860W y2362W), y suponiendo70% de energía nominal utilizable, dos packs equivalen energéticamente a4,77min al nivel de860W;4,06min con90% de ese nivel y10% del pico;1,74min al nivel pico. NO son autonomías de vuelo prometidas. No incluyen pérdidas de perfil de paso variable a alto régimen, consumo de servo/control, límites térmicos, transición ni combustible adicional. La batería mayor también cambiaría masa y demanda, por lo que sus duraciones en el JSON son comparación a carga eléctrica congelada.

A2362W y40V se requieren59,1A. Que el pack anuncie120C no acredita esa operación. Con44,4V de circuito abierto SUPUESTOS, mantener al menos42V a esa potencia exige resistencia total inferior a42,7mΩ; mantener44V exige menos de7,45mΩ. Son criterios de sensibilidad para contrastar mediciones, no resistencias conocidas del producto. La tensión necesaria del motor permanece pendiente de mapa empuje/paso/RPM.

## Módulos de paso variable contrastados

| Referencia | Evidencia | Decisión |
|---|---|---|
| MIT/Cutler | Prototipo experimental; cambio de paso en unos70ms | Referencia dinámica; no módulo comercial ni garantía a39N |
| Heliquad, Kulkarni/Sundaram | Prototipo experimental publicado como preprint; mecanismo mecanizado y motor modificado | Referencia mecánica; no trasladar masa al rotor de46cm |
| Sunnysky X2814 KV1250 + XRotor40A + ES08MD, estudio2020 | Conjunto identificado en artículo de asignación de actuadores | Candidato documental; falta contraste de curvas y masa para nuestro requisito |
| T-Motor MF2614VP | Ajuste manual mediante piezas de posicionamiento | Descartado para invertir empuje activamente en vuelo |

Heliquad informa un vehículo de626g: cuatro motores192g, mecanismos44g, servos48g y ocho palas48g. Equivale a35g de mecanismo+servo+palas por rotor en ESE prototipo, excluyendo motor y electrónica. No se escala linealmente a39N. Emplea eje hueco modificado y piezas mecanizadas: no es un accesorio compatible automáticamente con MN5008. Fuente: https://arxiv.org/html/2404.05591v1

Otras fuentes:
- MIT: https://acl.mit.edu/projects/variable-pitch-quadrotor
- Artículo2020: https://www.mdpi.com/1424-8220/20/19/5651 (acceso completo bloqueado en esta revisión; identificación de componentes en texto indexado, no curvas confirmadas)
- Ajuste manual: https://store.tmotor.com/product/mf2614vp-variable-pitch-propeller-for-uavs.html

## Selección provisional resultante

Batería GNB de dos packs: candidata a caracterización, no compra autorizada ni selección final. Motor MN5008KV170: referencia de potencia, pendiente de bobinado/curva a tensión mínima y compatibilidad mecánica. Módulo reversible: diseño específico basado en referencias experimentales, sin candidato comercial confirmado. Objetivos independientes:±29,7N para0,5g o±38,9N para1g, con reserva1Nm en el modelo.

No existe aún una lista completa de componentes verificados. El resultado de la búsqueda es una batería concreta que mejora el presupuesto y mecanismos documentados que orientan un módulo propio, no una aeronave de5kg validada. Para continuar sin ensayos, la siguiente tarea útil es dimensionar el mecanismo desde geometría de pala, cargas centrífugas y momento de paso; esos datos aún no están definidos.

Reproducción: comparar_candidatos.py; resultados/comparacion_baterias_concretas.json. No se enviaron consultas comerciales ni se compraron productos.
