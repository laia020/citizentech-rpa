"""Validação de artefatos, sem IA. --online verifica somente links GET/HEAD."""

import argparse
import hashlib
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pymupdf

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_url(url):
    try:
        with urlopen(Request(url, method="HEAD"), timeout=35) as response:
            return {"url": url, "status": response.status}
    except HTTPError as error:
        if error.code == 405:
            with urlopen(url, timeout=35) as response:
                response.read(1024)
                return {"url": url, "status": response.status}
        return {"url": url, "status": error.code}
    except OSError:
        return {"url": url, "erro": "falha_rede"}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--online",action="store_true")
    args=parser.parse_args()
    checks={"data_hora":datetime.now(timezone.utc).isoformat(),"teste_ia":False}
    test_info=json.loads((ROOT/"docs/evidencias/testes.json").read_text())
    assert test_info["aprovado"]
    for path,digest in test_info["sha256_fontes"].items():
        assert sha(ROOT/path)==digest, f"Fonte mudou após teste: {path}"
    checks["testes_aprovados"]=test_info["testes"]
    spec=json.loads((ROOT/"docs/evidencias/contrato-origem.json").read_text())
    assert sha(ROOT/"src/citizentech_rpa/contracts/ia.openapi.json")==spec["sha256"]
    checks["contrato_sha256_conferido"]=True
    evidence=[]
    for summary_path in sorted((ROOT/"docs/evidencias").glob("*/resumo.json")):
        summary=json.loads(summary_path.read_text())
        results=json.loads(summary_path.with_name("resultados.json").read_text())
        counts=summary["contagens"]
        assert len(results)==counts["processados"]+counts["duplicados"]+counts["pendencias"]+counts["falhas"]
        assert all(result["execucao_id"]==summary["execucao_id"] for result in results)
        if not summary.get("erro_execucao"):
            assert len(results)==counts["entradas"]
        if summary.get("entrada_sha256"):
            assert summary["entrada_sha256"] in {sha(path) for path in (ROOT/"examples").iterdir()}
        for line in summary_path.with_name("auditoria.jsonl").read_text().splitlines():
            event=json.loads(line)
            assert datetime.fromisoformat(event["data_hora"]).tzinfo is not None
            assert event["execucao_id"]==summary["execucao_id"]
        evidence.append({"cenario":summary_path.parent.name,"execucao_id":summary["execucao_id"],"contagens":counts})
    checks["evidencias"]=evidence
    tree=ET.parse(ROOT/"docs/processo.bpmn")
    ids=[node.get("id") for node in tree.iter() if node.get("id")]
    assert len(ids)==len(set(ids))
    for node in tree.iter():
        for name in ["sourceRef","targetRef","attachedToRef","processRef","bpmnElement","errorRef","default"]:
            if node.get(name):
                assert node.get(name) in ids
    checks["bpmn_ids_referencias"]=True
    schema=ROOT/"tmp/bpmn-xsd/BPMN20.xsd"
    if schema.exists() and shutil.which("xmllint"):
        result=subprocess.run(["xmllint","--noout","--schema",str(schema),str(ROOT/"docs/processo.bpmn")],capture_output=True,text=True,check=True)
        checks["bpmn_xsd_oficial"]={"aprovado":True,"origem":"https://www.omg.org/spec/BPMN/20100501/BPMN20.xsd","bpmn_sha256":sha(ROOT/"docs/processo.bpmn"),"schema_sha256":sha(schema)}
    with pymupdf.open(ROOT/"output/pdf/relatorio-tecnico-rpa.pdf") as doc:
        text="\n".join(page.get_text() for page in doc)
        info=json.loads((ROOT/"docs/entrega.json").read_text())
        for member in info["equipe"]:
            assert member["nome"] in text and member["rm"] in text
        assert "PENDENTE" in text and "503" in text and "BPMN" in text
        links=sorted({link["uri"] for page in doc for link in page.get_links() if link.get("uri")})
        assert all(link.startswith("https://") for link in links)
        for page in doc:
            for block in page.get_text("blocks"):
                rect=pymupdf.Rect(block[:4])
                assert page.rect.contains(rect),"Texto fora da página"
        checks["pdf"]={"paginas":len(doc),"equipe_conferida":True,"texto_dentro_das_paginas":True,"urls":links,"sha256":sha(ROOT/"output/pdf/relatorio-tecnico-rpa.pdf")}
    if args.online:
        with ThreadPoolExecutor(max_workers=4) as pool:
            checks["links_http"]=list(pool.map(check_url,links))
    # Manifesto das evidências: não inclui este arquivo para evitar hash circular.
    checks["sha256_evidencias"]={str(path.relative_to(ROOT)):sha(path) for path in sorted((ROOT/"docs/evidencias").rglob("*")) if path.is_file() and path.name!="validacao-artefatos.json"}
    (ROOT/"docs/evidencias/validacao-artefatos.json").write_text(json.dumps(checks,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"testes":checks["testes_aprovados"],"cenarios":len(evidence),"pdf_paginas":checks["pdf"]["paginas"],"bpmn_xsd":bool(checks.get("bpmn_xsd_oficial")),"links":checks.get("links_http","não consultados")},ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
