"""Cliente sequencial. Nunca repara JSON nem repete geração rejeitada (502)."""

import json
import socket
import time
import uuid
from http.client import HTTPException
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .validation import encode

ENDPOINT = "https://laia020-citizentech-iluminacao-ia.hf.space/v1/analisar"
MAX_BODY = 32 * 1024
MAX_RESPONSE = 256 * 1024


class ApiError(Exception):
    def __init__(self, code, *, retryable=False, uncertain=False):
        self.code = code
        self.retryable = retryable
        self.uncertain = uncertain
        super().__init__(code)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def retry_delay(value, fallback):
    if value is None:
        return fallback
    try:
        delay = float(value)
        if not (0 <= delay <= 86400):
            return 86400
        return delay
    except ValueError:
        try:
            date = parsedate_to_datetime(value)
            if date.tzinfo is None:
                return 86400
            return max(0, (date - datetime.now(timezone.utc)).total_seconds())
        except (ValueError, TypeError, OverflowError):
            return 86400  # Não antecipar Retry-After que não entendemos.


class ApiClient:
    mode = "real"

    def __init__(self, *, timeout=120, attempts=2, max_wait=15, opener=None, sleep=time.sleep):
        if not 1 <= attempts <= 3 or not 1 <= timeout <= 180 or not 0 <= max_wait <= 30:
            raise ValueError("configuracao_api_invalida")
        self.timeout = timeout
        self.attempts = attempts
        self.max_wait = max_wait
        self.opener = opener or build_opener(NoRedirect()).open
        self.sleep = sleep

    def analyze(self, payload, event):
        body = encode(payload)
        if len(body) > MAX_BODY:
            raise ApiError("corpo_excedido")
        request = Request(ENDPOINT, data=body, headers={
            "Content-Type": "application/json", "Accept": "application/json",
            "User-Agent": "CitizenTech-RPA-POC/0.1",
        }, method="POST")
        for attempt in range(1, self.attempts + 1):
            event("api", "tentativa", tentativa=attempt)
            try:
                with self.opener(request, timeout=self.timeout) as response:
                    raw = response.read(MAX_RESPONSE + 1)
                    if response.status != 200 or len(raw) > MAX_RESPONSE:
                        raise ApiError("resposta_invalida", uncertain=True)
                    try:
                        def reject_constant(value):
                            raise ValueError("json_nao_finito")
                        value = json.loads(raw, parse_constant=reject_constant)
                    except (ValueError, UnicodeError):
                        raise ApiError("resposta_invalida", uncertain=True) from None
                    event("api", "recebido", tentativa=attempt, http_status=200)
                    return value
            except HTTPError as error:
                status = error.code
                delay = retry_delay(error.headers.get("Retry-After"), 2 ** (attempt - 1))
                error.close()
                transient = status in {429, 503}
                event("api", "erro_http", tentativa=attempt, http_status=status, codigo=f"http_{status}")
                if transient and attempt < self.attempts and delay <= self.max_wait:
                    event("api", "aguardando", tentativa=attempt, espera_segundos=delay)
                    self.sleep(delay)
                    continue
                raise ApiError(f"http_{status}", retryable=transient) from None
            except (socket.timeout, TimeoutError, URLError, ConnectionError, OSError, HTTPException):
                # A API não oferece consulta/idempotency-key: um POST pode ter sido concluído.
                event("api", "resultado_incerto", tentativa=attempt, codigo="rede_ou_timeout")
                raise ApiError("rede_ou_timeout", uncertain=True) from None


class DemoClient:
    """Resposta fixa e explicitamente simulada, sem rede e sem inferência."""

    mode = "simulado"

    def analyze(self, payload, event):
        event("simulador", "resposta_simulada", tentativa=1)
        return {
            "request_id": "SIMULADO-" + uuid.uuid4().hex,
            "ocorrencia_id": payload["ocorrencia_id"],
            "analise": {
                "status": "analise_preliminar",
                "resumo": "SIMULAÇÃO: observação organizada, sem análise de modelo ou diagnóstico.",
                "hipoteses": [], "informacoes_faltantes": [], "fontes": [],
                "encaminhamento": "SIMULAÇÃO: submeter a revisão humana; nenhum chamado foi criado.",
            },
            "referencias": [],
            "execucao": {"modo": "rag_finetuning", "modelo": "SIMULADO - nenhum modelo executado",
                         "versao_base": "simulacao-rpa-1", "duracao_ms": 0},
        }
