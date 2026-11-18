"""Contrato público congelado e regras locais, sem inferir informações ausentes."""

import hashlib
import json
import re
import unicodedata
from datetime import datetime
from importlib.resources import files

from jsonschema import Draft202012Validator

SPEC = json.loads(files("citizentech_rpa").joinpath("contracts/ia.openapi.json").read_text())
INPUT_FIELDS = set(SPEC["components"]["schemas"]["Occurrence"]["properties"])
METADATA_FIELDS = {"tipo", "bairro", "ponto"}


def validator(name):
    return Draft202012Validator({
        "$ref": "#/components/schemas/" + name,
        "components": SPEC["components"],
    })


INPUT_VALIDATOR = validator("Occurrence")
OUTPUT_VALIDATOR = validator("AnalysisResponse")


class ItemError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def normalized(value):
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value).strip()
    if isinstance(value, dict):
        return {key: normalized(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalized(item) for item in value]
    return value


def validate_input(raw):
    if not isinstance(raw, dict):
        raise ItemError("registro_nao_objeto")
    if set(raw) - INPUT_FIELDS - METADATA_FIELDS:
        raise ItemError("campos_nao_permitidos")
    entry = normalized(raw)
    payload = {key: value for key, value in entry.items() if key in INPUT_FIELDS}
    if not INPUT_VALIDATOR.is_valid(payload):
        raise ItemError("contrato_entrada_invalido")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", payload["ocorrencia_id"]):
        raise ItemError("identificador_invalido")
    if payload["simulada"] is not True:
        raise ItemError("somente_dados_ficticios")
    if not payload["pergunta"]:
        raise ItemError("pergunta_ausente")
    if not (payload.get("relato") or payload.get("sensores") or payload.get("observacoes_visuais")):
        raise ItemError("observacao_ausente")
    for key in METADATA_FIELDS:
        if key in entry and (not isinstance(entry[key], str) or len(entry[key]) > 200):
            raise ItemError("metadado_invalido")
    if payload.get("observado_em"):
        try:
            date = datetime.fromisoformat(payload["observado_em"])
            if date.tzinfo is None or date.utcoffset() is None:
                raise ValueError
        except ValueError:
            raise ItemError("data_sem_fuso_ou_invalida") from None
    for sensor in payload.get("sensores", []):
        if not sensor["tipo"] or not sensor["unidade"]:
            raise ItemError("sensor_invalido")
        if sensor["calibrado"] and not sensor.get("referencia_calibracao"):
            raise ItemError("referencia_calibracao_ausente")
    if any(not visual["descricao"] for visual in payload.get("observacoes_visuais", [])):
        raise ItemError("observacao_visual_vazia")
    # Ausência e valor default são equivalentes para a idempotência.
    payload.setdefault("relato", "")
    payload.setdefault("sensores", [])
    payload.setdefault("observacoes_visuais", [])
    for key in ("municipio", "observado_em"):
        if payload.get(key) is None:
            payload.pop(key, None)
    entry = {**payload, **{key: entry[key] for key in sorted(METADATA_FIELDS) if key in entry}}
    try:
        digest = hashlib.sha256(encode(entry)).hexdigest()
    except (ValueError, UnicodeError):
        raise ItemError("texto_ou_numero_invalido") from None
    return entry, payload, digest


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def validate_response(value, occurrence_id):
    if not OUTPUT_VALIDATOR.is_valid(value):
        raise ItemError("contrato_resposta_invalido")
    if not value["request_id"].strip() or value["ocorrencia_id"] != occurrence_id:
        raise ItemError("correlacao_resposta_invalida")
    return value
