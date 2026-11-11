#!/usr/bin/env python3
"""
analizar_dependencias.py
========================
Script reproducible para cruzar las 48 tareas del Plan Maestro de Investigación
Aeronáutica con su estado de ejecución y dependencias en el grafo DAG.

Identifica:
1. Tareas computacionales con dependencias abiertas (sin declarar cierres).
2. Pasos paralelizables de preparación.
3. Tareas físicas y de contraste experimental.
4. Prioridades P0 y dependencias críticas.
5. Validación de integridad del grafo: detección de dependencias inexistentes y ciclos.

Cumple con las restricciones de ejecución aislada en sandbox, conservación de
unidades, fuentes canónicas y separación entre datos medidos, supuestos y cálculos.
"""

import csv
import json
import os
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

# Rutas predeterminadas relativas a la raíz de ejecución
WORKSPACE_DIR = Path(__file__).resolve().parent.parent
ENTRADAS_DIR = WORKSPACE_DIR / "entradas" / "investigacion-aeronautica"
TRABAJO_PATH = ENTRADAS_DIR / "plan_maestro" / "TRABAJO.csv"
ESTADO_PATH = ENTRADAS_DIR / "ejecucion" / "ESTADO-TAREAS.csv"
SALIDAS_DIR = WORKSPACE_DIR / "salidas"

# Conjuntos de definición técnica canónica
PREPARACION_IDS = {
    "T01",  # Inventariar documentación y scripts (G0, base documental)
    "T03",  # Comprobar aplicaciones, rutas y versiones (G0, entorno computacional)
    "T05",  # Seleccionar benchmarks y medir coste pequeño autorizado (G0, calibración)
    "T06",  # Cribar masa, área, potencia y energía en 2/5/10 kg (G1, screening preliminar)
    "T07",  # Crear configuración única para CAD/física/render (G0, setup canónico)
    "T08",  # Auditar A07 y distinguir piezas de reservas (G1, auditoría geométrica)
    "T09",  # Montar BOM de masas e inercias con incertidumbre (G1, BOM preliminar)
    "T10",  # Contrastar rotor/ventilador publicado y cribado de módulo propio (G2, benchmark polar)
    "T11",  # Preparar fluido del módulo y métodos por fidelidad (G2, preparación CFD)
    "T16",  # Sintetizar y alojar mecanismos de tapas/álabes (G3 - P3 empaquetado preliminar)
    "T19",  # Cribar envolvente exterior y variables de forma (G4 - P4 screening exterior)
    "T21",  # Contrastar solver compresible con experimento recuperable (G4 - P4 benchmark SU2)
    "T26",  # Construir envolvente de cargas y temperaturas (G5 - P5 cargas centrífugas)
    "T27",  # Seleccionar materiales y verificar modelos estructurales simples (G5 - P5 materiales)
    "T31",  # Acoplar planta identificada al 6DOF (G6 - dinámica de vuelo preliminar)
    "T42",  # Especificar banco, instrumentación y presupuesto de ensayos (F - planificación ensayos)
}

FISICAS_IDS = {
    "T42": "planificacion_banco_ensayos",
    "T43": "ensayo_fisico_banco_modulo",
    "T44": "ensayo_fisico_estructura_termico_mecanismos",
    "T45": "ensayo_fisico_vuelo_restringido",
    "T46": "ensayo_fisico_envolvente_ampliada",
    "T47": "correlacion_mixta_modelo_experimento",
    "T48": "producto_fabricable_cumplimiento",
}


