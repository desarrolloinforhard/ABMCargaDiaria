import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class ProjectStructureTest(unittest.TestCase):
    def test_expected_project_structure_exists(self):
        expected = [
            "app/main.py",
            "app/ui/main_window.py",
            "app/config/settings.py",
            "context/project_overview.md",
            "context/technical_architecture.md",
            "context/business_rules.md",
            "context/phases/fase_00_contexto.md",
            "context/phases/fase_01_base_proyecto.md",
        ]
        missing = [path for path in expected if not (PROJECT_ROOT / path).exists()]
        self.assertEqual(missing, [])

    def test_project_package_imports(self):
        import app

        self.assertEqual(app.__version__, "0.0.1")


if __name__ == "__main__":
    unittest.main()
