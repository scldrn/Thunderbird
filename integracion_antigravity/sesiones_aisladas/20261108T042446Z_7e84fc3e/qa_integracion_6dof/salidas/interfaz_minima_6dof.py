"""
interfaz_minima_6dof.py
=======================
Interfaz mínima para la integración futura de contratos de masa/CG y mapas instalados
de ventiladores con dinámica de vuelo de 6 grados de libertad (6-DOF).

Cumplimiento estricto de requisitos:
1. Transformación explícita de ejes entre CAD y FLU mediante matriz ortogonal diag(-1, -1, 1).
2. Transporte vectorial riguroso de momentos: M_cg = M_app + (r_app - r_cg) x F.
3. Rotación congruente del tensor de inercia 3x3: I_FLU = R * I_CAD * R^T.
4. Dinámica de Euler rotacional para tensor de inercia 3x3 completo (con productos de inercia).
5. Distinción explícita entre salida mecánica (F, M_app, P_mec) y entrada eléctrica (P_elec, V, I).
6. Distinción epistémica entre datos medidos, calculados y supuestos; y entre simulación y medición.
7. Preservación estricta de valores ausentes (None / null); rechazo de coerción espuria a cero.
8. Biblioteca estándar de Python (sin dependencias forzadas).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union


# =============================================================================
# ENUMERACIONES Y CONSTANTES DE REFERENCIA
# =============================================================================

class MarcoReferencia(str, Enum):
    """Marcos de referencia admitidos según C02_CANDIDATA y contratos."""
    CAD = "CAD"          # Datum CAD: Nariz en -X, Y lateral, Z hacia arriba
    FLU = "FLU"          # Flight Body: X Forward (nariz), Y Left (babor), Z Up (arriba)
    MODULO_LOCAL = "MODULO_LOCAL"  # Marco propio del ventilador en plano del rotor


class NaturalezaEpistemica(str, Enum):
    """Clasificación del origen del dato."""
    MEDIDO = "medido"          # Obtenido empíricamente en banco físico o balanza
    CALCULADO = "calculado"    # Resultado de integración CAD o dinámica numérica
    SUPUESTO = "supuesto"      # Hipótesis analítica, objetivo o cota de diseño
    NO_ASIGNADO = "no_asignado"  # Magnitud pendiente de determinación / reserva


# Matriz de rotación canónica CAD a FLU: R_FLU_from_CAD = diag(-1, -1, 1)
# Fuente: configuraciones/C02_CANDIDATA.json líneas 23-39 y contrato_masa_cg/contrato.py
MATRIZ_CAD_A_FLU: Tuple[Tuple[float, float, float], ...] = (
    (-1.0, 0.0, 0.0),
    (0.0, -1.0, 0.0),
    (0.0, 0.0, 1.0),
)


# =============================================================================
# ESTRUCTURAS DE DATOS TIPADAS
# =============================================================================

@dataclass(frozen=True)
class SalidaMecanicaVentilador:
    """
    Salida mecánica transmitida a la bancada por el módulo de ventilador.
    Expresada en el marco indicado (por defecto FLU) sobre el punto de aplicación P_app.
    """
    fuerza_vectorial_N: Tuple[float, float, float]
    momento_vectorial_Nm: Tuple[float, float, float]  # M_app: par de rotor, labio, álabes
    potencia_mecanica_W: Optional[float] = None       # P_mec = Q * omega
    marco: MarcoReferencia = MarcoReferencia.FLU
    naturaleza: NaturalezaEpistemica = NaturalezaEpistemica.SUPUESTO
    fuente: str = "desconocido"
    es_medicion: bool = False
    es_simulacion: bool = True
    notas: str = ""

    def __post_init__(self) -> None:
        if len(self.fuerza_vectorial_N) != 3:
            raise ValueError("fuerza_vectorial_N debe ser un vector de 3 componentes.")
        if len(self.momento_vectorial_Nm) != 3:
            raise ValueError("momento_vectorial_Nm debe ser un vector de 3 componentes.")
        for f in self.fuerza_vectorial_N:
            if not math.isfinite(f):
                raise ValueError("Componentes de fuerza deben ser finitas.")
        for m in self.momento_vectorial_Nm:
            if not math.isfinite(m):
                raise ValueError("Componentes de momento deben ser finitas.")
        if self.potencia_mecanica_W is not None:
            if not math.isfinite(self.potencia_mecanica_W) or self.potencia_mecanica_W < 0.0:
                raise ValueError("potencia_mecanica_W debe ser no negativa y finita.")


@dataclass(frozen=True)
class EntradaElectricaVentilador:
    """
    Entrada eléctrica consumida por el módulo motor/inversor.
    Distingue la potencia consumida de la potencia mecánica y del empuje aerodinámico.
    """
    potencia_electrica_W: Optional[float] = None
    voltaje_bus_V: Optional[float] = None
    corriente_A: Optional[float] = None
    naturaleza: NaturalezaEpistemica = NaturalezaEpistemica.SUPUESTO
    fuente: str = "desconocido"
    es_medicion: bool = False
    notas: str = ""

    def __post_init__(self) -> None:
        if self.potencia_electrica_W is not None:
            if not math.isfinite(self.potencia_electrica_W) or self.potencia_electrica_W < 0.0:
                raise ValueError("potencia_electrica_W debe ser no negativa y finita.")
        if self.voltaje_bus_V is not None:
            if not math.isfinite(self.voltaje_bus_V) or self.voltaje_bus_V < 0.0:
                raise ValueError("voltaje_bus_V debe ser no negativo y finito.")
        if self.corriente_A is not None:
            if not math.isfinite(self.corriente_A) or self.corriente_A < 0.0:
                raise ValueError("corriente_A debe ser no negativa y finita.")


@dataclass(frozen=True)
class PropiedadesInercialesVehiculo:
    """
    Propiedades inerciales del vehículo según ContratoMasaCG.
    Exige masa > 0, posición de CG y tensor 3x3 respecto al CG.
    """
    masa_kg: float
    posicion_cg_m: Tuple[float, float, float]
    tensor_inercia_cg_kgm2: Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]
    marco: MarcoReferencia = MarcoReferencia.FLU
    naturaleza_masa: NaturalezaEpistemica = NaturalezaEpistemica.SUPUESTO
    naturaleza_inercia: NaturalezaEpistemica = NaturalezaEpistemica.SUPUESTO
    fuente: str = "desconocido"

    def __post_init__(self) -> None:
        if not math.isfinite(self.masa_kg) or self.masa_kg <= 0.0:
            raise ValueError(f"masa_kg debe ser estrictamente positiva y finita, se recibió {self.masa_kg}")
        if len(self.posicion_cg_m) != 3:
            raise ValueError("posicion_cg_m debe ser una terna [x, y, z].")
        for c in self.posicion_cg_m:
            if not math.isfinite(c):
                raise ValueError("Las coordenadas del CG deben ser finitas.")
        if len(self.tensor_inercia_cg_kgm2) != 3:
            raise ValueError("tensor_inercia_cg_kgm2 debe ser una matriz 3x3.")
        for row in self.tensor_inercia_cg_kgm2:
            if len(row) != 3:
                raise ValueError("Cada fila del tensor de inercia debe tener longitud 3.")
            for val in row:
                if not math.isfinite(val):
                    raise ValueError("Elementos del tensor de inercia deben ser finitos.")


# =============================================================================
# FUNCIONES DE TRANSFORMACIÓN DE EJES (CAD <-> FLU)
# =============================================================================

def transformar_vector_cad_a_flu(vector_cad: Sequence[float]) -> List[float]:
    """
    Transforma un vector libre expresado en marco CAD al marco FLU:
    r_FLU = diag(-1, -1, 1) * r_CAD = [-x, -y, z].
    Fuente: C02_CANDIDATA.json l.23-39 y contrato_mapa_ventilador.py l.224-231.
    """
    if len(vector_cad) != 3:
        raise ValueError(f"Vector debe tener 3 componentes, longitud recibida: {len(vector_cad)}")
    for val in vector_cad:
        if val is None or not math.isfinite(val):
            raise ValueError("Componentes del vector deben ser numéricas y finitas.")
    return [-float(vector_cad[0]), -float(vector_cad[1]), float(vector_cad[2])]


def transformar_vector_flu_a_cad(vector_flu: Sequence[float]) -> List[float]:
    """
    Transforma un vector libre expresado en marco FLU al marco CAD:
    r_CAD = diag(-1, -1, 1) * r_FLU = [-x, -y, z].
    """
    if len(vector_flu) != 3:
        raise ValueError(f"Vector debe tener 3 componentes, longitud recibida: {len(vector_flu)}")
    for val in vector_flu:
        if val is None or not math.isfinite(val):
            raise ValueError("Componentes del vector deben ser numéricas y finitas.")
    return [-float(vector_flu[0]), -float(vector_flu[1]), float(vector_flu[2])]


def transformar_tensor_cad_a_flu(
    tensor_cad: Sequence[Sequence[float]],
) -> List[List[float]]:
    """
    Transforma un tensor de inercia 3x3 desde el marco CAD al marco FLU:
    I_FLU = R * I_CAD * R^T con R = diag(-1, -1, 1).
    Dado que R = R^T = diag(-1, -1, 1):
    I_FLU = [
        [ I_xx,  I_xy, -I_xz],
        [ I_yx,  I_yy, -I_yz],
        [-I_zx, -I_zy,  I_zz]
    ]
    Fuente: contrato_masa_cg/contrato.py l.497-535.
    """
    if len(tensor_cad) != 3:
        raise ValueError("El tensor debe tener 3 filas.")
    for r in tensor_cad:
        if len(r) != 3:
            raise ValueError("Cada fila del tensor debe tener 3 columnas.")
        for val in r:
            if val is None or not math.isfinite(val):
                raise ValueError("Elementos del tensor deben ser finitos.")

    t = tensor_cad
    return [
        [float(t[0][0]),  float(t[0][1]), -float(t[0][2])],
        [float(t[1][0]),  float(t[1][1]), -float(t[1][2])],
        [-float(t[2][0]), -float(t[2][1]), float(t[2][2])],
    ]


# =============================================================================
# OPERACIONES VECTORIALES Y TRANSPORTE DE MOMENTOS
# =============================================================================

def producto_vectorial(a: Sequence[float], b: Sequence[float]) -> List[float]:
    """Calcula el producto vectorial a x b en R^3."""
    return [
        float(a[1] * b[2] - a[2] * b[1]),
        float(a[2] * b[0] - a[0] * b[2]),
        float(a[0] * b[1] - a[1] * b[0]),
    ]


def transportar_momento_a_cg(
    fuerza_N: Sequence[float],
    momento_app_Nm: Sequence[float],
    r_app_m: Sequence[float],
    r_cg_m: Sequence[float],
) -> List[float]:
    """
    Transfiere el momento vectorial del punto de aplicación P_app al centro de gravedad CG:
    M_cg = M_app + (r_app - r_cg) x F

    Donde:
    - M_app: Momento propio del módulo (par de arrastre del rotor Q_rotor, momentos de álabes y labio).
    - (r_app - r_cg) x F: Momento ejercido por la fuerza instalada F respecto al CG.

    Fuente: contrato_mapa_ventilador.py l.244-271 y DOCUMENTACION_INTERFAZ.md l.52-64.
    """
    if len(fuerza_N) != 3 or len(momento_app_Nm) != 3:
        raise ValueError("fuerza_N y momento_app_Nm deben ser ternas 3D.")
    if len(r_app_m) != 3 or len(r_cg_m) != 3:
        raise ValueError("r_app_m y r_cg_m deben ser ternas de posición 3D.")

    brazo = [
        float(r_app_m[0] - r_cg_m[0]),
        float(r_app_m[1] - r_cg_m[1]),
        float(r_app_m[2] - r_cg_m[2]),
    ]

    brazo_x_f = producto_vectorial(brazo, fuerza_N)

    return [
        float(momento_app_Nm[0] + brazo_x_f[0]),
        float(momento_app_Nm[1] + brazo_x_f[1]),
        float(momento_app_Nm[2] + brazo_x_f[2]),
    ]


def combinar_propulsion_en_cg(
    salidas_mecanicas: Sequence[SalidaMecanicaVentilador],
    posiciones_fans_m: Sequence[Sequence[float]],
    posicion_cg_m: Sequence[float],
) -> Tuple[List[float], List[float]]:
    """
    Combina las fuerzas y momentos de N módulos de ventilador sobre el CG del vehículo:
    F_total = sum(F_i)
    M_total_cg = sum( M_app_i + (r_fan_i - r_cg) x F_i )

    Todas las magnitudes deben estar en el mismo marco de referencia (ej. FLU).
    """
    n = len(salidas_mecanicas)
    if len(posiciones_fans_m) != n:
        raise ValueError(
            f"El número de salidas de ventilador ({n}) no coincide con el de posiciones ({len(posiciones_fans_m)})."
        )
    if len(posicion_cg_m) != 3:
        raise ValueError("posicion_cg_m debe ser una terna 3D.")

    f_total = [0.0, 0.0, 0.0]
    m_total_cg = [0.0, 0.0, 0.0]

    for sm, r_fan in zip(salidas_mecanicas, posiciones_fans_m):
        f = sm.fuerza_vectorial_N
        m_cg_i = transportar_momento_a_cg(
            fuerza_N=f,
            momento_app_Nm=sm.momento_vectorial_Nm,
            r_app_m=r_fan,
            r_cg_m=posicion_cg_m,
        )
        f_total[0] += f[0]
        f_total[1] += f[1]
        f_total[2] += f[2]

        m_total_cg[0] += m_cg_i[0]
        m_total_cg[1] += m_cg_i[1]
        m_total_cg[2] += m_cg_i[2]

    return f_total, m_total_cg


# =============================================================================
# ÁLGEBRA MATRICIAL 3X3 PURA Y DINÁMICA ROTACIONAL 6-DOF
# =============================================================================

def determinante_3x3(m: Sequence[Sequence[float]]) -> float:
    """Calcula el determinante de una matriz 3x3."""
    return float(
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def invertir_matriz_3x3(m: Sequence[Sequence[float]]) -> List[List[float]]:
    """Calcula la matriz inversa analítica de una matriz 3x3 invertible."""
    det = determinante_3x3(m)
    if abs(det) < 1e-15:
        raise ValueError(f"Matriz singular o casi singular, det={det}")

    inv_det = 1.0 / det
    return [
        [
            (m[1][1] * m[2][2] - m[1][2] * m[2][1]) * inv_det,
            (m[0][2] * m[2][1] - m[0][1] * m[2][2]) * inv_det,
            (m[0][1] * m[1][2] - m[0][2] * m[1][1]) * inv_det,
        ],
        [
            (m[1][2] * m[2][0] - m[1][0] * m[2][2]) * inv_det,
            (m[0][0] * m[2][2] - m[0][2] * m[2][0]) * inv_det,
            (m[0][2] * m[1][0] - m[0][0] * m[1][2]) * inv_det,
        ],
        [
            (m[1][0] * m[2][1] - m[1][1] * m[2][0]) * inv_det,
            (m[0][1] * m[2][0] - m[0][0] * m[2][1]) * inv_det,
            (m[0][0] * m[1][1] - m[0][1] * m[1][0]) * inv_det,
        ],
    ]


def multiplicar_matriz_vector_3x3(
    m: Sequence[Sequence[float]], v: Sequence[float]
) -> List[float]:
    """Multiplica una matriz 3x3 por un vector columna 3D."""
    return [
        float(m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2]),
        float(m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2]),
        float(m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2]),
    ]


def calcular_aceleracion_angular_euler(
    tensor_inercia_3x3: Sequence[Sequence[float]],
    omega_rad_s: Sequence[float],
    torque_total_Nm: Sequence[float],
) -> List[float]:
    """
    Resuelve la ecuación diferencial de Euler rotacional para cuerpo rígido
    con tensor de inercia 3x3 arbitrario (diagonal o acoplado):
    I * d(omega)/dt + omega x (I * omega) = torque_total
    => d(omega)/dt = I^(-1) * [ torque_total - omega x (I * omega) ]
    """
    i_omega = multiplicar_matriz_vector_3x3(tensor_inercia_3x3, omega_rad_s)
    giroscopico = producto_vectorial(omega_rad_s, i_omega)

    rhs = [
        float(torque_total_Nm[0] - giroscopico[0]),
        float(torque_total_Nm[1] - giroscopico[1]),
        float(torque_total_Nm[2] - giroscopico[2]),
    ]

    inv_i = invertir_matriz_3x3(tensor_inercia_3x3)
    return multiplicar_matriz_vector_3x3(inv_i, rhs)


# =============================================================================
# DERIVADAS CINEMÁTICAS Y DINÁMICAS 6-DOF
# =============================================================================

def derivada_cuaternion(
    q: Sequence[float], omega_cuerpo: Sequence[float]
) -> List[float]:
    """
    Calcula la derivada temporal del cuaternión unitario de orientación [qx, qy, qz, qw]
    bajo la convención scipy/Hamilton:
    qdot = 0.5 * [ qw*w + (q_vec x w), -dot(q_vec, w) ]
    """
    qx, qy, qz, qw = q[0], q[1], q[2], q[3]
    wx, wy, wz = omega_cuerpo[0], omega_cuerpo[1], omega_cuerpo[2]

    # q_vec x w
    cross_x = qy * wz - qz * wy
    cross_y = qz * wx - qx * wz
    cross_z = qx * wy - qy * wx

    dot_val = qx * wx + qy * wy + qz * wz

    qdot_x = 0.5 * (qw * wx + cross_x)
    qdot_y = 0.5 * (qw * wy + cross_y)
    qdot_z = 0.5 * (qw * wz + cross_z)
    qdot_w = -0.5 * dot_val

    return [qdot_x, qdot_y, qdot_z, qdot_w]


def rotar_vector_por_cuaternion(q: Sequence[float], v: Sequence[float]) -> List[float]:
    """
    Aplica la rotación del cuaternión q = [qx, qy, qz, qw] a un vector v: v_rot = R(q) * v.
    """
    qx, qy, qz, qw = q[0], q[1], q[2], q[3]
    vx, vy, vz = v[0], v[1], v[2]

    # Fórmula de Rodrigues via cuaterniones: v' = v + 2*r x (r x v + w*v)
    rx, ry, rz = qx, qy, qz
    # cross1 = r x v + w*v
    c1x = ry * vz - rz * vy + qw * vx
    c1y = rz * vx - rx * vz + qw * vy
    c1z = rx * vy - ry * vx + qw * vz

    # cross2 = 2 * (r x c1)
    c2x = 2.0 * (ry * c1z - rz * c1y)
    c2y = 2.0 * (rz * c1x - rx * c1z)
    c2z = 2.0 * (rx * c1y - ry * c1x)

    return [vx + c2x, vy + c2y, vz + c2z]


def evaluar_rhs_6dof(
    estado_13: Sequence[float],
    prop_inerciales: PropiedadesInercialesVehiculo,
    salidas_ventiladores: Sequence[SalidaMecanicaVentilador],
    posiciones_fans_m: Sequence[Sequence[float]],
    fuerza_externa_inercial_N: Sequence[float] = (0.0, 0.0, 0.0),
    torque_externo_cuerpo_Nm: Sequence[float] = (0.0, 0.0, 0.0),
    g_m_s2: float = 9.80665,
) -> List[float]:
    """
    Evalúa las ecuaciones de derivadas de estado 6-DOF (RHS) para cuerpo rígido:
    Estado y = [pos(3), vel(3), q(4), omega(3)] (dimensión 13).

    Integración rigurosa:
    1. Masa positiva no nula obtenida del contrato.
    2. Tensor 3x3 completo (no asume diagonal).
    3. Combinación de M_app con r x F sobre el CG real.
    4. Distinción explícita de salidas mecánicas.
    """
    if len(estado_13) != 13:
        raise ValueError(f"estado_13 debe tener longitud 13, recibida: {len(estado_13)}")

    # Desempaquetar estado
    pos = estado_13[0:3]
    vel = estado_13[3:6]
    q = estado_13[6:10]
    omega = estado_13[10:13]

    # Normalizar cuaternión
    q_norm = math.sqrt(q[0]**2 + q[1]**2 + q[2]**2 + q[3]**2)
    if q_norm < 1e-12:
        raise ValueError("Norma de cuaternión nula o degenerada.")
    q_unit = [q[0] / q_norm, q[1] / q_norm, q[2] / q_norm, q[3] / q_norm]

    # Calcular fuerza neta y momento neto sobre el CG en marco cuerpo (FLU)
    f_prop_cuerpo, m_prop_cg_cuerpo = combinar_propulsion_en_cg(
        salidas_mecanicas=salidas_ventiladores,
        posiciones_fans_m=posiciones_fans_m,
        posicion_cg_m=prop_inerciales.posicion_cg_m,
    )

    # Aceleración lineal inercial: a_iner = (R(q) * F_cuerpo + F_ext) / masa - [0, 0, g]
    f_prop_iner = rotar_vector_por_cuaternion(q_unit, f_prop_cuerpo)
    m = prop_inerciales.masa_kg
    acc = [
        (f_prop_iner[0] + fuerza_externa_inercial_N[0]) / m,
        (f_prop_iner[1] + fuerza_externa_inercial_N[1]) / m,
        (f_prop_iner[2] + fuerza_externa_inercial_N[2]) / m - g_m_s2,
    ]

    # Cinemática de actitud: qdot
    qdot = derivada_cuaternion(q_unit, omega)

    # Dinámica rotacional: omegadot con tensor completo 3x3
    torque_total_cuerpo = [
        m_prop_cg_cuerpo[0] + torque_externo_cuerpo_Nm[0],
        m_prop_cg_cuerpo[1] + torque_externo_cuerpo_Nm[1],
        m_prop_cg_cuerpo[2] + torque_externo_cuerpo_Nm[2],
    ]
    omegadot = calcular_aceleracion_angular_euler(
        tensor_inercia_3x3=prop_inerciales.tensor_inercia_cg_kgm2,
        omega_rad_s=omega,
        torque_total_Nm=torque_total_cuerpo,
    )

    # Vector derivada ydot = [vel(3), acc(3), qdot(4), omegadot(3)]
    return [
        float(vel[0]), float(vel[1]), float(vel[2]),
        float(acc[0]), float(acc[1]), float(acc[2]),
        float(qdot[0]), float(qdot[1]), float(qdot[2]), float(qdot[3]),
        float(omegadot[0]), float(omegadot[1]), float(omegadot[2]),
    ]


# =============================================================================
# COMPROBACIÓN DE CONSISTENCIA ENERGÉTICA Y TRATAMIENTO DE FALTANTES
# =============================================================================

def comprobar_consistencia_energetica(
    mecanica: SalidaMecanicaVentilador,
    electrica: EntradaElectricaVentilador,
    tolerancia_W: float = 1e-3,
) -> Dict[str, Any]:
    """
    Comprueba la coherencia física entre la entrada eléctrica y la salida mecánica.
    Por primer y segundo principio de la termodinámica: P_mec <= P_elec (o eficiencia <= 100%).
    Preserva estrictamente el estado faltante si alguno es None, sin coercionarlo a cero.
    """
    p_mec = mecanica.potencia_mecanica_W
    p_elec = electrica.potencia_electrica_W

    if p_mec is None and p_elec is None:
        return {
            "estado": "AMBAS_NO_DISPONIBLES",
            "valido": True,
            "eficiencia": None,
            "mensaje": "Ambas potencias ausentes; preservadas como desconocidas sin alterar a cero.",
        }
    if p_mec is None:
        return {
            "estado": "MECANICA_NO_DISPONIBLE",
            "valido": True,
            "eficiencia": None,
            "mensaje": "Potencia mecánica no disponible; preservada como desconocida.",
        }
    if p_elec is None:
        return {
            "estado": "ELECTRICA_NO_DISPONIBLE",
            "valido": True,
            "eficiencia": None,
            "mensaje": "Potencia eléctrica no disponible; preservada como desconocida.",
        }

    # Ambas presentes: comprobar conservación de energía
    if p_elec == 0.0:
        if p_mec > tolerancia_W:
            return {
                "estado": "VIOLACION_TERMODINAMICA",
                "valido": False,
                "eficiencia": None,
                "mensaje": f"Potencia mecánica no nula ({p_mec:.2f} W) con potencia eléctrica 0.0 W (generación de energía de la nada).",
            }
        eficiencia = 1.0 if p_mec == 0.0 else 0.0
    else:
        eficiencia = p_mec / p_elec

    if p_mec > p_elec + tolerancia_W:
        return {
            "estado": "VIOLACION_TERMODINAMICA",
            "valido": False,
            "eficiencia": eficiencia,
            "mensaje": f"P_mec ({p_mec:.2f} W) > P_elec ({p_elec:.2f} W), eficiencia imposible ({eficiencia*100:.1f}%).",
        }

    return {
        "estado": "CONSISTENTE",
        "valido": True,
        "eficiencia": eficiencia,
        "mensaje": f"Consistente. Eficiencia electromecánica = {eficiencia*100:.1f}%.",
    }
