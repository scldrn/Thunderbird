#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resumen_lotes.py - Procesador y analizador de manifiestos RESUMEN.json de lotes computacionales.

Lee manifiestos de ejecución técnica por lotes, valida su integridad estructural
y sintáctica, detecta truncamientos y duplicidades de identificadores, y produce
tablas comprensibles con:
  1. Tabla de tareas (identificador, ocurrencia, necesidad de revisión, estado de validación).
  2. Estado técnico del lote (ejecución técnica finalizada, en curso o truncada).
  3. Número recogido de tareas (métrica de recolección de artefactos).
  4. Lista y detalle de tareas que requieren revisión técnica o científica.

===============================================================================
PRINCIPIO EPISTEMOLÓGICO Y METODOLÓGICO:
"No conviertas estado completado en aceptación científica."
El valor "completado" en el campo "estado" de un manifiesto únicamente certifica
que los procesos computacionales finalizaron su ejecución técnica (código de salida 0
o cierre de pipeline). De ninguna manera avala ni certifica la corrección física,
la convergencia numérica, la validez aerodinámica o la aceptación científica de los
resultados obtenidos. Toda tarea requiere revisión y validación metodológica formal.
===============================================================================
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple, Union


ESTADO_ACEPTACION_REVISION_REQUERIDA = "REQUIERE REVISIÓN TÉCNICA (Pendiente de validación científica)"
ESTADO_ACEPTACION_PENDIENTE = "PENDIENTE DE EVALUACIÓN CIENTÍFICA (Ejecución técnica finalizada; sin validación)"
ESTADO_ACEPTACION_NO_AVALADO = "NO AVALADO (Lote truncado o con fallos de ejecución)"

ADVERTENCIA_EPISTEMOLOGICA = (
    "AVISO METODOLÓGICO: El estado 'completado' del lote certifica únicamente la finalización "
    "del proceso computacional. NO equivale a aceptación científica, validación física ni aprobación "
    "técnica de los modelos o cálculos."
)


@dataclass
class TareaAnalizada:
    """Detalle de una tarea individual analizada a partir del manifiesto."""
    id_tarea: str
    indice_orden: int
    es_duplicada: bool
    numero_ocurrencia: int
    total_ocurrencias: int
    requiere_revision: bool
    estado_tecnico_lote: str
    estado_aceptacion_cientifica: str
    advertencias: List[str] = field(default_factory=list)


@dataclass
class ResumenLote:
    """Estructura que encapsula el análisis completo de un lote a partir de RESUMEN.json."""
    ruta_origen: str
    valido: bool
    es_truncado: bool
    error_parseo: Optional[str] = None

    # Datos leídos del manifiesto (preservación fiel de fuentes)
    inicio_utc: Optional[str] = None
    fin_utc: Optional[str] = None
    duracion_segundos: Optional[float] = None
    estado_lote: Optional[str] = None
    trabajadores: Optional[int] = None
    workspace_temporal: Optional[str] = None
    numero_recogido: Optional[int] = None

    # Listas originales
    tareas_crudas: List[str] = field(default_factory=list)
    requieren_revision_crudas: List[str] = field(default_factory=list)

    # Análisis de integridad y anomalías
    tareas_analizadas: List[TareaAnalizada] = field(default_factory=list)
    duplicados_tareas: Dict[str, int] = field(default_factory=dict)
    duplicados_revision: Dict[str, int] = field(default_factory=dict)
    revision_no_en_tareas: List[str] = field(default_factory=list)
    discrepancia_recogidas: Optional[Tuple[int, int]] = None  # (recogidas_declaradas, total_tareas_lista)
    advertencias_lote: List[str] = field(default_factory=list)

    def resumen_ejecutivo(self) -> Dict[str, Any]:
        """Devuelve un diccionario resumen con las métricas clave."""
        return {
            "origen": self.ruta_origen,
            "valido": self.valido,
            "es_truncado": self.es_truncado,
            "estado_lote": self.estado_lote,
            "numero_recogido": self.numero_recogido,
            "total_tareas_listadas": len(self.tareas_crudas),
            "total_requieren_revision": len(self.requieren_revision_crudas),
            "tareas_que_requieren_revision": list(dict.fromkeys(self.requieren_revision_crudas)),
            "duplicados_en_tareas": self.duplicados_tareas,
            "duplicados_en_revision": self.duplicados_revision,
            "advertencias": self.advertencias_lote,
            "aviso_metodologico": ADVERTENCIA_EPISTEMOLOGICA,
        }


