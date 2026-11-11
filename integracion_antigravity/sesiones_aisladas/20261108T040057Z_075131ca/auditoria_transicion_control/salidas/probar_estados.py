#!/usr/bin/env python3
"""
Suite de Pruebas de Estados y Transiciones de Control
Proyecto: Auditoria de Transicion y Control (Arquitectura A - Ventiladores Internos)
Ejecuta la verificacion de la logica discreta de transiciones, guardas,
tiempos de permanencia, saturacion y retorno ante anomalias segun
las especificaciones en salidas/maquina_estados.json.
Sin simulacion física; utiliza exclusivamente la libreria estandar de Python 3.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

class MotorMaquinaEstados:
    """Motor de ejecucion discreta para pruebas de la maquina de estados."""
    def __init__(self, spec: Dict[str, Any]):
        self.spec = spec
        self.estados: Dict[str, Dict[str, Any]] = {e["id"]: e for e in spec["estados"]}
        self.params: Dict[str, Any] = spec.get("parametros_referencia", {})
        self.estado_actual: str = "ESTACIONARIO_ACTIVO"
        self.tiempo_en_estado: float = 0.0
        self.historial: List[Tuple[float, str, str, str]] = []  # (t, origen, evento, destino)
        self.tiempo_global: float = 0.0

    def reiniciar(self, estado_inicial: str = "ESTACIONARIO_ACTIVO") -> None:
        if estado_inicial not in self.estados:
            raise ValueError(f"Estado inicial desconocido: {estado_inicial}")
        self.estado_actual = estado_inicial
        self.tiempo_en_estado = 0.0
        self.tiempo_global = 0.0
        self.historial.clear()

    def avanzar_tiempo(self, dt: float) -> None:
        self.tiempo_en_estado += dt
        self.tiempo_global += dt

    def evaluar_evento(self, evento: str, contexto: Dict[str, Any]) -> bool:
        """Intenta ejecutar una transicion basada en un evento y contexto de variables."""
        est_data = self.estados[self.estado_actual]
        transiciones = est_data.get("transiciones_salida", [])

        for tr in transiciones:
            if tr["evento"] == evento:
                guarda = tr["condicion_guarda"]
                if self._evaluar_guarda(guarda, contexto):
                    origen = self.estado_actual
                    destino = tr["destino"]
                    self.historial.append((self.tiempo_global, origen, evento, destino))
                    self.estado_actual = destino
                    self.tiempo_en_estado = 0.0
                    return True
        return False

    def _evaluar_guarda(self, expresion: str, ctx: Dict[str, Any]) -> bool:
        """Evaluador seguro de condiciones de guarda booleanas y de umbral."""
        exp_py = expresion.replace("&&", " and ").replace("||", " or ")
        exp_py = exp_py.replace("true", "True").replace("false", "False")
        entorno = dict(ctx)
        entorno["tiempo_estado"] = self.tiempo_en_estado
        entorno["tiempo_global"] = self.tiempo_global
        try:
            return bool(eval(exp_py, {"__builtins__": {}}, entorno))
        except Exception as e:
            raise RuntimeError(f"Error evaluando guarda '{expresion}' con contexto {entorno}: {e}")

class TestSuiteEstados:
    def __init__(self, ruta_json: Path):
        with open(ruta_json, "r", encoding="utf-8") as f:
            self.spec = json.load(f)
        self.maquina = MotorMaquinaEstados(self.spec)
        self.pruebas_ejecutadas = 0
        self.pruebas_pasadas = 0

    def assert_true(self, condicion: bool, mensaje: str) -> None:
        if not condicion:
            raise AssertionError(f"Fallo en asercion: {mensaje}")

    def assert_equal(self, a: Any, b: Any, mensaje: str) -> None:
        if a != b:
            raise AssertionError(f"Fallo de igualdad: {a} != {b}. {mensaje}")

    def ejecutar_test(self, nombre: str, func) -> None:
        self.pruebas_ejecutadas += 1
        print(f"\n[EJECUTANDO PRUEBA {self.pruebas_ejecutadas:02d}] {nombre}")
        try:
            func()
            self.pruebas_pasadas += 1
            print(f"[PASO] {nombre}")
        except Exception as e:
            print(f"[ERROR] {nombre}: {e}", file=sys.stderr)
            raise

    # -------------------------------------------------------------------------
    # PRUEBA 1: Transicion nominal completa de estacionario a avance puro
    # -------------------------------------------------------------------------
    def test_transicion_nominal_despegue_a_avance(self) -> None:
        m = self.maquina
        m.reiniciar("ESTACIONARIO_ACTIVO")

        # 1. Comando de transicion desde ESTACIONARIO_ACTIVO
        ctx = {"orden_operador": True, "salud_general": True, "energia_reserva": 0.85}
        trans = m.evaluar_evento("COMANDO_TRANSICION_AVANCE", ctx)
        self.assert_true(trans, "Debe transicionar a PREPARACION_TRANSICION_AVANCE")
        self.assert_equal(m.estado_actual, "PREPARACION_TRANSICION_AVANCE", "Estado incorrecto")

        # 2. Validacion de precondiciones
        m.avanzar_tiempo(0.5)
        ctx = {"autochequeo_ok": True, "sensores_ok": True}
        trans = m.evaluar_evento("PRECONDICIONES_VALIDADAS", ctx)
        self.assert_true(trans, "Debe transicionar a DESPIERTE_PROPULSION_AXIAL")
        self.assert_equal(m.estado_actual, "DESPIERTE_PROPULSION_AXIAL", "Estado incorrecto")

        # 3. Arranque axial y estabilizacion
        m.avanzar_tiempo(1.2)
        ctx = {"empuje_axial_estable": True}
        trans = m.evaluar_evento("PROPULSOR_AXIAL_ESTABLE", ctx)
        self.assert_true(trans, "Debe transicionar a ACELERACION_MIXTA")
        self.assert_equal(m.estado_actual, "ACELERACION_MIXTA", "Estado incorrecto")

        # 4. Aceleracion mixta hasta velocidad de transicion
        m.avanzar_tiempo(3.5)
        ctx = {"velocidad_aire_ms": 28.5, "presion_dinamica_Pa": 490.0}
        trans = m.evaluar_evento("VELOCIDAD_TRANSICION_ALCANZADA", ctx)
        self.assert_true(trans, "Debe transicionar a TRANSFERENCIA_AUTORIDAD_AERODINAMICA")
        self.assert_equal(m.estado_actual, "TRANSFERENCIA_AUTORIDAD_AERODINAMICA", "Estado incorrecto")

        # 5. Confirmacion de autoridad aerodinamica
        m.avanzar_tiempo(0.8)
        ctx = {"aletas_efectivas": True, "error_actitud": 1.2}
        trans = m.evaluar_evento("AUTORIDAD_AERO_CONFIRMADA", ctx)
        self.assert_true(trans, "Debe transicionar a CIERRE_TAPAS_VENTILADORES")
        self.assert_equal(m.estado_actual, "CIERRE_TAPAS_VENTILADORES", "Estado incorrecto")

        # 6. Cierre y enclavamiento de tapas
        m.avanzar_tiempo(1.4)
        ctx = {"todas_tapas_enrasadas": True, "cerrojos_enclavados": True}
        trans = m.evaluar_evento("TAPAS_ENRASADAS_Y_ENCLAVADAS", ctx)
        self.assert_true(trans, "Debe transicionar a AVANCE_PURO")
        self.assert_equal(m.estado_actual, "AVANCE_PURO", "Estado final incorrecto")

        # Verificacion de configuracion final
        cfg = m.estados["AVANCE_PURO"]["configuracion_actuadores"]
        self.assert_true(cfg["tapas"]["solape_nominal"] == "CERO", "El solape en avance puro debe ser CERO")
        self.assert_true(cfg["ventiladores_internos"]["empuje_N"] == 0.0, "Ventiladores deben estar inactivos")

    # -------------------------------------------------------------------------
    # PRUEBA 2: Transicion nominal completa de avance puro a estacionario
    # -------------------------------------------------------------------------
    def test_transicion_nominal_retorno_a_estacionario(self) -> None:
        m = self.maquina
        m.reiniciar("AVANCE_PURO")

        # 1. Comando de retorno
        ctx = {"orden_retorno": True, "velocidad_aire_ms": 50.0}
        trans = m.evaluar_evento("COMANDO_RETORNO_ESTACIONARIO", ctx)
        self.assert_true(trans, "Debe transicionar a PREPARACION_RETORNO")
        self.assert_equal(m.estado_actual, "PREPARACION_RETORNO", "Estado incorrecto")

        # 2. Desaceleracion hasta ventana segura de apertura de compuertas
        m.avanzar_tiempo(4.0)
        ctx = {"velocidad_aire_ms": 30.0, "presion_dinamica_Pa": 550.0}
        trans = m.evaluar_evento("VENTANA_APERTURA_ALCANZADA", ctx)
        self.assert_true(trans, "Debe transicionar a APERTURA_TAPAS_VENTILADORES")
        self.assert_equal(m.estado_actual, "APERTURA_TAPAS_VENTILADORES", "Estado incorrecto")

        # 3. Apertura completa de compuertas (10 mm elev + 110 deg)
        m.avanzar_tiempo(1.3)
        ctx = {"todas_tapas_abiertas_110deg": True, "elevacion_10mm_ok": True}
        trans = m.evaluar_evento("TAPAS_TOTALMENTE_ABIERTAS", ctx)
        self.assert_true(trans, "Debe transicionar a ARRANQUE_VENTILADORES")
        self.assert_equal(m.estado_actual, "ARRANQUE_VENTILADORES", "Estado incorrecto")

        # 4. Puesta en marcha de ventiladores a ralenti
        m.avanzar_tiempo(0.6)
        ctx = {"cuatro_ventiladores_ralenti": True}
        trans = m.evaluar_evento("VENTILADORES_LISTOS", ctx)
        self.assert_true(trans, "Debe transicionar a DESACELERACION_MIXTA")
        self.assert_equal(m.estado_actual, "DESACELERACION_MIXTA", "Estado incorrecto")

        # 5. Desaceleracion mixta a velocidad de aproximacion final
        m.avanzar_tiempo(3.0)
        ctx = {"velocidad_aire_ms": 3.0, "empuje_axial_N": 0.5}
        trans = m.evaluar_evento("VELOCIDAD_BAJA_ALCANZADA", ctx)
        self.assert_true(trans, "Debe transicionar a REESTABLECIMIENTO_ESTACIONARIO")
        self.assert_equal(m.estado_actual, "REESTABLECIMIENTO_ESTACIONARIO", "Estado incorrecto")

        # 6. Consolidacion de vuelo estacionario
        m.avanzar_tiempo(0.8)
        ctx = {"velocidad_aire_ms": 0.2, "estabilidad_ok": True}
        trans = m.evaluar_evento("ESTACIONARIO_CONSOLIDADO", ctx)
        self.assert_true(trans, "Debe transicionar a ESTACIONARIO_ACTIVO")
        self.assert_equal(m.estado_actual, "ESTACIONARIO_ACTIVO", "Estado final incorrecto")

    # -------------------------------------------------------------------------
    # PRUEBA 3: Aborto por fallo en encendido de propulsor axial
    # -------------------------------------------------------------------------
    def test_aborto_fallo_arranque_axial(self) -> None:
        m = self.maquina
        m.reiniciar("DESPIERTE_PROPULSION_AXIAL")

        # Simular timeout o perdida de encendido (> 3.0 s)
        m.avanzar_tiempo(3.2)
        ctx = {"perdida_encendido": True}
        trans = m.evaluar_evento("FALLO_ARRANQUE_AXIAL", ctx)
        self.assert_true(trans, "Debe transicionar a CONTINGENCIA_ABORT_A_ESTACIONARIO")
        self.assert_equal(m.estado_actual, "CONTINGENCIA_ABORT_A_ESTACIONARIO", "Estado incorrecto")

        # Recuperacion y parada a estacionario
        m.avanzar_tiempo(1.5)
        ctx = {"velocidad_aire_ms": 0.8, "estabilidad_ok": True}
        trans = m.evaluar_evento("FRENO_COMPLETO", ctx)
        self.assert_true(trans, "Debe retornar a ESTACIONARIO_ACTIVO")
        self.assert_equal(m.estado_actual, "ESTACIONARIO_ACTIVO", "Estado incorrecto")

    # -------------------------------------------------------------------------
    # PRUEBA 4: Bloqueo de seguridad: intento de abrir compuertas a alta velocidad
    # -------------------------------------------------------------------------
    def test_bloqueo_apertura_tapas_alta_presion_dinamica(self) -> None:
        m = self.maquina
        m.reiniciar("PREPARACION_RETORNO")

        # Caso peligroso: velocidad 45 m/s, presion dinamica > 650 Pa
        m.avanzar_tiempo(2.0)
        ctx = {"velocidad_aire_ms": 45.0, "presion_dinamica_Pa": 1200.0}
        trans = m.evaluar_evento("VENTANA_APERTURA_ALCANZADA", ctx)
        self.assert_true(not trans, "La guarda de seguridad DEBE rechazar la apertura si q > 650 Pa o V > 32 m/s")
        self.assert_equal(m.estado_actual, "PREPARACION_RETORNO", "Debe permanecer frenando")

        # Timeout de desaceleracion activa contingencia de crucero
        m.avanzar_tiempo(6.5)  # tiempo acumulado > 8.0 s
        ctx = {"velocidad_aire_ms": 40.0}
        trans = m.evaluar_evento("TIMEOUT_DESACELERACION", ctx)
        self.assert_true(trans, "Debe abortar hacia avance si no logra frenar")
        self.assert_equal(m.estado_actual, "CONTINGENCIA_ABORT_A_AVANCE", "Estado incorrecto")

    # -------------------------------------------------------------------------
    # PRUEBA 5: Aborto por atascamiento de tapas durante el cierre
    # -------------------------------------------------------------------------
    def test_anomalia_tapa_atascada_durante_cierre(self) -> None:
        m = self.maquina
        m.reiniciar("CIERRE_TAPAS_VENTILADORES")

        # Simular fallo de carrera / sobrecorriente de actuador
        m.avanzar_tiempo(1.9)
        ctx = {"fallo_cierre": True}
        trans = m.evaluar_evento("ATASCAMIENTO_O_FALLO_CIERRE_TAPAS", ctx)
        self.assert_true(trans, "Debe transicionar a CONTINGENCIA_TAPA_TRABADA")
        self.assert_equal(m.estado_actual, "CONTINGENCIA_TAPA_TRABADA", "Estado incorrecto")

        # Procedimiento de frenado de emergencia
        m.avanzar_tiempo(2.5)
        ctx = {"velocidad_aire_ms": 8.0}
        trans = m.evaluar_evento("DESACELERACION_Y_NIVELACION", ctx)
        self.assert_true(trans, "Debe transicionar a CONTINGENCIA_ABORT_A_ESTACIONARIO")
        self.assert_equal(m.estado_actual, "CONTINGENCIA_ABORT_A_ESTACIONARIO", "Estado incorrecto")

    # -------------------------------------------------------------------------
    # PRUEBA 6: Gestion de saturacion en aceleracion mixta
    # -------------------------------------------------------------------------
    def test_gestion_saturacion_angulo_vectorial(self) -> None:
        m = self.maquina
        m.reiniciar("ACELERACION_MIXTA")

        # Exceder angulo vectorial o timeout de aceleracion
        m.avanzar_tiempo(2.0)
        ctx = {"angulo_vector_excedido": True}
        trans = m.evaluar_evento("ANOMALIA_SATURACION_O_EMPUJE_INSUFICIENTE", ctx)
        self.assert_true(trans, "Debe abortar ante saturacion de angulo vectorial")
        self.assert_equal(m.estado_actual, "CONTINGENCIA_ABORT_A_ESTACIONARIO", "Estado incorrecto")

    # -------------------------------------------------------------------------
    # PRUEBA 7: Perdida de control aerodinamico antes de desconectar ventiladores
    # -------------------------------------------------------------------------
    def test_perdida_autoridad_aero_durante_transferencia(self) -> None:
        m = self.maquina
        m.reiniciar("TRANSFERENCIA_AUTORIDAD_AERODINAMICA")

        # Simular error excesivo de actitud o stall en superficies
        m.avanzar_tiempo(1.0)
        ctx = {"error_actitud": 6.5, "stall_aletas": True}
        trans = m.evaluar_evento("PERDIDA_CONTROL_AERODINAMICO", ctx)
        self.assert_true(trans, "Debe abortar transferencia si aletas entran en perdida")
        self.assert_equal(m.estado_actual, "CONTINGENCIA_ABORT_A_ESTACIONARIO", "Estado incorrecto")

    # -------------------------------------------------------------------------
    # PRUEBA 8: Fallo de apertura de tapas en retorno aborta a planeo/avance
    # -------------------------------------------------------------------------
    def test_fallo_apertura_tapas_retorno_aborta_a_avance(self) -> None:
        m = self.maquina
        m.reiniciar("APERTURA_TAPAS_VENTILADORES")

        # Falla de compuerta en apertura
        m.avanzar_tiempo(1.9)
        ctx = {"fallo_mecanismo_tapa": True}
        trans = m.evaluar_evento("FALLO_APERTURA_TAPAS", ctx)
        self.assert_true(trans, "Debe proteger la aeronave abortando a avance")
        self.assert_equal(m.estado_actual, "CONTINGENCIA_ABORT_A_AVANCE", "Estado incorrecto")

        # Recuperacion de velocidad de crucero
        m.avanzar_tiempo(2.0)
        ctx = {"velocidad_aire_ms": 38.0, "tapas_cerradas": True}
        trans = m.evaluar_evento("VELOCIDAD_SEGURA_RECUPERADA", ctx)
        self.assert_true(trans, "Debe regresar a AVANCE_PURO")
        self.assert_equal(m.estado_actual, "AVANCE_PURO", "Estado incorrecto")

    # -------------------------------------------------------------------------
    # Ejecucion general
    # -------------------------------------------------------------------------
    def ejecutar_todas(self) -> None:
        print("======================================================================")
        print("SUITE DE PRUEBAS DE LA MAQUINA DE ESTADOS DE TRANSICION")
        print("======================================================================")
        self.ejecutar_test("Transicion nominal despegue a avance puro", self.test_transicion_nominal_despegue_a_avance)
        self.ejecutar_test("Transicion nominal retorno a estacionario", self.test_transicion_nominal_retorno_a_estacionario)
        self.ejecutar_test("Aborto por fallo en arranque de propulsor axial", self.test_aborto_fallo_arranque_axial)
        self.ejecutar_test("Bloqueo de seguridad: apertura de tapas a alta velocidad", self.test_bloqueo_apertura_tapas_alta_presion_dinamica)
        self.ejecutar_test("Anomalia de tapa atascada durante secuencia de cierre", self.test_anomalia_tapa_atascada_durante_cierre)
        self.ejecutar_test("Gestion de saturacion vectorial en aceleracion mixta", self.test_gestion_saturacion_angulo_vectorial)
        self.ejecutar_test("Perdida de autoridad aerodinamica durante transferencia", self.test_perdida_autoridad_aero_durante_transferencia)
        self.ejecutar_test("Fallo de apertura de tapas en retorno aborta a avance", self.test_fallo_apertura_tapas_retorno_aborta_a_avance)
        print("\n======================================================================")
        print(f"[RESUMEN DE PRUEBAS] {self.pruebas_pasadas} de {self.pruebas_ejecutadas} pruebas pasaron con exito.")
        print("======================================================================")

def main() -> None:
    ruta_json = Path(__file__).resolve().parent / "maquina_estados.json"
    suite = TestSuiteEstados(ruta_json)
    suite.ejecutar_todas()

if __name__ == "__main__":
    main()
