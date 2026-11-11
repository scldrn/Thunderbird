#!/usr/bin/env python3
"""Check the maintained repository navigation without changing research data."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
AREAS = (
    "CFD", "ejecucion", "modelos_integrados", "configuraciones", "plan_maestro",
    "simulacion_vuelo_A", "vuelo_rapido_visual", "fuentes", "resultados",
    "integracion_apps", "integracion_antigravity", "entregas", "audits", "tools", "tests",
)
DOCUMENTS = (
    "README.md", "AGENTS.md", "docs/README.md", "docs/development_setup.md", "docs/research_context.md", "docs/research_index.md",
    "docs/legacy_research_index.md", "docs/repository_organization.md",
)
CORE_EVIDENCE = (
    "ESTADO-VERIFICACION-GLOBAL.md", "modelos_integrados/DECISION-ARQUITECTURA.md",
    "plan_maestro/PLAN-MAESTRO.md", "ejecucion/ESTADO-TAREAS.csv",
    "CFD/PAUSA_SOLICITADA_USUARIO.json", "configuraciones/A07_BASE.json",
    "configuraciones/C02_CANDIDATA.json", "audits/incomplete_case_scopes_2026-11-11.json",
)
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def main():
    problems = []
    documents = list(DOCUMENTS) + [f"{area}/README.md" for area in AREAS]
    for name in (*documents, *CORE_EVIDENCE):
        if not (ROOT / name).is_file():
            problems.append(f"Missing required file: {name}")
    for name in documents:
        source = ROOT / name
        if not source.is_file():
            continue
        for target in LINK.findall(source.read_text(encoding="utf-8")):
            parsed = urlsplit(target.strip().strip("<>"))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            destination = source.parent / unquote(parsed.path)
            if not destination.exists():
                problems.append(f"Broken link in {name}: {target}")
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print(f"Navigation OK: {len(documents)} documents and {len(CORE_EVIDENCE)} core evidence paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
