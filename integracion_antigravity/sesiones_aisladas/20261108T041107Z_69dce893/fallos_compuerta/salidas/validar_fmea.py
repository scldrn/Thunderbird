#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validar_fmea.py
Validador de campos, esquema y reglas semánticas para el análisis FMEA
conceptual de compuertas A07.

Comprueba:
1. Existencia del archivo y formato CSV UTF-8.
2. Cabeceras completas y sin campos vacíos.
3. Unicidad y patrón de id_caso (FMEA-A07-XXX).
4. Cobertura completa de los 7 modos de fallo requeridos:
   - Fallo al cerrar
   - Apertura no comandada
   - Una tapa atascada
   - Sensor discordante
   - Pérdida de energía
   - Fallo de sellos
   - Fallo de bloqueo
5. Cobertura de los dos estados conceptuales de vuelo: Bajo avance y Alto avance.
6. Severidad cualitativa en el conjunto permitido (Catastrófica, Crítica, Mayor, Menor).
7. Prohibición estricta de probabilidades cuantificadas no medidas.
8. Prohibición estricta de afirmar empuje proporcional a área.
9. Prohibición estricta de afirmar garantía de vuelo seguro.
10. Separación de hipótesis de implementación (declarando que no están en el CAD A07)
    y evidencia necesaria.
