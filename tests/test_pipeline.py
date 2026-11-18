"""Especificações escritas antes do pipeline; clientes abaixo são simulados."""

import json
import tempfile
import unittest
from pathlib import Path

from citizentech_rpa.pipeline import run_batch
from citizentech_rpa.api import ApiError


def occurrence(identifier="DEMO-001", **changes):
    return {
        "ocorrencia_id": identifier,
        "simulada": True,
        "pergunta": "Que registro pode ser feito sem determinar a causa?",
        "relato": "Luminária fictícia apagada à noite, sem inspeção de causa.",
        "tipo": "luminaria_apagada",
        "bairro": "Bairro demonstrativo",
        "ponto": "Poste fictício A",
        **changes,
    }


def response(identifier, status="analise_preliminar"):
    return {
        "request_id": "SIMULADO-" + identifier,
        "ocorrencia_id": identifier,
        "analise": {
            "status": status,
            "resumo": "Resposta simulada para testar o contrato; sem diagnóstico.",
            "hipoteses": [],
            "informacoes_faltantes": [],
            "encaminhamento": "Revisão humana.",
            "fontes": [],
        },
        "referencias": [],
        "execucao": {
            "modo": "rag_finetuning",
            "modelo": "SIMULADO, sem inferência",
            "versao_base": "teste",
            "duracao_ms": 0,
        },
    }


