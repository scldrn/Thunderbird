"""Create execution registers; values are planning decisions, not validated design data."""
from pathlib import Path
import csv, json

P = Path(__file__).resolve().parent

requirements = [
('R01','Arquitectura','Ventiladores internos; sin despliegue de rotores','confirmado','Inspección CAD y decisiones','G0'),
('R02','Familia de masas','2/5/10 kg objetivo; presupuesto independiente','confirmado_objetivo','BOM completa por variante y margen','G1;G7'),
('R03','Configuración de referencia','A07; 5 kg como ancla de integración propuesta','propuesta','Configuración única con huella y unidades','G0'),
('R04','Apariencia','Deportiva profesional/agresiva compatible con prestaciones','confirmado','Revisión visual y geométrica de configuración factible','G3;G7'),
('R05','Velocidad','600 km/h intermedio; 1000 km/h extensión a investigar','objetivo_no_demostrado','Equilibrio instalado; control; estructura; ensayo posterior','G4;G6;F'),
('R06','Estacionario','Altitud y orientación controladas; límites de error por fijar','pendiente_cuantificar','Control cerrado con planta y potencia identificadas','G1;G6'),
('R07','Traslación omnidireccional','XYZ con orientación independiente dentro de dominio declarado','confirmado_objetivo','Dominio simultáneo de fuerza/momento; gravedad y saturación','G2;G6'),
('R08','Actitud arbitraria','Separar reorientación de vuelo invertido; no imponer este último','alcance_por_fijar','Envolvente de actitud y reversibilidad','G1;G6'),
('R09','Agilidad','Aceleración neta, jerk, velocidad angular y giro 30/90°','pendiente_cuantificar','Métricas y tolerancias trazadas a maniobras','G1;G6'),
('R10','Radio de giro','Derivado de velocidad y aceleración; no giro instantáneo','restriccion_fisica','Integración dinámica y radio de trayectoria','G6'),
('R11','Autonomía','Matriz inicial 30/120/300 s por modo; misión final pendiente','escenarios_propuestos','Energía/potencia y masas simultáneas','G1;G3'),
('R12','Carga útil','Definir masa y volumen de equipos/carga deportiva','pendiente','BOM sin partidas desconocidas iguales a cero','G1;G3'),
('R13','Entorno','Altitud/densidad, temperatura, viento/ráfaga por delimitar','pendiente','Envolvente de operación y perturbaciones','G1;G6'),
('R14','Contaminación y clima','Agua/polvo/hielo/corrosión según dominio declarado','pendiente','Análisis de ingestión/atasco y ensayo aplicable','G5;F'),
('R15','Ruido y calor','Límites y zonas sensibles por definir','pendiente','Evaluación acústica/térmica e integración','G1;G5;F'),
('R16','Geometría funcional','Nariz/cola/secciones/tomas/salidas/puertas coherentes','abierto','STEP, dominio fluido y metrología de la misma revisión','G3;G4'),
('R17','Número y área de módulos','Cuatro como base; disposición y área optimizables dentro de A','propuesta_no_congelada','Alojamiento, potencia y dominio de fuerzas','G2;G7'),
('R18','Rotor','Paso/RPM/perfil/solidez/holgura, Reynolds y Mach locales','abierto','Mapa de fuerza/par/potencia con procedencia','G2'),
('R19','Vectorización','Mapa instalado; no sustituir por cono supuesto de 35/45°','abierto_critico','Seis cargas incluyendo reacción de paredes','G2'),
('R20','Reversibilidad','Definir estados que requieren fuerza descendente/inversión','abierto','Mapa bidireccional y respuesta si lo exige la misión','G2;G6'),
('R21','Actuación','Par, tasa, retardo, tensión, calor y vida bajo carga','abierto_critico','Curvas de actuador y acoplamiento con flujo','G2;G5'),
('R22','Empuje axial','Motor e instalación no seleccionados; tubo vacío','abierto_critico','Empuje neto instalado frente a demanda','G3;G4'),
('R23','Tomas y escape','Área de captura/paso, pérdidas, distorsión y temperatura','abierto_critico','Mapa conjunto motor-admisión-escape','G3;G4'),
('R24','Potencia y energía','Tensión mínima, corriente, combustible, refrigeración y reserva','abierto_critico','Balance por modo y transición; fuentes identificadas','G1;G3'),
('R25','Masa/CG/inercia','Equipos completos y estados de carga; margen propuesto 15%','abierto_critico','Cierre iterativo y tensor de configuración','G3;G7'),
('R26','Compuertas','Recorrido A07 candidato; requiere mecanismo y cierres','abierto_critico','Recorrido, tolerancias y cargas con herrajes','G3;G5'),
('R27','Aletas en X','Candidata A05-A07; dimensiones/deflexiones por justificar','propuesta_no_validada','Fuerzas/momentos, trimado, cargas y actuadores','G4;G5'),
('R28','Aerodinámica','Coeficientes del conjunto frente a Mach/Re/incidencia/deriva','abierto_critico','CFD contrastada y datos de incertidumbre','G4'),
('R29','Mach crítico/arrastre','Separar aparición sónica de divergencia; sin tabla universal','abierto','Presiones y curvas de arrastre con criterio definido','G4'),
('R30','Transición','Transferencia de control, puertas y flujo oblicuo bajo carga','abierto_critico','Trayectoria con autoridad y potencia continuas','G4;G6'),
('R31','Estructura','Materiales, laminados, aberturas, uniones, fatiga y márgenes','abierto_critico','FEM verificada y ensayos correlacionados','G5;F'),
('R32','Aeroelasticidad','Modos libres, flutter/divergencia, holgura y temperatura','abierto_critico','Modelo acoplado y dominio de validez','G5;F'),
('R33','Control robusto','Reserva simultánea de fuerza/momento/potencia bajo incertidumbre','abierto_critico','Pruebas fuera de ajuste y límites de saturación','G6'),
('R34','Fallos','Definir tolerancia a fallo de módulo/tapa/sensor/alimentación','pendiente','Autoridad remanente y recuperación demostradas en dominio','G1;G6;F'),
('R35','Autonomía','Estimación de estado, navegación y modos supervisados','objetivo_posterior','SIL/HIL y ensayos separados de entrenamiento','G8;F'),
('R36','Machine Learning','Solo con función/ventaja frente a controlador base','opcional_condicionado','Separación de datos, incertidumbre y restricciones duras','G8'),
('R37','Optimalidad','Frontera de Pareto y dominio estudiado; no óptimo global garantizado','criterio_de_investigacion','Comparación homogénea y confirmación de finalistas','G7'),
('R38','Trazabilidad','Geometría, entradas, versión, unidades, fuentes y alcance por resultado','obligatorio_metodologico','Manifiestos y reproducción','G0;G8'),
('R39','Verificación/validación','Separar chequeo numérico de contraste experimental','obligatorio_metodologico','Benchmarks, sensibilidad e incertidumbre','G2;G4;G5;G6;F'),
('R40','Presentación','CAD y videos derivados de la configuración/estados identificados','confirmado','Huellas y etiquetas de alcance','G8'),
('R41','Fabricación/mantenimiento','Tolerancias, montaje, acceso, reparabilidad y repetibilidad','abierto','Planos/BOM/procedimientos contrastados','G3;F'),
('R42','Recursos/plazo','Benchmark local; concurrencia y cómputo remoto por coste real','pendiente_medir','Calendario recalibrado con coste por caso','G0'),
('R43','Investigación pausada','El plan no reanuda solvers ni crea objetivo persistente','confirmado_estado','Autorización de ejecución y auditoría antes de reanudar','G0'),
('R44','Aviónica/comunicación','Sensores, cómputo, enlace/telemetría, latencia, EMC y pérdida de localización','abierto','Presupuesto eléctrico/datos; vibración, observabilidad y modos degradados','G3;G6;G8;F'),
('R45','Integridad del rotor','Retención de pala/buje y evaluación de fragmentos; conducto no garantiza contención','abierto_critico','Cargas centrífugas/fatiga y evidencia de protección en dominio declarado','G5;F'),
]