11. Trazabilidad de datos distinguiendo [CÁLCULO], [SUPUESTO], [NO MEDIDO] y fuentes canónicas.
"""

import csv
import os
import re
import sys

CABECERAS_REQUERIDAS = [
    "id_caso",
    "modo_fallo",
    "subsistema",
    "estado_vuelo",
    "condicion_operativa",
    "causa_raiz_potencial",
    "efecto_local",
    "efecto_vehiculo",
    "severidad_cualitativa",
    "deteccion_propuesta",
    "mitigacion_propuesta",
    "hipotesis_implementacion",
    "evidencia_necesaria",
    "probabilidad_cuantificada",
    "supuestos_y_datos_base",
]

MODOS_REQUERIDOS = {
    "Fallo al cerrar",
    "Apertura no comandada",
    "Una tapa atascada",
    "Sensor discordante",
    "Pérdida de energía",
    "Fallo de sellos",
    "Fallo de bloqueo",
}

ESTADOS_PERMITIDOS = {"Bajo avance", "Alto avance"}
SEVERIDADES_PERMITIDAS = {"Catastrófica", "Crítica", "Mayor", "Menor"}

PATRON_ID = re.compile(r"^FMEA-A07-\d{3}$")
PATRON_NUMEROS_PROBABILIDAD = re.compile(
    r"\b(\d+\.?\d*e[-+]?\d+|\d+\.\d+%(?:\s*h)?|\b0\.\d{3,}\b|\b10\^[-–]?\d+\b)",
    re.IGNORECASE,
)

FUENTES_CANONICAS = [
    "LEEME.md",
    "propuesta_elevacion.json",
    "C02_CANDIDATA.json",
    "PLAN-MAESTRO.md",
    "VERIFICACION_RECORRIDO.json",
]


class FMEAValidationError(Exception):
    """Excepción para errores de validación de FMEA."""
    pass


def validar_archivo_csv(ruta_csv):
    """Valida el archivo CSV de FMEA y retorna un reporte detallado."""
    errores = []
    advertencias = []
    
    if not os.path.exists(ruta_csv):
        raise FMEAValidationError(f"El archivo CSV no existe en la ruta: {ruta_csv}")

    with open(ruta_csv, mode="r", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        cabeceras = lector.fieldnames
        
        if not cabeceras:
            raise FMEAValidationError("El archivo CSV está vacío o carece de cabeceras.")
            
        # Comprobar cabeceras
        for col in CABECERAS_REQUERIDAS:
            if col not in cabeceras:
                errores.append(f"Falta la columna requerida: '{col}'")
                
        filas = list(lector)

    if not filas:
        raise FMEAValidationError("El archivo CSV no contiene registros de datos.")

    ids_vistos = set()
    modos_vistos = set()
    modos_por_estado = {est: set() for est in ESTADOS_PERMITIDOS}

    for num_fila, fila in enumerate(filas, start=2):
        # 1. Verificar campos no vacíos
        for col in CABECERAS_REQUERIDAS:
            valor = (fila.get(col) or "").strip()
            if not valor:
                errores.append(f"Fila {num_fila}: campo vacío o en blanco en columna '{col}'")

        # 2. Formato de ID y unicidad
        id_caso = (fila.get("id_caso") or "").strip()
        if not PATRON_ID.match(id_caso):
            errores.append(f"Fila {num_fila}: id_caso '{id_caso}' no cumple el patrón 'FMEA-A07-XXX'")
        if id_caso in ids_vistos:
            errores.append(f"Fila {num_fila}: id_caso duplicado '{id_caso}'")
        ids_vistos.add(id_caso)

        # 3. Modo de fallo y estado de vuelo
        modo = (fila.get("modo_fallo") or "").strip()
        modos_vistos.add(modo)
        if modo not in MODOS_REQUERIDOS:
            errores.append(f"Fila {num_fila}: modo_fallo '{modo}' no reconocido")

        estado = (fila.get("estado_vuelo") or "").strip()
        if estado not in ESTADOS_PERMITIDOS:
            errores.append(f"Fila {num_fila}: estado_vuelo '{estado}' no permitido (debe ser Bajo avance o Alto avance)")
        else:
            modos_por_estado[estado].add(modo)

        # 4. Severidad cualitativa
        severidad = (fila.get("severidad_cualitativa") or "").strip()
        if severidad not in SEVERIDADES_PERMITIDAS:
            errores.append(f"Fila {num_fila}: severidad_cualitativa '{severidad}' no permitida")

        # 5. Probabilidad: estrictamente cualitativa / no cuantificada
        prob = (fila.get("probabilidad_cuantificada") or "").strip()
        if "no cuantificada" not in prob.lower():
            errores.append(f"Fila {num_fila} ({id_caso}): probabilidad_cuantificada debe indicar 'No cuantificada'")
        # Comprobar que no se inventaron cifras de probabilidad (e.g., 1e-6, 0.0001)
        coincidencias_num = PATRON_NUMEROS_PROBABILIDAD.findall(prob)
        if coincidencias_num:
            errores.append(f"Fila {num_fila} ({id_caso}): probabilidad cuantificada numérica no permitida: {coincidencias_num}")

        # 6. Regla semántica: No atribuir empuje proporcional a área
        texto_completo_fila = " ".join((fila.get(c) or "") for c in CABECERAS_REQUERIDAS).lower()
        if "proporcional a" in texto_completo_fila and "área" in texto_completo_fila:
            # Debe estar negado explícitamente
            if not any(neg in texto_completo_fila for neg in [
                "no se atribuye empuje proporcional",
                "se rechaza explícitamente asumir empuje proporcional",
                "el empuje no es proporcional",
                "se excluye asumir empuje proporcional",
                "no es proporcional",
            ]):
                errores.append(
                    f"Fila {num_fila} ({id_caso}): se detectó mención de proporcionalidad a área sin aclaración explícita de su rechazo/invalidez"
                )

        # 7. Regla semántica: No atribuir garantía de vuelo seguro
        if "vuelo seguro" in texto_completo_fila:
            if not any(neg in texto_completo_fila for neg in [
                "sin garantía de vuelo seguro",
                "no existe garantía de vuelo seguro",
                "no confiere garantía de vuelo seguro",
                "no garantiza vuelo seguro",
                "no se garantiza la capacidad de mantener el vuelo seguro",
                "no se garantiza vuelo seguro",
            ]):
                errores.append(
                    f"Fila {num_fila} ({id_caso}): mención de 'vuelo seguro' sin deslinde explícito ('sin garantía de vuelo seguro')"
                )

        # 8. Hipótesis de implementación: debe aclarar que no está en el CAD A07
        hipotesis = (fila.get("hipotesis_implementacion") or "").strip().lower()
        if not any(frase in hipotesis for frase in ["no implementado", "no existen actuadores", "no existen", "hipótesis de diseño"]):
            errores.append(
                f"Fila {num_fila} ({id_caso}): hipotesis_implementacion debe explicitar que son hipótesis no implementadas en el CAD actual"
            )

        # 9. Evidencia necesaria
        evidencia = (fila.get("evidencia_necesaria") or "").strip().lower()
        if not any(ter in evidencia for ter in ["ensayo", "banco", "túnel", "cfd", "cálculo", "fsi", "simulación"]):
            advertencias.append(
                f"Fila {num_fila} ({id_caso}): evidencia_necesaria no menciona métodos estándar de ensayo o simulación"
            )

        # 10. Distinción de datos y fuentes en supuestos_y_datos_base
        base_datos = (fila.get("supuestos_y_datos_base") or "").strip()
        tags_encontrados = [tag for tag in ["[cálculo", "[supuesto", "[no medido"] if tag in base_datos.lower()]
        if len(tags_encontrados) < 2:
            errores.append(
                f"Fila {num_fila} ({id_caso}): supuestos_y_datos_base debe categorizar explícitamente los datos con etiquetas como [CÁLCULO...], [SUPUESTO...], [NO MEDIDO...]"
            )
        fuentes_encontradas = [f for f in FUENTES_CANONICAS if f in base_datos]
        if not fuentes_encontradas:
            advertencias.append(
                f"Fila {num_fila} ({id_caso}): supuestos_y_datos_base no cita una fuente canónica identificada ({FUENTES_CANONICAS})"
            )

    # 11. Comprobar que todos los modos requeridos están presentes
    modos_faltantes = MODOS_REQUERIDOS - modos_vistos
    if modos_faltantes:
        errores.append(f"Faltan los siguientes modos de fallo requeridos: {modos_faltantes}")

    # 12. Comprobar cobertura por estado
    for estado in ESTADOS_PERMITIDOS:
        modos_faltantes_estado = MODOS_REQUERIDOS - modos_por_estado[estado]
        if modos_faltantes_estado:
            errores.append(
                f"En estado '{estado}' faltan los modos de fallo: {modos_faltantes_estado}"
            )

    reporte = {
        "valido": len(errores) == 0,
        "total_registros": len(filas),
        "modos_analizados": sorted(list(modos_vistos)),
        "estados_analizados": sorted(list(ESTADOS_PERMITIDOS)),
        "errores": errores,
        "advertencias": advertencias,
    }
    return reporte


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv_defecto = os.path.join(script_dir, "fmea_compuertas_a07.csv")
    
    ruta_csv = sys.argv[1] if len(sys.argv) > 1 else ruta_csv_defecto
    
    print("=" * 70)
    print("VALIDADOR DE CAMPOS Y SEMÁNTICA - FMEA COMPUERTAS A07")
    print(f"Archivo objetivo: {ruta_csv}")
    print("=" * 70)
    
    try:
        reporte = validar_archivo_csv(ruta_csv)
    except FMEAValidationError as e:
        print(f"ERROR CRÍTICO: {e}")
        sys.exit(1)

    print(f"Total de registros evaluados: {reporte['total_registros']}")
    print(f"Modos de fallo cubiertos ({len(reporte['modos_analizados'])}): {', '.join(reporte['modos_analizados'])}")
    print(f"Estados de vuelo cubiertos: {', '.join(reporte['estados_analizados'])}")
    print("-" * 70)

    if reporte["advertencias"]:
        print(f"ADVERTENCIAS ({len(reporte['advertencias'])}):")
        for adv in reporte["advertencias"]:
            print(f"  [!] {adv}")
        print("-" * 70)

    if reporte["errores"]:
        print(f"ERRORES ENCONTRADOS ({len(reporte['errores'])}):")
        for err in reporte["errores"]:
            print(f"  [X] {err}")
        print("-" * 70)
        print("RESULTADO: VALIDACIÓN FALLIDA")
        sys.exit(1)
    else:
        print("RESULTADO: VALIDACIÓN EXITOSA (0 errores)")
        print("Todas las reglas de consistencia, sintaxis, semántica y restricciones se cumplen.")
        sys.exit(0)


if __name__ == "__main__":
    main()
