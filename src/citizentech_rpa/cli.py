import argparse
import json
from pathlib import Path

from .api import ApiClient, DemoClient
from .pipeline import run_batch


def main(argv=None):
    parser = argparse.ArgumentParser(description="CitizenTech RPA: somente ocorrências fictícias. Não cria chamados.")
    parser.add_argument("arquivo", type=Path, help="CSV UTF-8 ou JSON (lista), até 100 registros / 1 MiB")
    parser.add_argument("--modo", choices=["simulado", "real"], default="simulado", help="real consulta a IA pública; padrão: simulado, sem rede")
    parser.add_argument("--saida", type=Path, default=Path("runs"))
    parser.add_argument("--estado", type=Path, default=Path("state/ocorrencias.sqlite3"))
    parser.add_argument("--retomar-falhas", action="store_true", help="repete somente falhas 429/503 registradas, preservando sucessos e incertos")
    parser.add_argument("--timeout", type=int, default=120, choices=range(1, 181), metavar="1..180")
    parser.add_argument("--tentativas", type=int, choices=[1, 2, 3], default=2)
    args = parser.parse_args(argv)
    client = ApiClient(timeout=args.timeout, attempts=args.tentativas) if args.modo == "real" else DemoClient()
    summary = run_batch(args.arquivo, output_root=args.saida, state_path=args.estado, client=client, resume=args.retomar_falhas)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary["exit_code"]
