# Repository tests

Run `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests` from the repository root. These tests check navigation and representative historical module imports; they do not replace numerical, CAD or CFD verification scripts for each study. Set up `.venv` as described in `docs/development_setup.md`.