# Task tuple: id, gate, priority, dependencies, requirement IDs, action, output, acceptance, execution type.
tasks = [
('T01','G0','P0','','R38','Inventariar documentación y scripts','INVENTARIO-DOCUMENTAL.csv','547 entradas indexadas con huella; catálogo no equivale a validación','computacional'),
('T02','G0','P0','T01','R01;R03;R38;R43','Reconciliar decisiones y estados históricos','registro_decisiones_y_sustituciones','Arquitectura A inequívoca; geometría y alcance por resultado','revision'),
('T03','G0','P0','T01','R42','Comprobar aplicaciones, rutas y versiones','entorno_reproducible','Blender/FreeCAD/ParaView y dependencias con prueba registrada','mixto'),
('T04','G0','P0','T02','R02;R05;R06;R07;R08;R09;R11;R12;R13;R14;R15;R34','Fijar métricas y dominio de misión','requisitos_revision_1','Objetivos/escenarios/pendientes diferenciados; sin bajar objetivos en silencio','decision'),
('T05','G0','P0','T03;T04','R39;R42','Seleccionar benchmarks y medir coste pequeño autorizado','benchmark_y_presupuesto_calculo','Datos primarios recuperables y coste real; no campaña masiva inicial','computacional'),
('T06','G1','P0','T04','R02;R11;R12;R24;R25','Cribar masa, área, potencia y energía en 2/5/10 kg','presupuestos_preliminares','Misma misión y contabilidad completa; rangos explícitos','computacional'),
('T07','G0','P0','T02;T04','R03;R16;R38','Crear configuración única para CAD/física/render','configuracion_canonica','Unidades/ejes/IDs y conversión de todos los consumidores comprobados','computacional'),
('T08','G1','P0','T07','R16;R25;R26;R27','Auditar A07 y distinguir piezas de reservas','auditoria_cad_y_espacio','Huecos reales, solapes, espesores visuales y componentes ausentes identificados','computacional'),
('T09','G1','P0','T06;T08','R12;R24;R25','Montar BOM de masas e inercias con incertidumbre','bom_y_tensor_preliminar','Ningún desconocido tratado como cero; estados de combustible/batería','computacional'),
('T10','G2','P0','T05;T06','R17;R18;R39','Contrastar rotor/ventilador publicado y cribado de módulo propio','benchmark_rotor_y_predimensionado','Cobertura de polar/Re/Mach y diferencias de instalación declaradas','computacional'),
('T11','G2','P0','T08;T10','R18;R19;R20','Preparar fluido del módulo y métodos por fidelidad','casos_modulo_identificados','Dominio, rotor/disco, paredes y contornos coherentes','computacional'),
('T12','G2','P0','T11','R19;R20;R24;R39','Calcular mapa instalado de seis cargas y potencia','mapa_modulo_con_incertidumbre','Balances y sensibilidad; reacción de paredes incluida; extrapolación marcada','computacional'),
('T13','G2','P0','T12','R20;R21','Identificar respuesta y límites temporales del módulo','modelo_respuesta_condicionado','Comando-respuesta y demanda de servo; sin equiparar fuerza vectorial a ángulo mecánico','computacional'),
('T14','G2','P0','T09;T12;T13','R07;R08;R09;R17;R24;R25','Decidir factibilidad del módulo integrado','decision_modulo','Capacidad útil simultánea compatible con presupuesto o rediseño explícito','decision'),
('T15','G3','P0','T06;T08','R22;R23;R24;R25','Comparar integración propulsiva axial','opciones_propulsion_instalada','Motor/ruta/toma/escape/masa/energía y procedencia del empuje neto','computacional'),
('T16','G3','P0','T08;T12','R21;R26;R41','Sintetizar y alojar mecanismos de tapas/álabes','cad_mecanismos','Guías, transmisiones, cierres, sensores, cableado y recorridos con tolerancias','mixto'),
('T17','G3','P0','T14;T15;T16','R16;R17;R22;R23;R26;R41','Consolidar CAD funcional paramétrico','revision_funcional_identificada','Todos los componentes e interfaces reales o incertidumbre explícita; montaje revisado','computacional'),
('T18','G3','P0','T09;T17','R02;R24;R25','Cerrar masa/CG/inercia y energía de la integración','presupuesto_integrado','Cabe con reserva acordada y consume dentro del dominio; sin doble cuenta','computacional'),
('T19','G4','P1','T05;T08','R16;R28;R29','Cribar envolvente exterior y variables de forma','sensibilidad_exterior_preliminar','Determina casos decisivos sin heredarlos como resultado instalado','computacional'),
('T20','G4','P0','T17;T19','R16;R28;R39','Generar mallas de aceptación de configuración instalada','familia_mallas_identificada','Tratamiento de pared y geometría conservados; calidad documentada','computacional'),
('T21','G4','P0','T05','R28;R29;R39','Contrastar solver compresible con experimento recuperable','benchmark_compresible','Comparación de presión/cargas y diferencias de condiciones declaradas','computacional'),
('T22','G4','P0','T20;T21','R05;R28;R29','Resolver avance base 600/1000 y puntos intermedios decisivos','mapa_avance_base','Convergencia, balances y sensibilidad; fricción/base/tomas contabilizadas','computacional'),
('T23','G4','P0','T22','R09;R27;R28;R33','Resolver incidencia/deriva/deflexión y trimado','mapa_aerodinamico_control','Fuerzas, momentos, derivadas y estabilidad del conjunto con dominio conocido','computacional'),
('T24','G4','P0','T15;T23','R05;R22;R23;R24','Cerrar empuje-arrastre y aceleración/consumo','balance_avance_instalado','Empuje neto y potencia coinciden con la misma geometría/condición','computacional'),
('T25','G4','P0','T12;T13;T16;T24','R21;R26;R30;R33','Evaluar transición y transferencia de control','envolvente_transicion','Autoridad, tasas y potencia continuas; puertas/flujo oblicuo y fallo definidos','computacional'),
('T26','G5','P0','T18;T23;T25','R21;R26;R27;R31;R32','Construir envolvente de cargas y temperaturas','casos_carga_trazados','Presión distribuida, equipos, rotor y maniobra separados y combinados justificadamente','computacional'),
('T27','G5','P1','T08;T09','R31;R39','Seleccionar materiales y verificar modelos estructurales simples','benchmarks_y_materiales','Propiedades trazables; modelos analíticos y límites claros','computacional'),
('T28','G5','P0','T26;T27','R25;R31;R41;R45','Dimensionar estructura, uniones y modos libres','FEM_y_presupuesto_actualizado','Convergencia y márgenes; masa/rigidez devueltas a configuración','computacional'),
('T29','G5','P0','T12;T13;T16;T26','R21;R26;R27','Dimensionar ejes, cojinetes, actuadores y cierres','seleccion_o_especificacion_mecanica','Par/tasa/temperatura/vida y holgura bajo carga; no servo sin carga','mixto'),
('T30','G5','P0','T23;T28;T29','R31;R32','Evaluar aeroelasticidad y restricciones de envolvente','evaluacion_flutter_divergencia','No declarar aprobación por frecuencia de viga; incertidumbre y límites explícitos','especializado'),
('T31','G6','P0','T13;T18;T23;T24;T29','R07;R09;R30;R33','Acoplar planta identificada al 6DOF','simulador_predictivo_condicionado','Mapas/masa/tasas/potencia y parámetros con procedencia; verificadores pasan','computacional'),
('T32','G6','P0','T31','R06;R07;R09;R10;R30;R33','Desarrollar control base de maniobras y transición','control_base_y_metricas','Errores/tiempos/saturaciones dentro de requisitos fijados','computacional'),
('T33','G6','P0','T30;T32','R13;R14;R33;R34;R44','Ensayar incertidumbre, perturbaciones y fallos declarados','envolvente_robusta','Pruebas fuera de ajuste y márgenes superiores a incertidumbre identificada','computacional'),
('T34','G7','P0','T14;T18;T23;T30;T33','R04;R09;R24;R25;R37','Optimizar finalistas y confirmar mejoras','Pareto_y_decision','Misma misión; diferencia mayor que incertidumbre o empate técnico declarado','computacional'),
('T35','G7','P0','T34','R02;R17;R25','Recalcular versiones 2 y 10 con hardware propio de escala','variantes_independientes','No simple semejanza geométrica; regreso a G2-G6 donde corresponda','computacional'),
('T36','G7','P0','T34;T35','R38;R39','Ejecutar regresión integrada de revisiones finales','regresion_y_matriz_cobertura','Cambios de masa/forma/mapas propagan a todos los resultados afectados','computacional'),
('T37','G8','P1','T31','R35;R44','Integrar estimación de estado y sensores','modelo_sensores_estimador','Ruido, retardos, observabilidad y estados degradados definidos','computacional'),
('T38','G8','P1','T33;T37','R35;R44','Añadir navegación y supervisor de modos','autonomia_base','Misión con límites y recuperación; evaluación separada de ajuste','computacional'),
('T39','G8','P2','T38','R36','Evaluar ML solo si aporta una función y ventaja medibles','comparativa_ML_o_decision_omitir','Base vs ML con datos separados y restricciones; omisión no bloquea producto','opcional'),
('T40','G8','P1','T36;T38','R35;R38;R39','Comprobar software en bucle y repetibilidad','SIL_y_paquete_reproducible','Estados, estimador y mandos realmente acoplados; no solo animación','computacional'),
('T41','G8','P0','T36;T38;T40','R38;R40;R41','Entregar paquete digital y visualización de estados calculados','entrega_digital','BOM/CAD/mapas/control/pruebas/limitaciones enlazados; alcance declarado','revision'),
('T42','F','P1','T05;T06','R18;R21;R31;R39','Especificar banco, instrumentación y presupuesto de ensayos','plan_ensayos_fisicos','Rangos, calibración, incertidumbre, instalaciones y revisión especializada','planificacion'),
('T43','F','P0','T14;T42','R18;R19;R20;R21;R24;R39','Contrastar módulo propio en banco','mapas_medidos_y_respuesta','Ensayos reproducibles y actualización de mapas; adelantar si hay medios','fisico'),
('T44','F','P0','T28;T29;T42','R14;R15;R26;R31;R41;R44;R45','Contrastar estructura, térmico y mecanismos','ensayos_componentes','Cargas/temperaturas/vida y discrepancias documentadas','fisico'),
('T45','F','P0','T33;T43;T44','R06;R07;R09;R34;R35','Probar vuelo restringido y correlacionar control','ensayos_baja_velocidad','Envolvente inicial y recuperación comprobadas con medios apropiados','fisico'),
('T46','F','P0','T24;T30;T45','R05;R28;R30;R31;R32','Ampliar envolvente en instalaciones adecuadas','ensayos_transicion_avance','Progresión instrumentada y criterios de parada; no salto directo al máximo','fisico'),
('T47','F','P0','T43;T44;T46','R38;R39','Actualizar modelos con datos físicos y repetir regresión','correlacion_modelo_experimento','Errores y límites identificados; evidencia por variante','mixto'),
('T48','F','P1','T41;T47','R04;R14;R15;R35;R40;R41','Cerrar diseño fabricable, vida útil, mantenimiento y cumplimiento','producto_documentado','Revisión especializada, repetibilidad y dominio de uso contrastado','fisico_y_documental'),
]

