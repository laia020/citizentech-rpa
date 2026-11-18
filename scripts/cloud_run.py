"""Entrada do workflow hospedado; não cria infraestrutura nem publica código."""

import json
import os
import sqlite3
import subprocess
from pathlib import Path

from citizentech_rpa.api import ApiClient, DemoClient
from citizentech_rpa.pipeline import run_batch


def restore_state(run_id, initialize, directory):
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    database = directory / "ocorrencias.sqlite3"
    if run_id:
        if not run_id.isascii() or not run_id.isdigit() or int(run_id) < 1:
            raise ValueError("execucao_anterior_invalida")
        subprocess.run([
            "gh", "run", "download", run_id, "--name", "rpa-state", "--dir", str(directory),
        ], check=True, capture_output=True, timeout=90)
        if not database.is_file():
            raise ValueError("artefato_sem_estado")
        with sqlite3.connect(f"file:{database}?mode=ro", uri=True) as connection:
            if connection.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise ValueError("estado_invalido")
            connection.execute("SELECT mode,id,fingerprint,status,result FROM occurrences LIMIT 1")
    elif not initialize:
        raise ValueError("restaure_estado_ou_confirme_inicializacao")
    elif database.exists():
        raise ValueError("nao_substituir_estado_existente")


def main():
    mode = os.environ.get("RPA_MODE", "simulado")
    example = os.environ.get("RPA_EXAMPLE", "lote-demo.json")
    if mode not in {"simulado", "real"} or example not in {"lote-demo.json", "lote-demo.csv", "lote-real.json"}:
        raise ValueError("entrada_workflow_invalida")
    previous = os.environ.get("RPA_PREVIOUS_RUN", "").strip()
    initialize = os.environ.get("RPA_INITIALIZE", "false") == "true"
    restore_state(previous, initialize, Path("state"))
    # Sem este marcador o workflow não arquiva uma restauração incompleta.
    with open(os.environ["GITHUB_OUTPUT"], "a") as stream:
        stream.write("estado_pronto=true\n")
    client = ApiClient() if mode == "real" else DemoClient()
    result = run_batch(
        Path("examples") / example, output_root=Path("runs"),
        state_path=Path("state/ocorrencias.sqlite3"), client=client,
        resume=os.environ.get("RPA_RESUME", "false") == "true",
    )
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as stream:
        stream.write(f"### CitizenTech RPA - {mode}\n\n")
        stream.write(f"Execução: `{result['execucao_id']}`. Estado anterior: `{previous or 'NOVO, confirmado'}`.\n\n")
        stream.write("| Resultado | Itens |\n|---|---:|\n")
        for key, count in result["contagens"].items():
            stream.write(f"| {key} | {count} |\n")
        stream.write("\nBaixe `rpa-resultados` e `rpa-state`. Na próxima execução restaure o estado deste run.\n")
        stream.write("O consumidor Akona ainda não foi conectado. Modo simulado não comprova integração.\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result["exit_code"]


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, sqlite3.Error, subprocess.SubprocessError):
        print("Falha na preparação do estado: confira run anterior, artefato e confirmação de estado novo.")
        raise SystemExit(2) from None
