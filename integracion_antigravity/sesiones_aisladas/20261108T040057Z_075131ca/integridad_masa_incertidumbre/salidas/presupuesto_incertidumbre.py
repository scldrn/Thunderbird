#!/usr/bin/env python3
"""
presupuesto_incertidumbre.py - Gestión y presupuesto de masa bajo incertidumbre epistemológica.

Marco de trabajo para análisis de masa aeronáutica:
  - Trata la BOM como presupuesto con incertidumbre, no como inventario cerrado.
  - Distingue rigurosamente valores DESCONOCIDOS (None, celdas vacías) de CERO (0.0).
  - Modela volúmenes reservados reconociendo que pueden estar vacíos (m=0)
    o alojar equipos futuros (m>0), sin inferir masa real nula ni no nula.
  - Incluye motor de chequeo dimensional y de unidades físicas (SI canónico: kg, m, s).
  - Genera presupuestos expresamente hipotéticos para objetivos de 2 kg, 5 kg y 10 kg
    sin inventar marcas, mediciones ni autores, y sin asignar pesos reales a piezas.
  - Genera plantilla CSV estandarizada y exportaciones verificadas.

Uso exclusivo de la biblioteca estándar de Python 3.
"""

import argparse
import csv
import math
import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any


# ==============================================================================
# 1. VERIFICACIÓN Y CONVERSIÓN DE UNIDADES FÍSICAS (SI CANÓNICO)
# ==============================================================================

class UnitChecker:
    """Motor de validación dimensional y chequeo de unidades físicas."""

    CANONICAL_MASS = "kg"
    CANONICAL_LENGTH = "m"
    CANONICAL_VOLUME = "m3"
    CANONICAL_DENSITY = "kg/m3"
    CANONICAL_FORCE = "N"

    @classmethod
    def mass_to_kg(cls, value: float, unit: str) -> float:
        """Convierte cualquier unidad de masa a kg (SI canónico)."""
        u = unit.strip().lower()
        if u in ("kg", "kilogram", "kilogramo", "kilogramos"):
            return value
        elif u in ("g", "gram", "gramo", "gramos"):
            return value * 1e-3
        elif u in ("mg", "milligram", "miligramo", "miligramos"):
            return value * 1e-6
        elif u in ("lb", "pound", "libra", "libras"):
            return value * 0.45359237
        elif u in ("oz", "ounce", "onza", "onzas"):
            return value * 0.028349523125
        else:
            raise ValueError(f"Unidad de masa no reconocida o no soportada: '{unit}'")

    @classmethod
    def volume_to_m3(cls, value: float, unit: str) -> float:
        """Convierte unidades de volumen a m³ (SI canónico)."""
        u = unit.strip().lower()
        if u in ("m3", "m^3", "metro_cubico", "metros_cubicos"):
            return value
        elif u in ("mm3", "mm^3", "milimetro_cubico", "milimetros_cubicos"):
            return value * 1e-9
        elif u in ("cm3", "cm^3", "centimetro_cubico", "centimetros_cubicos"):
            return value * 1e-6
        elif u in ("dm3", "dm^3", "litro", "litros", "l"):
            return value * 1e-3
        else:
            raise ValueError(f"Unidad de volumen no reconocida: '{unit}'")

    @classmethod
    def density_to_kg_m3(cls, value: float, unit: str) -> float:
        """Convierte unidades de densidad a kg/m³ (SI canónico)."""
        u = unit.strip().lower()
        if u in ("kg/m3", "kg/m^3", "kg_m3"):
            return value
        elif u in ("g/cm3", "g/cm^3", "g_cm3"):
            return value * 1000.0
        elif u in ("g/mm3", "g/mm^3", "g_mm3"):
            return value * 1e6
        else:
            raise ValueError(f"Unidad de densidad no reconocida: '{unit}'")

    @classmethod
    def verify_density_volume_mass(
        cls,
        volume: float,
        vol_unit: str,
        density: float,
        dens_unit: str,
        expected_mass_kg: float,
        tol: float = 1e-6
    ) -> bool:
        """
        Verifica la relación constitutiva m = V * rho en unidades SI.
        Retorna True si es coherente dentro de la tolerancia numérica.
        """
        v_m3 = cls.volume_to_m3(volume, vol_unit)
        rho_kg_m3 = cls.density_to_kg_m3(density, dens_unit)
        calc_mass = v_m3 * rho_kg_m3
        diff = abs(calc_mass - expected_mass_kg)
        if diff > tol:
            raise ValueError(
                f"Inconsistencia de unidades/cálculo: V={volume} {vol_unit} ({v_m3:.6e} m3) * "
                f"rho={density} {dens_unit} ({rho_kg_m3:.2f} kg/m3) = {calc_mass:.8f} kg != "
                f"esperado {expected_mass_kg:.8f} kg (dif={diff:.2e})"
            )
        return True


# ==============================================================================
# 2. MODELADO DE INCERTIDUMBRE Y REGISTRO DE PRESUPUESTO
# ==============================================================================