risks = [
('K01','critica','R19;R33','Vectorización útil menor que cono supuesto','Carga local y reacción total discrepan o región útil insuficiente','Medir/calcular módulo completo; rediseñar canales y disposición','T12;T14'),
('K02','critica','R24;R25','Potencia/masa/energía incompatibles','BOM excede masa o pack/motor no entrega potencia','Iterar área, integración y misión; conservar requisitos originales visibles','T06;T18'),
('K03','critica','R22;R23','Instalación axial no cabe o pierde empuje','Reserva de tubo insuficiente; distorsión/temperatura/CG inaceptables','Resolver motor+toma+escape con planos y mapas','T15;T24'),
('K04','critica','R28;R29','Arrastre o separación en avance mayor que hipótesis','Solución compresible aceptada excede presupuesto de empuje','Optimizar forma/tomas y reevaluar velocidad factible','T22;T24'),
('K05','critica','R26;R30','Tapas no funcionan bajo carga o se atascan','Interferencia, par excesivo o asimetría de apertura','Diseñar mecanismo y cierres; simular fallo y transición','T16;T25;T29'),
('K06','critica','R31;R32','Flutter, pérdida de rigidez o fallo local','Sensibilidad a holgura/temperatura o modo cercano a excitación','Aeroelasticidad y redimensionamiento con masa devuelta al modelo','T28;T30'),
('K07','alta','R21;R33','Control consume toda la reserva nominal','Saturación o margen comparable a incertidumbre; ejemplo 34.92/35°','Identificar mapa y límites; escenarios robustos; no aprobar por seguimiento nominal','T13;T33'),
('K08','alta','R38;R39','Mezcla de geometrías/datos históricos','Masa, estaciones, número de rotores o método no coinciden','Configuración y huellas únicas; resultados incompatibles separados','T02;T07;T36'),
('K09','alta','R02;R17','Escalado algebraico no realizable','Rotor/motor/estructura cambia de régimen al variar masa','Redimensionar cada variante y validar mapas propios','T35'),
('K10','alta','R13;R14','Operación ambiental mal definida','Petición de cualquier condición sin rangos o fallos de ingestión','Definir envolvente y ensayos; no prometer inmunidad universal','T04;T33;T44'),
('K11','alta','R35;R36','ML explota errores del simulador','Buen entrenamiento y fallo en estados fuera de ajuste','Base interpretable, datos separados y recuperación independiente','T38;T39'),
('K12','alta','R42','Coste computacional y herramientas bloquean ruta','Caso caro sin convergencia; apps no arrancan; RAM insuficiente','Benchmark, diagnóstico con límite de coste y cómputo remoto si se justifica','T03;T05'),
('K13','alta','R39','Convergencia confundida con validez física','Campos finitos o End usados como aceptación','Criterios predefinidos, balances, sensibilidad y contraste','T05;T12;T22'),
('K14','alta','R38;R40','Render presentado como vuelo validado','Trayectoria impuesta o control/fluido ausentes sin etiqueta','Separar visualización y predicción; rastrear fuente de estados','T41'),
('K15','alta','R41','Producto visualmente terminado pero no fabricable','Faltan interfaces, montaje, tolerancias o mantenimiento','Cerrar mecánica/BOM/planos con revisión de fabricación','T17;T48'),
('K16','alta','R31;R34','Fallos de rotor o alimentación sin recuperación','La autoridad remanente no cubre gravedad/momentos','Definir el requisito; comprobar dominio de fallos y modos de recuperación','T04;T33;T45'),
('K17','alta','R44;R45','Aviónica/rotor afectados por vibración o integración','Sensores saturados, pérdida de enlace, interferencia o retención insuficiente','Presupuesto de vibración/EMC/datos; analizar buje, pala y protección','T28;T33;T37;T44'),
]

