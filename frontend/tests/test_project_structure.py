import sys
import unittest
from pathlib import Path

FRONTEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = FRONTEND_ROOT.parents[0]
if str(FRONTEND_ROOT) not in sys.path:
    sys.path.insert(0, str(FRONTEND_ROOT))


class ProjectStructureTest(unittest.TestCase):
    def test_expected_project_structure_exists(self):
        expected_frontend = [
            "app/main.py",
            "app/ui/main_window.py",
            "app/config/settings.py",
            "app/models/movimiento.py",
        ]
        expected_repo = [
            "backend/package.json",
            "backend/src/server.js",
            "context/project_overview.md",
            "context/technical_architecture.md",
            "context/business_rules.md",
            "context/phases/fase_00_contexto.md",
            "context/phases/fase_01_base_proyecto.md",
        ]
        missing_frontend = [path for path in expected_frontend if not (FRONTEND_ROOT / path).exists()]
        missing_repo = [path for path in expected_repo if not (REPO_ROOT / path).exists()]
        self.assertEqual(missing_frontend + missing_repo, [])

    def test_project_package_imports(self):
        import app
        from app.models import Movimiento, TipoMovimiento, EstadoMovimiento, OrigenMovimiento

        self.assertEqual(app.__version__, "0.0.1")
        self.assertIsNotNone(Movimiento)
        self.assertEqual(TipoMovimiento.INGRESO.value, "ingreso")
        self.assertEqual(EstadoMovimiento.PENDIENTE.value, "pendiente")
        self.assertEqual(OrigenMovimiento.MANUAL.value, "manual")


if __name__ == "__main__":
    unittest.main()
