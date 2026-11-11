#!/usr/bin/env python3
"""
Script de Validacion Sintactica y Semantica de la Maquina de Estados de Transicion
Proyecto: Auditoria de Transicion y Control (Arquitectura A - Ventiladores Internos)
Valida la integridad estructural, semantica, alcanzabilidad y limites fisicos
definidos en salidas/maquina_estados.json utilizando exclusivamente la libreria estandar de Python 3.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Set

def fail(msg: str) -> None:
    print(f"[FALLO] {msg}", file=sys.stderr)

def success(msg: str) -> None:
    print(f"[OK] {msg}")

def warn(msg: str) -> None:
    print(f"[AVISO] {msg}")

def validar_archivo_json(ruta: Path) -> Dict[str, Any]:
    if not ruta.is_file():
        fail(f"El archivo {ruta} no existe.")
        sys.exit(1)
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        success(f"Archivo JSON parseado correctamente: {ruta.name}")
        return data
    except json.JSONDecodeError as e:
        fail(f"Error de sintaxis JSON en {ruta.name}: {e}")
        sys.exit(1)

def validar_metadatos_y_declaraciones(data: Dict[str, Any]) -> None:
    print("\n--- Validando Metadatos y Declaraciones de Construccion ---")
    meta = data.get("metadatos", {})
    campos_requeridos = [
        "titulo", "arquitectura_base", "referencia_geometrica",
        "declaracion_estado_construccion", "citas_fuentes_hechos"
    ]
    for c in campos_requeridos:
        if c not in meta:
            fail(f"Campo de metadatos faltante: '{c}'")
            sys.exit(1)
        success(f"Metadato presente: '{c}'")

    declaracion = meta["declaracion_estado_construccion"].lower()
    if "no se declara que las tapas o controladores esten construidos" not in declaracion:
        fail("Falta declaracion explicita de que tapas o controladores no estan construidos.")
        sys.exit(1)
    if "mapa experimental" not in declaracion or ("no existe" not in declaracion and "ni que exista" not in declaracion):
        fail("Falta declaracion explicita de inexistencia de mapa experimental.")
        sys.exit(1)
    if "pausa" not in declaracion or "no se reanudan" not in declaracion:
        fail("Falta declaracion explicita sobre retencion de solvers CFD pausados.")
        sys.exit(1)
    success("Declaraciones obligatorias de no construccion, no mapa experimental y CFD pausado validadas.")

def validar_taxonomia_datos(data: Dict[str, Any]) -> None:
    print("\n--- Validando Taxonomia de Datos (Medidos, Supuestos, Calculados, Propuestas) ---")
    tax = data.get("taxonomia_datos", {})
    categorias = ["datos_medidos", "datos_supuestos", "datos_calculados", "propuestas_tecnicas"]
    for cat in categorias:
        if cat not in tax or not isinstance(tax[cat], dict):
            fail(f"Categoria taxonomica '{cat}' ausente o invalida.")
            sys.exit(1)
        num_items = len(tax[cat])
        if num_items == 0:
            fail(f"Categoria '{cat}' vacia.")
            sys.exit(1)
        success(f"Categoria taxonomica '{cat}' verificada con {num_items} elementos.")

    for nombre, item in tax["datos_medidos"].items():
        if "unidad" not in item or "fuente" not in item or "naturaleza" not in item:
            fail(f"Item medido '{nombre}' incompleto en unidad/fuente/naturaleza.")
            sys.exit(1)
    for nombre, item in tax["datos_supuestos"].items():
        if "fuente" not in item or "naturaleza" not in item:
            fail(f"Item supuesto '{nombre}' incompleto en fuente/naturaleza.")
            sys.exit(1)
    for nombre, item in tax["datos_calculados"].items():
        if "fuente" not in item or "naturaleza" not in item:
            fail(f"Item calculado '{nombre}' incompleto en fuente/naturaleza.")
            sys.exit(1)
    for nombre, item in tax["propuestas_tecnicas"].items():
        if "naturaleza" not in item or "[PROPUESTA]" not in item["naturaleza"]:
            fail(f"Item de propuesta '{nombre}' no marcado explicitamente con [PROPUESTA].")
            sys.exit(1)
    success("Atributos de unidades, fuentes y marcas de propuesta validados en todas las entradas taxonomicas.")

def validar_grafos_y_estados(data: Dict[str, Any]) -> None:
    print("\n--- Validando Grafo de Estados, Transiciones y Precondiciones ---")
    estados_lista = data.get("estados", [])
    if not isinstance(estados_lista, list) or len(estados_lista) < 5:
        fail("Lista de estados ausente o con definicion insuficiente.")
        sys.exit(1)

    ids_estados: Set[str] = set()
    estados_map: Dict[str, Dict[str, Any]] = {}
    tipos_validos = {"ESTABLE", "TRANSITORIO", "CONTINGENCIA"}

    for est in estados_lista:
        eid = est.get("id")
        if not eid or not isinstance(eid, str):
            fail(f"Estado con ID invalido: {eid}")
            sys.exit(1)
        if eid in ids_estados:
            fail(f"ID de estado duplicado: '{eid}'")
            sys.exit(1)
        ids_estados.add(eid)
        estados_map[eid] = est

        tipo = est.get("tipo")
        if tipo not in tipos_validos:
            fail(f"Tipo invalido '{tipo}' en estado '{eid}'. Debe ser uno de {tipos_validos}")
            sys.exit(1)

        for campo in ["configuracion_actuadores", "precondiciones_entrada", "criterios_saturacion", "politica_saturacion", "transiciones_salida"]:
            if campo not in est:
                fail(f"Campo obligatorio '{campo}' faltante en estado '{eid}'")
                sys.exit(1)

        t_max = est.get("tiempo_maximo_permanencia_s")
        if tipo in {"TRANSITORIO", "CONTINGENCIA"}:
            if t_max is None or not (isinstance(t_max, (int, float)) and t_max > 0):
                fail(f"Estado '{eid}' de tipo {tipo} debe tener 'tiempo_maximo_permanencia_s' numerico y > 0.")
                sys.exit(1)
        elif tipo == "ESTABLE":
            if t_max is not None:
                warn(f"Estado estable '{eid}' define tiempo maximo ({t_max}s); comunmente es indefinido (null).")

    success(f"Total de {len(ids_estados)} estados sintacticamente validos registrados.")

    # Validar transiciones de cada estado
    total_transiciones = 0
    for eid, est in estados_map.items():
        trans = est.get("transiciones_salida", [])
        if len(trans) == 0:
            fail(f"Estado '{eid}' no tiene transiciones de salida (pozo muerto).")
            sys.exit(1)
        
        eventos_vistos: Set[str] = set()
        for tr in trans:
            ev = tr.get("evento")
            dest = tr.get("destino")
            guarda = tr.get("condicion_guarda")
            tipo_tr = tr.get("tipo_transicion")

            if not ev or not dest or not guarda or not tipo_tr:
                fail(f"Transicion incompleta en estado '{eid}': {tr}")
                sys.exit(1)
            
            if ev in eventos_vistos:
                fail(f"Determinismo violado en estado '{eid}': evento duplicado '{ev}'.")
                sys.exit(1)
            eventos_vistos.add(ev)

            if dest not in ids_estados:
                fail(f"Destino invalido '{dest}' en transicion desde '{eid}'. El estado no existe.")
                sys.exit(1)

            total_transiciones += 1

    success(f"Total de {total_transiciones} transiciones validadas contra el catalogo de estados (cierre de grafo garantizado).")

    # Validar alcanzabilidad nominal
    print("\n--- Verificando Caminos de Transicion Nominal y Retorno ---")
    if "ESTACIONARIO_ACTIVO" not in ids_estados:
        fail("Estado inicial 'ESTACIONARIO_ACTIVO' no encontrado.")
        sys.exit(1)
    if "AVANCE_PURO" not in ids_estados:
        fail("Estado de avance 'AVANCE_PURO' no encontrado.")
        sys.exit(1)

    # Camino de ida nominal: BFS
    visitados = set()
    cola = [("ESTACIONARIO_ACTIVO", ["ESTACIONARIO_ACTIVO"])]
    camino_ida = None

    while cola:
        actual, path = cola.pop(0)
        if actual == "AVANCE_PURO":
            camino_ida = path
            break
        if actual in visitados:
            continue
        visitados.add(actual)

        for tr in estados_map[actual]["transiciones_salida"]:
            if tr["tipo_transicion"] == "NOMINAL":
                cola.append((tr["destino"], path + [tr["destino"]]))

    if not camino_ida:
        fail("No existe un camino nominal completo desde ESTACIONARIO_ACTIVO hasta AVANCE_PURO.")
        sys.exit(1)
    success(f"Camino nominal de despegue/transicion a avance verificado ({len(camino_ida)} pasos): {' -> '.join(camino_ida)}")

    # Camino de regreso nominal: BFS
    visitados = set()
    cola = [("AVANCE_PURO", ["AVANCE_PURO"])]
    camino_retorno = None

    while cola:
        actual, path = cola.pop(0)
        if actual == "ESTACIONARIO_ACTIVO":
            camino_retorno = path
            break
        if actual in visitados:
            continue
        visitados.add(actual)

        for tr in estados_map[actual]["transiciones_salida"]:
            if tr["tipo_transicion"] == "NOMINAL":
                cola.append((tr["destino"], path + [tr["destino"]]))

    if not camino_retorno:
        fail("No existe un camino nominal completo desde AVANCE_PURO hasta ESTACIONARIO_ACTIVO.")
        sys.exit(1)
    success(f"Camino nominal de retorno a estacionario verificado ({len(camino_retorno)} pasos): {' -> '.join(camino_retorno)}")

    # Validar que todos los estados transitorios de ida tienen al menos un camino de aborto
    estados_ida_transitorios = set(camino_ida[1:-1])
    for s in estados_ida_transitorios:
        trans = estados_map[s]["transiciones_salida"]
        tiene_aborto = any(tr["tipo_transicion"] in {"ABORT_RECUPERACION", "EMERGENCIA"} for tr in trans)
        if not tiene_aborto:
            fail(f"El estado transitorio '{s}' carece de ruta de escape o aborto.")
            sys.exit(1)
    success("Todos los estados intermedios de transicion disponen de rutas comprobadas de aborto y contingencia.")

def validar_limites_fisicos_y_saturacion(data: Dict[str, Any]) -> None:
    print("\n--- Validando Limites Fisicos, Tolerancias y Cotas de Saturacion ---")
    params = data.get("parametros_referencia", {})
    limite_empuje = params.get("limite_empuje_modulo_N")
    limite_cono = params.get("limite_cono_vectorial_deg")
    tasa_fuerza = params.get("tasa_maxima_cambio_fuerza_Ns")

    if limite_empuje != 21.0:
        fail(f"Limite de empuje esperado 21.0 N (INFORME.md:20), encontrado: {limite_empuje}")
        sys.exit(1)
    if limite_cono != 35.0:
        fail(f"Limite de cono esperado 35.0 deg (INFORME.md:20), encontrado: {limite_cono}")
        sys.exit(1)
    if tasa_fuerza != 50.0:
        fail(f"Tasa de variacion de fuerza esperada 50.0 N/s (INFORME.md:20), encontrado: {tasa_fuerza}")
        sys.exit(1)
    success("Parametros clave de saturacion física coinciden exactamente con los supuestos documentados.")

def validar_variables_desconocidas(data: Dict[str, Any]) -> None:
    print("\n--- Validando Catalogo de Variables Desconocidas ---")
    vars_desc = data.get("variables_desconocidas", [])
    if not isinstance(vars_desc, list) or len(vars_desc) < 4:
        fail("Listado de variables desconocidas insuficiente o vacio.")
        sys.exit(1)
    for v in vars_desc:
        if "id" not in v or "parametro" not in v or "impacto_transicion" not in v or "requisito_para_cierre" not in v:
            fail(f"Variable desconocida incompleta: {v}")
            sys.exit(1)
    success(f"Catalogo de {len(vars_desc)} variables no resueltas validado con impacto y requisitos de cierre.")

def main() -> None:
    print("======================================================================")
    print("VALIDADOR SINTACTICO Y SEMANTICO: MAQUINA DE ESTADOS DE TRANSICION")
    print("======================================================================")
    ruta_json = Path(__file__).resolve().parent / "maquina_estados.json"
    data = validar_archivo_json(ruta_json)
    validar_metadatos_y_declaraciones(data)
    validar_taxonomia_datos(data)
    validar_grafos_y_estados(data)
    validar_limites_fisicos_y_saturacion(data)
    validar_variables_desconocidas(data)
    print("\n======================================================================")
    print("[EXITO COMPLETO] La especificacion en maquina_estados.json cumple el 100% de reglas sintacticas y semanticas.")
    print("======================================================================")
    sys.exit(0)

if __name__ == "__main__":
    main()
