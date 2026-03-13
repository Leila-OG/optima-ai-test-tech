import sys
from pathlib import Path

# Ajout de la racine du projet au PYTHONPATH pour les tests
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))