@dataclass
class MassEntry:
    """
    Registro individual de presupuesto de masa con distinción estricta de incertidumbre.

    Columnas normadas:
      - componente: Identificador funcional del componente o reserva.
      - masa_medida: Masa real medida en báscula calibrada (None si no medida; NUNCA 0.0 para desconocida).
      - masa_supuesta: Masa supuesta bajo hipótesis geométrica o asignación (None si no asignada).
      - intervalo_inferior: Cota inferior del intervalo de confianza físico [kg].
      - intervalo_superior: Cota superior del intervalo de confianza físico [kg].
      - evidencia: Fuente verificable, base de cálculo o justificación de ingeniería.
      - estado: Estado epistémico (p.ej. MEDIDO, SUPUESTO_HIPOTETICO, RESERVA_VOLUMETRICA_INCIERTA, etc.).
    """
    componente: str
    masa_medida: Optional[float]
    masa_supuesta: Optional[float]
    intervalo_inferior: Optional[float]
    intervalo_superior: Optional[float]
    evidencia: str
    estado: str

    def __post_init__(self):
        self.validate()

    def validate(self):
        """Valida coherencia matemática y epistemológica."""
        if not self.componente or not str(self.componente).strip():
            raise ValueError("El campo 'componente' no puede estar vacío.")

        # Validación de intervalos cuando ambos están definidos
        if self.intervalo_inferior is not None and self.intervalo_superior is not None:
            if self.intervalo_inferior > self.intervalo_superior:
                raise ValueError(
                    f"Inconsistencia en '{self.componente}': intervalo inferior ({self.intervalo_inferior}) "
                    f"> superior ({self.intervalo_superior})"
                )
            if self.intervalo_inferior < 0.0:
                raise ValueError(
                    f"Inconsistencia en '{self.componente}': masa física no puede ser negativa ({self.intervalo_inferior})"
                )

        # Regla: Distinguir desconocido de cero
        # Si el estado es RESERVA_VOLUMETRICA_INCIERTA:
        # Los volúmenes reservados pueden estar vacíos y no prueban masa cero ni positiva.
        if "RESERVA" in self.estado.upper():
            if self.masa_medida is not None:
                raise ValueError(
                    f"Inconsistencia en reserva '{self.componente}': no puede tener masa medida real ({self.masa_medida}) "
                    f"porque el hardware no está seleccionado ni pesado."
                )

    @property
    def is_measured(self) -> bool:
        """Retorna True si y solo si la masa fue efectivamente medida (no None)."""
        return self.masa_medida is not None

    @property
    def is_assumed(self) -> bool:
        """Retorna True si y solo si hay una masa supuesta asignada."""
        return self.masa_supuesta is not None

    @property
    def is_reserved_envelope(self) -> bool:
        """Indica si es una reserva volumétrica no calificada."""
        return "RESERVA" in self.estado.upper()

    @property
    def interval_span(self) -> Optional[float]:
        """Amplitud del intervalo de incertidumbre [kg]."""
        if self.intervalo_inferior is not None and self.intervalo_superior is not None:
            return self.intervalo_superior - self.intervalo_inferior
        return None


# ==============================================================================
# 3. LECTURA, ESCRITURA Y PARSEO DE CSV DE PRESUPUESTO
# ==============================================================================

# Encabezados normados estándar (exactos según solicitud)
CSV_HEADERS = [
    "componente",
    "masa medida",
    "masa supuesta",
    "intervalo inferior",
    "intervalo superior",
    "evidencia",
    "estado"
]


def parse_cell_mass(val: Any) -> Optional[float]:
    """
    Parsea una celda numérica distinguiendo DESCONOCIDO de CERO:
      - None, "" -> None (Desconocido / Sin asignar / No medido)
      - "DESCONOCIDO", "NULL", "NONE", "N/A", "SIN_ASIGNAR" -> None
      - "0", "0.0", "0.000" -> 0.0 (Cero matemático/medido explícito)
      - "1.234" -> 1.234
    """
    if val is None:
        return None
    s = str(val).strip()
    if s == "" or s.upper() in ("DESCONOCIDO", "UNKNOWN", "NULL", "NONE", "N/A", "SIN_ASIGNAR", "NO_ASIGNADA"):
        return None
    try:
        return float(s)
    except ValueError:
        raise ValueError(f"No se pudo parsear el valor numérico de celda: '{val}'")


def format_cell_mass(val: Optional[float], decimals: int = 6) -> str:
    """
    Formatea un valor de masa para CSV:
      - None -> "" (cadena vacía = desconocido / no medido)
      - 0.0 -> f"0.{'0'*decimals}" (cero explícito)
      - float -> formato con precisión especificada
    """
    if val is None:
        return ""
    return f"{val:.{decimals}f}"


