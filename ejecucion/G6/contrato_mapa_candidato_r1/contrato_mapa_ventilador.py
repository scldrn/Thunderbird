#!/usr/bin/env python3
"""
Módulo: contrato_mapa_ventilador.py
Contrato de datos versionado y validador en Python estándar para mapas instalados
de módulos de ventilador (fan modules) en vehículos aeroespaciales.

Versión del contrato: 1.0.0
Autoría / Contexto: Especificación de ingeniería para candidatos de arquitectura A (ventiladores internos).
Restricción: No coerciona datos faltantes a cero. Rechaza NaNs, unidades ausentes,
geometría/ejes desconocidos, muestras duplicadas y extrapolación declarada.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Versión canónica del contrato de datos
CONTRATO_VERSION = "1.0.0"

# Unidades canónicas admitidas por dimensión
UNIDADES_CANONICAS_VALIDAS = {
    "longitud": {"m", "mm"},
    "fuerza": {"N", "kN"},
    "momento": {"N*m", "N m", "Nm"},
    "velocidad": {"m/s", "m_s"},
    "densidad": {"kg/m^3", "kg/m3", "kg_m3"},
    "potencia": {"W", "kW"},
    "angulo": {"deg", "rad"},
    "velocidad_rotacion": {"rpm", "rad/s"},
    "presion": {"Pa", "kPa", "bar"},
    "temperatura": {"K", "degC"},
}

MARCOS_REFERENCIA_VALIDOS = {"MODULO_LOCAL", "CAD_VEHICULO", "FLU_CUERPO"}
SENTIDOS_GIRO_VALIDOS = {"CW", "CCW"}
ESTADOS_COMPUERTA_VALIDOS = {"abierto", "cerrado", "transicion", "corte"}
CATEGORIAS_ORIGEN_VALIDAS = {"medido", "calculo", "supuesto"}
# ADVERTIR se retiró: el contrato anterior aceptaba silenciosamente datos
# fuera del dominio sin registrar ningún aviso para el consumidor.
POLITICAS_EXTRAPOLACION_VALIDAS = {"RECHAZAR"}
TIPOS_INCERTIDUMBRE_VALIDOS = {"EXPANDIDA_K2", "ESTANDAR_1SIGMA", "INTERVALO_TOLERANCIA"}
ESTADOS_DATO_FALTANTE = {"NO_MEDIDO", "NO_CALCULADO", "NO_APLICABLE", "DATO_FALTANTE"}


class CodigoErrorValidacion(str, Enum):
    """Códigos formales de error de validación del contrato."""
    UNIDADES_AUSENTES = "UNIDADES_AUSENTES"
    VALOR_NAN_DETECTADO = "VALOR_NAN_DETECTADO"
    GEOMETRIA_O_EJES_DESCONOCIDOS = "GEOMETRIA_O_EJES_DESCONOCIDOS"
    MUESTRAS_DUPLICADAS = "MUESTRAS_DUPLICADAS"
    EXTRAPOLACION_DECLARADA = "EXTRAPOLACION_DECLARADA"
    ESTRUCTURA_INVALIDA = "ESTRUCTURA_INVALIDA"
    CAMPO_OBLIGATORIO_FALTANTE = "CAMPO_OBLIGATORIO_FALTANTE"
    DOMINIO_INVALIDO = "DOMINIO_INVALIDO"
    COERCION_A_CERO_PROHIBIDA = "COERCION_A_CERO_PROHIBIDA"


class ErrorValidacionContrato(Exception):
    """Excepción específica lanzada por violaciones al contrato de datos."""
    def __init__(self, codigo: CodigoErrorValidacion, mensaje: str, ruta: str = ""):
        self.codigo = codigo
        self.mensaje = mensaje
        self.ruta = ruta
        super().__init__(f"[{codigo.value}] en '{ruta}': {mensaje}" if ruta else f"[{codigo.value}] {mensaje}")


@dataclass
class RegistroDatoFaltante:
    """
    Representación explícita de un dato faltante o no medido.
    Garantiza que el dato NO sea coercionado a 0.0.
    """
    estado: str = "NO_MEDIDO"
    motivo: str = ""
    es_dato_faltante: bool = True

    def __repr__(self) -> str:
        return f"RegistroDatoFaltante(estado='{self.estado}', motivo='{self.motivo}')"


@dataclass
class UnidadesContrato:
    """Unidades físicas explícitas aplicables al mapa instalado."""
    longitud: str = "m"
    fuerza: str = "N"
    momento: str = "N*m"
    velocidad: str = "m/s"
    densidad: str = "kg/m^3"
    potencia: str = "W"
    angulo: str = "deg"
    velocidad_rotacion: str = "rpm"
    presion: str = "Pa"
    temperatura: str = "K"


@dataclass
class PuntoAplicacion:
    """
    Punto explícito de aplicación física de la fuerza y centro de reducción de momentos.
    """
    marco_referencia: str
    coordenadas_m: List[float]
    descripcion: str


@dataclass
class MetadatosOrigen:
    """Trazabilidad completa del origen de los datos."""
    categoria: str  # 'medido', 'calculo', 'supuesto'
    es_sintetico: bool
    fuente_tipo: str  # e.g. 'ensayo_banco', 'simulacion_cfd', 'sintetico_demostracion'
    instalacion_o_herramienta: str
    codigo_o_metodo: str
    referencia_caso: str
    fecha: str
    nivel_resolucion: Optional[str] = None
    notas: str = ""


@dataclass
class GeometriaReferencia:
    """Especificación geométrica del módulo de ventilador."""
    geometria_id: str
    modulo_id: str
    diametro_paso_nominal_m: float
    radio_pala_nominal_m: float
    escala_geom: float
    sentido_giro: str  # 'CW' o 'CCW'
    estados_compuertas_soportados: List[str]


@dataclass
class RangoDominio:
    """Límites inferior y superior para una variable física."""
    minimo: float
    maximo: float

    def contiene(self, valor: float, tol: float = 1e-9) -> bool:
        return (self.minimo - tol) <= valor <= (self.maximo + tol)


@dataclass
class DominioValidez:
    """Dominio físico de validez del mapa instalado."""
    densidad_kg_m3: RangoDominio
    velocidad_modulo_m_s: RangoDominio
    rpm: RangoDominio
    deflexion_alabes_deg: RangoDominio
    politica_extrapolacion: str = "RECHAZAR"


@dataclass
class EntradaFlujoLocal:
    """Entradas aerodinámicas locales relativas al módulo."""
    velocidad_vectorial_m_s: List[float]  # [vx, vy, vz]
    densidad_kg_m3: float
    temperatura_K: Optional[float] = 288.15
    presion_estatica_Pa: Optional[float] = 101325.0


@dataclass
class EntradaMandoEstado:
    """Entradas cinemáticas y de mando del módulo."""
    rpm: float
    mando_normalizado: float  # [0, 1]
    deflexion_alabes_deg: List[float]  # [delta_x, delta_y]
    estado_compuerta: str  # 'abierto', 'cerrado', 'transicion'


@dataclass
class IncertidumbreSalidas:
    """Incertidumbre asociada a las salidas físicas del módulo."""
    fuerza_vectorial_N: List[float]  # [u_Fx, u_Fy, u_Fz]
    momento_vectorial_Nm: List[float]  # [u_Mx, u_My, u_Mz]
    potencia_electrica_W: Optional[Union[float, RegistroDatoFaltante]] = None
    potencia_mecanica_W: Optional[Union[float, RegistroDatoFaltante]] = None
    tipo_incertidumbre: str = "EXPANDIDA_K2"
    nivel_confianza_pct: float = 95.0
    metodo_evaluacion: str = ""


@dataclass
class MuestraMapa:
    """
    Punto de muestreo individual del mapa instalado.
    Las potencias no medidas se representan con None o RegistroDatoFaltante (NUNCA 0.0).
    """
    id_muestra: str
    flujo_local: EntradaFlujoLocal
    mando_estado: EntradaMandoEstado
    fuerza_vectorial_N: List[float]  # [Fx, Fy, Fz]
    momento_vectorial_Nm: List[float]  # [Mx, My, Mz]
    potencia_electrica_W: Optional[Union[float, RegistroDatoFaltante]]
    potencia_mecanica_W: Optional[Union[float, RegistroDatoFaltante]]
    incertidumbre: IncertidumbreSalidas
    es_extrapolacion: bool = False
    marcas_datos_faltantes: Dict[str, str] = field(default_factory=dict)
    notas: str = ""


@dataclass
class MapaInstaladoFan:
    """Estructura raíz completa del mapa instalado del módulo de ventilador."""
    contrato_version: str
    mapa_id: str
    descripcion: str
    unidades: UnidadesContrato
    marcos_referencia: Dict[str, Any]
    punto_aplicacion: PuntoAplicacion
    metadatos_origen: MetadatosOrigen
    geometria_referencia: GeometriaReferencia
    dominio_validez: DominioValidez
    muestras: List[MuestraMapa]


# -----------------------------------------------------------------------------
# Transformaciones de Coordenadas y Reducción de Momentos
# -----------------------------------------------------------------------------

def rotacion_cad_a_flu(vector_cad: List[float]) -> List[float]:
    """
    Transforma un vector libre expresado en CAD a FLU según C02_CANDIDATA:
    x_flu = -x_cad, y_flu = -y_cad, z_flu = +z_cad
    """
    if len(vector_cad) != 3:
        raise ValueError("El vector debe tener exactamente 3 componentes.")
    return [-vector_cad[0], -vector_cad[1], vector_cad[2]]


def rotacion_flu_a_cad(vector_flu: List[float]) -> List[float]:
    """
    Transforma un vector libre expresado en FLU a CAD:
    x_cad = -x_flu, y_cad = -y_flu, z_cad = +z_flu
    """
    if len(vector_flu) != 3:
        raise ValueError("El vector debe tener exactamente 3 componentes.")
    return [-vector_flu[0], -vector_flu[1], vector_flu[2]]


def transferir_momento(
    fuerza_N: List[float],
    momento_en_app_Nm: List[float],
    r_app_m: List[float],
    r_nuevo_m: List[float],
) -> List[float]:
    """
    Transfiere el momento vectorial del punto de aplicación r_app a un nuevo punto r_nuevo:
    M_nuevo = M_app + (r_app - r_nuevo) x F
    """
    dx = r_app_m[0] - r_nuevo_m[0]
    dy = r_app_m[1] - r_nuevo_m[1]
    dz = r_app_m[2] - r_nuevo_m[2]

    Fx, Fy, Fz = fuerza_N[0], fuerza_N[1], fuerza_N[2]

    # Producto vectorial (r_app - r_nuevo) x F
    brazo_x_fuerza = [
        dy * Fz - dz * Fy,
        dz * Fx - dx * Fz,
        dx * Fy - dy * Fx,
    ]

    return [
        momento_en_app_Nm[0] + brazo_x_fuerza[0],
        momento_en_app_Nm[1] + brazo_x_fuerza[1],
        momento_en_app_Nm[2] + brazo_x_fuerza[2],
    ]


# -----------------------------------------------------------------------------
# Validador de Contrato de Datos (Python Estándar)
# -----------------------------------------------------------------------------

class ValidadorMapaInstalado:
    """
    Validador estricto sin dependencias externas.
    Reglas evaluadas:
      1. Unidades presentes y válidas para todas las dimensiones físicas requeridas.
      2. Detección y rechazo riguroso de NaN en cualquier campo numérico.
      3. Verificación de marcos de referencia y geometrías conocidas y no degeneradas.
      4. Detección y rechazo de muestras de entrada duplicadas.
      5. Detección y rechazo de extrapolación declarada o muestras fuera de dominio si la política es RECHAZAR.
      6. Aceptación explícita de marcas de datos faltantes, verificando que NO sean convertidos en 0.0.
    """

    def __init__(self, tolerancia_duplicados: float = 1e-6):
        self.tolerancia_duplicados = tolerancia_duplicados

    def validar_dict(self, datos: Dict[str, Any]) -> MapaInstaladoFan:
        """Valida una estructura de diccionario cruda y retorna el objeto tipado si es válida."""
        if not isinstance(datos, dict):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.ESTRUCTURA_INVALIDA,
                "La raíz del documento debe ser un objeto JSON (dict).",
                ruta="$",
            )

        # 1. Chequeo de NaN en todo el árbol de datos
        self._verificar_ausencia_nan(datos, ruta="$")

        # 2. Versión del contrato
        version = datos.get("contrato_version")
        if not version or not isinstance(version, str):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.ESTRUCTURA_INVALIDA,
                "Campo 'contrato_version' ausente o no es una cadena válida.",
                ruta="$.contrato_version",
            )
        if version.split(".")[0] != CONTRATO_VERSION.split(".")[0]:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.ESTRUCTURA_INVALIDA,
                f"Versión de contrato '{version}' no compatible con la versión del validador '{CONTRATO_VERSION}'.",
                ruta="$.contrato_version",
            )

        # 3. Validación de Unidades
        unidades_dict = datos.get("unidades")
        unidades_obj = self._validar_unidades(unidades_dict, ruta="$.unidades")

        # 4. Marcos de referencia y Punto de aplicación
        marcos_dict = datos.get("marcos_referencia")
        self._validar_marcos_referencia(marcos_dict, ruta="$.marcos_referencia")

        punto_app_dict = datos.get("punto_aplicacion")
        punto_app_obj = self._validar_punto_aplicacion(punto_app_dict, ruta="$.punto_aplicacion")

        # 5. Metadatos de Origen
        origen_dict = datos.get("metadatos_origen")
        origen_obj = self._validar_metadatos_origen(origen_dict, ruta="$.metadatos_origen")

        # 6. Geometría de Referencia
        geom_dict = datos.get("geometria_referencia")
        geom_obj = self._validar_geometria(geom_dict, ruta="$.geometria_referencia")

        # 7. Dominio de Validez
        dominio_dict = datos.get("dominio_validez")
        dominio_obj = self._validar_dominio_validez(dominio_dict, ruta="$.dominio_validez")

        # 8. Muestras
        muestras_raw = datos.get("muestras")
        if not isinstance(muestras_raw, list) or len(muestras_raw) == 0:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.ESTRUCTURA_INVALIDA,
                "El campo 'muestras' debe ser una lista no vacía de puntos de muestreo.",
                ruta="$.muestras",
            )

        muestras_obj = self._validar_muestras(
            muestras_raw,
            geom_obj,
            dominio_obj,
            ruta="$.muestras",
        )

        return MapaInstaladoFan(
            contrato_version=version,
            mapa_id=str(datos.get("mapa_id", "")),
            descripcion=str(datos.get("descripcion", "")),
            unidades=unidades_obj,
            marcos_referencia=marcos_dict,
            punto_aplicacion=punto_app_obj,
            metadatos_origen=origen_obj,
            geometria_referencia=geom_obj,
            dominio_validez=dominio_obj,
            muestras=muestras_obj,
        )

    # -------------------------------------------------------------------------
    # Regla 1: Detección y rechazo de NaN
    # -------------------------------------------------------------------------
    def _verificar_ausencia_nan(self, elemento: Any, ruta: str) -> None:
        if isinstance(elemento, float):
            if math.isnan(elemento) or math.isinf(elemento):
                raise ErrorValidacionContrato(
                    CodigoErrorValidacion.VALOR_NAN_DETECTADO,
                    f"Valor no finito o NaN detectado: {elemento}",
                    ruta=ruta,
                )
        elif isinstance(elemento, str):
            if elemento.strip().lower() in {"nan", "+nan", "-nan", "infinity", "+inf", "-inf"}:
                raise ErrorValidacionContrato(
                    CodigoErrorValidacion.VALOR_NAN_DETECTADO,
                    f"Cadena con valor numérico inválido detectada: '{elemento}'",
                    ruta=ruta,
                )
        elif isinstance(elemento, dict):
            for k, v in elemento.items():
                self._verificar_ausencia_nan(v, ruta=f"{ruta}.{k}")
        elif isinstance(elemento, list):
            for idx, item in enumerate(elemento):
                self._verificar_ausencia_nan(item, ruta=f"{ruta}[{idx}]")

    # -------------------------------------------------------------------------
    # Regla 2: Unidades presentes y no vacías
    # -------------------------------------------------------------------------
    def _validar_unidades(self, unidades: Any, ruta: str) -> UnidadesContrato:
        if not isinstance(unidades, dict):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.UNIDADES_AUSENTES,
                "El bloque 'unidades' es obligatorio y debe ser un diccionario.",
                ruta=ruta,
            )

        campos_requeridos = [
            "longitud",
            "fuerza",
            "momento",
            "velocidad",
            "densidad",
            "potencia",
            "angulo",
            "velocidad_rotacion",
            "presion",
            "temperatura",
        ]

        valores = {}
        for campo in campos_requeridos:
            val = unidades.get(campo)
            if val is None or not isinstance(val, str) or not val.strip():
                raise ErrorValidacionContrato(
                    CodigoErrorValidacion.UNIDADES_AUSENTES,
                    f"La unidad para la dimensión física '{campo}' está ausente o vacía.",
                    ruta=f"{ruta}.{campo}",
                )
            val_limpio = val.strip()
            # Validación contra el conjunto canónico permitido
            permitidas = UNIDADES_CANONICAS_VALIDAS.get(campo, set())
            if val_limpio not in permitidas:
                raise ErrorValidacionContrato(
                    CodigoErrorValidacion.UNIDADES_AUSENTES,
                    f"Unidad '{val_limpio}' no permitida para '{campo}'. Opciones válidas: {sorted(permitidas)}",
                    ruta=f"{ruta}.{campo}",
                )
            valores[campo] = val_limpio

        return UnidadesContrato(**valores)

    # -------------------------------------------------------------------------
    # Regla 3: Marcos de referencia y Punto de aplicación
    # -------------------------------------------------------------------------
    def _validar_marcos_referencia(self, marcos: Any, ruta: str) -> None:
        if not isinstance(marcos, dict):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                "El bloque 'marcos_referencia' es obligatorio y debe ser un diccionario.",
                ruta=ruta,
            )

        marco_primario = marcos.get("marco_primario")
        if not marco_primario or marco_primario not in MARCOS_REFERENCIA_VALIDOS:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                f"Marco primario '{marco_primario}' desconocido. Marcos permitidos: {sorted(MARCOS_REFERENCIA_VALIDOS)}",
                ruta=f"{ruta}.marco_primario",
            )

        definiciones = marcos.get("definiciones")
        if not isinstance(definiciones, dict) or marco_primario not in definiciones:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                f"Falta la definición detallada de ejes para el marco primario '{marco_primario}'.",
                ruta=f"{ruta}.definiciones.{marco_primario}",
            )

        def_primaria = definiciones[marco_primario]
        if not isinstance(def_primaria, dict):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                f"La definición del marco '{marco_primario}' debe ser un diccionario.",
                ruta=f"{ruta}.definiciones.{marco_primario}",
            )

        for eje in ["eje_x", "eje_y", "eje_z"]:
            if eje not in def_primaria or not isinstance(def_primaria[eje], str) or not def_primaria[eje].strip():
                raise ErrorValidacionContrato(
                    CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                    f"Descripción ausente o vacía para el eje '{eje}' en marco '{marco_primario}'.",
                    ruta=f"{ruta}.definiciones.{marco_primario}.{eje}",
                )

    def _validar_punto_aplicacion(self, punto: Any, ruta: str) -> PuntoAplicacion:
        if not isinstance(punto, dict):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                "El bloque 'punto_aplicacion' es obligatorio y debe ser un diccionario.",
                ruta=ruta,
            )

        marco = punto.get("marco_referencia")
        if not marco or marco not in MARCOS_REFERENCIA_VALIDOS:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                f"Marco de referencia del punto de aplicación '{marco}' desconocido. Permitidos: {sorted(MARCOS_REFERENCIA_VALIDOS)}",
                ruta=f"{ruta}.marco_referencia",
            )

        coords = punto.get("coordenadas_m")
        if not isinstance(coords, list) or len(coords) != 3 or not all(isinstance(c, (int, float)) for c in coords):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                "Las 'coordenadas_m' del punto de aplicación deben ser una lista de 3 números [x, y, z].",
                ruta=f"{ruta}.coordenadas_m",
            )

        desc = punto.get("descripcion", "")
        if not isinstance(desc, str) or not desc.strip():
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                "El punto de aplicación debe contener una 'descripcion' textual explícita.",
                ruta=f"{ruta}.descripcion",
            )

        return PuntoAplicacion(
            marco_referencia=marco,
            coordenadas_m=[float(c) for c in coords],
            descripcion=desc.strip(),
        )

    # -------------------------------------------------------------------------
    # Regla 4: Metadatos de origen
    # -------------------------------------------------------------------------
    def _validar_metadatos_origen(self, origen: Any, ruta: str) -> MetadatosOrigen:
        if not isinstance(origen, dict):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.CAMPO_OBLIGATORIO_FALTANTE,
                "El bloque 'metadatos_origen' es obligatorio.",
                ruta=ruta,
            )

        categoria = origen.get("categoria")
        if not categoria or categoria not in CATEGORIAS_ORIGEN_VALIDAS:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.ESTRUCTURA_INVALIDA,
                f"Categoría de origen '{categoria}' inválida. Permitidas: {sorted(CATEGORIAS_ORIGEN_VALIDAS)}",
                ruta=f"{ruta}.categoria",
            )

        es_sintetico = origen.get("es_sintetico")
        if not isinstance(es_sintetico, bool):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.CAMPO_OBLIGATORIO_FALTANTE,
                "El campo 'es_sintetico' (booleano) es obligatorio para distinguir datos sintéticos de datos medidos.",
                ruta=f"{ruta}.es_sintetico",
            )

        campos_texto = ["fuente_tipo", "instalacion_o_herramienta", "codigo_o_metodo", "referencia_caso", "fecha"]
        for c in campos_texto:
            val = origen.get(c)
            if not val or not isinstance(val, str) or not val.strip():
                raise ErrorValidacionContrato(
                    CodigoErrorValidacion.CAMPO_OBLIGATORIO_FALTANTE,
                    f"Campo obligatorio de origen '{c}' ausente o vacío.",
                    ruta=f"{ruta}.{c}",
                )

        return MetadatosOrigen(
            categoria=categoria,
            es_sintetico=es_sintetico,
            fuente_tipo=origen["fuente_tipo"].strip(),
            instalacion_o_herramienta=origen["instalacion_o_herramienta"].strip(),
            codigo_o_metodo=origen["codigo_o_metodo"].strip(),
            referencia_caso=origen["referencia_caso"].strip(),
            fecha=origen["fecha"].strip(),
            nivel_resolucion=origen.get("nivel_resolucion"),
            notas=str(origen.get("notas", "")),
        )

    # -------------------------------------------------------------------------
    # Regla 5: Geometría de referencia
    # -------------------------------------------------------------------------
    def _validar_geometria(self, geom: Any, ruta: str) -> GeometriaReferencia:
        if not isinstance(geom, dict):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                "El bloque 'geometria_referencia' es obligatorio.",
                ruta=ruta,
            )

        gid = geom.get("geometria_id")
        if not gid or not isinstance(gid, str) or not gid.strip() or gid.strip().lower() in {"desconocido", "unknown"}:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                f"Identificador de geometría '{gid}' ausente o desconocido.",
                ruta=f"{ruta}.geometria_id",
            )

        mid = geom.get("modulo_id")
        if not mid or not isinstance(mid, str) or not mid.strip():
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                "Identificador de módulo 'modulo_id' ausente o vacío.",
                ruta=f"{ruta}.modulo_id",
            )

        diam = geom.get("diametro_paso_nominal_m")
        if not isinstance(diam, (int, float)) or diam <= 0.0:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                f"Diámetro de paso nominal '{diam}' debe ser un número positivo.",
                ruta=f"{ruta}.diametro_paso_nominal_m",
            )

        radio = geom.get("radio_pala_nominal_m")
        if not isinstance(radio, (int, float)) or radio <= 0.0 or radio > diam:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                f"Radio de pala nominal '{radio}' inválido frente al diámetro de paso '{diam}'.",
                ruta=f"{ruta}.radio_pala_nominal_m",
            )

        escala = geom.get("escala_geom")
        if not isinstance(escala, (int, float)) or escala <= 0.0:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                f"Escala geométrica '{escala}' debe ser un factor positivo.",
                ruta=f"{ruta}.escala_geom",
            )

        giro = geom.get("sentido_giro")
        if not giro or giro not in SENTIDOS_GIRO_VALIDOS:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                f"Sentido de giro '{giro}' desconocido. Valores permitidos: {sorted(SENTIDOS_GIRO_VALIDOS)}",
                ruta=f"{ruta}.sentido_giro",
            )

        estados_comp = geom.get("estados_compuertas_soportados")
        if not isinstance(estados_comp, list) or len(estados_comp) == 0:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                "Debe declarar al menos un estado de compuertas soportado.",
                ruta=f"{ruta}.estados_compuertas_soportados",
            )
        for est in estados_comp:
            if est not in ESTADOS_COMPUERTA_VALIDOS:
                raise ErrorValidacionContrato(
                    CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                    f"Estado de compuerta '{est}' desconocido. Valores permitidos: {sorted(ESTADOS_COMPUERTA_VALIDOS)}",
                    ruta=f"{ruta}.estados_compuertas_soportados",
                )

        return GeometriaReferencia(
            geometria_id=gid.strip(),
            modulo_id=mid.strip(),
            diametro_paso_nominal_m=float(diam),
            radio_pala_nominal_m=float(radio),
            escala_geom=float(escala),
            sentido_giro=giro,
            estados_compuertas_soportados=estados_comp,
        )

    # -------------------------------------------------------------------------
    # Regla 6: Dominio de validez
    # -------------------------------------------------------------------------
    def _validar_dominio_validez(self, dom: Any, ruta: str) -> DominioValidez:
        if not isinstance(dom, dict):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.DOMINIO_INVALIDO,
                "El bloque 'dominio_validez' es obligatorio.",
                ruta=ruta,
            )

        rangos_req = ["densidad_kg_m3", "velocidad_modulo_m_s", "rpm", "deflexion_alabes_deg"]
        rangos_obj = {}

        for campo in rangos_req:
            r = dom.get(campo)
            if not isinstance(r, (list, tuple)) or len(r) != 2:
                raise ErrorValidacionContrato(
                    CodigoErrorValidacion.DOMINIO_INVALIDO,
                    f"Rango de dominio para '{campo}' debe ser [min, max].",
                    ruta=f"{ruta}.{campo}",
                )
            vmin, vmax = r[0], r[1]
            if not isinstance(vmin, (int, float)) or not isinstance(vmax, (int, float)) or vmin > vmax:
                raise ErrorValidacionContrato(
                    CodigoErrorValidacion.DOMINIO_INVALIDO,
                    f"Rango para '{campo}' [{vmin}, {vmax}] inconsistente.",
                    ruta=f"{ruta}.{campo}",
                )
            rangos_obj[campo] = RangoDominio(minimo=float(vmin), maximo=float(vmax))

        politica = dom.get("politica_extrapolacion", "RECHAZAR")
        if politica not in POLITICAS_EXTRAPOLACION_VALIDAS:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.DOMINIO_INVALIDO,
                f"Política de extrapolación '{politica}' desconocida. Permitidas: {sorted(POLITICAS_EXTRAPOLACION_VALIDAS)}",
                ruta=f"{ruta}.politica_extrapolacion",
            )

        return DominioValidez(
            densidad_kg_m3=rangos_obj["densidad_kg_m3"],
            velocidad_modulo_m_s=rangos_obj["velocidad_modulo_m_s"],
            rpm=rangos_obj["rpm"],
            deflexion_alabes_deg=rangos_obj["deflexion_alabes_deg"],
            politica_extrapolacion=politica,
        )

    # -------------------------------------------------------------------------
    # Regla 7: Validación de Muestras (duplicados, extrapolación, datos faltantes)
    # -------------------------------------------------------------------------
    def _validar_muestras(
        self,
        muestras: List[Any],
        geom: GeometriaReferencia,
        dom: DominioValidez,
        ruta: str,
    ) -> List[MuestraMapa]:
        huellas_vistas: Dict[Tuple, str] = {}
        resultado: List[MuestraMapa] = []

        for idx, m_raw in enumerate(muestras):
            subruta = f"{ruta}[{idx}]"
            if not isinstance(m_raw, dict):
                raise ErrorValidacionContrato(
                    CodigoErrorValidacion.ESTRUCTURA_INVALIDA,
                    "Cada muestra debe ser un diccionario.",
                    ruta=subruta,
                )

            id_m = str(m_raw.get("id_muestra", f"M_{idx:04d}"))

            # 7.1 Flujo local
            flujo_raw = m_raw.get("flujo_local")
            flujo_obj = self._validar_flujo_local(flujo_raw, ruta=f"{subruta}.flujo_local")

            # 7.2 Mando / estado
            mando_raw = m_raw.get("mando_estado")
            mando_obj = self._validar_mando_estado(mando_raw, geom, ruta=f"{subruta}.mando_estado")

            # 7.3 Comprobación de duplicados en el espacio de entradas físicas
            huella_entrada = self._generar_huella_entrada(flujo_obj, mando_obj)
            if huella_entrada in huellas_vistas:
                anterior_id = huellas_vistas[huella_entrada]
                raise ErrorValidacionContrato(
                    CodigoErrorValidacion.MUESTRAS_DUPLICADAS,
                    f"Muestra duplicada detectada: '{id_m}' tiene entradas idénticas a la muestra previa '{anterior_id}'.",
                    ruta=subruta,
                )
            huellas_vistas[huella_entrada] = id_m

            # 7.4 Comprobación de Extrapolación Declarada o fuera de dominio
            es_extrap = bool(m_raw.get("es_extrapolacion", False))
            fuera_dominio, motivo_fuera = self._verificar_fuera_dominio(flujo_obj, mando_obj, dom)

            if es_extrap:
                raise ErrorValidacionContrato(
                    CodigoErrorValidacion.EXTRAPOLACION_DECLARADA,
                    f"La muestra '{id_m}' tiene declarada explícitamente extrapolación ('es_extrapolacion': true).",
                    ruta=f"{subruta}.es_extrapolacion",
                )

            if fuera_dominio:
                raise ErrorValidacionContrato(
                    CodigoErrorValidacion.EXTRAPOLACION_DECLARADA,
                    f"La muestra '{id_m}' excede el dominio de validez declarado: {motivo_fuera}",
                    ruta=subruta,
                )

            # 7.5 Salidas: Fuerzas y Momentos vectoriales (obligatorios y 3D)
            fuerza_N = self._validar_vector_3d(m_raw.get("fuerza_vectorial_N"), ruta=f"{subruta}.fuerza_vectorial_N")
            momento_Nm = self._validar_vector_3d(m_raw.get("momento_vectorial_Nm"), ruta=f"{subruta}.momento_vectorial_Nm")

            # 7.6 Potencias eléctrica y mecánica: aceptar marcas de datos faltantes SIN convertir a 0.0
            marcas = m_raw.get("marcas_datos_faltantes", {})
            if not isinstance(marcas, dict):
                marcas = {}

            p_elec_raw = m_raw.get("potencia_electrica_W")
            p_elec_obj = self._validar_potencia_o_dato_faltante(
                p_elec_raw,
                nombre_campo="potencia_electrica_W",
                marca_faltante=marcas.get("potencia_electrica_W"),
                ruta=f"{subruta}.potencia_electrica_W",
            )

            p_mec_raw = m_raw.get("potencia_mecanica_W")
            p_mec_obj = self._validar_potencia_o_dato_faltante(
                p_mec_raw,
                nombre_campo="potencia_mecanica_W",
                marca_faltante=marcas.get("potencia_mecanica_W"),
                ruta=f"{subruta}.potencia_mecanica_W",
            )

            # 7.7 Incertidumbre
            incert_raw = m_raw.get("incertidumbre")
            incert_obj = self._validar_incertidumbre(incert_raw, ruta=f"{subruta}.incertidumbre")

            resultado.append(
                MuestraMapa(
                    id_muestra=id_m,
                    flujo_local=flujo_obj,
                    mando_estado=mando_obj,
                    fuerza_vectorial_N=fuerza_N,
                    momento_vectorial_Nm=momento_Nm,
                    potencia_electrica_W=p_elec_obj,
                    potencia_mecanica_W=p_mec_obj,
                    incertidumbre=incert_obj,
                    es_extrapolacion=es_extrap,
                    marcas_datos_faltantes=marcas,
                    notas=str(m_raw.get("notas", "")),
                )
            )

        return resultado

    def _validar_flujo_local(self, flujo: Any, ruta: str) -> EntradaFlujoLocal:
        if not isinstance(flujo, dict):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.CAMPO_OBLIGATORIO_FALTANTE,
                "El bloque 'flujo_local' es obligatorio.",
                ruta=ruta,
            )

        vel = self._validar_vector_3d(flujo.get("velocidad_vectorial_m_s"), ruta=f"{ruta}.velocidad_vectorial_m_s")
        rho = flujo.get("densidad_kg_m3")
        if not isinstance(rho, (int, float)) or rho <= 0.0:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.CAMPO_OBLIGATORIO_FALTANTE,
                f"La densidad 'densidad_kg_m3' debe ser un número positivo (obtenido: {rho}).",
                ruta=f"{ruta}.densidad_kg_m3",
            )

        t_k = flujo.get("temperatura_K", 288.15)
        if t_k is not None:
            if not isinstance(t_k, (int, float)) or t_k <= 0.0:
                raise ErrorValidacionContrato(
                    CodigoErrorValidacion.CAMPO_OBLIGATORIO_FALTANTE,
                    f"La temperatura 'temperatura_K' debe ser positiva en Kelvin.",
                    ruta=f"{ruta}.temperatura_K",
                )

        p_pa = flujo.get("presion_estatica_Pa", 101325.0)
        if p_pa is not None:
            if not isinstance(p_pa, (int, float)) or p_pa <= 0.0:
                raise ErrorValidacionContrato(
                    CodigoErrorValidacion.CAMPO_OBLIGATORIO_FALTANTE,
                    f"La presión estática 'presion_estatica_Pa' debe ser positiva en Pascales.",
                    ruta=f"{ruta}.presion_estatica_Pa",
                )

        return EntradaFlujoLocal(
            velocidad_vectorial_m_s=vel,
            densidad_kg_m3=float(rho),
            temperatura_K=float(t_k) if t_k is not None else None,
            presion_estatica_Pa=float(p_pa) if p_pa is not None else None,
        )

    def _validar_mando_estado(self, mando: Any, geom: GeometriaReferencia, ruta: str) -> EntradaMandoEstado:
        if not isinstance(mando, dict):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.CAMPO_OBLIGATORIO_FALTANTE,
                "El bloque 'mando_estado' es obligatorio.",
                ruta=ruta,
            )

        rpm = mando.get("rpm")
        if not isinstance(rpm, (int, float)) or rpm < 0.0:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.CAMPO_OBLIGATORIO_FALTANTE,
                f"RPM debe ser un número mayor o igual a cero (obtenido: {rpm}).",
                ruta=f"{ruta}.rpm",
            )

        u = mando.get("mando_normalizado")
        if not isinstance(u, (int, float)) or u < -1.0 or u > 1.0:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.CAMPO_OBLIGATORIO_FALTANTE,
                f"El mando normalizado debe estar en el intervalo [-1, 1] o [0, 1] (obtenido: {u}).",
                ruta=f"{ruta}.mando_normalizado",
            )

        deflex = mando.get("deflexion_alabes_deg")
        if not isinstance(deflex, list) or len(deflex) == 0 or not all(isinstance(d, (int, float)) for d in deflex):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.CAMPO_OBLIGATORIO_FALTANTE,
                "La deflexión de álabes 'deflexion_alabes_deg' debe ser una lista de números en grados.",
                ruta=f"{ruta}.deflexion_alabes_deg",
            )

        comp = mando.get("estado_compuerta")
        if not comp or comp not in ESTADOS_COMPUERTA_VALIDOS:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                f"Estado de compuerta '{comp}' desconocido.",
                ruta=f"{ruta}.estado_compuerta",
            )
        if comp not in geom.estados_compuertas_soportados:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS,
                f"Estado de compuerta '{comp}' no está en los soportados por la geometría: {geom.estados_compuertas_soportados}",
                ruta=f"{ruta}.estado_compuerta",
            )

        return EntradaMandoEstado(
            rpm=float(rpm),
            mando_normalizado=float(u),
            deflexion_alabes_deg=[float(d) for d in deflex],
            estado_compuerta=comp,
        )

    def _validar_vector_3d(self, v: Any, ruta: str) -> List[float]:
        if not isinstance(v, list) or len(v) != 3 or not all(isinstance(x, (int, float)) for x in v):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.ESTRUCTURA_INVALIDA,
                f"Debe ser un vector tridimensional [x, y, z] numérico (obtenido: {v}).",
                ruta=ruta,
            )
        return [float(x) for x in v]

    def _validar_potencia_o_dato_faltante(
        self,
        val: Any,
        nombre_campo: str,
        marca_faltante: Optional[str],
        ruta: str,
    ) -> Optional[Union[float, RegistroDatoFaltante]]:
        """
        Garantiza que un dato no medido o faltante sea aceptado con su marca explícita,
        y comprueba estrictamente que NO se convierta en 0.0.
        """
        # Caso 1: Estructura explícita de dato faltante
        if isinstance(val, dict) and val.get("es_dato_faltante") is True:
            estado = val.get("estado", "NO_MEDIDO")
            motivo = val.get("motivo", "")
            return RegistroDatoFaltante(estado=estado, motivo=motivo, es_dato_faltante=True)

        # Caso 2: None explícito (null en JSON)
        if val is None:
            estado_marca = marca_faltante if marca_faltante else "NO_MEDIDO"
            return RegistroDatoFaltante(
                estado=estado_marca,
                motivo=f"Campo '{nombre_campo}' marcado explícitamente como ausente/no disponible.",
                es_dato_faltante=True,
            )

        # Caso 3: Número real conocido
        if isinstance(val, (int, float)):
            # Advertencia/comprobación conceptual: si es 0.0 y no está en RPM=0, verificar
            return float(val)

        raise ErrorValidacionContrato(
            CodigoErrorValidacion.ESTRUCTURA_INVALIDA,
            f"Valor inválido para '{nombre_campo}': {val}. Debe ser float, null o estructura RegistroDatoFaltante.",
            ruta=ruta,
        )

    def _validar_incertidumbre(self, inc: Any, ruta: str) -> IncertidumbreSalidas:
        if not isinstance(inc, dict):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.CAMPO_OBLIGATORIO_FALTANTE,
                "El bloque 'incertidumbre' en cada muestra es obligatorio.",
                ruta=ruta,
            )

        u_f = self._validar_vector_3d(inc.get("fuerza_vectorial_N"), ruta=f"{ruta}.fuerza_vectorial_N")
        u_m = self._validar_vector_3d(inc.get("momento_vectorial_Nm"), ruta=f"{ruta}.momento_vectorial_Nm")

        # Verificar que las incertidumbres sean no-negativas
        if any(x < 0.0 for x in u_f) or any(x < 0.0 for x in u_m):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.ESTRUCTURA_INVALIDA,
                "Los componentes de incertidumbre deben ser no-negativos.",
                ruta=ruta,
            )

        u_pe = inc.get("potencia_electrica_W")
        if u_pe is not None and not isinstance(u_pe, (int, float, dict)):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.ESTRUCTURA_INVALIDA,
                f"Incertidumbre de potencia eléctrica inválida: {u_pe}",
                ruta=f"{ruta}.potencia_electrica_W",
            )
        u_pe_val = float(u_pe) if isinstance(u_pe, (int, float)) else None

        u_pm = inc.get("potencia_mecanica_W")
        if u_pm is not None and not isinstance(u_pm, (int, float, dict)):
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.ESTRUCTURA_INVALIDA,
                f"Incertidumbre de potencia mecánica inválida: {u_pm}",
                ruta=f"{ruta}.potencia_mecanica_W",
            )
        u_pm_val = float(u_pm) if isinstance(u_pm, (int, float)) else None

        tipo_inc = inc.get("tipo_incertidumbre", "EXPANDIDA_K2")
        if tipo_inc not in TIPOS_INCERTIDUMBRE_VALIDOS:
            raise ErrorValidacionContrato(
                CodigoErrorValidacion.ESTRUCTURA_INVALIDA,
                f"Tipo de incertidumbre '{tipo_inc}' no reconocido. Permitidos: {sorted(TIPOS_INCERTIDUMBRE_VALIDOS)}",
                ruta=f"{ruta}.tipo_incertidumbre",
            )

        conf = inc.get("nivel_confianza_pct", 95.0)
        metodo = str(inc.get("metodo_evaluacion", ""))

        return IncertidumbreSalidas(
            fuerza_vectorial_N=u_f,
            momento_vectorial_Nm=u_m,
            potencia_electrica_W=u_pe_val,
            potencia_mecanica_W=u_pm_val,
            tipo_incertidumbre=tipo_inc,
            nivel_confianza_pct=float(conf),
            metodo_evaluacion=metodo,
        )

    def _generar_huella_entrada(self, flujo: EntradaFlujoLocal, mando: EntradaMandoEstado) -> Tuple:
        """Genera una tupla cuantizada de entradas físicas para detectar duplicados."""
        tol = self.tolerancia_duplicados

        def q(val: float) -> int:
            return int(round(val / tol))

        return (
            q(flujo.velocidad_vectorial_m_s[0]),
            q(flujo.velocidad_vectorial_m_s[1]),
            q(flujo.velocidad_vectorial_m_s[2]),
            q(flujo.densidad_kg_m3),
            q(mando.rpm),
            q(mando.mando_normalizado),
            tuple(q(d) for d in mando.deflexion_alabes_deg),
            mando.estado_compuerta,
        )

    def _verificar_fuera_dominio(
        self,
        flujo: EntradaFlujoLocal,
        mando: EntradaMandoEstado,
        dom: DominioValidez,
    ) -> Tuple[bool, str]:
        """Comprueba si las entradas exceden los rangos declarados en el dominio."""
        if not dom.densidad_kg_m3.contiene(flujo.densidad_kg_m3):
            return True, f"densidad {flujo.densidad_kg_m3} fuera de [{dom.densidad_kg_m3.minimo}, {dom.densidad_kg_m3.maximo}]"

        v_mag = math.sqrt(sum(c * c for c in flujo.velocidad_vectorial_m_s))
        if not dom.velocidad_modulo_m_s.contiene(v_mag):
            return True, f"módulo de velocidad {v_mag:.2f} m/s fuera de [{dom.velocidad_modulo_m_s.minimo}, {dom.velocidad_modulo_m_s.maximo}]"

        if not dom.rpm.contiene(mando.rpm):
            return True, f"RPM {mando.rpm} fuera de [{dom.rpm.minimo}, {dom.rpm.maximo}]"

        for d in mando.deflexion_alabes_deg:
            if not dom.deflexion_alabes_deg.contiene(d):
                return True, f"deflexión de álabe {d}° fuera de [{dom.deflexion_alabes_deg.minimo}, {dom.deflexion_alabes_deg.maximo}]"

        return False, ""


# -----------------------------------------------------------------------------
# Funciones de Serialización y Carga Preservando Datos Faltantes
# -----------------------------------------------------------------------------

def cargar_mapa_json(ruta_o_str: Union[str, Path, Dict[str, Any]]) -> MapaInstaladoFan:
    """Carga y valida un mapa instalado desde archivo JSON o dict."""
    if isinstance(ruta_o_str, dict):
        datos = ruta_o_str
    else:
        ruta = Path(ruta_o_str)
        if not ruta.is_file():
            raise FileNotFoundError(f"Archivo de mapa no encontrado: {ruta}")
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)

    validador = ValidadorMapaInstalado()
    return validador.validar_dict(datos)


def guardar_mapa_json(mapa: Union[MapaInstaladoFan, Dict[str, Any]], ruta_salida: Union[str, Path]) -> None:
    """
    Serializa un mapa a JSON preservando explícitamente los valores null
    sin convertirlos en ceros.
    """
    if isinstance(mapa, MapaInstaladoFan):
        # Convertir a dict serializable preservando nulls
        raw = asdict(mapa)
        # Adaptar registros de datos faltantes para que serialicen a null en el valor
        for m in raw.get("muestras", []):
            if isinstance(m.get("potencia_electrica_W"), dict) and m["potencia_electrica_W"].get("es_dato_faltante"):
                m["potencia_electrica_W"] = None
            if isinstance(m.get("potencia_mecanica_W"), dict) and m["potencia_mecanica_W"].get("es_dato_faltante"):
                m["potencia_mecanica_W"] = None
    else:
        raw = mapa

    ruta = Path(ruta_salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2, ensure_ascii=False)


# -----------------------------------------------------------------------------
# Interfaz de Línea de Comandos (CLI)
# -----------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) < 2:
        print(f"Uso: python3 {Path(__file__).name} [validar <archivo.json> | version]")
        return 1

    cmd = sys.argv[1].lower()
    if cmd == "version":
        print(f"Contrato de Mapa Instalado v{CONTRATO_VERSION}")
        return 0

    if cmd == "validar":
        if len(sys.argv) < 3:
            print("Error: Indique la ruta del archivo JSON a validar.")
            return 1
        archivo = sys.argv[2]
        try:
            mapa = cargar_mapa_json(archivo)
            print(f"[OK] El archivo '{archivo}' cumple rigurosamente con el contrato de datos v{mapa.contrato_version}.")
            print(f"     ID Mapa: {mapa.mapa_id}")
            print(f"     Geometría: {mapa.geometria_referencia.geometria_id} ({mapa.geometria_referencia.modulo_id})")
            print(f"     Total de muestras validadas: {len(mapa.muestras)}")
            faltantes_pe = sum(1 for m in mapa.muestras if isinstance(m.potencia_electrica_W, RegistroDatoFaltante))
            faltantes_pm = sum(1 for m in mapa.muestras if isinstance(m.potencia_mecanica_W, RegistroDatoFaltante))
            print(f"     Muestras con potencia eléctrica no medida: {faltantes_pe} (preservadas como faltantes, no cero)")
            print(f"     Muestras con potencia mecánica no calculada: {faltantes_pm}")
            return 0
        except ErrorValidacionContrato as e:
            print(f"[RECHAZADO] Error de validación: {e}")
            return 2
        except Exception as e:
            print(f"[ERROR] Error inesperado durante validación: {e}")
            return 3

    print(f"Comando desconocido: '{cmd}'")
    return 1


if __name__ == "__main__":
    sys.exit(main())