class FakeClient:
    mode = "simulado"

    def __init__(self, status="analise_preliminar", failures=None):
        self.calls = []
        self.status = status
        self.failures = failures or {}

    def analyze(self, payload, event):
        self.calls.append(payload)
        event("api", "tentativa", tentativa=1)
        if payload["ocorrencia_id"] in self.failures:
            raise self.failures[payload["ocorrencia_id"]]
        return response(payload["ocorrencia_id"], self.status)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.client = FakeClient()

    def run_rows(self, rows, **kwargs):
        path = self.root / "input.json"
        path.write_text(json.dumps(rows), encoding="utf-8")
        return self.run_path(path, **kwargs)

    def run_path(self, path, **kwargs):
        return run_batch(
            path, output_root=self.root / "runs", state_path=self.root / "state.sqlite3",
            client=self.client, **kwargs,
        )

    def outputs(self, summary):
        return json.loads((Path(summary["diretorio"]) / "resultados.json").read_text())

    def test_valid_batch_and_contract_mapping(self):
        result = self.run_rows([occurrence(), occurrence("DEMO-002")])
        self.assertEqual(result["contagens"], {
            "entradas": 2, "processados": 2, "duplicados": 0, "pendencias": 0, "falhas": 0,
        })
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(len(self.client.calls), 2)
        self.assertNotIn("bairro", self.client.calls[0])
        self.assertNotIn("ponto", self.client.calls[0])
        self.assertEqual(self.outputs(result)[0]["ia"]["ocorrencia_id"], "DEMO-001")

    def test_decision_incomplete_continues_remaining_items(self):
        result = self.run_rows([occurrence(pergunta=""), occurrence("DEMO-002")])
        self.assertEqual(result["contagens"]["pendencias"], 1)
        self.assertEqual(result["contagens"]["processados"], 1)
        self.assertEqual(len(self.client.calls), 1)

    def test_duplicates_conflict_and_restart(self):
        result = self.run_rows([occurrence(), occurrence(), occurrence(relato="Texto diferente.")])
        self.assertEqual(result["contagens"]["processados"], 1)
        self.assertEqual(result["contagens"]["duplicados"], 1)
        self.assertEqual(result["contagens"]["pendencias"], 1)
        self.assertEqual(self.outputs(result)[2]["codigo"], "id_conflitante")
        self.client = FakeClient()
        again = self.run_rows([occurrence()])
        self.assertEqual(again["contagens"]["duplicados"], 1)
        self.assertEqual(self.client.calls, [])
        self.assertEqual(self.outputs(again)[0]["ia"]["request_id"], "SIMULADO-DEMO-001")

    def test_missing_invalid_file_and_invalid_collection(self):
        missing = self.run_path(self.root / "missing.json")
        self.assertEqual(missing["erro_arquivo"], "arquivo_ausente")
        invalid = self.root / "invalid.json"
        for content in ['{', '{"ocorrencias": []}', '[]']:
            invalid.write_text(content)
            result = self.run_path(invalid)
            self.assertEqual(result["exit_code"], 2)
        self.assertEqual(self.client.calls, [])

    def test_csv_boolean_mapping_and_bad_row(self):
        path = self.root / "input.csv"
        path.write_text(
            'ocorrencia_id,simulada,pergunta,relato,bairro\n'
            'CSV-001,true,Como registrar?,Luminária fictícia apagada.,Centro fictício\n'
            'CSV-002,false,Como registrar?,Dado não autorizado.,Centro fictício\n', encoding="utf-8"
        )
        result = self.run_path(path)
        self.assertEqual(result["contagens"]["processados"], 1)
        self.assertEqual(result["contagens"]["pendencias"], 1)
        self.assertIs(self.client.calls[0]["simulada"], True)

    def test_rejects_unknown_fields_real_data_naive_date_and_calibration(self):
        result = self.run_rows([
            occurrence(email="nao-enviar@example.invalid"),
            occurrence("DEMO-002", simulada=False),
            occurrence("DEMO-003", observado_em="2026-11-18T22:00:00"),
            occurrence("DEMO-004", sensores=[{
                "tipo": "luminosidade", "valor": 10, "unidade": "ADC", "calibrado": True,
            }]),
            123,
        ])
        self.assertEqual(result["contagens"]["pendencias"], 5)
        self.assertEqual(self.client.calls, [])
        audit = (Path(result["diretorio"]) / "auditoria.jsonl").read_text()
        self.assertNotIn("nao-enviar", audit)
        self.assertNotIn("Luminária", audit)

    def test_business_refusal_is_processed_and_routes_to_human(self):
        self.client = FakeClient(status="informacao_insuficiente")
        result = self.run_rows([occurrence()])
        output = self.outputs(result)[0]
        self.assertEqual(output["status_rpa"], "processado")
        self.assertEqual(output["status_ia"], "informacao_insuficiente")
        self.assertEqual(output["destino"], "complementar_informacoes")

    def test_failed_item_requires_explicit_resume_and_preserves_others(self):
        self.client = FakeClient(failures={"DEMO-001": ApiError("http_503", retryable=True)})
        first = self.run_rows([occurrence(), occurrence("DEMO-002")])
        self.assertEqual(first["contagens"]["falhas"], 1)
        self.assertEqual(first["contagens"]["processados"], 1)
        self.client = FakeClient()
        second = self.run_rows([occurrence(), occurrence("DEMO-002")])
        self.assertEqual(second["contagens"]["pendencias"], 1)
        self.assertEqual(second["contagens"]["duplicados"], 1)
        self.assertEqual(self.client.calls, [])
        resumed = self.run_rows([occurrence()], resume=True)
        self.assertEqual(resumed["contagens"]["processados"], 1)
        self.assertEqual(len(self.client.calls), 1)

    def test_schema_or_correlation_error_is_not_success(self):
        for broken in [{"request_id": "x"}, response("wrong-id")]:
            with self.subTest(broken=broken):
                self.client.analyze = lambda payload, event: broken
                result = self.run_rows([occurrence("SCHEMA-" + str(len(broken)))])
                self.assertEqual(result["contagens"]["falhas"], 1)

    def test_resume_does_not_repeat_same_failed_id_inside_one_batch(self):
        self.client = FakeClient(failures={"DEMO-001": ApiError("http_503", retryable=True)})
        self.run_rows([occurrence()])
        self.client = FakeClient(failures={"DEMO-001": ApiError("http_503", retryable=True)})
        result = self.run_rows([occurrence(), occurrence()], resume=True)
        self.assertEqual(len(self.client.calls), 1)
        self.assertEqual(result["contagens"]["falhas"], 1)
        self.assertEqual(result["contagens"]["pendencias"], 1)

    def test_traceability_input_to_response_and_audit(self):
        result = self.run_rows([occurrence()])
        output = self.outputs(result)[0]
        audit = [json.loads(line) for line in (Path(result["diretorio"]) / "auditoria.jsonl").read_text().splitlines()]
        self.assertEqual(output["execucao_id"], result["execucao_id"])
        self.assertEqual(output["request_id"], output["ia"]["request_id"])
        self.assertEqual(output["integracao"], "simulada")
        self.assertTrue(all(row["execucao_id"] == result["execucao_id"] for row in audit))
        self.assertTrue(all(row["data_hora"].endswith("+00:00") for row in audit))


if __name__ == "__main__":
    unittest.main()
