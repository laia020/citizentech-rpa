"""Contrato operacional de restauração da nuvem, com gh simulado."""

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class CloudTests(unittest.TestCase):
    def load(self):
        path = Path(__file__).resolve().parents[1] / "scripts/cloud_run.py"
        spec = importlib.util.spec_from_file_location("cloud_run", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_missing_state_cannot_be_silently_reset(self):
        module = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                module.restore_state("", False, Path(tmp))

    def test_new_state_is_explicit_and_bad_run_id_cannot_execute_shell(self):
        module = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            module.restore_state("", True, Path(tmp))
            with patch("subprocess.run") as execute:
                with self.assertRaises(ValueError):
                    module.restore_state("1;echo token", False, Path(tmp))
                execute.assert_not_called()

    def test_restore_failure_aborts_without_fresh_database(self):
        import subprocess
        module = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "gh")):
                with self.assertRaises(subprocess.CalledProcessError):
                    module.restore_state("123", False, Path(tmp))
            self.assertFalse((Path(tmp) / "ocorrencias.sqlite3").exists())