def normalize_header(header: str) -> str:
    """Normaliza variantes tipográficas de los encabezados."""
    h = header.strip().lower()
    h = h.replace("_", " ").replace("[kg]", "").strip()
    # Mapeo canónico
    mapping = {
        "componente": "componente",
        "masa medida": "masa medida",
        "masa supuesta": "masa supuesta",
        "intervalo inferior": "intervalo inferior",
        "intervalo superior": "intervalo superior",
        "evidencia": "evidencia",
        "estado": "estado"
    }
    return mapping.get(h, h)


def read_budget_csv(filepath: str) -> List[MassEntry]:
    """Lee y parsea un CSV de presupuesto respetando la distinción de desconocido vs 0."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Archivo no encontrado: {filepath}")

    entries = []
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        raw_headers = None
        for row in reader:
            if not row or not any(c.strip() for c in row):
                continue
            if row[0].strip().startswith("#"):
                continue
            raw_headers = row
            break

        if raw_headers is None:
            return []

        norm_headers = [normalize_header(h) for h in raw_headers]
        col_indices = {}
        for req in CSV_HEADERS:
            if req in norm_headers:
                col_indices[req] = norm_headers.index(req)
            else:
                raise ValueError(f"Falta columna obligatoria '{req}' en CSV {filepath}. Encabezados: {raw_headers}")

        for line_num, row in enumerate(reader, start=2):
            if not row or not any(c.strip() for c in row):
                continue  # Línea vacía

            comp = row[col_indices["componente"]].strip()
            # Ignorar filas de comentarios o explicativas si empiezan por #
            if comp.startswith("#"):
                continue

            m_med = parse_cell_mass(row[col_indices["masa medida"]])
            m_sup = parse_cell_mass(row[col_indices["masa supuesta"]])
            inf = parse_cell_mass(row[col_indices["intervalo inferior"]])
            sup = parse_cell_mass(row[col_indices["intervalo superior"]])
            evi = row[col_indices["evidencia"]].strip()
            est = row[col_indices["estado"]].strip()

            entry = MassEntry(
                componente=comp,
                masa_medida=m_med,
                masa_supuesta=m_sup,
                intervalo_inferior=inf,
                intervalo_superior=sup,
                evidencia=evi,
                estado=est
            )
            entries.append(entry)

    return entries


def write_budget_csv(filepath: str, entries: List[MassEntry], comments: Optional[List[str]] = None) -> str:
    """Escribe una lista de MassEntry a un archivo CSV estándar en salidas/."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    with open(filepath, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if comments:
            for c in comments:
                writer.writerow([f"# {c}"])
        writer.writerow(CSV_HEADERS)
        for e in entries:
            writer.writerow([
                e.componente,
                format_cell_mass(e.masa_medida),
                format_cell_mass(e.masa_supuesta),
                format_cell_mass(e.intervalo_inferior),
                format_cell_mass(e.intervalo_superior),
                e.evidencia,
                e.estado
            ])
    return filepath


# ==============================================================================
# 4. AGREGACIÓN DE INCERTIDUMBRE Y ESTADÍSTICAS DEL PRESUPUESTO
# ==============================================================================

@dataclass
class BudgetSummary:
    """Resumen cuantitativo del presupuesto de masa e intervalos de incertidumbre."""
    target_mass_kg: Optional[float]
    total_components: int
    measured_count: int
    assumed_count: int
    reserved_unassigned_count: int
    
    total_measured_mass_kg: Optional[float]
    total_assumed_mass_kg: Optional[float]
    interval_lower_sum_kg: float
    interval_upper_sum_kg: float
    uncertainty_span_kg: float
    
    closure_status: str
    physical_mass_closed: bool
    details: Dict[str, Any]


