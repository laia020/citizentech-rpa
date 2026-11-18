import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from citizentech_rpa.pipeline import read_batch, run_batch
from citizentech_rpa.storage import open_state, save
from citizentech_rpa.validation import ItemError, validate_input
from test_pipeline import FakeClient, occurrence


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.state = self.root / "state.sqlite3"
        self.path = self.root / "in.json"
        self.path.write_text(json.dumps([occurrence()]))
        self.client = FakeClient()

    def run_batch(self, **kwargs):
        return run_batch(self.path, output_root=self.root / "runs", state_path=self.state,
                         client=self.client, **kwargs)

    def test_interruption_after_send_marker_requires_human_review(self):
        _, _, fingerprint = validate_input(occurrence())
        with open_state(self.state) as connection:
            save(connection, "simulado", "DEMO-001", fingerprint, "em_envio")
        summary = self.run_batch(resume=True)
        self.assertEqual(summary["contagens"]["pendencias"], 1)
        outputs = json.loads((Path(summary["diretorio"]) / "resultados.json").read_text())
        self.assertEqual(outputs[0]["codigo"], "resultado_incerto_revisao")
        self.assertEqual(self.client.calls, [])

    def test_concurrent_batch_cannot_use_locked_state(self):
        with open_state(self.state):
            summary = self.run_batch()
        self.assertEqual(summary["erro_execucao"], "estado_em_uso")
        self.assertEqual(summary["exit_code"], 2)
        self.assertEqual(self.client.calls, [])

    def test_simulation_does_not_suppress_real_integration(self):
        self.run_batch()
        # Mesmo cliente simulado, namespace real: comprova isolamento sem chamar rede.
        self.client = FakeClient()
        self.client.mode = "real"
        result = self.run_batch()
        self.assertEqual(result["contagens"]["processados"], 1)
        self.assertEqual(len(self.client.calls), 1)

    def test_nonfinite_json_and_duplicate_keys_are_rejected(self):
        for text in ['[{"valor": NaN}]', '[{"id": 1, "id": 2}]']:
            self.path.write_text(text)
            with self.assertRaises(ItemError):
                read_batch(self.path)

    def test_unicode_and_default_arrays_are_idempotent(self):
        first = occurrence(relato="Luminária fictícia.")
        second = occurrence(relato="  Lumina\u0301ria fictícia.  ", sensores=[], observacoes_visuais=[])
        self.assertEqual(validate_input(first)[2], validate_input(second)[2])


if __name__ == "__main__":
    unittest.main()