def calcular_duracion_segundos(inicio_utc: Optional[str], fin_utc: Optional[str]) -> Optional[float]:
    """Calcula la duración en segundos entre inicio y fin en formato ISO 8601 preservando unidades."""
    if not inicio_utc or not fin_utc:
        return None
    try:
        t0 = datetime.fromisoformat(inicio_utc)
        t1 = datetime.fromisoformat(fin_utc)
        return (t1 - t0).total_seconds()
    except (ValueError, TypeError):
        return None


def clasificar_aceptacion_cientifica(requiere_revision: bool, estado_lote: Optional[str]) -> str:
    """
    Aplica la regla epistemológica: bajo ninguna circunstancia se asigna aceptación
    científica automática a un resultado por el hecho de haber completado su ejecución técnica.
    """
    if estado_lote != "completado":
        return ESTADO_ACEPTACION_NO_AVALADO
    if requiere_revision:
        return ESTADO_ACEPTACION_REVISION_REQUERIDA
    return ESTADO_ACEPTACION_PENDIENTE


def parsear_manifiesto_json(contenido_str: str, ruta_origen: str = "<memoria>") -> ResumenLote:
    """
    Parsea y analiza el contenido textual de un manifiesto RESUMEN.json.
    Detecta truncamiento, JSON malformado, duplicados e inconsistencias lógicas.
    """
    resumen = ResumenLote(
        ruta_origen=ruta_origen,
        valido=False,
        es_truncado=False,
    )

    if not contenido_str.strip():
        resumen.error_parseo = "El archivo de manifiesto está completamente vacío."
        resumen.es_truncado = True
        resumen.advertencias_lote.append("Archivo vacío: truncamiento o creación inconclusa.")
        return resumen

    try:
        datos = json.loads(contenido_str)
    except json.JSONDecodeError as err:
        resumen.es_truncado = True
        resumen.error_parseo = f"Error de decodificación JSON (posible truncamiento): {err.msg} (línea {err.lineno}, columna {err.colno})"
        resumen.advertencias_lote.append(
            f"Manifiesto truncado o con sintaxis inválida en línea {err.lineno}, col {err.colno}: {err.msg}"
        )
        return resumen

    if not isinstance(datos, dict):
        resumen.error_parseo = f"Estructura raíz inválida: se esperaba un objeto JSON (dict), se obtuvo {type(datos).__name__}."
        resumen.advertencias_lote.append("Estructura raíz no es un diccionario JSON.")
        return resumen

    resumen.valido = True
    resumen.inicio_utc = datos.get("inicio_utc")
    resumen.fin_utc = datos.get("fin_utc")
    resumen.duracion_segundos = calcular_duracion_segundos(resumen.inicio_utc, resumen.fin_utc)
    resumen.estado_lote = str(datos.get("estado")) if datos.get("estado") is not None else "no_declarado"
    resumen.trabajadores = datos.get("trabajadores")
    resumen.workspace_temporal = datos.get("workspace_temporal")
    resumen.numero_recogido = datos.get("recolectadas")

    # Extraer tareas
    tareas_raw = datos.get("tareas", [])
    if isinstance(tareas_raw, list):
        resumen.tareas_crudas = [str(t) for t in tareas_raw]
    else:
        resumen.advertencias_lote.append("El campo 'tareas' no es una lista válida.")
        resumen.tareas_crudas = []

    # Extraer tareas que requieren revisión
    revision_raw = datos.get("requieren_revision", [])
    if isinstance(revision_raw, list):
        resumen.requieren_revision_crudas = [str(t) for t in revision_raw]
    else:
        resumen.advertencias_lote.append("El campo 'requieren_revision' no es una lista válida.")
        resumen.requieren_revision_crudas = []

    # Validar duplicados en tareas
    conteo_tareas = Counter(resumen.tareas_crudas)
    for tid, count in conteo_tareas.items():
        if count > 1:
            resumen.duplicados_tareas[tid] = count
            resumen.advertencias_lote.append(
                f"ID de tarea duplicado en 'tareas': '{tid}' aparece {count} veces."
            )

    # Validar duplicados en requieren_revision
    conteo_revision = Counter(resumen.requieren_revision_crudas)
    for tid, count in conteo_revision.items():
        if count > 1:
            resumen.duplicados_revision[tid] = count
            resumen.advertencias_lote.append(
                f"ID de tarea duplicado en 'requieren_revision': '{tid}' aparece {count} veces."
            )

    # Validar si hay tareas en requieren_revision que no están en tareas
    conjunto_tareas = set(resumen.tareas_crudas)
    for tid in resumen.requieren_revision_crudas:
        if tid not in conjunto_tareas and tid not in resumen.revision_no_en_tareas:
            resumen.revision_no_en_tareas.append(tid)
            resumen.advertencias_lote.append(
                f"Tarea en 'requieren_revision' no declarada en lista 'tareas': '{tid}'."
            )

    # Validar discrepancia de recolección
    if resumen.numero_recogido is not None and isinstance(resumen.numero_recogido, int):
        if resumen.numero_recogido != len(resumen.tareas_crudas):
            resumen.discrepancia_recogidas = (resumen.numero_recogido, len(resumen.tareas_crudas))
            resumen.advertencias_lote.append(
                f"Discrepancia de recolección: 'recolectadas' declara {resumen.numero_recogido}, "
                f"pero la lista 'tareas' contiene {len(resumen.tareas_crudas)} elementos."
            )

    # Construir lista de tareas analizadas
    revision_set = set(resumen.requieren_revision_crudas)
    contador_apariciones: Dict[str, int] = Counter()

    for idx, tid in enumerate(resumen.tareas_crudas, start=1):
        contador_apariciones[tid] += 1
        num_ocurrencia = contador_apariciones[tid]
        total_ocurrencias = conteo_tareas[tid]
        es_dup = total_ocurrencias > 1

        req_rev = tid in revision_set
        estado_acept = clasificar_aceptacion_cientifica(req_rev, resumen.estado_lote)

        advertencias_tarea = []
        if es_dup:
            advertencias_tarea.append(f"Duplicado ({num_ocurrencia}/{total_ocurrencias})")

        resumen.tareas_analizadas.append(
            TareaAnalizada(
                id_tarea=tid,
                indice_orden=idx,
                es_duplicada=es_dup,
                numero_ocurrencia=num_ocurrencia,
                total_ocurrencias=total_ocurrencias,
                requiere_revision=req_rev,
                estado_tecnico_lote=resumen.estado_lote,
                estado_aceptacion_cientifica=estado_acept,
                advertencias=advertencias_tarea,
            )
        )

    return resumen


