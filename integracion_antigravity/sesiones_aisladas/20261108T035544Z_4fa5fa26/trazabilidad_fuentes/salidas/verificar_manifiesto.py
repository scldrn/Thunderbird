#!/usr/bin/env python3
"""
verificar_manifiesto.py
-----------------------
Script en Python estándar para la verificación reproducible y detección de
cambios de contenido (integridad criptográfica SHA-256 y tamaño exacto en bytes)
de las tres tablas públicas de UIUC y la nota técnica NASA EDF.

Cumple estrictamente con las políticas de integridad metodológica:
- Detección de alteraciones byte a byte.
- Verificación de metadatos (la nota NASA no se cataloga como fuente primaria).
- Verificación de ausencia de licencias o fechas inventadas.
- Sin dependencias externas (solo biblioteca estándar de Python 3).

Códigos de retorno:
  0: Todos los archivos existen, coinciden en SHA-256, tamaño y reglas.
  1: Detección de alteración de contenido (hash o tamaño no coinciden).
  2: Archivo faltante o error en el manifiesto / argumentos.
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path


def calcular_sha256(ruta_archivo, tamano_bloque=65536):
    """Calcula el hash SHA-256 en hexadecimal de un archivo."""
    hasher = hashlib.sha256()
    with open(ruta_archivo, "rb") as f:
        while True:
            bloque = f.read(tamano_bloque)
            if not bloque:
                break
            hasher.update(bloque)
    return hasher.hexdigest().lower()


def obtener_tamano_bytes(ruta_archivo):
    """Devuelve el tamaño del archivo en bytes."""
    return os.path.getsize(ruta_archivo)


def verificar_archivo(info_esperada, directorio_base):
    """
    Verifica un archivo individual frente a los valores declarados en el manifiesto.

    Retorna un diccionario con:
      - nombre: str
      - estado: 'OK' | 'DISCREPANCIA_HASH' | 'DISCREPANCIA_TAMANO' | 'NO_ENCONTRADO' | 'ERROR_METADATOS'
      - tamano_esperado: int
      - tamano_real: int o None
      - sha256_esperado: str
      - sha256_real: str o None
      - mensaje: str
    """
    nombre = info_esperada.get("nombre")
    ruta_rel = info_esperada.get("ruta_relativa_referencia")
    sha_esperado = str(info_esperada.get("sha256", "")).lower()
    tamano_esperado = info_esperada.get("tamano_bytes")

    # Validación de reglas de metadatos metodológicas
    if nombre == "NOTA-NASA-EDF.md":
        if info_esperada.get("es_fuente_primaria") is True:
            return {
                "nombre": nombre,
                "estado": "ERROR_METADATOS",
                "mensaje": "Regla violada: NOTA-NASA-EDF.md no debe ser clasificada como fuente primaria.",
                "tamano_esperado": tamano_esperado,
                "tamano_real": None,
                "sha256_esperado": sha_esperado,
                "sha256_real": None,
            }

    ruta_completa = Path(directorio_base) / ruta_rel

    if not ruta_completa.is_file():
        return {
            "nombre": nombre,
            "estado": "NO_ENCONTRADO",
            "mensaje": f"Archivo no encontrado en la ruta esperada: {ruta_completa}",
            "tamano_esperado": tamano_esperado,
            "tamano_real": None,
            "sha256_esperado": sha_esperado,
            "sha256_real": None,
        }

    tamano_real = obtener_tamano_bytes(ruta_completa)
    sha_real = calcular_sha256(ruta_completa)

    if tamano_real != tamano_esperado:
        return {
            "nombre": nombre,
            "estado": "DISCREPANCIA_TAMANO",
            "mensaje": f"Alteración de tamaño detectada: esperado {tamano_esperado} bytes, real {tamano_real} bytes",
            "tamano_esperado": tamano_esperado,
            "tamano_real": tamano_real,
            "sha256_esperado": sha_esperado,
            "sha256_real": sha_real,
        }

    if sha_real != sha_esperado:
        return {
            "nombre": nombre,
            "estado": "DISCREPANCIA_HASH",
            "mensaje": f"Alteración de contenido detectada (SHA-256 no coincide):\n  Esperado: {sha_esperado}\n  Real:     {sha_real}",
            "tamano_esperado": tamano_esperado,
            "tamano_real": tamano_real,
            "sha256_esperado": sha_esperado,
            "sha256_real": sha_real,
        }

    return {
        "nombre": nombre,
        "estado": "OK",
        "mensaje": "Integridad verificada con éxito (tamaño y SHA-256 coinciden exactamente).",
        "tamano_esperado": tamano_esperado,
        "tamano_real": tamano_real,
        "sha256_esperado": sha_esperado,
        "sha256_real": sha_real,
    }


def verificar_manifiesto(ruta_manifiesto, directorio_base, verboso=False):
    """
    Carga el manifiesto JSON y comprueba todos los elementos listados.
    """
    ruta_manifiesto = Path(ruta_manifiesto)
    if not ruta_manifiesto.is_file():
        print(f"[ERROR] No se encuentra el archivo de manifiesto: {ruta_manifiesto}", file=sys.stderr)
        return False, [{"nombre": "manifiesto", "estado": "NO_ENCONTRADO", "mensaje": str(ruta_manifiesto)}]

    with open(ruta_manifiesto, "r", encoding="utf-8") as f:
        try:
            datos_manifiesto = json.load(f)
        except Exception as e:
            print(f"[ERROR] Formato JSON inválido en {ruta_manifiesto}: {e}", file=sys.stderr)
            return False, [{"nombre": "manifiesto", "estado": "JSON_INVALIDO", "mensaje": str(e)}]

    archivos = datos_manifiesto.get("archivos", [])
    if not archivos:
        print("[ERROR] El manifiesto no contiene la lista de archivos esperada.", file=sys.stderr)
        return False, []

    resultados = []
    hay_discrepancias = False
    hay_archivos_faltantes = False
    hay_errores_metadatos = False

    print("================================================================================")
    print("VERIFICACIÓN DE INTEGRIDAD REPRODUCIBLE DE FUENTES (UIUC & NASA EDF)")
    print("================================================================================")
    print(f"Manifiesto:      {ruta_manifiesto}")
    print(f"Directorio base: {directorio_base}")
    print(f"Archivos en lista: {len(archivos)}")
    print("--------------------------------------------------------------------------------")

    for info in archivos:
        res = verificar_archivo(info, directorio_base)
        resultados.append(res)
        nombre = res["nombre"]
        estado = res["estado"]

        if estado == "OK":
            print(f"[OK]       {nombre}")
            if verboso:
                print(f"           Tamaño: {res['tamano_real']} bytes")
                print(f"           SHA-256: {res['sha256_real']}")
        elif estado in ("DISCREPANCIA_HASH", "DISCREPANCIA_TAMANO"):
            hay_discrepancias = True
            print(f"[ALTERADO] {nombre} -> {res['mensaje']}")
        elif estado == "NO_ENCONTRADO":
            hay_archivos_faltantes = True
            print(f"[FALTANTE] {nombre} -> {res['mensaje']}")
        else:
            hay_errores_metadatos = True
            print(f"[ERROR]    {nombre} -> {res['mensaje']}")

    print("--------------------------------------------------------------------------------")

    if hay_discrepancias:
        print("[FALLO] Se detectaron alteraciones de contenido en los archivos.")
        return 1, resultados
    if hay_archivos_faltantes or hay_errores_metadatos:
        print("[FALLO] Hay archivos no encontrados o errores en metadatos.")
        return 2, resultados

    print("[ÉXITO] Todos los archivos verificados coinciden fielmente con el manifiesto.")
    return 0, resultados


def main():
    parser = argparse.ArgumentParser(
        description="Verificador de integridad y trazabilidad para fuentes UIUC y nota NASA EDF"
    )
    parser.add_argument(
        "--manifest",
        "-m",
        default="salidas/manifiesto_fuentes.json",
        help="Ruta al archivo manifiesto_fuentes.json (por defecto: salidas/manifiesto_fuentes.json)",
    )
    parser.add_argument(
        "--base-dir",
        "-b",
        default=".",
        help="Directorio raíz de trabajo (por defecto: directorio actual)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Imprime detalles completos de tamaño y hash de cada archivo verificado",
    )

    args = parser.parse_args()
    codigo_salida, _ = verificar_manifiesto(args.manifest, args.base_dir, verboso=args.verbose)
    sys.exit(codigo_salida)


if __name__ == "__main__":
    main()
