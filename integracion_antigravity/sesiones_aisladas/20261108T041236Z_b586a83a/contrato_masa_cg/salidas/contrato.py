"""
Módulo de Contrato Versionado para Masa, Posición del Centro de Gravedad (CG)
y Tensor de Inercia respecto al CG.

Implementado en Python estándar (sin dependencias externas).
Compatible con Python 3.9+.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

VERSION_CONTRATO = "1.0.0"

# Matriz de transformación de CAD a FLU: diag(-1, -1, 1)
# CAD: X longitudinal (nariz en X negativo), Y lateral, Z vertical hacia arriba.
# FLU: X forward (hacia la nariz), Y left (izquierda), Z up (arriba).
MATRIZ_CAD_A_FLU: List[List[float]] = [
    [-1.0, 0.0, 0.0],
    [0.0, -1.0, 0.0],
    [0.0, 0.0, 1.0],
]

ADVERTENCIA_PSD_INSUFICIENTE = (
    "ADVERTENCIA FÍSICA CRÍTICA: La condición de semidefinición positiva (PSD, "
    "menores principales >= 0) es matemáticamente necesaria para garantizar que la "
    "energía cinética rotacional sea no negativa (T = 0.5 * omega^T * I * omega >= 0), "
    "pero NO ES SUFICIENTE para aceptar una medición física ni demuestra todas las "
    "restricciones de un cuerpo físico real. Un tensor PSD puede violar las desigualdades "
    "triangulares de momentos de inercia de una masa continua distribuida en 3D "
    "(I_xx + I_yy >= I_zz, I_xx + I_zz >= I_yy, I_yy + I_zz >= I_xx), no garantiza la "
    "ausencia de perturbaciones o sesgos experimentales en el banco de prueba, no asegura "
    "compatibilidad con la envolvente geométrica del vehículo, ni valida por sí sola la "
    "consistencia respecto al CG real o al teorema de Steiner."
)


class TipoNaturaleza(str, Enum):
    """Clasificación epistémica del origen del dato."""
    MEDIDO = "medido"          # Medido físicamente en banco, balanza, péndulo trifilar, etc.
    SUPUESTO = "supuesto"      # Hipótesis de diseño, presupuesto, objetivo o cota preliminar.
    CALCULADO = "calculado"    # Derivado numéricamente de CAD, mallas, integración, etc.
    NO_ASIGNADO = "no_asignado"  # Reserva o componente pendiente de definición/medición.


class MarcoReferencia(str, Enum):
    """Marcos de referencia para ejes y orientaciones."""
    CAD = "CAD"  # Ejes del modelo CAD (nariz en -X, Y lateral, Z arriba)
    FLU = "FLU"  # Flight Body Frame (X forward hacia nariz, Y left, Z up)


@dataclass
class MetadatosTrazabilidad:
    """Metadatos de trazabilidad y procedencia de cada magnitud física."""
    naturaleza: TipoNaturaleza
    fuente: str
    metodo: Optional[str] = None
    fecha: Optional[str] = None
    incertidumbre: Optional[str] = None
    notas: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "naturaleza": self.naturaleza.value if isinstance(self.naturaleza, TipoNaturaleza) else str(self.naturaleza),
            "fuente": self.fuente,
            "metodo": self.metodo,
            "fecha": self.fecha,
            "incertidumbre": self.incertidumbre,
            "notas": self.notas,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MetadatosTrazabilidad:
        naturaleza_str = data.get("naturaleza", TipoNaturaleza.NO_ASIGNADO.value)
        return cls(
            naturaleza=TipoNaturaleza(naturaleza_str),
            fuente=data.get("fuente", "desconocida"),
            metodo=data.get("metodo"),
            fecha=data.get("fecha"),
            incertidumbre=data.get("incertidumbre"),
            notas=data.get("notas"),
        )


@dataclass
class PropiedadMasa:
    """Masa con unidad y trazabilidad. Si es null, NUNCA se sustituye por cero."""
    valor_kg: Optional[float]
    unidad: str = "kg"
    trazabilidad: MetadatosTrazabilidad = field(
        default_factory=lambda: MetadatosTrazabilidad(
            naturaleza=TipoNaturaleza.NO_ASIGNADO,
            fuente="no_especificada",
        )
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valor_kg": self.valor_kg,  # Preserva None como null en JSON
            "unidad": self.unidad,
            "trazabilidad": self.trazabilidad.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PropiedadMasa:
        raw_val = data.get("valor_kg")
        val = float(raw_val) if raw_val is not None else None
        return cls(
            valor_kg=val,
            unidad=data.get("unidad", "kg"),
            trazabilidad=MetadatosTrazabilidad.from_dict(data.get("trazabilidad", {})),
        )


@dataclass
class PropiedadPosicionCG:
    """Posición del centro de gravedad con marco, origen y trazabilidad."""
    valor_m: Optional[List[float]]  # [x, y, z] o None
    unidad: str = "m"
    marco_referencia: MarcoReferencia = MarcoReferencia.CAD
    origen_referencia: str = "CAD_DATUM"  # Ej: "CAD_DATUM" o "CG_FISICO"
    trazabilidad: MetadatosTrazabilidad = field(
        default_factory=lambda: MetadatosTrazabilidad(
            naturaleza=TipoNaturaleza.NO_ASIGNADO,
            fuente="no_especificada",
        )
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valor_m": list(self.valor_m) if self.valor_m is not None else None,
            "unidad": self.unidad,
            "marco_referencia": self.marco_referencia.value if isinstance(self.marco_referencia, MarcoReferencia) else str(self.marco_referencia),
            "origen_referencia": self.origen_referencia,
            "trazabilidad": self.trazabilidad.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PropiedadPosicionCG:
        raw_val = data.get("valor_m")
        val = [float(v) for v in raw_val] if raw_val is not None else None
        marco_str = data.get("marco_referencia", MarcoReferencia.CAD.value)
        return cls(
            valor_m=val,
            unidad=data.get("unidad", "m"),
            marco_referencia=MarcoReferencia(marco_str),
            origen_referencia=data.get("origen_referencia", "CAD_DATUM"),
            trazabilidad=MetadatosTrazabilidad.from_dict(data.get("trazabilidad", {})),
        )


@dataclass
class PropiedadTensorInerciaCG:
    """Tensor de inercia 3x3 respecto al CG, con marco, unidad y trazabilidad."""
    valor_kg_m2: Optional[List[List[float]]]  # Matriz 3x3 o None
    unidad: str = "kg m^2"
    marco_referencia: MarcoReferencia = MarcoReferencia.CAD
    respecto_al_cg: bool = True
    trazabilidad: MetadatosTrazabilidad = field(
        default_factory=lambda: MetadatosTrazabilidad(
            naturaleza=TipoNaturaleza.NO_ASIGNADO,
            fuente="no_especificada",
        )
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valor_kg_m2": [list(row) for row in self.valor_kg_m2] if self.valor_kg_m2 is not None else None,
            "unidad": self.unidad,
            "marco_referencia": self.marco_referencia.value if isinstance(self.marco_referencia, MarcoReferencia) else str(self.marco_referencia),
            "respecto_al_cg": self.respecto_al_cg,
            "trazabilidad": self.trazabilidad.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PropiedadTensorInerciaCG:
        raw_val = data.get("valor_kg_m2")
        val = [[float(elem) for elem in row] for row in raw_val] if raw_val is not None else None
        marco_str = data.get("marco_referencia", MarcoReferencia.CAD.value)
        return cls(
            valor_kg_m2=val,
            unidad=data.get("unidad", "kg m^2"),
            marco_referencia=MarcoReferencia(marco_str),
            respecto_al_cg=data.get("respecto_al_cg", True),
            trazabilidad=MetadatosTrazabilidad.from_dict(data.get("trazabilidad", {})),
        )


@dataclass
class ContratoMasaCG:
    """Contrato formal versionado para propiedades de masa, CG e inercia."""
    version_esquema: str = VERSION_CONTRATO
    id_contrato: str = "CONTRATO_001"
    fecha: str = "2026-11-08"
    descripcion: str = ""
    unidades_canonicas: Dict[str, str] = field(
        default_factory=lambda: {
            "masa": "kg",
            "longitud": "m",
            "inercia": "kg m^2",
            "angulo": "rad",
        }
    )
    masa: PropiedadMasa = field(default_factory=lambda: PropiedadMasa(valor_kg=None))
    posicion_cg: PropiedadPosicionCG = field(default_factory=lambda: PropiedadPosicionCG(valor_m=None))
    tensor_inercia_cg: PropiedadTensorInerciaCG = field(
        default_factory=lambda: PropiedadTensorInerciaCG(valor_kg_m2=None)
    )
    notas_adicionales: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_esquema": self.version_esquema,
            "id_contrato": self.id_contrato,
            "fecha": self.fecha,
            "descripcion": self.descripcion,
            "unidades_canonicas": dict(self.unidades_canonicas),
            "masa": self.masa.to_dict(),
            "posicion_cg": self.posicion_cg.to_dict(),
            "tensor_inercia_cg": self.tensor_inercia_cg.to_dict(),
            "notas_adicionales": self.notas_adicionales,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContratoMasaCG:
        return cls(
            version_esquema=data.get("version_esquema", VERSION_CONTRATO),
            id_contrato=data.get("id_contrato", "CONTRATO_DESCONOCIDO"),
            fecha=data.get("fecha", ""),
            descripcion=data.get("descripcion", ""),
            unidades_canonicas=data.get("unidades_canonicas", {
                "masa": "kg",
                "longitud": "m",
                "inercia": "kg m^2",
                "angulo": "rad",
            }),
            masa=PropiedadMasa.from_dict(data.get("masa", {})),
            posicion_cg=PropiedadPosicionCG.from_dict(data.get("posicion_cg", {})),
            tensor_inercia_cg=PropiedadTensorInerciaCG.from_dict(data.get("tensor_inercia_cg", {})),
            notas_adicionales=data.get("notas_adicionales"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> ContratoMasaCG:
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class ResultadoValidacion:
    """Resultado estructurado de las comprobaciones de validación."""
    es_valido: bool
    errores: List[str] = field(default_factory=list)
    advertencias: List[str] = field(default_factory=list)
    menores_principales: Optional[Dict[str, float]] = None
    desigualdades_triangulares_cumplidas: Optional[bool] = None
    resumen_trazabilidad: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "es_valido": self.es_valido,
            "errores": list(self.errores),
            "advertencias": list(self.advertencias),
            "menores_principales": dict(self.menores_principales) if self.menores_principales else None,
            "desigualdades_triangulares_cumplidas": self.desigualdades_triangulares_cumplidas,
            "resumen_trazabilidad": dict(self.resumen_trazabilidad),
        }


# ============================================================================
# FUNCIONES DE VALIDACIÓN PURAS (PYTHON ESTÁNDAR)
# ============================================================================

def validar_matriz_3x3_finita(matriz: Any) -> Tuple[bool, Optional[str]]:
    """
    Valida que la entrada sea una matriz 3x3 cuyos 9 elementos sean números reales finitos.
    Rechaza None, dimensiones incorrectas, NaN, +Inf y -Inf.
    """
    if matriz is None:
        return False, "La matriz es null/None."
    if not isinstance(matriz, (list, tuple)) or len(matriz) != 3:
        return False, f"La matriz debe ser una lista de 3 filas, se recibió longitud {len(matriz) if isinstance(matriz, (list, tuple)) else type(matriz)}."
    for i, fila in enumerate(matriz):
        if not isinstance(fila, (list, tuple)) or len(fila) != 3:
            return False, f"La fila {i} debe tener longitud 3."
        for j, elem in enumerate(fila):
            if elem is None:
                return False, f"El elemento [{i}][{j}] es null (no se permite null dentro de matriz especificada)."
            if not isinstance(elem, (int, float)):
                return False, f"El elemento [{i}][{j}] no es numérico (tipo {type(elem)})."
            if not math.isfinite(elem):
                return False, f"El elemento [{i}][{j}]={elem} no es un número finito (NaN o Inf)."
    return True, None


def validar_simetria_matriz_3x3(matriz: List[List[float]], tol: float = 1e-9) -> Tuple[bool, Optional[str]]:
    """
    Valida que la matriz 3x3 sea simétrica dentro de la tolerancia numérica especificada:
    |M_ij - M_ji| <= tol para todo i, j.
    """
    valida, err = validar_matriz_3x3_finita(matriz)
    if not valida:
        return False, f"Fallo de validación previa al comprobar simetría: {err}"
    for i in range(3):
        for j in range(i + 1, 3):
            dif = abs(matriz[i][j] - matriz[j][i])
            if dif > tol:
                return False, (
                    f"Asimetría detectada en posiciones ({i},{j}) y ({j},{i}): "
                    f"M[{i}][{j}]={matriz[i][j]}, M[{j}][{i}]={matriz[j][i]}, "
                    f"diferencia={dif:.6e} > tolerancia={tol:.6e}."
                )
    return True, None


def validar_masa_positiva(
    masa_kg: Optional[float],
    permitir_null: bool = False,
) -> Tuple[bool, Optional[str]]:
    """
    Valida que la masa sea estrictamente positiva (> 0) y finita.
    REGLA CRÍTICA: Nunca sustituye null por cero.
    Si masa_kg es None:
      - Si permitir_null=True: es válido (se interpreta como reserva sin masa asignada).
      - Si permitir_null=False: se rechaza indicando explícitamente que la masa es null
        (pero NUNCA se asume como 0 kg).
    """
    if masa_kg is None:
        if permitir_null:
            return True, None
        return False, "La masa es null (reserva no asignada; prohibido sustituir null por cero)."
    if not isinstance(masa_kg, (int, float)):
        return False, f"La masa debe ser numérica, se recibió {type(masa_kg)}."
    if not math.isfinite(masa_kg):
        return False, f"La masa no es finita: {masa_kg}."
    if masa_kg <= 0.0:
        return False, f"La masa debe ser estrictamente positiva (> 0 kg), se recibió {masa_kg} kg."
    return True, None


def calcular_menores_principales_3x3(matriz: List[List[float]]) -> Dict[str, float]:
    """
    Calcula los 7 menores principales de una matriz simétrica 3x3:
    - 3 menores principales de orden 1 (elementos de la diagonal principal).
    - 3 menores principales de orden 2 (determinantes de submatrices 2x2 principales).
    - 1 menor principal de orden 3 (determinante completo 3x3).
    """
    m00, m01, m02 = matriz[0][0], matriz[0][1], matriz[0][2]
    m10, m11, m12 = matriz[1][0], matriz[1][1], matriz[1][2]
    m20, m21, m22 = matriz[2][0], matriz[2][1], matriz[2][2]

    # Orden 1
    d1_0 = m00
    d1_1 = m11
    d1_2 = m22

    # Orden 2
    d2_01 = m00 * m11 - m01 * m10
    d2_02 = m00 * m22 - m02 * m20
    d2_12 = m11 * m22 - m12 * m21

    # Orden 3 (determinante 3x3 por Laplace sobre la fila 0)
    det3 = (
        m00 * (m11 * m22 - m12 * m21)
        - m01 * (m10 * m22 - m12 * m20)
        + m02 * (m10 * m21 - m11 * m20)
    )

    return {
        "orden1_M00": d1_0,
        "orden1_M11": d1_1,
        "orden1_M22": d1_2,
        "orden2_M01": d2_01,
        "orden2_M02": d2_02,
        "orden2_M12": d2_12,
        "orden3_det": det3,
    }


def validar_energia_cinetica_no_negativa(
    matriz: List[List[float]],
    tol: float = 1e-12,
) -> Tuple[bool, Dict[str, float], Optional[str]]:
    """
    Valida que la energía cinética T = 0.5 * omega^T * I * omega sea no negativa para todo omega
    mediante el criterio de menores principales (semidefinición positiva / PSD).

    Para una matriz real simétrica, la semidefinición positiva exige que TODOS sus menores
    principales (de órdenes 1, 2 y 3) sean mayores o iguales a cero (con tolerancia numérica).
    """
    valida, err = validar_simetria_matriz_3x3(matriz)
    if not valida:
        return False, {}, f"Fallo al comprobar simetría para energía cinética: {err}"

    menores = calcular_menores_principales_3x3(matriz)

    # Comprobar que todos los menores principales sean >= -tol
    menores_negativos = []
    for nombre, valor in menores.items():
        if valor < -tol:
            menores_negativos.append(f"{nombre}={valor:.6e}")

    if menores_negativos:
        mensaje_err = (
            "Violación de energía cinética no negativa (la matriz no es semidefinida positiva PSD). "
            f"Menores principales negativos encontrados: {', '.join(menores_negativos)} "
            f"(tolerancia = -{tol:.2e})."
        )
        return False, menores, mensaje_err

    return True, menores, None


def verificar_desigualdades_triangulares_fisicas(
    matriz: List[List[float]],
    tol: float = 1e-9,
) -> Tuple[bool, Dict[str, float], Optional[str]]:
    """
    Verifica las desigualdades triangulares para momentos de inercia de un cuerpo rígido físico real:
    I_xx + I_yy >= I_zz
    I_xx + I_zz >= I_yy
    I_yy + I_zz >= I_xx

    ADVERTENCIA: Esta verificación ilustra por qué la semidefinición positiva (PSD) es necesaria
    pero NO suficiente para aceptar una medición física de un cuerpo real continuo.
    """
    valida, err = validar_matriz_3x3_finita(matriz)
    if not valida:
        return False, {}, err

    ixx = matriz[0][0]
    iyy = matriz[1][1]
    izz = matriz[2][2]

    dif_z = (ixx + iyy) - izz
    dif_y = (ixx + izz) - iyy
    dif_x = (iyy + izz) - ixx

    detalles = {
        "Ixx_mas_Iyy_menos_Izz": dif_z,
        "Ixx_mas_Izz_menos_Iyy": dif_y,
        "Iyy_mas_Izz_menos_Ixx": dif_x,
    }

    fallos = []
    if dif_z < -tol:
        fallos.append(f"(Ixx + Iyy) < Izz por {abs(dif_z):.6e}")
    if dif_y < -tol:
        fallos.append(f"(Ixx + Izz) < Iyy por {abs(dif_y):.6e}")
    if dif_x < -tol:
        fallos.append(f"(Iyy + Izz) < Ixx por {abs(dif_x):.6e}")

    if fallos:
        msg = (
            "Violación de desigualdades triangulares de cuerpo físico continuo: "
            + "; ".join(fallos)
            + ". Aunque el tensor pudiera ser PSD, no corresponde a una distribución "
            "de masa real en espacio tridimensional euclidiano."
        )
        return False, detalles, msg

    return True, detalles, None


# ============================================================================
# CONVERSIÓN DE COORDENADAS: CAD -> FLU APLICANDO DIAG(-1, -1, 1)
# ============================================================================

def convertir_posicion_cad_a_flu(posicion_cad: Optional[List[float]]) -> Optional[List[float]]:
    """
    Convierte un vector de posición [x, y, z] desde el marco CAD al marco FLU:
    r_FLU = diag(-1, -1, 1) * r_CAD = [-x, -y, z].

    REGLA: Si la posición es None (null), se retorna None. NUNCA se sustituye por [0,0,0].
    """
    if posicion_cad is None:
        return None
    if not isinstance(posicion_cad, (list, tuple)) or len(posicion_cad) != 3:
        raise ValueError(
            f"La posición CAD debe ser una terna [x, y, z], se recibió: {posicion_cad}"
        )
    for i, c in enumerate(posicion_cad):
        if c is None or not isinstance(c, (int, float)) or not math.isfinite(c):
            raise ValueError(f"Coordenada [{i}]={c} inválida o no finita.")

    x, y, z = float(posicion_cad[0]), float(posicion_cad[1]), float(posicion_cad[2])
    return [-x, -y, z]


def convertir_tensor_cad_a_flu(
    tensor_cad: Optional[List[List[float]]],
) -> Optional[List[List[float]]]:
    """
    Convierte un tensor de inercia 3x3 desde ejes CAD a ejes FLU:
    I_FLU = R * I_CAD * R^T, donde R = diag(-1, -1, 1).
    Dado que R = R^T = diag(-1, -1, 1), la transformación resulta:
    I_FLU[0][0] = I_xx
    I_FLU[0][1] = I_xy
    I_FLU[0][2] = -I_xz
    I_FLU[1][0] = I_yx
    I_FLU[1][1] = I_yy
    I_FLU[1][2] = -I_yz
    I_FLU[2][0] = -I_zx
    I_FLU[2][1] = -I_zy
    I_FLU[2][2] = I_zz

    REGLA: Si el tensor es None (null), se retorna None. NUNCA se sustituye por ceros.
    """
    if tensor_cad is None:
        return None

    valida, err = validar_matriz_3x3_finita(tensor_cad)
    if not valida:
        raise ValueError(f"Tensor CAD inválido para conversión: {err}")

    t = tensor_cad
    return [
        [float(t[0][0]), float(t[0][1]), -float(t[0][2])],
        [float(t[1][0]), float(t[1][1]), -float(t[1][2])],
        [-float(t[2][0]), -float(t[2][1]), float(t[2][2])],
    ]


def transformar_contrato_a_flu(contrato: ContratoMasaCG) -> ContratoMasaCG:
    """
    Transforma un ContratoMasaCG completo definido en CAD a FLU:
    - Convierte la posición CG con diag(-1, -1, 1) si está en CAD.
    - Convierte el tensor de inercia respecto al CG con R*I*R^T si está en CAD.
    - Preserva estrictamente los valores null (no los sustituye por cero).
    - Preserva unidades y metadatos de trazabilidad.
    """
    # Nueva posición
    if contrato.posicion_cg.valor_m is not None:
        if contrato.posicion_cg.marco_referencia == MarcoReferencia.CAD:
            nueva_pos = convertir_posicion_cad_a_flu(contrato.posicion_cg.valor_m)
        else:
            nueva_pos = list(contrato.posicion_cg.valor_m)
    else:
        nueva_pos = None

    # Nuevo tensor
    if contrato.tensor_inercia_cg.valor_kg_m2 is not None:
        if contrato.tensor_inercia_cg.marco_referencia == MarcoReferencia.CAD:
            nuevo_tensor = convertir_tensor_cad_a_flu(contrato.tensor_inercia_cg.valor_kg_m2)
        else:
            nuevo_tensor = [list(r) for r in contrato.tensor_inercia_cg.valor_kg_m2]
    else:
        nuevo_tensor = None

    trazabilidad_pos = MetadatosTrazabilidad.from_dict(contrato.posicion_cg.trazabilidad.to_dict())
    trazabilidad_ten = MetadatosTrazabilidad.from_dict(contrato.tensor_inercia_cg.trazabilidad.to_dict())
    trazabilidad_masa = MetadatosTrazabilidad.from_dict(contrato.masa.trazabilidad.to_dict())

    # Anotación en notas de trazabilidad
    nota_transf = "Transformado a marco FLU mediante diag(-1,-1,1)."
    trazabilidad_pos.notas = f"{trazabilidad_pos.notas or ''} [{nota_transf}]".strip()
    trazabilidad_ten.notas = f"{trazabilidad_ten.notas or ''} [{nota_transf}]".strip()

    return ContratoMasaCG(
        version_esquema=contrato.version_esquema,
        id_contrato=f"{contrato.id_contrato}_FLU",
        fecha=contrato.fecha,
        descripcion=f"{contrato.descripcion} (convertido a FLU)",
        unidades_canonicas=dict(contrato.unidades_canonicas),
        masa=PropiedadMasa(
            valor_kg=contrato.masa.valor_kg,
            unidad=contrato.masa.unidad,
            trazabilidad=trazabilidad_masa,
        ),
        posicion_cg=PropiedadPosicionCG(
            valor_m=nueva_pos,
            unidad=contrato.posicion_cg.unidad,
            marco_referencia=MarcoReferencia.FLU,
            origen_referencia=contrato.posicion_cg.origen_referencia,
            trazabilidad=trazabilidad_pos,
        ),
        tensor_inercia_cg=PropiedadTensorInerciaCG(
            valor_kg_m2=nuevo_tensor,
            unidad=contrato.tensor_inercia_cg.unidad,
            marco_referencia=MarcoReferencia.FLU,
            respecto_al_cg=contrato.tensor_inercia_cg.respecto_al_cg,
            trazabilidad=trazabilidad_ten,
        ),
        notas_adicionales=f"{contrato.notas_adicionales or ''} [Ejes convertidos a FLU]".strip(),
    )


# ============================================================================
# VALIDACIÓN GLOBAL DEL CONTRATO
# ============================================================================

def validar_contrato(
    contrato: ContratoMasaCG,
    exigir_completo: bool = False,
    tol_simetria: float = 1e-9,
    tol_psd: float = 1e-12,
) -> ResultadoValidacion:
    """
    Ejecuta la suite integral de validación sobre una instancia de ContratoMasaCG:
    1. Masa: estrictamente positiva si está presente. Si es null y exigir_completo=False,
       se respeta como reserva no asignada (NUNCA se reemplaza por cero).
    2. Posición CG: si está presente, debe ser vector finito de longitud 3.
    3. Tensor de inercia: si está presente:
       - Matriz 3x3 finita.
       - Simetría.
       - Energía cinética no negativa vía menores principales (PSD).
       - Comprobación de desigualdades triangulares físicas (advertencia).
    4. Advertencia obligatoria: PSD es necesaria pero no suficiente.
    5. Trazabilidad: distinción de medido vs supuesto vs calculado vs no asignado.
    """
    errores: List[str] = []
    advertencias: List[str] = []
    menores_principales_res: Optional[Dict[str, float]] = None
    desigualdades_cumplidas: Optional[bool] = None

    # Registrar resumen de trazabilidad
    resumen_trazabilidad = {
        "masa": contrato.masa.trazabilidad.naturaleza.value,
        "posicion_cg": contrato.posicion_cg.trazabilidad.naturaleza.value,
        "tensor_inercia_cg": contrato.tensor_inercia_cg.trazabilidad.naturaleza.value,
    }

    # 1. Validación de Masa
    valida_m, err_m = validar_masa_positiva(contrato.masa.valor_kg, permitir_null=not exigir_completo)
    if not valida_m:
        errores.append(f"Masa inválida: {err_m}")
    elif contrato.masa.valor_kg is None:
        advertencias.append(
            "Masa no asignada (null): se conserva como reserva sin masa asignada; "
            "no se infiere masa cero ni no nula."
        )

    # 2. Validación de Posición CG
    cg_val = contrato.posicion_cg.valor_m
    if cg_val is not None:
        if not isinstance(cg_val, (list, tuple)) or len(cg_val) != 3:
            errores.append(f"Posición CG debe ser un vector 3D [x, y, z], se recibió: {cg_val}")
        else:
            for idx, c in enumerate(cg_val):
                if c is None or not isinstance(c, (int, float)) or not math.isfinite(c):
                    errores.append(f"Posición CG componente [{idx}]={c} inválida o no finita.")
    else:
        if exigir_completo:
            errores.append("Posición CG es null (requerida en modo completo; nunca sustituir por cero).")
        else:
            advertencias.append("Posición CG no asignada (null).")

    # 3. Validación de Tensor de Inercia
    tensor_val = contrato.tensor_inercia_cg.valor_kg_m2
    if tensor_val is not None:
        # Finitud y dimensiones 3x3
        val_finita, err_finita = validar_matriz_3x3_finita(tensor_val)
        if not val_finita:
            errores.append(f"Tensor de inercia inválido: {err_finita}")
        else:
            # Simetría
            val_sim, err_sim = validar_simetria_matriz_3x3(tensor_val, tol=tol_simetria)
            if not val_sim:
                errores.append(f"Tensor de inercia asimétrico: {err_sim}")

            # Energía cinética no negativa vía menores principales (PSD)
            val_psd, menores, err_psd = validar_energia_cinetica_no_negativa(tensor_val, tol=tol_psd)
            menores_principales_res = menores
            if not val_psd:
                errores.append(f"Tensor de inercia no cumple energía cinética no negativa: {err_psd}")

            # Desigualdades triangulares físicas de cuerpo continuo
            desig_ok, det_desig, err_desig = verificar_desigualdades_triangulares_fisicas(tensor_val)
            desigualdades_cumplidas = desig_ok
            if not desig_ok:
                advertencias.append(f"ADVERTENCIA FÍSICA: {err_desig}")

            # Advertencia sistemática sobre PSD
            advertencias.append(ADVERTENCIA_PSD_INSUFICIENTE)
    else:
        if exigir_completo:
            errores.append("Tensor de inercia es null (requerido en modo completo; nunca sustituir por cero).")
        else:
            advertencias.append("Tensor de inercia no asignado (null).")

    es_valido = len(errores) == 0
    return ResultadoValidacion(
        es_valido=es_valido,
        errores=errores,
        advertencias=advertencias,
        menores_principales=menores_principales_res,
        desigualdades_triangulares_cumplidas=desigualdades_cumplidas,
        resumen_trazabilidad=resumen_trazabilidad,
    )


# ============================================================================
# PROTECCIÓN CONTRA SUSTITUCIÓN INDEBIDA DE NULL POR CERO
# ============================================================================

def es_reserva_no_asignada(contrato: ContratoMasaCG) -> bool:
    """
    Indica si el contrato representa una reserva o componente sin asignación completa
    (es decir, si masa, posición CG o tensor de inercia es null).
    """
    return (
        contrato.masa.valor_kg is None
        or contrato.posicion_cg.valor_m is None
        or contrato.tensor_inercia_cg.valor_kg_m2 is None
    )


def obtener_masa_estricta(contrato: ContratoMasaCG) -> float:
    """
    Obtiene el valor numérico de la masa si está asignado (> 0).
    Lanza ValueError si la masa es None (null), impidiendo taxativamente que
    códigos aguas abajo asuman silenciosamente masa cero (0.0) o masa no nula arbitraria.
    """
    if contrato.masa.valor_kg is None:
        raise ValueError(
            f"El contrato '{contrato.id_contrato}' tiene masa null (no asignada). "
            "REGLA CRÍTICA: Nunca sustituyas null por cero ni infieras masa nula o no nula."
        )
    return contrato.masa.valor_kg


# ============================================================================
# INTERFAZ DE LÍNEA DE COMANDOS (CLI)
# ============================================================================

def main() -> int:
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Herramienta CLI para validación y conversión de contratos de Masa, CG e Inercia."
    )
    parser.add_argument("archivo", help="Ruta al archivo JSON con la instancia del contrato.")
    parser.add_argument(
        "--convertir-flu",
        action="store_true",
        help="Aplica la transformación diag(-1,-1,1) para convertir posición y tensor a FLU.",
    )
    parser.add_argument(
        "--exigir-completo",
        action="store_true",
        help="Rechaza instancias que contengan campos en null (por defecto se admiten como reservas).",
    )
    parser.add_argument(
        "--guardar",
        metavar="RUTA_SALIDA",
        help="Guarda el resultado (validado o convertido) en la ruta indicada.",
    )

    args = parser.parse_args()

    try:
        with open(args.archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
        contrato = ContratoMasaCG.from_json(contenido)
    except Exception as e:
        print(f"ERROR al cargar contrato desde '{args.archivo}': {e}", file=sys.stderr)
        return 1

    if args.convertir_flu:
        contrato = transformar_contrato_a_flu(contrato)

    resultado = validar_contrato(contrato, exigir_completo=args.exigir_completo)

    print("=" * 70)
    print(f"CONTRATO: {contrato.id_contrato} (Esquema v{contrato.version_esquema})")
    print(f"ESTADO DE VALIDACIÓN: {'VÁLIDO' if resultado.es_valido else 'INVÁLIDO'}")
    print(f"TRAZABILIDAD: {resultado.resumen_trazabilidad}")
    print("=" * 70)

    if resultado.errores:
        print("\nERRORES ENCONTRADOS:")
        for err in resultado.errores:
            print(f"  [X] {err}")

    if resultado.advertencias:
        print("\nADVERTENCIAS / NOTAS TÉCNICAS:")
        for adv in resultado.advertencias:
            print(f"  [!] {adv}\n")

    if resultado.menores_principales:
        print("MENORES PRINCIPALES (PSD):")
        for k, v in resultado.menores_principales.items():
            print(f"  - {k}: {v:.6e}")

    if resultado.desigualdades_triangulares_cumplidas is not None:
        print(f"\nDESIGUALDADES TRIANGULARES FÍSICAS: {'CUMPLIDAS' if resultado.desigualdades_triangulares_cumplidas else 'VIOLADAS'}")

    if args.guardar:
        with open(args.guardar, "w", encoding="utf-8") as f:
            f.write(contrato.to_json(indent=2))
        print(f"\nContrato guardado exitosamente en '{args.guardar}'.")

    return 0 if resultado.es_valido else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())