def leer_manifiesto_archivo(ruta_archivo: Union[Path, str]) -> ResumenLote:
    """Lee un archivo de disco y procesa su manifiesto RESUMEN.json de forma segura."""
    path = Path(ruta_archivo)
    if not path.is_file():
        resumen = ResumenLote(
            ruta_origen=str(path),
            valido=False,
            es_truncado=False,
            error_parseo=f"Archivo no encontrado: {path}",
        )
        resumen.advertencias_lote.append(f"No existe el archivo: {path}")
        return resumen

    try:
        contenido = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            contenido = path.read_text(encoding="latin-1")
        except Exception as exc:
            resumen = ResumenLote(
                ruta_origen=str(path),
                valido=False,
                es_truncado=False,
                error_parseo=f"Error de lectura al decodificar archivo: {exc}",
            )
            resumen.advertencias_lote.append(str(exc))
            return resumen
    except Exception as exc:
        resumen = ResumenLote(
            ruta_origen=str(path),
            valido=False,
            es_truncado=False,
            error_parseo=f"Error inesperado al abrir archivo: {exc}",
        )
        resumen.advertencias_lote.append(str(exc))
        return resumen

    return parsear_manifiesto_json(contenido, str(path))


def buscar_manifiestos_en_directorio(directorio_base: Union[Path, str]) -> List[Path]:
    """Busca recursivamente archivos RESUMEN.json dentro de un directorio."""
    base = Path(directorio_base)
    if not base.is_dir():
        return []
    return sorted(base.rglob("RESUMEN.json"))


