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

    def test_c0326(self):
        msg = "Exactly one space required around assignment"
        self.assertEqual(pylint_errors.c0326(["x=5\n"], 0, msg), ["x = 5\n"])
        msg = "Exactly one space required around comparison"
        self.assertEqual(pylint_errors.c0326(["if z==11:\n"], 0, msg), ["if z == 11:\n"])
        msg = "Exactly one space required after comma"
        self.assertEqual(pylint_errors.c0326(["numbers = [1 ,2]\n"], 0, msg), ["numbers = [1, 2]\n"])
        msg = "No space allowed after bracket"
        self.assertEqual(pylint_errors.c0326(["print( text)\n"], 0, msg), ["print(text)\n"])
        msg = "No space allowed before bracket"
        self.assertEqual(pylint_errors.c0326(["print(text )\n"], 0, msg), ["print(text)\n"])
        msg = "No space allowed before :"
        self.assertEqual(pylint_errors.c0326(["if z == 11 :\n"], 0, msg), ["if z == 11:\n"])

    def test_c0410(self):
        """'Multiple imports in one line' marcados correctamente"""
        self.assertEqual(pylint_errors.c0410(["import os, re\n"], 0), ["#IMPORTSPLITimport os, re\n"])

    def test_c0411(self):
        """'wrong-import-order: %s comes before %s' marcados correctamente"""
        msg = 'standard import "import os" comes before "import requests"\n'
        self.assertEqual(pylint_errors.c0411(["import requests\n", "import os\n"], 1, msg), ["import requests\n", "#TOPimport os\n"])
        msg = 'external import "import requests" comes before "from fork import USERNAME"\n'
        self.assertEqual(pylint_errors.c0411(["import os\n", "from fork import USERNAME\n", "import requests\n"], 2, msg), ["import os\n", "from fork import USERNAME\n", "#EXT1#EXTimport requests\n"])

    def test_c0413(self):
        """'Import should be placed at the top of the module' marcados correctamente"""
        self.assertEqual(pylint_errors.c0413(["x = 5", "import os", "y = 6"], 1), ["x = 5", "#TOPimport os", "y = 6"])

    def test_w0404(self):
        """'Unused import' marcado correctamente"""
        self.assertEqual(pylint_errors.w0404(["import os\n", "import os\n", "import requests\n"], 1), ["import os\n", "#DELimport os\n", "import requests\n"])

    def test_w0611(self):
        """'Unused import' marcado correctamente"""
        self.assertEqual(pylint_errors.w0611(["import os\n"], 0), ["#DELimport os\n"])

    def test_placeholder_split(self):
        """Placeholder #SPLIT eliminado y línea corregida correctamente"""
        self.assertEqual(pylint_errors.placeholder_split("#SPLIT6#SPLITx = 5;y = 6\n"), "x = 5\ny = 6\n")

    def test_placeholder_importsplit(self):
        """Placeholder #IMPORTSPLIT eliminado y línea corregida correctamente"""
        self.assertEqual(pylint_errors.placeholder_importsplit("#IMPORTSPLITimport os, re\n"), "import os\nimport re\n")

    def test_placeholder_external(self):
        """Placeholder #EXT eliminado y línea corregida correctamente"""
        self.assertEqual(pylint_errors.placeholder_external(["import os\n", "from fork import USERNAME\n", "#EXT1#EXTimport requests\n"], 2), ["import os\n", "import requests\n", "from fork import USERNAME\n"])

    def test_placeholder_top(self):
        """Placeholder #TOP eliminado y línea corregida correctamente"""
        self.assertEqual(pylint_errors.placeholder_top(["x = 5", "#TOPimport os", "y = 6"], 1), ["import os", "x = 5", "y = 6"])
