"""Uma execução transforma um lote em resultados e auditoria verificáveis."""

import csv
import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .api import ApiError
from .storage import lookup, open_state, save
from .validation import ItemError, validate_input, validate_response

MAX_FILE = 1024 * 1024
MAX_ITEMS = 100


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def write_json(path, value):
    # Destinos por UUID e abertura exclusiva: nunca substituir evidência existente.
    with open(path, "x", encoding="utf-8") as stream:
        os.chmod(path, 0o600)
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def strict_constant(value):
    raise ValueError("json_nao_finito")


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("chave_json_repetida")
        obj[key] = value
    return obj


def read_batch(path):
    try:
        # Limite aplicado à leitura, inclusive se o arquivo crescer durante a execução.
        with open(path, "rb") as stream:
            raw = stream.read(MAX_FILE + 1)
        if len(raw) > MAX_FILE:
            raise ItemError("arquivo_grande")
        text = raw.decode("utf-8-sig")
        if path.suffix.lower() == ".json":
            records = json.loads(text, parse_constant=strict_constant, object_pairs_hook=unique_object)
        elif path.suffix.lower() == ".csv":
            import io
            reader = csv.DictReader(io.StringIO(text), strict=True)
            fields = reader.fieldnames or []
            if not fields or len(fields) != len(set(fields)) or any(not f for f in fields):
                raise ItemError("cabecalho_csv_invalido")
            records = []
            for row in reader:
                if None in row or any(value is None for value in row.values()):
                    raise ItemError("colunas_csv_inconsistentes")
                row = {key: value for key, value in row.items() if value.strip()}
                if "simulada" in row:
                    row["simulada"] = {"true": True, "false": False}.get(row["simulada"].strip().lower(), row["simulada"])
                for key in ("sensores", "observacoes_visuais"):
                    if key in row:
                        try:
                            row[key] = json.loads(row[key], parse_constant=strict_constant, object_pairs_hook=unique_object)
                        except ValueError:
                            row[key] = None  # Validação do item registra a pendência sem abortar os demais.
                records.append(row)
        else:
            raise ItemError("formato_nao_suportado")
        if not isinstance(records, list) or not 1 <= len(records) <= MAX_ITEMS:
            raise ItemError("colecao_invalida")
        return records, hashlib.sha256(raw).hexdigest()
    except FileNotFoundError:
        raise ItemError("arquivo_ausente") from None
    except (OSError, UnicodeError, ValueError, csv.Error, RecursionError):
        raise ItemError("arquivo_invalido") from None


def process_item(raw, line, run_id, mode, connection, client, event, resume):
    result = {"execucao_id": run_id, "linha": line, "integracao": "real" if mode == "real" else "simulada"}
    try:
        entry, payload, fingerprint = validate_input(raw)
    except ItemError as error:
        return {**result, "status_rpa": "pendente", "codigo": error.code}
    identifier = payload["ocorrencia_id"]
    item_ref = hashlib.sha256(identifier.encode()).hexdigest()[:16]
    result.update(ocorrencia_id=identifier, item_ref=item_ref, fingerprint=fingerprint, entrada=entry)

    def item_event(stage, outcome, **details):
        event(stage, outcome, linha=line, item_ref=item_ref, **details)

    previous = lookup(connection, mode, identifier)
    if previous:
        if previous["fingerprint"] != fingerprint:
            return {**result, "status_rpa": "pendente", "codigo": "id_conflitante"}
        if previous["status"] == "processado":
            original = previous["result"]
            return {**result, "status_rpa": "duplicado", "codigo": "ja_processado",
                    "execucao_original": original["execucao_id"], "ia": original["ia"],
                    "request_id": original["request_id"], "status_ia": original["status_ia"],
                    "destino": original["destino"]}
        if previous["status"] in {"em_envio", "incerto"}:
            return {**result, "status_rpa": "pendente", "codigo": "resultado_incerto_revisao"}
        if not (resume and previous["result"].get("repetivel") and previous["result"]["execucao_id"] != run_id):
            return {**result, "status_rpa": "pendente", "codigo": "falha_anterior_revisao"}
    # Persistir antes do POST: interrupção não autoriza repetir uma chamada de resultado desconhecido.
    save(connection, mode, identifier, fingerprint, "em_envio")
    item_event("validacao", "aprovado")
    try:
        answer = validate_response(client.analyze(payload, item_event), identifier)
    except (ApiError, ItemError) as error:
        uncertain = isinstance(error, ItemError) or getattr(error, "uncertain", False)
        result.update(status_rpa="falha", codigo=error.code,
                      repetivel=getattr(error, "retryable", False), resultado_incerto=uncertain)
        save(connection, mode, identifier, fingerprint, "incerto" if uncertain else "falha", result)
        item_event("integracao", "falha", codigo=error.code)
        return result
    status = answer["analise"]["status"]
    route = {"analise_preliminar": "revisao_humana", "informacao_insuficiente": "complementar_informacoes",
             "fora_escopo": "revisao_de_escopo"}[status]
    result.update(status_rpa="processado", codigo="ok", entrada=entry, ia=answer,
                  status_ia=status, destino=route, request_id=answer["request_id"])
    save(connection, mode, identifier, fingerprint, "processado", result)
    item_event("integracao", "processado", request_id=answer["request_id"], status_ia=status)
    return result


