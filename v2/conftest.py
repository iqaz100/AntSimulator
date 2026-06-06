"""Konfiguracja pytest — dodaje katalog v2 do ścieżki importów."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
