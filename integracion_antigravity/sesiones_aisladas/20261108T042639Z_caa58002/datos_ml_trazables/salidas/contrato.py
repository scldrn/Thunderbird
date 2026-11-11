"""Contrato de trazabilidad para datos de entrenamiento, validación y prueba de ML.

Define las estructuras de datos y el esquema de contrato para garantizar la
trazabilidad de episodios de simulación y futuros datos físicos, distinguiendo
rigurosamente datos medidos, supuestos, calculados y desconocidos.

Fuentes de referencia del proyecto:
- entradas/investigacion-aeronautica/configuraciones/C02_CANDIDATA.json
- entradas/investigacion-aeronautica/simulacion_vuelo_A/INFORME.md
- entradas/investigacion-aeronautica/plan_maestro/PLAN-MAESTRO.md
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class Particion(str, Enum):
    """Partición del conjunto de datos de ML."""
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"


class ProcedenciaDato(str, Enum):
    """Categoría epistemológica del parámetro o dato."""
    MEDIDO = "medido"          # Medición física instrumental directa verificable
    SUPUESTO = "supuesto"      # Hipótesis de diseño o valor nominal no contrastado
    CALCULADO = "calculado"    # Resultado numérico derivado de ecuaciones o modelos
    DESCONOCIDO = "desconocido"  # Ausencia de evidencia; no inferir cero ni no-cero


class TipoDatoEpisodio(str, Enum):
    """Origen del episodio."""
    SINTETICO = "sintetico"            # Procedente de simulación numérica
    MEDIDO_BANCO = "medido_banco"      # Datos físicos reales de banco de ensayos
    MEDIDO_VUELO = "medido_vuelo"      # Datos físicos reales de vuelo instrumental


@dataclass
class ParametroTrazable:
    """Parámetro individual con unidades, procedencia epistemológica y fuente."""
    nombre: str
    valor: Optional[Union[float, int, str, list]]
    unidad: str
    procedencia: ProcedenciaDato
    fuente: str
    notas: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nombre": self.nombre,
            "valor": self.valor,
            "unidad": self.unidad,
            "procedencia": self.procedencia.value if isinstance(self.procedencia, ProcedenciaDato) else str(self.procedencia),
            "fuente": self.fuente,
            "notas": self.notas,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ParametroTrazable:
        proc_raw = data.get("procedencia", ProcedenciaDato.DESCONOCIDO.value)
        try:
            procedencia = ProcedenciaDato(proc_raw)
        except ValueError:
            procedencia = ProcedenciaDato.DESCONOCIDO
        return cls(
            nombre=data["nombre"],
            valor=data.get("valor"),
            unidad=data.get("unidad", ""),
            procedencia=procedencia,
            fuente=data.get("fuente", "desconocido"),
            notas=data.get("notas"),
        )


@dataclass
class PasoAccion:
    """Paso temporal de demanda o acción del controlador/actuadores."""
    timestamp_s: float
    fuerzas_demanda_N: List[float]       # [Fx, Fy, Fz] en marco de cuerpo FLU
    empuje_modulos_N: List[float]        # Fuerzas por módulo [T1, T2, T3, T4]
    angulos_cono_deg: List[float]        # Deflexión vectorial por módulo [c1, c2, c3, c4]
    unidades: Dict[str, str] = field(default_factory=lambda: {
        "timestamp_s": "s",
        "fuerzas_demanda_N": "N",
        "empuje_modulos_N": "N",
        "angulos_cono_deg": "deg",
    })

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PasoAccion:
        return cls(
            timestamp_s=float(data["timestamp_s"]),
            fuerzas_demanda_N=[float(x) for x in data.get("fuerzas_demanda_N", [])],
            empuje_modulos_N=[float(x) for x in data.get("empuje_modulos_N", [])],
            angulos_cono_deg=[float(x) for x in data.get("angulos_cono_deg", [])],
            unidades=data.get("unidades", {
                "timestamp_s": "s",
                "fuerzas_demanda_N": "N",
                "empuje_modulos_N": "N",
                "angulos_cono_deg": "deg",
            }),
        )


@dataclass
class MetricasEpisodio:
    """Métricas del episodio con procedencia y unidades explícitas."""
    velocidad_max_m_s: Optional[float]
    aceleracion_neta_max_g: Optional[float]
    empuje_modulo_max_N: Optional[float]
    angulo_cono_max_deg: Optional[float]
    optimizador_factible: bool
    procedencia: ProcedenciaDato = ProcedenciaDato.CALCULADO
    fuente: str = "simulador_numerico"
    unidades: Dict[str, str] = field(default_factory=lambda: {
        "velocidad_max_m_s": "m/s",
        "aceleracion_neta_max_g": "g",
        "empuje_modulo_max_N": "N",
        "angulo_cono_max_deg": "deg",
        "optimizador_factible": "adimensional_bool",
    })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "velocidad_max_m_s": self.velocidad_max_m_s,
            "aceleracion_neta_max_g": self.aceleracion_neta_max_g,
            "empuje_modulo_max_N": self.empuje_modulo_max_N,
            "angulo_cono_max_deg": self.angulo_cono_max_deg,
            "optimizador_factible": self.optimizador_factible,
            "procedencia": self.procedencia.value if isinstance(self.procedencia, ProcedenciaDato) else str(self.procedencia),
            "fuente": self.fuente,
            "unidades": self.unidades,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MetricasEpisodio:
        proc_raw = data.get("procedencia", ProcedenciaDato.CALCULADO.value)
        try:
            procedencia = ProcedenciaDato(proc_raw)
        except ValueError:
            procedencia = ProcedenciaDato.CALCULADO
        return cls(
            velocidad_max_m_s=data.get("velocidad_max_m_s"),
            aceleracion_neta_max_g=data.get("aceleracion_neta_max_g"),
            empuje_modulo_max_N=data.get("empuje_modulo_max_N"),
            angulo_cono_max_deg=data.get("angulo_cono_max_deg"),
            optimizador_factible=bool(data.get("optimizador_factible", False)),
            procedencia=procedencia,
            fuente=data.get("fuente", "simulador_numerico"),
            unidades=data.get("unidades", {
                "velocidad_max_m_s": "m/s",
                "aceleracion_neta_max_g": "g",
                "empuje_modulo_max_N": "N",
                "angulo_cono_max_deg": "deg",
                "optimizador_factible": "adimensional_bool",
            }),
        )


@dataclass
class EspecificacionSimulador:
    """Especificación técnica del simulador empleado para generar el episodio."""
    nombre: str
    version: str
    integrador: str                    # Ej. "RK4_paso_fijo"
    paso_integracion_s: float          # Ej. 0.005 s (fuente: INFORME.md)
    nivel_fidelidad: str               # Ej. "demostrador_ideal_6dof_sin_aerodinamica_externa"
    es_ensayo_fisico: bool = False
    fuente_codigo: str = "entradas/investigacion-aeronautica/simulacion_vuelo_A/INFORME.md"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EspecificacionSimulador:
        return cls(
            nombre=data["nombre"],
            version=data["version"],
            integrador=data.get("integrador", "desconocido"),
            paso_integracion_s=float(data.get("paso_integracion_s", 0.0)),
            nivel_fidelidad=data.get("nivel_fidelidad", "desconocido"),
            es_ensayo_fisico=bool(data.get("es_ensayo_fisico", False)),
            fuente_codigo=data.get("fuente_codigo", "desconocido"),
        )


@dataclass
class EspecificacionEnsayoFisico:
    """Especificación de banco físico o vuelo real (cuando los datos son medidos)."""
    id_banco_o_vehiculo: str
    id_calibracion_sensores: str
    instalacion: str
    fecha_ensayo_iso: str
    responsable_ensayo: str
    registro_calibracion_disponible: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EspecificacionEnsayoFisico:
        return cls(
            id_banco_o_vehiculo=data["id_banco_o_vehiculo"],
            id_calibracion_sensores=data["id_calibracion_sensores"],
            instalacion=data.get("instalacion", "desconocido"),
            fecha_ensayo_iso=data.get("fecha_ensayo_iso", "desconocido"),
            responsable_ensayo=data.get("responsable_ensayo", "desconocido"),
            registro_calibracion_disponible=bool(data.get("registro_calibracion_disponible", False)),
        )


@dataclass
class RegistroEpisodio:
    """Contrato completo y canónico de un episodio de datos ML con trazabilidad."""
    episode_id: str
    seed: int
    scenario_family: str
    geometry_hash: str                 # SHA-256 de geometría CAD de referencia
    plant_version: str                 # ID de versión de planta (ej. C02_COMPACTA_x160_5kg_2026-11-03_r2)
    plant_model_status: str            # Ej. "no_identificado_ideal_6dof" o "calibrado_fisicamente"
    data_type: TipoDatoEpisodio
    partition: Particion
    parametros: Dict[str, ParametroTrazable]
    acciones: List[PasoAccion]
    metricas: MetricasEpisodio
    simulador: Optional[EspecificacionSimulador] = None
    ensayo_fisico: Optional[EspecificacionEnsayoFisico] = None
    notas: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "seed": self.seed,
            "scenario_family": self.scenario_family,
            "geometry_hash": self.geometry_hash,
            "plant_version": self.plant_version,
            "plant_model_status": self.plant_model_status,
            "data_type": self.data_type.value if isinstance(self.data_type, TipoDatoEpisodio) else str(self.data_type),
            "partition": self.partition.value if isinstance(self.partition, Particion) else str(self.partition),
            "parametros": {k: v.to_dict() for k, v in self.parametros.items()},
            "acciones": [a.to_dict() for a in self.acciones],
            "metricas": self.metricas.to_dict(),
            "simulador": self.simulador.to_dict() if self.simulador else None,
            "ensayo_fisico": self.ensayo_fisico.to_dict() if self.ensayo_fisico else None,
            "notas": self.notas,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RegistroEpisodio:
        tipo_raw = data.get("data_type", TipoDatoEpisodio.SINTETICO.value)
        try:
            data_type = TipoDatoEpisodio(tipo_raw)
        except ValueError:
            data_type = TipoDatoEpisodio.SINTETICO

        part_raw = data.get("partition", Particion.TRAIN.value)
        try:
            partition = Particion(part_raw)
        except ValueError:
            partition = Particion.TRAIN

        parametros = {}
        for k, v in data.get("parametros", {}).items():
            if isinstance(v, ParametroTrazable):
                parametros[k] = v
            elif isinstance(v, dict):
                parametros[k] = ParametroTrazable.from_dict(v)

        acciones = []
        for a in data.get("acciones", []):
            if isinstance(a, PasoAccion):
                acciones.append(a)
            elif isinstance(a, dict):
                acciones.append(PasoAccion.from_dict(a))

        metricas_raw = data.get("metricas", {})
        if isinstance(metricas_raw, MetricasEpisodio):
            metricas = metricas_raw
        elif isinstance(metricas_raw, dict):
            metricas = MetricasEpisodio.from_dict(metricas_raw)
        else:
            metricas = MetricasEpisodio(None, None, None, None, False)

        sim_raw = data.get("simulador")
        simulador = EspecificacionSimulador.from_dict(sim_raw) if isinstance(sim_raw, dict) else sim_raw

        ensayo_raw = data.get("ensayo_fisico")
        ensayo_fisico = EspecificacionEnsayoFisico.from_dict(ensayo_raw) if isinstance(ensayo_raw, dict) else ensayo_raw

        return cls(
            episode_id=data["episode_id"],
            seed=int(data["seed"]),
            scenario_family=data["scenario_family"],
            geometry_hash=data["geometry_hash"],
            plant_version=data["plant_version"],
            plant_model_status=data.get("plant_model_status", "no_identificado_ideal_6dof"),
            data_type=data_type,
            partition=partition,
            parametros=parametros,
            acciones=acciones,
            metricas=metricas,
            simulador=simulador,
            ensayo_fisico=ensayo_fisico,
            notas=data.get("notas"),
        )


@dataclass
class ManifiestoDatasetML:
    """Manifiesto que agrupa episodios de entrenamiento, validación y prueba."""
    dataset_id: str
    fecha_creacion_iso: str
    referencia_canonica: str
    descripcion: str
    episodios: List[RegistroEpisodio]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "fecha_creacion_iso": self.fecha_creacion_iso,
            "referencia_canonica": self.referencia_canonica,
            "descripcion": self.descripcion,
            "episodios": [ep.to_dict() for ep in self.episodios],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ManifiestoDatasetML:
        episodios = []
        for ep in data.get("episodios", []):
            if isinstance(ep, RegistroEpisodio):
                episodios.append(ep)
            elif isinstance(ep, dict):
                episodios.append(RegistroEpisodio.from_dict(ep))
        return cls(
            dataset_id=data["dataset_id"],
            fecha_creacion_iso=data.get("fecha_creacion_iso", ""),
            referencia_canonica=data.get("referencia_canonica", ""),
            descripcion=data.get("descripcion", ""),
            episodios=episodios,
        )

    @classmethod
    def from_json(cls, json_str: str) -> ManifiestoDatasetML:
        data = json.loads(json_str)
        return cls.from_dict(data)