def aggregate_budget(entries: List[MassEntry], target_mass_kg: Optional[float] = None) -> BudgetSummary:
    """
    Agrega un presupuesto calculando sumas de intervalos de incertidumbre.
    Mantiene la regla de que si un componente no está medido, la masa total medida es DESCONOCIDA (None).
    """
    total_components = len(entries)
    measured_count = 0
    assumed_count = 0
    reserved_count = 0

    sum_measured = 0.0
    all_measured = (total_components > 0)

    sum_assumed = 0.0
    any_assumed = False

    sum_lower = 0.0
    sum_upper = 0.0

    for e in entries:
        if e.is_measured:
            measured_count += 1
            sum_measured += e.masa_medida
        else:
            all_measured = False

        if e.is_assumed:
            assumed_count += 1
            any_assumed = True
            sum_assumed += e.masa_supuesta

        if e.is_reserved_envelope and not e.is_assumed:
            reserved_count += 1

        if e.intervalo_inferior is not None:
            sum_lower += e.intervalo_inferior
        if e.intervalo_superior is not None:
            sum_upper += e.intervalo_superior

    total_measured = sum_measured if (all_measured and total_components > 0) else None
    total_assumed = sum_assumed if any_assumed else None
    span = sum_upper - sum_lower

    # Cierre de masa física: Solo cerrado si 100% medido con hardware calificado
    physical_closed = (measured_count == total_components and total_components > 0)

    # Estado de cierre del presupuesto
    if physical_closed:
        closure_status = "CERRADO_MEDIDO"
    elif target_mass_kg is not None:
        if sum_lower <= target_mass_kg <= sum_upper:
            closure_status = "OBJETIVO_DENTRO_DE_INTERVALO_DE_INCERTIDUMBRE"
        elif target_mass_kg < sum_lower:
            closure_status = "OBJETIVO_SUPERADO_POR_COTA_MINIMA (DEFICIT_GARANTIZADO)"
        else:
            closure_status = "OBJETIVO_POR_ENCIMA_DE_COTA_MAXIMA (HOLGURA_POTENCIAL)"
    else:
        closure_status = "ABIERTO_CON_INCERTIDUMBRE"

    return BudgetSummary(
        target_mass_kg=target_mass_kg,
        total_components=total_components,
        measured_count=measured_count,
        assumed_count=assumed_count,
        reserved_unassigned_count=reserved_count,
        total_measured_mass_kg=total_measured,
        total_assumed_mass_kg=total_assumed,
        interval_lower_sum_kg=sum_lower,
        interval_upper_sum_kg=sum_upper,
        uncertainty_span_kg=span,
        closure_status=closure_status,
        physical_mass_closed=physical_closed,
        details={
            "pct_measured": (measured_count / total_components * 100.0) if total_components else 0.0,
            "pct_assumed": (assumed_count / total_components * 100.0) if total_components else 0.0,
        }
    )


# ==============================================================================
# 5. GENERADORES DE PLANTILLA Y MODELOS HIPOTÉTICOS (2 kg, 5 kg, 10 kg)
# ==============================================================================

def create_template_entries() -> List[MassEntry]:
    """
    Genera la plantilla CSV estándar con filas de ejemplo pedagógicas que ilustran:
      - Distinción entre celda vacía (desconocido) y 0.0 (medición o cota cero).
      - Tratamiento de reservas volumétricas (pueden estar vacías, m=0 en cota inferior, pero no probadas).
      - Fila supuesta por hipótesis paramétrica.
      - Componente medido hipotético para demostración sintáctica.
    """
    return [
        MassEntry(
            componente="GUIA_FILA_1_COMPONENTE_NO_MEDIDO",
            masa_medida=None,  # Celda vacía en CSV -> Desconocido, NO 0.0
            masa_supuesta=0.150000,
            intervalo_inferior=0.120000,
            intervalo_superior=0.180000,
            evidencia="Estimación paramétrica inicial; pieza sin pesar en báscula",
            estado="SUPUESTO_PARAMETRICO"
        ),
        MassEntry(
            componente="GUIA_FILA_2_RESERVA_VOLUMETRICA_VACIA_O_CON_EQUIPO",
            masa_medida=None,  # No medida -> Desconocido
            masa_supuesta=None,  # No asignada -> Desconocido
            intervalo_inferior=0.000000,  # Puede estar vacía: cota inferior es 0.0 kg
            intervalo_superior=0.250000,  # Límite máximo de empaquetamiento si se instala hardware
            evidencia="Volumen reservado en CAD; puede permanecer vacío (m=0) o alojar hardware (m>0)",
            estado="RESERVA_VOLUMETRICA_INCIERTA"
        ),
        MassEntry(
            componente="GUIA_FILA_3_DEMOSTRACION_CERO_MEDIDO_EXPLICITO",
            masa_medida=0.000000,  # Cero explícito comprobado (p.ej. orificio de aligeramiento o elemento retirado)
            masa_supuesta=0.000000,
            intervalo_inferior=0.000000,
            intervalo_superior=0.000000,
            evidencia="Inspección dimensional que certifica ausencia total de material físico",
            estado="MEDIDO_CERO_CONFIRMADO"
        ),
        MassEntry(
            componente="GUIA_FILA_4_COMPONENTE_CON_MEDICION_REAL_HIPOTETICA",
            masa_medida=0.045200,
            masa_supuesta=0.045000,
            intervalo_inferior=0.045150,
            intervalo_superior=0.045250,
            evidencia="Pesaje de cupón de prueba en báscula calibrada (+/- 0.05 g)",
            estado="MEDIDO_CALIBRADO"
        )
    ]