def write(name, fields, rows):
    assert all(len(row) == len(fields) for row in rows), name
    with (P/name).open('w', newline='') as out:
        writer = csv.writer(out)
        writer.writerow(fields)
        writer.writerows(rows)

write('REQUISITOS.csv', ['id','frente','requisito_o_variable','estado_inicial','aceptacion','hitos'], requirements)
task_rows = []
for task in tasks:
    if task[0] == 'T01':
        status, evidence = 'completado_inventario', 'INVENTARIO-DOCUMENTAL.csv;INVENTARIO-RESUMEN.json'
    elif task[0] == 'T02':
        status, evidence = 'parcial_registro_consolidado', 'PLAN-MAESTRO.md;../modelos_integrados/DECISION-ARQUITECTURA.md'
    elif task[0] == 'T03':
        status, evidence = 'parcial_aplicaciones_pendientes', '../integracion_apps/LEEME.md'
    elif task[0] == 'T04':
        status, evidence = 'propuesta_por_cuantificar', 'REQUISITOS.csv'
    elif task[0] == 'T39':
        status, evidence = 'opcional_no_bloqueante', ''
    else:
        status, evidence = 'pendiente', ''
    task_rows.append((*task, status, evidence))
write('TRABAJO.csv', ['id','hito','prioridad','depende_de','requisitos','tarea','salida','criterio_aceptacion','tipo_ejecucion','estado_inicial','evidencia_inicial'], task_rows)
write('RIESGOS.csv', ['id','severidad_juicio','requisitos','riesgo','senal_temprana','respuesta','tareas'], risks)

