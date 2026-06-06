"""Lekki runner testów (bez zależności zewnętrznych).

Uruchamia wszystkie funkcje ``test_*`` z modułów ``tests/test_*.py``. Pozwala
weryfikować logikę, gdy w środowisku nie ma zainstalowanego pytest. Pliki testów
pozostają w stylu pytest, więc działają również pod ``python -m pytest``.

Użycie:
    cd v2
    python run_tests.py
"""

from __future__ import annotations

import importlib
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TESTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")


def _discover_modules() -> list[str]:
    names = []
    for filename in sorted(os.listdir(TESTS_DIR)):
        if filename.startswith("test_") and filename.endswith(".py"):
            names.append(f"tests.{filename[:-3]}")
    return names


def main() -> int:
    passed = 0
    failures: list[str] = []

    for module_name in _discover_modules():
        module = importlib.import_module(module_name)
        for attr in sorted(dir(module)):
            if not attr.startswith("test_"):
                continue
            func = getattr(module, attr)
            if not callable(func):
                continue
            label = f"{module_name}.{attr}"
            try:
                func()
                passed += 1
                print(f"  PASS  {label}")
            except Exception:
                failures.append(label)
                print(f"  FAIL  {label}")
                traceback.print_exc()

    print(f"\nWynik: {passed} zaliczonych, {len(failures)} niezaliczonych")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
