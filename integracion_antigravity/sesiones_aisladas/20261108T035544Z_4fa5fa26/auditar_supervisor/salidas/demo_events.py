#!/usr/bin/env python3
"""Prueba demostrativa de preservación de eventos y errores de parseo en parse_stream."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "entradas" / "investigacion-aeronautica" / "integracion_antigravity"))
import orquestar as common

def test_parse_stream_behavior():
    # 1. Advertencia no JSON en stdout (e.g., UserWarning o mensaje de librería)
    stdout_with_warning = (
        "UserWarning: unclosed file descriptor\n"
        '{"event": "result", "result": {"status": "SUCCESS"}}\n'
    )
    events, tool_errors, parse_errors, envelope = common.parse_stream(stdout_with_warning)
    print("Parse errors con warning no JSON:", parse_errors)
    assert len(parse_errors) == 1
    assert "Línea 1:" in parse_errors[0]
    # El resultado envelope fue extraído, pero parse_errors descalifica exito_tecnico
    assert envelope == {"status": "SUCCESS"}
    
    # 2. Sin evento 'result' (e.g. proceso abortado o interrumpido)
    stdout_no_result = (
        '{"event": "step_update", "step_update": {"step_type": "text", "text": "hola"}}\n'
    )
    events2, tool_errors2, parse_errors2, envelope2 = common.parse_stream(stdout_no_result)
    print("Parse errors sin result:", parse_errors2)
    assert envelope2 is None
    assert any("Se esperaba un único resultado final" in err for err in parse_errors2)
    
    # 3. Múltiples eventos 'result'
    stdout_multi_result = (
        '{"event": "result", "result": {"status": "SUCCESS"}}\n'
        '{"event": "result", "result": {"status": "SUCCESS"}}\n'
    )
    events3, tool_errors3, parse_errors3, envelope3 = common.parse_stream(stdout_multi_result)
    print("Parse errors con multi result:", parse_errors3)
    assert envelope3 is None
    assert any("se recibieron 2" in err for err in parse_errors3)
    
    print("DEMOSTRACIÓN EXITOSA: parse_stream es frágil ante mensajes auxiliares en stdout y rechaza streams incompletos.")

if __name__ == "__main__":
    test_parse_stream_behavior()