def cargar_datos(
    ruta_trabajo: Path = TRABAJO_PATH, ruta_estado: Path = ESTADO_PATH
) -> Tuple[List[Dict[str, str]], Dict[str, Dict[str, str]]]:
    """Carga los archivos canónicos de trabajo y estado asegurando integridad."""
    if not ruta_trabajo.exists():
        raise FileNotFoundError(f"No se encontró el archivo canónico de trabajo: {ruta_trabajo}")
    if not ruta_estado.exists():
        raise FileNotFoundError(f"No se encontró el archivo canónico de estado: {ruta_estado}")

    with open(ruta_trabajo, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        trabajo = list(reader)

    with open(ruta_estado, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        estado = {r["id"].strip(): r for r in reader}

    if len(trabajo) != 48:
        raise ValueError(f"Se esperaban 48 tareas en TRABAJO.csv, se encontraron {len(trabajo)}")
    if len(estado) != 48:
        raise ValueError(f"Se esperaban 48 tareas en ESTADO-TAREAS.csv, se encontraron {len(estado)}")

    return trabajo, estado


def parsear_dependencias(raw_deps: str) -> List[str]:
    """Parsea la cadena delimitada por punto y coma de dependencias."""
    if not raw_deps or not raw_deps.strip():
        return []
    return [d.strip() for d in raw_deps.split(";") if d.strip()]


def validar_dependencias_existentes(
    tareas: List[Dict[str, str]]
) -> Dict[str, List[str]]:
    """Identifica cualquier tarea que dependa de IDs no existentes en el conjunto."""
    todos_los_ids = {r["id"].strip() for r in tareas}
    errores = defaultdict(list)
    for r in tareas:
        tid = r["id"].strip()
        deps = parsear_dependencias(r.get("depende_de", ""))
        for d in deps:
            if d not in todos_los_ids:
                errores[tid].append(d)
    return dict(errores)


def detectar_ciclos(
    tareas: List[Dict[str, str]]
) -> Tuple[bool, List[str], List[str]]:
    """
    Detecta si existen ciclos en el grafo de dependencias mediante el algoritmo de Kahn
    y búsqueda de ciclos por coloración DFS.
    
    Retorna:
    - tiene_ciclo: booleano
    - orden_topologico: lista con orden si no hay ciclos
    - ciclo_detectado: lista con la ruta del ciclo si existe
    """
    todos_los_ids = [r["id"].strip() for r in tareas]
    adj = defaultdict(list)  # dep -> dependientes (arista dirigida dep -> task)
    in_degree = {tid: 0 for tid in todos_los_ids}
    grafo_deps = defaultdict(list)  # task -> deps directas

    for r in tareas:
        tid = r["id"].strip()
        deps = parsear_dependencias(r.get("depende_de", ""))
        grafo_deps[tid] = deps
        for d in deps:
            if d in in_degree:
                adj[d].append(tid)
                in_degree[tid] += 1

    # Algoritmo de Kahn
    queue = deque([tid for tid, deg in in_degree.items() if deg == 0])
    orden_topologico = []

    while queue:
        curr = queue.popleft()
        orden_topologico.append(curr)
        for vecino in adj[curr]:
            in_degree[vecino] -= 1
            if in_degree[vecino] == 0:
                queue.append(vecino)

    tiene_ciclo = len(orden_topologico) != len(todos_los_ids)
    ciclo_detectado = []

    if tiene_ciclo:
        # Encontrar el ciclo específico mediante DFS de 3 colores
        # 0 = sin visitar, 1 = en proceso (gris), 2 = procesado (negro)
        color = {tid: 0 for tid in todos_los_ids}
        padre = {}

        def dfs_ciclo(nodo: str, path: List[str]) -> bool:
            color[nodo] = 1
            path.append(nodo)
            for d in grafo_deps[nodo]:
                if color.get(d) == 1:
                    # Ciclo encontrado
                    idx = path.index(d)
                    ciclo_detectado.extend(path[idx:] + [d])
                    return True
                elif color.get(d) == 0:
                    if dfs_ciclo(d, path):
                        return True
            color[nodo] = 2
            path.pop()
            return False

        for tid in todos_los_ids:
            if color[tid] == 0:
                if dfs_ciclo(tid, []):
                    break

    return tiene_ciclo, orden_topologico, ciclo_detectado


def calcular_niveles_y_ancestros(
    tareas: List[Dict[str, str]]
) -> Tuple[Dict[str, int], Dict[str, Set[str]], Dict[str, Set[str]]]:
    """Calcula el nivel en el DAG (camino más largo desde la raíz), ancestros y descendientes."""
    deps_map = {
        r["id"].strip(): set(parsear_dependencias(r.get("depende_de", "")))
        for r in tareas
    }

    ancestros = defaultdict(set)

    def resolver_ancestros(tid: str) -> Set[str]:
        if tid in ancestros:
            return ancestros[tid]
        res = set(deps_map[tid])
        for d in deps_map[tid]:
            res.update(resolver_ancestros(d))
        ancestros[tid] = res
        return res

    for tid in deps_map:
        resolver_ancestros(tid)

    # Descendientes (inverso de ancestros)
    descendientes = defaultdict(set)
    for tid, ancs in ancestros.items():
        for a in ancs:
            descendientes[a].add(tid)

    # Nivel DAG (longitud de camino más largo desde la raíz)
    nivel = {}

    def resolver_nivel(tid: str) -> int:
        if tid in nivel:
            return nivel[tid]
        if not deps_map[tid]:
            nivel[tid] = 0
            return 0
        l = 1 + max(resolver_nivel(d) for d in deps_map[tid])
        nivel[tid] = l
        return l

    for tid in deps_map:
        resolver_nivel(tid)

    return nivel, dict(ancestros), dict(descendientes)


def cruzar_y_clasificar(
    trabajo: List[Dict[str, str]],
    estado: Dict[str, Dict[str, str]]
) -> List[Dict[str, Any]]:
    """
    Cruza cada tarea con su estado, calcula dependencias abiertas bajo el principio
    estricto 'sin declarar cierres', y asigna las banderas requeridas.
    """
    nivel_dag, ancestros, descendientes = calcular_niveles_y_ancestros(trabajo)
    todos_los_ids = {r["id"].strip() for r in trabajo}

    # Determinación de tareas concurrentes (paralelizables en estructura DAG):
    # Dos tareas A y B son concurrentes si ninguna es ancestro de la otra.
    concurrentes = defaultdict(set)
    for tid_a in todos_los_ids:
        for tid_b in todos_los_ids:
            if tid_a != tid_b:
                if (tid_b not in ancestros.get(tid_a, set()) and
                    tid_a not in ancestros.get(tid_b, set())):
                    concurrentes[tid_a].add(tid_b)

    registros = []
    for r in trabajo:
        tid = r["id"].strip()
        est = estado.get(tid, {})
        deps = parsear_dependencias(r.get("depende_de", ""))
        tipo_ejecucion = r.get("tipo_ejecucion", "").strip()
        prioridad = r.get("prioridad", "").strip()
        hito = r.get("hito", "").strip()
        estado_act = est.get("estado_actual", "").strip()
        pendiente_limite = est.get("pendiente_o_limite", "").strip()

        # Principio "Sin declarar cierres":
        # Ninguna tarea se considera cerrada de manera canónica/definitiva porque
        # todas presentan límites, snapshot inicial, o resultados parciales.
        # Por tanto, todas las dependencias upstream permanecen ABIERTAS para fines
        # de cierre técnico formal.
        deps_abiertas = list(deps)
        num_deps = len(deps)
        num_deps_abiertas = len(deps_abiertas)

        # 1. Tarea computacional
        es_computacional = (tipo_ejecucion == "computacional")

        # 1.1 Tarea computacional con dependencias abiertas
        es_computacional_abierta = es_computacional and (num_deps_abiertas > 0)

        # 2. Paso de preparación
        es_paso_preparacion = (tid in PREPARACION_IDS)

        # 2.1 Paralelizable (tiene al menos una tarea concurrente independiente en el DAG)
        es_paralelizable = len(concurrentes[tid]) > 0

        # 2.2 Paso paralelizable de preparación
        es_preparacion_paralelizable = es_paso_preparacion and es_paralelizable

        # 3. Tarea física o de contraste experimental
        es_tarea_fisica = (tipo_ejecucion in ("fisico", "fisico_y_documental") or hito == "F")
        subtipo_fisica = FISICAS_IDS.get(tid, "no_aplica")

        # Bloqueo técnico: tiene dependencias abiertas y está pendiente o sin mapa cerrado
        bloqueada = (num_deps_abiertas > 0) and (estado_act == "pendiente_ejecucion_plan")

        reg = {
            "id": tid,
            "hito": hito,
            "prioridad": prioridad,
            "tarea": r.get("tarea", "").strip(),
            "tipo_ejecucion": tipo_ejecucion,
            "estado_actual": estado_act,
            "estado_inicial": r.get("estado_inicial", "").strip(),
            "depende_de": ";".join(deps),
            "num_dependencias": num_deps,
            "dependencias_abiertas": ";".join(deps_abiertas),
            "num_dependencias_abiertas": num_deps_abiertas,
            "es_computacional": es_computacional,
            "es_computacional_abierta": es_computacional_abierta,
            "es_paso_preparacion": es_paso_preparacion,
            "es_paralelizable": es_paralelizable,
            "es_preparacion_paralelizable": es_preparacion_paralelizable,
            "es_tarea_fisica": es_tarea_fisica,
            "subtipo_fisica": subtipo_fisica,
            "nivel_dag": nivel_dag.get(tid, 0),
            "num_concurrentes": len(concurrentes[tid]),
            "bloqueada_por_dependencias": bloqueada,
            "criterio_aceptacion": r.get("criterio_aceptacion", "").strip(),
            "salida_esperada": r.get("salida", "").strip(),
            "evidencia_actual": est.get("evidencia", "").strip(),
            "pendiente_o_limite": pendiente_limite,
            "fecha_estado": est.get("fecha", "").strip(),
        }
        registros.append(reg)

    return registros


def exportar_csvs(registros: List[Dict[str, Any]], destino_dir: Path = SALIDAS_DIR) -> Dict[str, Path]:
    """Genera el CSV maestro reproducible y vistas CSV especializadas en salidas/."""
    destino_dir.mkdir(parents=True, exist_ok=True)
    rutas_generadas = {}

    # 1. Matriz Maestra Completa (48 tareas)
    ruta_maestra = destino_dir / "matriz_tareas_dependencias.csv"
    campos_maestra = list(registros[0].keys())
    with open(ruta_maestra, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos_maestra)
        writer.writeheader()
        writer.writerows(registros)
    rutas_generadas["matriz_maestra"] = ruta_maestra

    # 2. Tareas Computacionales con Dependencias Abiertas
    ruta_comp_abiertas = destino_dir / "tareas_computacionales_abiertas.csv"
    regs_comp = [r for r in registros if r["es_computacional_abierta"]]
    with open(ruta_comp_abiertas, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos_maestra)
        writer.writeheader()
        writer.writerows(regs_comp)
    rutas_generadas["computacionales_abiertas"] = ruta_comp_abiertas

    # 3. Pasos Paralelizables de Preparación
    ruta_prep_paralelas = destino_dir / "pasos_preparacion_paralelizables.csv"
    regs_prep = [r for r in registros if r["es_preparacion_paralelizable"]]
    with open(ruta_prep_paralelas, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos_maestra)
        writer.writeheader()
        writer.writerows(regs_prep)
    rutas_generadas["preparacion_paralelizables"] = ruta_prep_paralelas

    # 4. Tareas Físicas
    ruta_fisicas = destino_dir / "tareas_fisicas.csv"
    regs_fisicas = [r for r in registros if r["es_tarea_fisica"]]
    with open(ruta_fisicas, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos_maestra)
        writer.writeheader()
        writer.writerows(regs_fisicas)
    rutas_generadas["tareas_fisicas"] = ruta_fisicas

    # 5. Resumen de Prioridades P0
    ruta_p0 = destino_dir / "resumen_prioridades_P0.csv"
    regs_p0 = [r for r in registros if r["prioridad"] == "P0"]
    with open(ruta_p0, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos_maestra)
        writer.writeheader()
        writer.writerows(regs_p0)
    rutas_generadas["prioridades_p0"] = ruta_p0

    return rutas_generadas


def calcular_estadisticas(registros: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcula las métricas cuantitativas clave de la ejecución."""
    total = len(registros)
    p0 = [r for r in registros if r["prioridad"] == "P0"]
    p1 = [r for r in registros if r["prioridad"] == "P1"]
    p2 = [r for r in registros if r["prioridad"] == "P2"]

    comp_abiertas = [r for r in registros if r["es_computacional_abierta"]]
    comp_abiertas_p0 = [r for r in comp_abiertas if r["prioridad"] == "P0"]
    comp_abiertas_p1 = [r for r in comp_abiertas if r["prioridad"] == "P1"]

    prep_paralelas = [r for r in registros if r["es_preparacion_paralelizable"]]
    prep_paralelas_p0 = [r for r in prep_paralelas if r["prioridad"] == "P0"]
    prep_paralelas_p1 = [r for r in prep_paralelas if r["prioridad"] == "P1"]

    fisicas = [r for r in registros if r["es_tarea_fisica"]]
    fisicas_p0 = [r for r in fisicas if r["prioridad"] == "P0"]
    fisicas_p1 = [r for r in fisicas if r["prioridad"] == "P1"]

    # Identificar tareas P1 que son prerequisito directo de tareas P0
    p0_ids = {r["id"] for r in p0}
    p1_bloquean_p0 = defaultdict(list)
    for r in p0:
        deps = parsear_dependencias(r["depende_de"])
        for d in deps:
            # Buscar si d es P1
            d_reg = next((x for x in registros if x["id"] == d), None)
            if d_reg and d_reg["prioridad"] == "P1":
                p1_bloquean_p0[d].append(r["id"])

    stats = {
        "total_tareas": total,
        "conteo_p0": len(p0),
        "conteo_p1": len(p1),
        "conteo_p2": len(p2),
        "total_computacionales": sum(1 for r in registros if r["es_computacional"]),
        "computacionales_abiertas_total": len(comp_abiertas),
        "computacionales_abiertas_p0": len(comp_abiertas_p0),
        "computacionales_abiertas_p1": len(comp_abiertas_p1),
        "preparacion_paralelizable_total": len(prep_paralelas),
        "preparacion_paralelizable_p0": len(prep_paralelas_p0),
        "preparacion_paralelizable_p1": len(prep_paralelas_p1),
        "fisicas_total": len(fisicas),
        "fisicas_p0": len(fisicas_p0),
        "fisicas_p1": len(fisicas_p1),
        "p1_que_desbloquean_p0": dict(p1_bloquean_p0),
    }
    return stats


def ejecutar_analisis_completo() -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, Path]]:
    """Ejecuta el pipeline completo y valida integridad del grafo."""
    print("=" * 70)
    print("ANÁLISIS DE DEPENDENCIAS Y ESTADO - PLAN MAESTRO AERONÁUTICO")
    print("=" * 70)

    # 1. Cargar datos canónicos
    trabajo, estado = cargar_datos()
    print(f"[OK] Cargadas 48 tareas desde {TRABAJO_PATH.name} y {ESTADO_PATH.name}")

    # 2. Validación de dependencias inexistentes
    errores_deps = validar_dependencias_existentes(trabajo)
    if errores_deps:
        print(f"[ALERTA] Dependencias inexistentes detectadas: {errores_deps}")
    else:
        print("[OK] Verificación de dependencias: 0 referencias inexistentes o huérfanas.")

    # 3. Detección de ciclos
    tiene_ciclo, orden, ciclo = detectar_ciclos(trabajo)
    if tiene_ciclo:
        print(f"[ERROR] ¡Ciclo detectado en el grafo!: {' -> '.join(ciclo)}")
    else:
        print(f"[OK] Grafo verificado como DAG acíclico estricto (48 nodos ordenables).")

    # 4. Cruce y clasificación
    registros = cruzar_y_clasificar(trabajo, estado)
    print(f"[OK] Clasificadas las 48 tareas bajo el principio 'sin declarar cierres'.")

    # 5. Exportar CSVs
    rutas = exportar_csvs(registros)
    print(f"[OK] Generados {len(rutas)} archivos CSV reproducibles en {SALIDAS_DIR}/:")
    for k, v in rutas.items():
        print(f"     - {k:28}: {v.name}")

    # 6. Estadísticas clave
    stats = calcular_estadisticas(registros)
    print("\nRESUMEN CUANTITATIVO:")
    print(f"  * Total tareas evaluadas: {stats['total_tareas']}")
    print(f"  * Prioridades: P0 = {stats['conteo_p0']}, P1 = {stats['conteo_p1']}, P2 = {stats['conteo_p2']}")
    print(f"  * Tareas computacionales totales: {stats['total_computacionales']}")
    print(f"  * Computacionales con dependencias abiertas: {stats['computacionales_abiertas_total']} (P0: {stats['computacionales_abiertas_p0']}, P1: {stats['computacionales_abiertas_p1']})")
    print(f"  * Pasos paralelizables de preparación: {stats['preparacion_paralelizable_total']} (P0: {stats['preparacion_paralelizable_p0']}, P1: {stats['preparacion_paralelizable_p1']})")
    print(f"  * Tareas físicas (Hito F): {stats['fisicas_total']} (P0: {stats['fisicas_p0']}, P1: {stats['fisicas_p1']})")
    print(f"  * Tareas P1 críticas que desbloquean tareas P0: {list(stats['p1_que_desbloquean_p0'].keys())}")
    for p1_id, p0_bloqueadas in stats["p1_que_desbloquean_p0"].items():
        print(f"      - {p1_id} desbloquea -> {p0_bloqueadas}")

    print("=" * 70)
    return registros, stats, rutas


if __name__ == "__main__":
    ejecutar_analisis_completo()