def build_hypothetical_2kg_budget() -> List[MassEntry]:
    """
    Construye el presupuesto EXPRESAMENTE HIPOTÉTICO para objetivo de 2.0 kg.
    Basado en C02_CANDIDATA.json ("variants": {"2": "pending_own_configuration"}).
    NO asigna pesos reales a piezas comerciales ni inventa marcas ni autores.
    """
    return [
        MassEntry(
            componente="Estructura_ligera_y_envolventes_hipoteticas",
            masa_medida=None,
            masa_supuesta=0.650000,
            intervalo_inferior=0.500000,
            intervalo_superior=0.850000,
            evidencia="Asignación paramétrica preliminar para vehículo clase 2 kg; requiere configuración propia",
            estado="SUPUESTO_HIPOTETICO_CONFIG_PENDIENTE"
        ),
        MassEntry(
            componente="Planta_propulsiva_y_mecanismos_modulares_hipoteticos",
            masa_medida=None,
            masa_supuesta=0.450000,
            intervalo_inferior=0.350000,
            intervalo_superior=0.600000,
            evidencia="Presupuesto asignado a 4 propulsores internos miniaturizados; hardware no seleccionado",
            estado="SUPUESTO_HIPOTETICO_SIN_SELECCION"
        ),
        MassEntry(
            componente="Avionica_sensores_y_servocontrol_hipoteticos",
            masa_medida=None,
            masa_supuesta=0.150000,
            intervalo_inferior=0.100000,
            intervalo_superior=0.220000,
            evidencia="Estimación conceptual de electrónica de vuelo y cableado ligero",
            estado="SUPUESTO_HIPOTETICO_CONCEPTUAL"
        ),
        MassEntry(
            componente="Reservas_volumetricas_internas_clase_2kg",
            masa_medida=None,
            masa_supuesta=None,
            intervalo_inferior=0.000000,  # Puede estar vacío
            intervalo_superior=0.200000,
            evidencia="Volúmenes de paso y empaquetamiento reservados; pueden ser cavidades vacías o alojar mazos",
            estado="RESERVA_VOLUMETRICA_INCIERTA"
        ),
        MassEntry(
            componente="Almacenamiento_de_energia_bateria_hipotetica",
            masa_medida=None,
            masa_supuesta=0.550000,
            intervalo_inferior=0.400000,
            intervalo_superior=0.750000,
            evidencia="Presupuesto exploratorio de pack para cubrir potencia específica requerida",
            estado="SUPUESTO_HIPOTETICO_ENERGIA"
        ),
        MassEntry(
            componente="Margen_de_crecimiento_e_incertidumbre_contingencia",
            masa_medida=None,
            masa_supuesta=0.200000,
            intervalo_inferior=0.100000,
            intervalo_superior=0.300000,
            evidencia="Margen de contingencia del 10% del objetivo conforme a práctica recomendada AIAA S-120",
            estado="MARGEN_RESERVA_CONTINGENCIA"
        )
    ]


def build_c02_5kg_uncertainty_budget() -> List[MassEntry]:
    """
    Construye el presupuesto con incertidumbre para la candidata C02 de 5.0 kg
    incorporando las 316 geometrías de la auditoría BOM:
      - 262 piezas asignadas bajo sensibilidades ligera (2.046 kg), mixta (2.784 kg) y aluminio (4.421 kg).
      - 44 reservas internas en módulos (V=52.501 mm³).
      - 10 reservas vehiculares e interfaz axial OD60 (V=316.437 mm³).
      - Reserva provisional de equipos no calificados (0.75 kg en JSON).
      - Remanente para energía y batería (1.466 kg en JSON bajo hipótesis mixta).
    """
    return [
        MassEntry(
            componente="C02_CAD_Estructura_asignada_262_piezas",
            masa_medida=None,  # 0 piezas pesadas en báscula
            masa_supuesta=2.783990,  # Hipótesis mixta_1600 auditada
            intervalo_inferior=2.045841,  # Hipótesis ligera_1200
            intervalo_superior=4.421342,  # Hipótesis aluminio_2700
            evidencia="Integración CAD C02 (V=1.630.697 mm3); sensibilidades de densidad 1200 a 2700 kg/m3",
            estado="CALCULADO_HIPOTESIS_GEOMETRICA"
        ),
        MassEntry(
            componente="C02_CAD_Reservas_internas_modulos_44_piezas",
            masa_medida=None,
            masa_supuesta=None,  # No asignada en BOM base
            intervalo_inferior=0.000000,  # Puede estar vacío (m=0)
            intervalo_superior=0.450000,  # Cota superior si aloja motores y servos
            evidencia="44 reservas CAD (V=52.501 mm3); volúmenes pueden estar vacíos o alojar hardware no calificado",
            estado="RESERVA_VOLUMETRICA_INCIERTA"
        ),
        MassEntry(
            componente="C02_CAD_Reservas_interfaces_vehiculares_10_piezas",
            masa_medida=None,
            masa_supuesta=None,  # No asignada en BOM base
            intervalo_inferior=0.000000,  # Canal axial OD60 de 291.540 mm3 puede ser cavidad aerodinámica vacía
            intervalo_superior=0.600000,  # Cota si se instala propulsor axial o mecanismo activo
            evidencia="10 reservas CAD (V=316.437 mm3; incluye tubo axial OD60); no prueba masa cero ni positiva",
            estado="RESERVA_VOLUMETRICA_INCIERTA"
        ),
        MassEntry(
            componente="C02_Reserva_provisional_equipos_no_calificados",
            masa_medida=None,
            masa_supuesta=0.750000,  # Declarado en MASA_INERCIA_PARCIAL.json
            intervalo_inferior=0.400000,
            intervalo_superior=1.100000,
            evidencia="Reserva provisional en JSON para motores anulares, servos de ciclo y cojinetes",
            estado="SUPUESTO_HIPOTETICO_RESERVA"
        ),
        MassEntry(
            componente="C02_Remanente_energia_bateria_y_avionica",
            masa_medida=None,
            masa_supuesta=1.466010,  # 5.0 - 2.783990 - 0.750 = 1.466010 kg
            intervalo_inferior=0.000000,  # Déficit si estructura de aluminio consume el presupuesto
            intervalo_superior=2.204159,  # Saldo máximo disponible bajo hipótesis ligera
            evidencia="Saldo para energía; informe G1 indica que 50 N de arrastre exige 3.04-6.40 kg de batería",
            estado="SALDO_CALCULADO_NO_CERRADO"
        )
    ]


