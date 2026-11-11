# Mediciones y estado de integración

Estos modelos son ensamblajes de envolventes para detectar problemas de integración. No son planos de fabricación ni una demostración de viabilidad. STEP utiliza milímetros; CSV/JSON utilizan metros, kilogramos y segundos. El eje x es longitudinal, positivo hacia la cola; el origen es el centro geométrico del fuselaje.

## Lo generado por cálculo

`crear_modelos.py` es la definición paramétrica reproducible de ambas variantes. Cada carpeta contiene configuración, ensamblaje STEP con componentes separados, STL de componentes, tabla de masas asignadas, intersecciones de sólidos y mediciones digitales. Los discos representan volumen barrido, no ocho rotores sólidos. Las masas de módulos incluyen elementos todavía no dibujados: el tensor calculado les asigna la distribución de su envolvente cilíndrica; por ello NO es un tensor físico validado. Las partidas sin ubicación se excluyen explícitamente del centro de masa y tensor.

Se mantiene L/D=6 y la distribución angular del estudio de control, con estaciones ±L/4. Esta geometría es nueva respecto al estudio detallado de rotor de 5 kg con L/D=4: sus resultados dinámicos anteriores no certifican este ensamblaje. Las superficies usan las áreas del modelo de trimado existente; sus espesores y formas rectangulares son hipótesis.

El fuselaje todavía no tiene aberturas. El conducto es una reserva cilíndrica, no una toma aerodinámica terminada. Hay que resolver conexiones, difusor, escape, aislamiento térmico, depósito, bujes de paso variable, retracción y refuerzos. No se exporta un supuesto modo de crucero plegado: todavía no existe una cinemática que lo justifique. Las intersecciones son volúmenes CAD, no márgenes de seguridad; algunas conexiones brazo-motor son deliberadas. No se evalúa interferencia aerodinámica de estelas.

Para 10 kg los rotores, módulos y baterías son escalados de referencia: no se ha seleccionado un conjunto comercial equivalente. Las dimensiones del reactor corresponden a la referencia histórica P250-Pro-S del estudio, no garantizan disponibilidad o equivalencia con versiones nuevas.

## Registro físico — todavía vacío

`registro_fisico.csv` contiene solo cabecera. Cada fila debe identificar pieza, instrumento, calibración, fecha, condiciones, valor, unidad e incertidumbre. No insertar valores de simulación en ese archivo.

| Medición | Método y equipo | Resultado necesario |
|---|---|---|
| Dimensiones y holguras | Calibre y regla con trazabilidad; comparar con CAD | Dimensiones reales, tolerancias y discrepancias |
| Masa de cada pieza y conjunto | Balanza calibrada adecuada al rango | BOM real incluyendo cables, fijaciones y combustible |
| Centro de masa | Reacciones en apoyos de posiciones conocidas, repetir en tres orientaciones | CG tridimensional y dispersión; registrar distancias y reacciones originales |
| Inercia | Péndulo bifilar/trifilar y ensayo de referencia; descontar útil | Periodos, geometría del útil, amplitud pequeña, masa e incertidumbre; tensor cuando existan mediciones suficientes |
| Empuje y par de rotor | Banco instrumentado con protección y mando remoto | Mapa firmado de empuje, par, RPM, paso, tensión, corriente y temperatura |
| Respuesta de paso | Sensor de posición y adquisición sincronizada con fuerza | Retardo, tiempo de respuesta, sobreimpulso y caída de RPM bajo carga |
| Flexión de estructura | Cargas calibradas incrementales con medición de desplazamiento | Curvas carga-deformación y deformación residual; límites definidos antes del ensayo |
| Cinemática | Maqueta sin propulsión, posiciones medidas durante todo recorrido | Holgura mínima real, enclavamiento y cargas de actuación |

Los ensayos energizados necesitan diseño específico del banco y límites mecánicos y eléctricos de los componentes. No hay todavía un prototipo que permita ejecutar esas mediciones.

## Orden de cierre

1. Resolver interferencias de envolventes internas y justificar el volumen del conducto.
2. Seleccionar módulos reales para 10 kg y cerrar masas faltantes para ambos tamaños.
3. Diseñar y verificar la cinemática de retracción; recalcular masa, CG e inercia en todo el recorrido.
4. Recalcular control y aerodinámica con esta única configuración; validar con mapas medidos y CFD/túnel.
5. Sustituir valores supuestos por medidas físicas trazables.

## Reproducir

Desde la raíz del proyecto:

```
.venv-cad/bin/python investigacion-aeronautica/modelos_integrados/crear_modelos.py
```

Python 3.11 y CadQuery están instalados en el entorno local `.venv-cad`. No es necesario instalar una aplicación para generar los archivos. Para editar o explorar STEP mediante interfaz gráfica se puede usar un CAD compatible; su instalación es opcional.

## Verificación final de esta entrega

Los STEP se reimportaron correctamente y todos sus sólidos resultaron válidos. Tras desplazar la reserva de combustible y situar los soportes de motor en el lado adecuado de cada disco, quedaron únicamente ocho intersecciones brazo-módulo previstas por ensamblaje. No se detectaron intersecciones de barridos de rotor entre sí, con otros componentes comprobados o con el fuselaje exterior en la posición desplegada. Esto no verifica tolerancias, flexión, estelas ni movimientos de plegado. Los presupuestos son 5.498 y 10.685 kg, incluidos márgenes asignados pero con elementos todavía ausentes; no son masas medidas ni cierres definitivos.
