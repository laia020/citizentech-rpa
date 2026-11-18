"""HTTP controlado em memória; nenhum teste desta suíte acessa a internet."""

import io
import json
import socket
import unittest
from urllib.error import HTTPError, URLError
from unittest.mock import Mock

from citizentech_rpa.api import ApiClient, ApiError
from test_pipeline import occurrence, response


def http_error(code, retry_after=None):
    headers = {} if retry_after is None else {"Retry-After": retry_after}
    return HTTPError("https://example.invalid", code, "mensagem não deve vazar", headers, io.BytesIO(b"segredo"))


def ok(body=None):
    stream = io.BytesIO(json.dumps(body or response("DEMO-001")).encode())
    stream.status = 200
    return stream


class ApiTests(unittest.TestCase):
    def client(self, effects, **kwargs):
        self.opener = Mock(side_effect=effects)
        self.sleep = Mock()
        self.events = []
        return ApiClient(opener=self.opener, sleep=self.sleep, **kwargs)

    def event(self, *args, **kwargs):
        self.events.append((args, kwargs))

    def test_429_respects_retry_after_and_limits_attempts(self):
        client = self.client([http_error(429, "3"), ok()])
        result = client.analyze(occurrence(), self.event)
        self.assertEqual(result["request_id"], "SIMULADO-DEMO-001")
        self.sleep.assert_called_once_with(3.0)
        self.assertEqual(self.opener.call_count, 2)
        self.assertEqual(self.opener.call_args.kwargs["timeout"], 120)

    def test_excessive_retry_after_defers_instead_of_retrying_early(self):
        client = self.client([http_error(429, "3600")])
        with self.assertRaises(ApiError) as error:
            client.analyze(occurrence(), self.event)
        self.assertEqual(error.exception.code, "http_429")
        self.sleep.assert_not_called()
        self.assertEqual(self.opener.call_count, 1)

    def test_503_retry_exhausted(self):
        client = self.client([http_error(503)] * 3, attempts=3)
        with self.assertRaises(ApiError) as error:
            client.analyze(occurrence(), self.event)
        self.assertEqual(error.exception.code, "http_503")
        self.assertEqual(self.opener.call_count, 3)
        self.assertTrue(error.exception.retryable)

    def test_502_413_422_are_not_retried(self):
        for status in [502, 413, 422]:
            client = self.client([http_error(status)])
            with self.assertRaises(ApiError) as error:
                client.analyze(occurrence(), self.event)
            self.assertEqual(error.exception.code, f"http_{status}")
            self.assertNotIn("segredo", str(error.exception))
            self.assertEqual(self.opener.call_count, 1)

    def test_timeout_is_uncertain_and_not_repeated_automatically(self):
        for failure in [socket.timeout(), URLError("rede indisponível")]:
            client = self.client([failure])
            with self.assertRaises(ApiError) as error:
                client.analyze(occurrence(), self.event)
            self.assertTrue(error.exception.uncertain)
            self.assertEqual(self.opener.call_count, 1)

    def test_body_limit_prevents_network_call(self):
        client = self.client([])
        with self.assertRaises(ApiError) as error:
            client.analyze({"relato": "a" * 32768}, self.event)
        self.assertEqual(error.exception.code, "corpo_excedido")
        self.opener.assert_not_called()

    def test_invalid_json_not_repaired(self):
        stream = io.BytesIO(b'{"invalido":')
        stream.status = 200
        client = self.client([stream])
        with self.assertRaises(ApiError) as error:
            client.analyze(occurrence(), self.event)
        self.assertEqual(error.exception.code, "resposta_invalida")
        self.assertEqual(self.opener.call_count, 1)


if __name__ == "__main__":
    unittest.main()