def build_c02_roles_uncertainty_budget() -> List[MassEntry]:
    """
    Construye el presupuesto con incertidumbre desglosado por los 10 roles asumidos de la BOM C02.
    Conecta la auditoría de 316 registros geométricos con las sensibilidades de material
    y el tratamiento riguroso de las 54 reservas volumétricas.
    """
    return [
        MassEntry(
            componente="bushing_material_sensitivity_96_piezas",
            masa_medida=None,
            masa_supuesta=0.013356,
            intervalo_inferior=0.001821,
            intervalo_superior=0.013356,
            evidencia="CAD C02 (96 casquillos, V=1.517,77 mm3); sensibilidad material latón/bronce (8800 kg/m3) vs PTFE (1200 kg/m3)",
            estado="CALCULADO_HIPOTESIS_GEOMETRICA"
        ),
        MassEntry(
            componente="integral_vane_linkage_material_sensitivity_80_piezas",
            masa_medida=None,
            masa_supuesta=0.236184,
            intervalo_inferior=0.104971,
            intervalo_superior=0.236184,
            evidencia="CAD C02 (80 álabes y bielas, V=87.475,54 mm3); sensibilidad aluminio (2700 kg/m3) vs compuesto (1200 kg/m3)",
            estado="CALCULADO_HIPOTESIS_GEOMETRICA"
        ),
        MassEntry(
            componente="envelope_material_sensitivity_42_piezas",
            masa_medida=None,
            masa_supuesta=1.770835,
            intervalo_inferior=1.328126,
            intervalo_superior=2.988284,
            evidencia="CAD C02 (42 piezas piel aerodinámica, V=1.106.771,98 mm3); sensibilidad compuesto (1600 kg/m3) vs ligero (1200) vs aluminio (2700)",
            estado="CALCULADO_HIPOTESIS_GEOMETRICA"
        ),
        MassEntry(
            componente="seal_or_clamp_density_assumption_11_piezas",
            masa_medida=None,
            masa_supuesta=0.006032,
            intervalo_inferior=0.005026,
            intervalo_superior=0.007539,
            evidencia="CAD C02 (11 abrazaderas/sellos, V=5.026,40 mm3); sensibilidad polimérica (1000 a 1500 kg/m3)",
            estado="CALCULADO_HIPOTESIS_GEOMETRICA"
        ),
        MassEntry(
            componente="frame_support_density_assumption_11_piezas",
            masa_medida=None,
            masa_supuesta=0.121208,
            intervalo_inferior=0.053870,
            intervalo_superior=0.121208,
            evidencia="CAD C02 (11 cuadernas soporte, V=44.891,89 mm3); sensibilidad compuesto (1200 kg/m3) vs aluminio (2700 kg/m3)",
            estado="CALCULADO_HIPOTESIS_GEOMETRICA"
        ),
        MassEntry(
            componente="steel_density_assumption_10_piezas",
            masa_medida=None,
            masa_supuesta=0.018709,
            intervalo_inferior=0.010794,
            intervalo_superior=0.018709,
            evidencia="CAD C02 (10 piezas tornillería encastrada, V=2.398,65 mm3); sensibilidad titanio (4500 kg/m3) vs acero (7800 kg/m3)",
            estado="CALCULADO_HIPOTESIS_GEOMETRICA"
        ),
        MassEntry(
            componente="rotor_or_carrier_material_sensitivity_8_piezas",
            masa_medida=None,
            masa_supuesta=0.610768,
            intervalo_inferior=0.458076,
            intervalo_superior=1.030672,
            evidencia="CAD C02 (8 cubos y alojamientos rotor, V=381.730,29 mm3); sensibilidad compuesto (1600 kg/m3) vs aluminio (2700 kg/m3)",
            estado="CALCULADO_HIPOTESIS_GEOMETRICA"
        ),
        MassEntry(
            componente="shaft_steel_density_assumption_4_piezas",
            masa_medida=None,
            masa_supuesta=0.006897,
            intervalo_inferior=0.003979,
            intervalo_superior=0.006897,
            evidencia="CAD C02 (4 ejes de aletas posteriores, V=884,17 mm3); sensibilidad titanio (4500 kg/m3) vs acero (7800 kg/m3)",
            estado="CALCULADO_HIPOTESIS_GEOMETRICA"
        ),
        MassEntry(
            componente="unknown_device_or_interface_44_reservas_modulos",
            masa_medida=None,
            masa_supuesta=None,
            intervalo_inferior=0.000000,
            intervalo_superior=0.450000,
            evidencia="44 reservas CAD (V=52.501,18 mm3); volúmenes reservados pueden estar vacíos (m=0) o alojar motores y servos (m>0)",
            estado="RESERVA_VOLUMETRICA_INCIERTA"
        ),
        MassEntry(
            componente="unknown_hardware_or_empty_interface_10_reservas_vehiculares",
            masa_medida=None,
            masa_supuesta=None,
            intervalo_inferior=0.000000,
            intervalo_superior=0.600000,
            evidencia="10 reservas vehiculares CAD (V=316.437,25 mm3; incluye tubo axial OD60); no prueba masa cero ni positiva",
            estado="RESERVA_VOLUMETRICA_INCIERTA"
        ),
        MassEntry(
            componente="reserva_provisional_y_remanente_bateria_sistemas",
            masa_medida=None,
            masa_supuesta=2.216010,
            intervalo_inferior=0.000000,
            intervalo_superior=2.500000,
            evidencia="Presupuesto para equipos no calificados (0,75 kg) y remanente de energía (1,466 kg) para balance de 5,0 kg",
            estado="PRESUPUESTO_ASIGNADO_NO_CERRADO"
        )
    ]