def generar_tabla_texto(lote: ResumenLote) -> str:
    """Genera una representación en texto plano formateado con tablas de tareas y estado."""
    lineas: List[str] = []
    lineas.append("=" * 100)
    lineas.append(f"REPORTE DE MANIFIESTO DE LOTE: {lote.ruta_origen}")
    lineas.append("=" * 100)
    lineas.append(f"  * Estado Técnico del Lote : {lote.estado_lote}")
    lineas.append(f"  * Número Recogido (Métrica): {lote.numero_recogido if lote.numero_recogido is not None else 'N/D'}")
    lineas.append(f"  * Total Tareas Declaradas : {len(lote.tareas_crudas)}")
    lineas.append(f"  * Tareas Requieren Revisión: {len(lote.requieren_revision_crudas)}")
    if lote.duracion_segundos is not None:
        lineas.append(f"  * Duración de Ejecución    : {lote.duracion_segundos:.2f} s")
    if lote.trabajadores is not None:
        lineas.append(f"  * Trabajadores Asignados   : {lote.trabajadores}")
    if lote.workspace_temporal:
        lineas.append(f"  * Espacio Temporal         : {lote.workspace_temporal}")

    lineas.append("-" * 100)
    lineas.append(f"  [!] REGLA EPISTEMOLÓGICA: {ADVERTENCIA_EPISTEMOLOGICA}")
    lineas.append("-" * 100)

    if not lote.valido:
        lineas.append(f"  [ERROR / TRUNCAMIENTO]: {lote.error_parseo}")
        if lote.advertencias_lote:
            lineas.append("  Advertencias:")
            for adv in lote.advertencias_lote:
                lineas.append(f"    - {adv}")
        lineas.append("=" * 100)
        return "\n".join(lineas)

    if lote.advertencias_lote:
        lineas.append("  ALERTAS DE INTEGRIDAD DETECTADAS:")
        for adv in lote.advertencias_lote:
            lineas.append(f"    [!] {adv}")
        lineas.append("-" * 100)

    # Detalle de tareas que requieren revisión
    if lote.requieren_revision_crudas:
        lineas.append("  LISTA DE TAREAS QUE REQUIEREN REVISIÓN TÉCNICA:")
        for tid in list(dict.fromkeys(lote.requieren_revision_crudas)):
            lineas.append(f"    -> {tid}")
    else:
        lineas.append("  LISTA DE TAREAS QUE REQUIEREN REVISIÓN: Ninguna marcada explícitamente.")

    lineas.append("-" * 100)
    lineas.append("  TABLA DETALLADA DE TAREAS:")
    encabezado = f"{'#':<4} | {'ID DE TAREA':<28} | {'REVISIÓN':<10} | {'ESTADO ACEPTACIÓN CIENTÍFICA':<45} | {'NOTAS'}"
    lineas.append(encabezado)
    lineas.append("-" * 100)

    for t in lote.tareas_analizadas:
        rev_str = "SÍ" if t.requiere_revision else "NO"
        notas_str = "; ".join(t.advertencias) if t.advertencias else "-"
        fila = f"{t.indice_orden:<4} | {t.id_tarea:<28} | {rev_str:<10} | {t.estado_aceptacion_cientifica:<45} | {notas_str}"
        lineas.append(fila)

    lineas.append("=" * 100)
    return "\n".join(lineas)


def generar_tabla_markdown(lote: ResumenLote) -> str:
    """Genera una tabla y reporte en formato GitHub Flavored Markdown."""
    lineas: List[str] = []
    lineas.append(f"### Manifiesto: `{os.path.basename(lote.ruta_origen)}`")
    lineas.append(f"**Ruta de origen:** `{lote.ruta_origen}`  ")
    lineas.append(f"**Estado técnico del lote:** `{lote.estado_lote}`  ")
    lineas.append(f"**Número recogido (tareas recolectadas):** `{lote.numero_recogido}`  ")
    lineas.append(f"**Tareas declaradas en lista:** `{len(lote.tareas_crudas)}`  ")
    lineas.append(f"**Tareas que requieren revisión:** `{len(lote.requieren_revision_crudas)}`  ")
    if lote.duracion_segundos is not None:
        lineas.append(f"**Duración registrada:** `{lote.duracion_segundos:.2f} s`  ")
    if lote.trabajadores is not None:
        lineas.append(f"**Trabajadores concurrentes:** `{lote.trabajadores}`  ")
    if lote.workspace_temporal:
        lineas.append(f"**Espacio temporal:** `{lote.workspace_temporal}`  ")

    lineas.append("")
    lineas.append("> [!IMPORTANT]")
    lineas.append(f"> **Principio de Rigor:** {ADVERTENCIA_EPISTEMOLOGICA}")
    lineas.append("")

    if not lote.valido:
        lineas.append("> [!CAUTION]")
        lineas.append(f"> **Error de Integridad / Truncamiento:** {lote.error_parseo}")
        lineas.append("")
        return "\n".join(lineas)

    if lote.advertencias_lote:
        lineas.append("> [!WARNING]")
        lineas.append("> **Alertas de Integridad y Validación:**")
        for adv in lote.advertencias_lote:
            lineas.append(f"> - {adv}")
        lineas.append("")

    lineas.append("#### Tareas que Requieren Revisión")
    if lote.requieren_revision_crudas:
        lineas.append("Las siguientes tareas han sido marcadas para revisión obligatoria:")
        for tid in list(dict.fromkeys(lote.requieren_revision_crudas)):
            lineas.append(f"- `{tid}`")
    else:
        lineas.append("_Ninguna tarea marcada para revisión explícita en este lote._")
    lineas.append("")

    lineas.append("#### Tabla de Tareas del Lote")
    lineas.append("| # | ID de Tarea | Requiere Revisión | Estado de Aceptación Científica | Notas / Anomalías |")
    lineas.append("|---|-------------|:-----------------:|---------------------------------|-------------------|")

    for t in lote.tareas_analizadas:
        rev_badge = "**SÍ**" if t.requiere_revision else "No"
        notas = "<br>".join(t.advertencias) if t.advertencias else "—"
        lineas.append(f"| {t.indice_orden} | `{t.id_tarea}` | {rev_badge} | {t.estado_aceptacion_cientifica} | {notas} |")

    lineas.append("")
    return "\n".join(lineas)


