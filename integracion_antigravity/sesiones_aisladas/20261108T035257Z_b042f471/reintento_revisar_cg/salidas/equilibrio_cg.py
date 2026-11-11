#!/usr/bin/env python3
"""
===============================================================================
MÓDULO DE CHEQUEO ANALÍTICO DE EQUILIBRIO VERTICAL 2D PARA 4 FUERZAS
CONFIGURACIÓN C02 (x = ±0.160 m, y = ±0.076 m)
===============================================================================

DECLARACIÓN DEL MODELO:
- Modelo: Estático ideal de cuatro fuerzas propulsoras verticales puras (0 <= f_i <= F_max).
  No incluye mapa instalado de ventilador/conducto/álabes, ni pérdidas aerodinámicas.
- Ejes de referencia: Sistema CAD oficial de C02:
  * +x: longitudinal hacia la cola (cola en +x, nariz en -x).
  * +y: lateral hacia la izquierda/babor.
  * +z: vertical hacia arriba.
- Hipótesis de fuerzas: Sin fuerzas horizontales (Fx = Fy = 0) ni momentos aerodinámicos
  o giroscópicos externos. Empuje vertical unidireccional (+z).
- Distinción metodológica de datos:
  * Datos medidos: Ninguno (geometría C02 en fase de diseño; masa real, CG real
    e inercia real son null en C02_CANDIDATA.json; installed_map_available = false).
  * Supuestos de referencia:
    - Brazos geométricos CAD: Lx = 0.160 m, Ly = 0.076 m (C02_CANDIDATA.json).
    - Masa de integración de referencia: m = 5.0 kg (meta de diseño).
    - Aceleración de la gravedad estándar: g = 9.80665 m/s^2 (operating_reference).
    - Límites de empuje por módulo: F_max = 20.58 N (caso ideal previo) y
      F_max = 25.00 N (hipótesis complementaria de dimensionamiento).
  * Cálculos:
    - Peso estático W = m * g.
    - Condición analítica de intersección de intervalos para f4.
    - Construcción exacta y comprobación de residuales de equilibrio y cotas.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math


@dataclass(frozen=True)
class PropulsionGeometry:
    """Geometría de los 4 módulos de empuje en coordenadas CAD [m]."""
    lx: float = 0.160  # Semibrazo longitudinal [m]
    ly: float = 0.076  # Semibrazo lateral [m]

    @property
    def positions(self) -> List[Tuple[float, float]]:
        """
        Coordenadas (x_i, y_i) de los módulos 1 a 4:
        Módulo 1: (-Lx, -Ly) -> Nariz / Derecha
        Módulo 2: (-Lx, +Ly) -> Nariz / Izquierda
        Módulo 3: (+Lx, -Ly) -> Cola / Derecha
        Módulo 4: (+Lx, +Ly) -> Cola / Izquierda
        """
        return [
            (-self.lx, -self.ly),
            (-self.lx, +self.ly),
            (+self.lx, -self.ly),
            (+self.lx, +self.ly),
        ]


@dataclass(frozen=True)
class IntervalBounds:
    """Límites analíticos del intervalo para la cuarta fuerza f4."""
    # Cotas inferiores individuales
    L1: float  # de f1 >= 0: S_left - S_front
    L2: float  # de f2 <= Fmax: S_left - Fmax
    L3: float  # de f3 <= Fmax: S_rear - Fmax
    L4: float  # de f4 >= 0: 0.0

    # Cotas superiores individuales
    U1: float  # de f1 <= Fmax: S_left - S_front + Fmax
    U2: float  # de f2 >= 0: S_left
    U3: float  # de f3 >= 0: S_rear
    U4: float  # de f4 <= Fmax: Fmax

    # Intersección
    f4_min: float
    f4_max: float
    holgura: float  # f4_max - f4_min (>= 0 si admisible)
    es_admisible: bool


@dataclass
class EquilibriumSolution:
    """Resultado completo del análisis de equilibrio vertical."""
    # Parámetros de entrada
    m_kg: float
    xcg_m: float
    ycg_m: float
    Fmax_N: float
    g_m_s2: float
    W_N: float

    # Totales requeridos por bordes
    S_rear_N: float   # f3 + f4
    S_front_N: float  # f1 + f2
    S_left_N: float   # f2 + f4
    S_right_N: float  # f1 + f3

    # Estado del intervalo analítico
    intervalo: IntervalBounds
    es_factible: bool

    # Fuerzas calculadas [N]
    f1_N: Optional[float]
    f2_N: Optional[float]
    f3_N: Optional[float]
    f4_N: Optional[float]

    # Fuerzas mínimas cuadradas (pseudo-inversa sin cotas)
    f_ls_N: Tuple[float, float, float, float]

    # Residuales de equilibrio
    res_fuerza_N: float    # sum(f_i) - W
    res_momento_x_Nm: float  # sum(y_i * f_i) - y_cg * W (Balance de alabeo)
    res_momento_y_Nm: float  # sum(x_i * f_i) - x_cg * W (Balance de cabeceo)

    # Indicadores
    max_fuerza_N: Optional[float]
    min_fuerza_N: Optional[float]
    margen_fmax_N: Optional[float]
    solucion_tipo: str  # "centro_intervalo", "pseudo_inversa_proyectada", "no_factible"


def derivar_limites_f4(
    W: float,
    xcg: float,
    ycg: float,
    Fmax: float,
    geom: PropulsionGeometry = PropulsionGeometry(),
) -> Tuple[float, float, float, float, IntervalBounds]:
    """
    Deriva analíticamente las cotas inferior y superior para la cuarta fuerza f4.

    Ecuaciones de equilibrio:
      1) f1 + f2 + f3 + f4 = W
      2) -Lx*(f1 + f2) + Lx*(f3 + f4) = xcg * W
      3) -Ly*(f1 + f3) + Ly*(f2 + f4) = ycg * W

    Definiendo los totales marginales:
      S_rear  = f3 + f4 = (W / 2) * (1 + xcg / Lx)
      S_front = f1 + f2 = (W / 2) * (1 - xcg / Lx)
      S_left  = f2 + f4 = (W / 2) * (1 + ycg / Ly)
      S_right = f1 + f3 = (W / 2) * (1 - ycg / Ly)

    Despejando en función de f4:
      f3 = S_rear - f4
      f2 = S_left - f4
      f1 = S_front - S_left + f4

    Sujeto a 0 <= f_i <= Fmax para i = 1, 2, 3, 4:
      De f4: 0 <= f4 <= Fmax
      De f3: S_rear - Fmax <= f4 <= S_rear
      De f2: S_left - Fmax <= f4 <= S_left
      De f1: S_left - S_front <= f4 <= S_left - S_front + Fmax
    """
    Lx = geom.lx
    Ly = geom.ly

    S_rear = 0.5 * W * (1.0 + xcg / Lx)
    S_front = 0.5 * W * (1.0 - xcg / Lx)
    S_left = 0.5 * W * (1.0 + ycg / Ly)
    S_right = 0.5 * W * (1.0 - ycg / Ly)

    # Cotas inferiores
    L1 = S_left - S_front
    L2 = S_left - Fmax
    L3 = S_rear - Fmax
    L4 = 0.0

    # Cotas superiores
    U1 = S_left - S_front + Fmax
    U2 = S_left
    U3 = S_rear
    U4 = Fmax

    f4_min = max(L1, L2, L3, L4)
    f4_max = min(U1, U2, U3, U4)
    holgura = f4_max - f4_min
    es_admisible = (holgura >= -1e-12) and (W >= 0.0)

    bounds = IntervalBounds(
        L1=L1, L2=L2, L3=L3, L4=L4,
        U1=U1, U2=U2, U3=U3, U4=U4,
        f4_min=f4_min,
        f4_max=f4_max,
        holgura=holgura,
        es_admisible=es_admisible,
    )
    return S_rear, S_front, S_left, S_right, bounds


def calcular_fuerzas_desde_f4(
    f4: float,
    S_rear: float,
    S_front: float,
    S_left: float,
) -> Tuple[float, float, float, float]:
    """Reconstruye las cuatro fuerzas a partir de f4 y los marginales."""
    f3 = S_rear - f4
    f2 = S_left - f4
    f1 = S_front - S_left + f4
    return (f1, f2, f3, f4)


def pseudo_inversa_sin_cotas(
    W: float,
    xcg: float,
    ycg: float,
    geom: PropulsionGeometry = PropulsionGeometry(),
) -> Tuple[float, float, float, float]:
    """
    Solución analítica de mínima norma euclídea (pseudo-inversa de Moore-Penrose).
    f_LS,i = (W / 4) * (1 + x_i * xcg / Lx^2 + y_i * ycg / Ly^2)
    """
    Lx = geom.lx
    Ly = geom.ly
    positions = geom.positions
    forces = []
    for xi, yi in positions:
        fi = 0.25 * W * (1.0 + (xi * xcg) / (Lx * Lx) + (yi * ycg) / (Ly * Ly))
        forces.append(fi)
    return (forces[0], forces[1], forces[2], forces[3])


def verificar_equilibrio(
    m_kg: float = 5.0,
    xcg_m: float = 0.0,
    ycg_m: float = 0.0,
    Fmax_N: float = 20.58,
    g_m_s2: float = 9.80665,
    geom: PropulsionGeometry = PropulsionGeometry(),
    estrategia: str = "centro_intervalo",
) -> EquilibriumSolution:
    """
    Comprueba analíticamente la factibilidad del equilibrio y construye fuerzas.

    Estrategias para elegir f4 dentro de [f4_min, f4_max]:
    - 'centro_intervalo': f4 = (f4_min + f4_max) / 2 (maximiza robustez ante incertidumbres)
    - 'pseudo_inversa_proyectada': f4 proyectado al intervalo más cercano a la solución LS
    """
    W = m_kg * g_m_s2
    S_rear, S_front, S_left, S_right, bounds = derivar_limites_f4(
        W, xcg_m, ycg_m, Fmax_N, geom
    )

    f_ls = pseudo_inversa_sin_cotas(W, xcg_m, ycg_m, geom)

    if not bounds.es_admisible:
        return EquilibriumSolution(
            m_kg=m_kg,
            xcg_m=xcg_m,
            ycg_m=ycg_m,
            Fmax_N=Fmax_N,
            g_m_s2=g_m_s2,
            W_N=W,
            S_rear_N=S_rear,
            S_front_N=S_front,
            S_left_N=S_left,
            S_right_N=S_right,
            intervalo=bounds,
            es_factible=False,
            f1_N=None,
            f2_N=None,
            f3_N=None,
            f4_N=None,
            f_ls_N=f_ls,
            res_fuerza_N=float("nan"),
            res_momento_x_Nm=float("nan"),
            res_momento_y_Nm=float("nan"),
            max_fuerza_N=None,
            min_fuerza_N=None,
            margen_fmax_N=None,
            solucion_tipo="no_factible",
        )

    # Selección de f4
    f4_min = bounds.f4_min
    f4_max = bounds.f4_max

    if estrategia == "pseudo_inversa_proyectada":
        f4_ls = f_ls[3]
        f4_chosen = max(f4_min, min(f4_max, f4_ls))
        sol_tipo = "pseudo_inversa_proyectada"
    else:
        # Por defecto: centro del intervalo
        f4_chosen = 0.5 * (f4_min + f4_max)
        sol_tipo = "centro_intervalo"

    f1, f2, f3, f4 = calcular_fuerzas_desde_f4(f4_chosen, S_rear, S_front, S_left)

    # Comprobación de equilibrio estático
    pos = geom.positions
    f_total = f1 + f2 + f3 + f4
    res_fuerza = f_total - W

    # Momentos:
    # Eje x (alabeo): sum(y_i * f_i) - ycg * W = 0
    momento_x = pos[0][1] * f1 + pos[1][1] * f2 + pos[2][1] * f3 + pos[3][1] * f4
    res_momento_x = momento_x - ycg_m * W

    # Eje y (cabeceo): sum(x_i * f_i) - xcg * W = 0
    momento_y = pos[0][0] * f1 + pos[1][0] * f2 + pos[2][0] * f3 + pos[3][0] * f4
    res_momento_y = momento_y - xcg_m * W

    max_f = max(f1, f2, f3, f4)
    min_f = min(f1, f2, f3, f4)
    margen = Fmax_N - max_f

    return EquilibriumSolution(
        m_kg=m_kg,
        xcg_m=xcg_m,
        ycg_m=ycg_m,
        Fmax_N=Fmax_N,
        g_m_s2=g_m_s2,
        W_N=W,
        S_rear_N=S_rear,
        S_front_N=S_front,
        S_left_N=S_left,
        S_right_N=S_right,
        intervalo=bounds,
        es_factible=True,
        f1_N=f1,
        f2_N=f2,
        f3_N=f3,
        f4_N=f4,
        f_ls_N=f_ls,
        res_fuerza_N=res_fuerza,
        res_momento_x_Nm=res_momento_x,
        res_momento_y_Nm=res_momento_y,
        max_fuerza_N=max_f,
        min_fuerza_N=min_f,
        margen_fmax_N=margen,
        solucion_tipo=sol_tipo,
    )


def max_fuerza_vertical_admisible(
    xcg_m: float,
    ycg_m: float,
    Fmax_N: float,
    geom: PropulsionGeometry = PropulsionGeometry(),
) -> float:
    """
    Calcula analíticamente la máxima fuerza vertical Fz que el sistema de 4 módulos
    puede generar en equilibrio estático sin momentos para una posición CG dada.
    """
    Lx = geom.lx
    Ly = geom.ly
    ax = abs(xcg_m) / Lx
    ay = abs(ycg_m) / Ly

    # Si CG está fuera del polígono base [-Lx, Lx] x [-Ly, Ly], no hay sustentación posible
    if ax > 1.0 + 1e-12 or ay > 1.0 + 1e-12:
        return 0.0

    # Restricciones analíticas de capacidad vertical:
    # 1) Fz <= 4 * Fmax  (suma de los 4 motores)
    # 2) Fz * (1 + ax) / 2 <= 2 * Fmax  =>  Fz <= 4 * Fmax / (1 + ax)  (par delantero/trasero)
    # 3) Fz * (1 + ay) / 2 <= 2 * Fmax  =>  Fz <= 4 * Fmax / (1 + ay)  (par izquierdo/derecho)
    # 4) Fz * (ax + ay) / 2 <= Fmax     =>  Fz <= 2 * Fmax / (ax + ay)  (diagonal / saturación de esquina)
    limites = [
        4.0 * Fmax_N,
        4.0 * Fmax_N / (1.0 + ax),
        4.0 * Fmax_N / (1.0 + ay),
    ]

    if (ax + ay) > 1e-12:
        limites.append(2.0 * Fmax_N / (ax + ay))

    return max(0.0, min(limites))


if __name__ == "__main__":
    import sys
    print("Módulo de equilibrio analítico C02 cargado correctamente.")
    sol = verificar_equilibrio(m_kg=5.0, xcg_m=0.0, ycg_m=0.0, Fmax_N=20.58)
    print(f"Prueba nominal centrada: Factible={sol.es_factible}, W={sol.W_N:.4f} N")
    print(f"Fuerzas: f1={sol.f1_N:.4f}, f2={sol.f2_N:.4f}, f3={sol.f3_N:.4f}, f4={sol.f4_N:.4f}")
    print(f"Residuales: dW={sol.res_fuerza_N:.2e} N, dMx={sol.res_momento_x_Nm:.2e} Nm, dMy={sol.res_momento_y_Nm:.2e} Nm")