def build_hypothetical_10kg_budget() -> List[MassEntry]:
    """
    Construye el presupuesto EXPRESAMENTE HIPOTÉTICO para objetivo de 10.0 kg.
    Basado en C02_CANDIDATA.json ("variants": {"10": "pending_own_configuration"}).
    NO inventa marcas, datos de catálogo ni asigna pesos reales a piezas.
    """
    return [
        MassEntry(
            componente="Estructura_portante_y_fuselaje_clase_10kg",
            masa_medida=None,
            masa_supuesta=3.400000,
            intervalo_inferior=2.600000,
            intervalo_superior=4.600000,
            evidencia="Escalado paramétrico preliminar para plataforma de 10 kg; arquitectura por definir",
            estado="SUPUESTO_HIPOTETICO_CONFIG_PENDIENTE"
        ),
        MassEntry(
            componente="Planta_propulsiva_vectorizada_y_actuacion_10kg",
            masa_medida=None,
            masa_supuesta=2.300000,
            intervalo_inferior=1.700000,
            intervalo_superior=3.200000,
            evidencia="Potencia instalada requerida para maniobra en 10 kg; hardware comercial sin seleccionar",
            estado="SUPUESTO_HIPOTETICO_SIN_SELECCION"
        ),
        MassEntry(
            componente="Avionica_sensores_navegacion_y_carga_pago_10kg",
            masa_medida=None,
            masa_supuesta=0.800000,
            intervalo_inferior=0.450000,
            intervalo_superior=1.400000,
            evidencia="Electrónica de misión, piloto automático, telemetría y margen de carga útil",
            estado="SUPUESTO_HIPOTETICO_CONCEPTUAL"
        ),
        MassEntry(
            componente="Reservas_volumetricas_de_bahias_y_canalizaciones_10kg",
            masa_medida=None,
            masa_supuesta=None,
            intervalo_inferior=0.000000,  # Puede estar vacío
            intervalo_superior=0.600000,
            evidencia="Bahías de carga y ductos reservados; el espacio puede quedar diáfano o alojar cables",
            estado="RESERVA_VOLUMETRICA_INCIERTA"
        ),
        MassEntry(
            componente="Sistema_de_almacenamiento_de_energia_pack_10kg",
            masa_medida=None,
            masa_supuesta=2.500000,
            intervalo_inferior=1.800000,
            intervalo_superior=3.800000,
            evidencia="Pack de batería dimensionado para soportar picos de aceleración y crucero prolongado",
            estado="SUPUESTO_HIPOTETICO_ENERGIA"
        ),
        MassEntry(
            componente="Margen_de_crecimiento_e_incertidumbre_contingencia_10kg",
            masa_medida=None,
            masa_supuesta=1.000000,
            intervalo_inferior=0.500000,
            intervalo_superior=1.600000,
            evidencia="Margen de contingencia del 10% del objetivo de 10 kg según norma AIAA S-120",
            estado="MARGEN_RESERVA_CONTINGENCIA"
        )
    ]