def run_batch(input_path, *, output_root, state_path, client, resume=False):
    run_id = uuid.uuid4().hex
    directory = Path(output_root) / run_id
    directory.mkdir(parents=True, mode=0o700)
    summary = {"versao": "1.0", "execucao_id": run_id, "inicio": now(),
               "modo": client.mode, "diretorio": str(directory), "contagens": {
                   "entradas": 0, "processados": 0, "duplicados": 0, "pendencias": 0, "falhas": 0,
               }, "exit_code": 0}
    results = []
    with open(directory / "auditoria.jsonl", "x", encoding="utf-8") as audit:
        os.chmod(directory / "auditoria.jsonl", 0o600)

        def event(stage, outcome, **details):
            audit.write(json.dumps({"data_hora": now(), "execucao_id": run_id,
                                    "etapa": stage, "resultado": outcome, **details}, ensure_ascii=False) + "\n")
            audit.flush()
            os.fsync(audit.fileno())

        event("lote", "iniciado", modo=client.mode)
        try:
            records, digest = read_batch(Path(input_path))
            summary["entrada_sha256"] = digest
            summary["contagens"]["entradas"] = len(records)
            with open_state(state_path) as connection:
                for line, raw in enumerate(records, 1):
                    result = process_item(raw, line, run_id, client.mode, connection, client, event, resume)
                    results.append(result)
                    counter = {"processado": "processados", "duplicado": "duplicados", "pendente": "pendencias", "falha": "falhas"}
                    summary["contagens"][counter[result["status_rpa"]]] += 1
                    event("item", result["status_rpa"], linha=line, codigo=result["codigo"], item_ref=result.get("item_ref"))
        except ItemError as error:
            summary.update(erro_arquivo=error.code, exit_code=2)
            event("arquivo", "falha", codigo=error.code)
        except (RuntimeError, OSError, sqlite3.Error) as error:
            # Sem traceback, caminho, corpo de API ou texto arbitrário em auditoria pública.
            code = "estado_em_uso" if str(error) == "estado_em_uso" else "falha_infraestrutura"
            summary.update(erro_execucao=code, exit_code=2)
            event("infraestrutura", "falha", codigo=code)
        if summary["contagens"]["falhas"] and summary["exit_code"] == 0:
            summary["exit_code"] = 1
        summary["fim"] = now()
        summary["situacao"] = (
            "falha" if summary["exit_code"] else
            "concluida_com_pendencias" if summary["contagens"]["pendencias"] else "concluida"
        )
        event("lote", summary["situacao"], contagens=summary["contagens"], exit_code=summary["exit_code"])
    write_json(directory / "resultados.json", results)
    write_json(directory / "pendencias.json", [item for item in results if item["status_rpa"] in {"pendente", "falha"}])
    write_json(directory / "resumo.json", summary)
    return summary
