from django.test import TestCase
from analyzerapp import pylint_errors
import os

# Create your tests here.
class PylintErrorsTestCase(TestCase):
    def test_c0303(self):
        """'Trailing whitespace' eliminados correctamente"""
        self.assertEqual(pylint_errors.c0303(["x= 5 \n"], 0), ["x= 5\n"])

    def test_c0321(self):
        """'More than one statement in a single line' marcados correctamente"""
        self.assertEqual(pylint_errors.c0321(["x = 5;y = 6\n"], 0, 6), ["#SPLIT6#SPLITx = 5;y = 6\n"])

    def test_placeholder_split(self):
        """Placeholder #SPLIT eliminado y línea corregida correctamente"""
        self.assertEqual(pylint_errors.placeholder_split("#SPLIT6#SPLITx = 5;y = 6\n"), "x = 5\ny = 6\n")

    def test_c0410(self):
        """'Multiple imports in one line' marcados correctamente"""
        self.assertEqual(pylint_errors.c0410(["import os, re\n"], 0), ["#IMPORTSPLITimport os, re\n"])

    def test_placeholder_importsplit(self):
        """Placeholder #IMPORTSPLIT eliminado y línea corregida correctamente"""
        self.assertEqual(pylint_errors.placeholder_importsplit("#IMPORTSPLITimport os, re\n"), "import os\nimport re\n")

    def test_c0413(self):
        """'Import should be placed at the top of the module' marcados correctamente"""
        self.assertEqual(pylint_errors.c0413(["x = 5", "import os", "y = 6"], 1), ["x = 5", "#TOPimport os", "y = 6"])

    def test_placeholder_top(self):
        """Placeholder #TOP eliminado y línea corregida correctamente"""
        self.assertEqual(pylint_errors.placeholder_top(["x = 5", "#TOPimport os", "y = 6"], 1), ["import os", "x = 5", "y = 6"])

    def test_w0611(self):
        """'Unused import' marcado correctamente"""
        self.assertEqual(pylint_errors.w0611(["import os\n"], 0), ["#DELimport os\n"])