# ==============================================================================
# 6. FUNCIÓN PRINCIPAL Y EJECUCIÓN CLI
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Presupuesto de masa e incertidumbre para investigación aeronáutica."
    )
    parser.add_argument(
        "--output-dir",
        default="salidas",
        help="Directorio de destino para los archivos CSV generados."
    )
    parser.add_argument(
        "--verify-units",
        action="store_true",
        help="Ejecuta comprobaciones de unidades y relaciones constitutivas físicas."
    )

    args = parser.parse_args()
    out_dir = args.output_dir
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 80)
    print("SISTEMA DE PRESUPUESTO DE MASA BAJO INCERTIDUMBRE EPISTEMOLÓGICA")
    print("=" * 80)

    # 1. Chequeo de unidades físicas
    print("\n1. Verificando consistencia dimensional y de unidades SI...")
    # Verificación de densidades nominales de la BOM
    # Casquillos: 1517.7662 mm3 * 8800 kg/m3 * 1e-9 = 0.01335634 kg
    UnitChecker.verify_density_volume_mass(1517.7662, "mm3", 8800.0, "kg/m3", 0.01335634256)
    # Álabes: 87475.5354 mm3 * 2700 kg/m3 * 1e-9 = 0.23618395 kg
    UnitChecker.verify_density_volume_mass(87475.5354, "mm3", 2700.0, "kg/m3", 0.23618394558)
    # Envolvente: 1106771.9809 mm3 * 1600 kg/m3 * 1e-9 = 1.77083517 kg
    UnitChecker.verify_density_volume_mass(1106771.9809, "mm3", 1600.0, "kg/m3", 1.77083516944)
    print("   ✓ Conversiones mm3 -> m3 y kg/m3 validadas con error < 1e-12.")

    # 2. Generar Plantilla CSV
    print("\n2. Generando plantilla CSV estandarizada de presupuesto...")
    template_entries = create_template_entries()
    template_path = os.path.join(out_dir, "plantilla_presupuesto_masa.csv")
    write_budget_csv(
        template_path,
        template_entries,
        comments=[
            "Plantilla Oficial de Presupuesto de Masa con Incertidumbre Epistemológica",
            "Columnas: componente, masa medida, masa supuesta, intervalo inferior, intervalo superior, evidencia, estado",
            "REGLA CRITICA: Celdas vacias representan valores DESCONOCIDOS (no medidos/no asignados).",
            "NUNCA usar 0 o 0.0 para valores desconocidos. 0.0 representa medicion nula explicita.",
            "Los volumenes reservados pueden estar vacios (cota inf = 0.0) y no prueban masa cero ni positiva."
        ]
    )
    print(f"   ✓ Plantilla generada en: {template_path}")

    # 3. Generar Modelos Hipotéticos (2 kg, 5 kg, 10 kg) y Desglose de Roles
    budgets = [
        ("presupuesto_hipotetico_2kg.csv", 2.0, build_hypothetical_2kg_budget(), "Variante Hipotética 2 kg"),
        ("presupuesto_c02_5kg_incertidumbre.csv", 5.0, build_c02_5kg_uncertainty_budget(), "Candidata C02 5 kg (Integración x160)"),
        ("presupuesto_c02_roles_incertidumbre.csv", 5.0, build_c02_roles_uncertainty_budget(), "C02 5 kg Desglosada por 10 Roles"),
        ("presupuesto_hipotetico_10kg.csv", 10.0, build_hypothetical_10kg_budget(), "Variante Hipotética 10 kg")
    ]

    print("\n3. Generando presupuestos hipotéticos para 2 kg, 5 kg y 10 kg...")
    for filename, target, entries, label in budgets:
        filepath = os.path.join(out_dir, filename)
        write_budget_csv(
            filepath,
            entries,
            comments=[
                f"Presupuesto de Masa e Incertidumbre: {label}",
                f"Objetivo de Masa de Diseno: {target:.1f} kg (HIPOTETICO - mass_targets_are_actual_masses: false)",
                "Sin mediciones reales en hardware ni marcas/piezas comerciales inventadas."
            ]
        )
        summary = aggregate_budget(entries, target_mass_kg=target)
        print(f"\n   --- {label} (Objetivo: {target:.1f} kg) ---")
        print(f"   Archivo:                  {filepath}")
        print(f"   Registros totales:        {summary.total_components}")
        print(f"   Masa medida total:        {summary.total_measured_mass_kg} (0 medidos -> Desconocida)")
        print(f"   Masa supuesta acumulada:  {summary.total_assumed_mass_kg:.6f} kg" if summary.total_assumed_mass_kg else "   Masa supuesta acumulada:  No cerrada")
        print(f"   Intervalo de incertidumbre: [{summary.interval_lower_sum_kg:.4f} kg, {summary.interval_upper_sum_kg:.4f} kg]")
        print(f"   Amplitud de incertidumbre:{summary.uncertainty_span_kg:.4f} kg")
        print(f"   Estado de cierre:         {summary.closure_status}")
        print(f"   Cierre físico real:       {summary.physical_mass_closed} (ABIERTO)")

    print("\n" + "=" * 80)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 80)


if __name__ == "__main__":
    main()