ids = {t[0] for t in tasks}
reqids = {r[0] for r in requirements}
assert len(ids) == len(tasks) and len(reqids) == len(requirements)
graph = {}
for task in tasks:
    deps = [d for d in task[3].split(';') if d]
    assert set(deps) <= ids and task[0] not in deps
    assert set(task[4].split(';')) <= reqids
    graph[task[0]] = deps
seen, visiting = set(), set()
def visit(node):
    assert node not in visiting, 'Dependency cycle: ' + node
    if node in seen:
        return
    visiting.add(node)
    for dep in graph[node]:
        visit(dep)
    visiting.remove(node)
    seen.add(node)
for node in graph:
    visit(node)
for risk in risks:
    assert set(risk[2].split(';')) <= reqids
    assert set(risk[6].split(';')) <= ids
coverage = {req: [t[0] for t in tasks if req in t[4].split(';')] for req in sorted(reqids)}
assert all(coverage.values())
required_files = ['PLAN-MAESTRO.md','INVENTARIO-DOCUMENTAL.csv','INVENTARIO-RESUMEN.json','REQUISITOS.csv','TRABAJO.csv','RIESGOS.csv']
assert all((P/f).is_file() for f in required_files)
summary = dict(date='2026-11-02',requirements=len(requirements),tasks=len(tasks),risks=len(risks),unique_ids=True,
               dependency_graph_acyclic=True,all_requirement_ids_linked_to_tasks=True,requirement_coverage=coverage,
               required_plan_files_present=True,scope='Planning register consistency only; no engineering acceptance or physical validation.')
(P/'VERIFICACION-PLAN.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps({k:v for k,v in summary.items() if k!='requirement_coverage'},indent=2,ensure_ascii=False))