def procesar_lotes(rutas: List[Union[Path, str]]) -> List[ResumenLote]:
    """Procesa una lista de rutas de archivos o directorios buscando y analizando manifiestos."""
    archivos_objetivo: List[Path] = []
    for r in rutas:
        p = Path(r)
        if p.is_dir():
            encontrados = buscar_manifiestos_en_directorio(p)
            archivos_objetivo.extend(encontrados)
        elif p.is_file():
            archivos_objetivo.append(p)
        else:
            # Archivo inexistente para registrarlo en el análisis
            archivos_objetivo.append(p)

    # Eliminar duplicados de archivos conservando orden
    archivos_unicos = list(dict.fromkeys(archivos_objetivo))
    return [leer_manifiesto_archivo(a) for a in archivos_unicos]


def generar_salida_unificada(lotes: List[ResumenLote], formato: str = "texto") -> str:
    """Genera la salida global formateada para todos los lotes evaluados."""
    if formato == "json":
        resumenes = [l.resumen_ejecutivo() for l in lotes]
        return json.dumps(resumenes, indent=2, ensure_ascii=False)
    elif formato == "markdown":
        bloques = ["# Resumen de Procesamiento de Lotes Computacionales\n"]
        for l in lotes:
            bloques.append(generar_tabla_markdown(l))
        return "\n".join(bloques)
    else:  # texto plano
        bloques = []
        for l in lotes:
            bloques.append(generar_tabla_texto(l))
        return "\n\n".join(bloques)


def main(argv: Optional[List[str]] = None) -> int:
    """Punto de entrada de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Analizador e intérprete de manifiestos RESUMEN.json de lotes."
    )
    parser.add_argument(
        "rutas",
        nargs="*",
        help="Rutas a archivos RESUMEN.json o directorios que los contengan.",
    )
    parser.add_argument(
        "--formato",
        choices=["texto", "markdown", "json"],
        default="texto",
        help="Formato de salida (texto, markdown o json). Por defecto: texto.",
    )
    parser.add_argument(
        "--buscar-dir",
        dest="buscar_dir",
        help="Directorio base para buscar automáticamente manifiestos RESUMEN.json.",
    )
    parser.add_argument(
        "--guardar",
        dest="guardar",
        help="Ruta donde guardar la salida generada en lugar de solo imprimirla.",
    )

    args = parser.parse_args(argv)

    rutas_a_procesar: List[Union[Path, str]] = []
    if args.rutas:
        rutas_a_procesar.extend(args.rutas)
    if args.buscar_dir:
        rutas_a_procesar.append(args.buscar_dir)

    # Si no se suministraron argumentos, buscar por defecto en 'entradas' si existe
    if not rutas_a_procesar:
        directorio_default = Path("entradas")
        if directorio_default.exists():
            rutas_a_procesar.append(directorio_default)
        else:
            rutas_a_procesar.append(Path("."))

    lotes = procesar_lotes(rutas_a_procesar)
    if not lotes:
        print("No se encontraron manifiestos RESUMEN.json para analizar.", file=sys.stderr)
        return 1

    salida = generar_salida_unificada(lotes, formato=args.formato)

    if args.guardar:
        ruta_salida = Path(args.guardar)
        ruta_salida.parent.mkdir(parents=True, exist_ok=True)
        ruta_salida.write_text(salida, encoding="utf-8")
        print(f"Salida guardada exitosamente en: {ruta_salida}")
    else:
        print(salida)

    # Verificar si hubo anomalías graves (truncamientos)
    hay_truncamientos = any(l.es_truncado or not l.valido for l in lotes)
    return 1 if hay_truncamientos else 0


if __name__ == "__main__":
    sys.exit(main())
