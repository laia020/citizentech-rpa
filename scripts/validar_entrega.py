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
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import pymupdf
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def text_hash_match(path, digest):
    """Reconhece só LF/CRLF, sem modificar o arquivo ou o hash histórico."""
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() == digest:
        return "bytes_originais"
    if hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest() == digest:
        return "equivalencia_lf_crlf"
    raise AssertionError(f"Hash textual divergente: {path}")


def check_url(url):
    for method in ("HEAD", "GET"):
        try:
            with urlopen(Request(url, method=method), timeout=35) as response:
                response.read(1024)
                return {"url": url, "status": response.status}
        except HTTPError as error:
            status=error.code
            error.close()
            if status==405 and method=="HEAD":
                continue
            return {"url": url, "status": status}
        except OSError:
            return {"url": url, "erro": "falha_rede"}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--online",action="store_true")
    parser.add_argument("--final",action="store_true",help="recusa prontidão se faltar item obrigatório da entrega; exige --online")
    parser.add_argument("--saida", type=Path, default=ROOT/"docs/evidencias/validacao-atual.json")
    args=parser.parse_args()
    if args.final and not args.online:
        parser.error("Use --online com --final para conferir os links de entrega.")
    output=args.saida.resolve()
    if output == (ROOT/"docs/evidencias/validacao-artefatos.json").resolve():
        parser.error("Preserve o manifesto histórico; escolha outra saída.")
    checks={"data_hora":datetime.now(timezone.utc).isoformat(),"teste_ia":False,
            "suite_reexecutada":False,"verificacao":"artefatos preservados e relatório"}
    for path in ["README.md","docs/PDD.md","docs/processo.bpmn","docs/seguranca.md",
                 "docs/integracao.md","docs/auditoria-entrega.md","docs/dados-demonstracao.md",
                 "docs/roteiro-video.md","docs/narracao-video-rpa.md","docs/evidencias/enunciado-origem.json"]:
        assert (ROOT/path).is_file(),f"Documento obrigatório ausente: {path}"
    checks["enunciado_original"]=read_json(ROOT/"docs/evidencias/enunciado-origem.json")
    assert checks["enunciado_original"]["sha256"]=="236c35530bc23f3f6c48211f022862ff5d1458f17ad2d813e1f9d5130b696c87"
    test_info=read_json(ROOT/"docs/evidencias/testes.json")
    assert test_info["aprovado"]
    checks["fontes_do_registro_historico"]={}
    for path,digest in test_info["sha256_fontes"].items():
        checks["fontes_do_registro_historico"][path]=text_hash_match(ROOT/path,digest)
    checks["testes_aprovados_no_registro_historico"]=test_info["testes"]
    spec=read_json(ROOT/"docs/evidencias/contrato-origem.json")
    assert sha(ROOT/"src/citizentech_rpa/contracts/ia.openapi.json")==spec["sha256"]
    checks["contrato_sha256_conferido"]=True
    contract=read_json(ROOT/"src/citizentech_rpa/contracts/ia.openapi.json")
    response_validator=Draft202012Validator({"$ref":"#/components/schemas/AnalysisResponse",
                                           "components":contract["components"]})
    evidence=[]
    for summary_path in sorted((ROOT/"docs/evidencias").glob("*/resumo.json")):
        summary=read_json(summary_path)
        results=read_json(summary_path.with_name("resultados.json"))
        counts=summary["contagens"]
        assert len(results)==counts["processados"]+counts["duplicados"]+counts["pendencias"]+counts["falhas"]
        assert all(result["execucao_id"]==summary["execucao_id"] for result in results)
        if not summary.get("erro_execucao"):
            assert len(results)==counts["entradas"]
        if summary.get("entrada_sha256"):
            input_matches=[]
            for path in (ROOT/"examples").iterdir():
                if path.suffix not in {".csv", ".json"}:
                    continue
                try:
                    match=text_hash_match(path,summary["entrada_sha256"])
                except AssertionError:
                    continue
                input_matches.append({"arquivo":path.name,"comparacao":match})
            assert input_matches, f"Lote não corresponde ao resumo: {summary_path}"
        else:
            input_matches=[]
        for result in results:
            if result["status_rpa"] in {"processado","duplicado"}:
                response_validator.validate(result["ia"])
                assert result["request_id"].strip()
                assert result["ia"]["ocorrencia_id"]==result["ocorrencia_id"]
                assert result["ia"]["request_id"]==result["request_id"]
                assert result["ia"]["analise"]["status"]==result["status_ia"]
        for line in summary_path.with_name("auditoria.jsonl").read_text(encoding="utf-8").splitlines():
            event=json.loads(line)
            assert datetime.fromisoformat(event["data_hora"]).tzinfo is not None
            assert event["execucao_id"]==summary["execucao_id"]
        evidence.append({"cenario":summary_path.parent.name,"execucao_id":summary["execucao_id"],
                         "contagens":counts,"lotes_compativeis":input_matches})
    checks["evidencias"]=evidence
    real_dir=ROOT/"docs/evidencias/nuvem-real"
    real=read_json(real_dir/"github-run.json")
    real_summary=read_json(real_dir/"resumo.json")
    real_results=read_json(real_dir/"resultados.json")
    real_events=[json.loads(line) for line in (real_dir/"auditoria.jsonl").read_text(encoding="utf-8").splitlines()]
    assert real["run_id"]==44327757282 and real["estado_anterior_run_id"]==44296159102
    assert real["status"]=="completed" and real["conclusion"]=="success"
    assert real["inputs"]=={"modo":"real","exemplo":"lote-real.json","estado_run_id":"44296159102",
                            "iniciar_estado":"false","retomar_falhas":"false"}
    assert real_summary["modo"]=="real" and real_summary["exit_code"]==0
    assert real_summary["contagens"]=={"entradas":4,"processados":2,"duplicados":1,"pendencias":1,"falhas":0}
    attempts=[event for event in real_events if event["etapa"]=="api" and event["resultado"]=="tentativa"]
    received=[event for event in real_events if event["etapa"]=="api" and event["resultado"]=="recebido"]
    assert len(attempts)==len(received)==2 and all(event["http_status"]==200 for event in received)
    assert all(item["integracao"]=="real" for item in real_results)
    assert all(item["entrada"]["simulada"] is True for item in real_results if "entrada" in item)
    assert real_results[1]["status_rpa"]=="duplicado"
    assert real_results[0]["request_id"]==real_results[1]["request_id"]
    assert {item["status_ia"] for item in real_results if item["status_rpa"]=="processado"}=={"analise_preliminar","informacao_insuficiente"}
    assert {(event["linha"],event["request_id"]) for event in real_events if event["etapa"]=="integracao" and event["resultado"]=="processado"}=={(item["linha"],item["request_id"]) for item in real_results if item["status_rpa"]=="processado"}
    checks["integracao_real_preservada"]={"run_id":real["run_id"],"contrato_e_correlacao":True,
                                          "chamadas":2,"respostas_http_200":2,"duplicata_sem_nova_consulta":True}
    mapping=read_json(real_dir/"mapeamento-entrada-ia.json")
    checks["mapeamento_comparacao_fonte"]=text_hash_match(real_dir/"resultados.json",mapping["resultado_fonte_sha256"])
    assert mapping["novas_chamadas_ia"]==0 and len(mapping["itens"])==2
    input_validator=Draft202012Validator({"$ref":"#/components/schemas/Occurrence","components":contract["components"]})
    for item in mapping["itens"]:
        payload=item["payload_normalizado"]
        input_validator.validate(payload)
        assert not set(payload).intersection({"tipo","bairro","ponto"})
        matches=[result for result in real_results if result.get("ocorrencia_id")==payload["ocorrencia_id"] and result.get("request_id")==item["resposta_request_id"] and result["status_rpa"]=="processado"]
        assert len(matches)==1
        assert payload=={key:value for key,value in matches[0]["entrada"].items() if key in contract["components"]["schemas"]["Occurrence"]["properties"]}
        assert item["fingerprint"]==matches[0]["fingerprint"]
    checks["mapeamento_normalizado_conferido"]=True
    tree=ET.parse(ROOT/"docs/processo.bpmn")
    ids=[node.get("id") for node in tree.iter() if node.get("id")]
    assert len(ids)==len(set(ids))
    for node in tree.iter():
        for name in ["sourceRef","targetRef","attachedToRef","processRef","bpmnElement","errorRef","default"]:
            if node.get(name):
                assert node.get(name) in ids
    checks["bpmn_ids_referencias"]=True
    historic=read_json(ROOT/"docs/evidencias/validacao-artefatos.json")
    checks["bpmn_registro_xsd_historico"]={
        "arquivo":"docs/evidencias/validacao-artefatos.json",
        "comparacao_fonte":text_hash_match(ROOT/"docs/processo.bpmn",historic["bpmn_xsd_oficial"]["bpmn_sha256"]),
    }
    checks["bpmn_xsd_revalidado"]=False
    schema=ROOT/"tmp/bpmn-xsd/BPMN20.xsd"
    if schema.exists() and shutil.which("xmllint"):
        result=subprocess.run(["xmllint","--noout","--schema",str(schema),str(ROOT/"docs/processo.bpmn")],capture_output=True,text=True,check=True)
        checks["bpmn_xsd_oficial"]={"aprovado":True,"origem":"https://www.omg.org/spec/BPMN/20100501/BPMN20.xsd","bpmn_sha256":sha(ROOT/"docs/processo.bpmn"),"schema_sha256":sha(schema)}
        checks["bpmn_xsd_revalidado"]=True
    with pymupdf.open(ROOT/"output/pdf/relatorio-tecnico-rpa.pdf") as doc:
        text="\n".join(page.get_text() for page in doc)
        info=read_json(ROOT/"docs/entrega.json")
        for member in info["equipe"]:
            assert member["nome"] in text and member["rm"] in text
        assert "PENDENTE" in text and "503" in text and "BPMN" in text
        assert "HTTP 200" in text and str(real["run_id"]) in text
        for item in real_results:
            if item["status_rpa"]=="processado":
                assert item["request_id"] in text
        assert info["integracao_bem_sucedida"] is True
        assert info["integracao_evidencia_url"]==real["url"]
        assert info["estado_ultimo_run_id"]==real["run_id"]
        links=sorted({link["uri"] for page in doc for link in page.get_links() if link.get("uri")})
        assert all(link.startswith("https://") for link in links)
        assert real["url"] in links
        if info["video_url"]:
            assert info["video_url"] in links
            assert info["video_url"] in (ROOT/"README.md").read_text(encoding="utf-8")
        else:
            assert "PENDENTE - vídeo não gravado" in text
        for page in doc:
            for block in page.get_text("blocks"):
                rect=pymupdf.Rect(block[:4])
                assert page.rect.contains(rect),"Texto fora da página"
        checks["pdf"]={"paginas":len(doc),"equipe_conferida":True,"texto_dentro_das_paginas":True,"urls":links,"sha256":sha(ROOT/"output/pdf/relatorio-tecnico-rpa.pdf")}
    if args.online:
        with ThreadPoolExecutor(max_workers=4) as pool:
            checks["links_http"]=list(pool.map(check_url,links))
    pending=[]
    video=info.get("video_url")
    if not video or urlparse(video).scheme!="https" or not urlparse(video).netloc:
        pending.append("video_publicado_com_url_https")
    duration=info.get("video_duracao_segundos")
    if isinstance(duration,bool) or not isinstance(duration,(int,float)) or not 0<duration<=180:
        pending.append("duracao_video_medida_ate_180_segundos")
    for field in ["video_acesso_publico_conferido","ficha_alinhada_com_grupo","revisao_documental_publicada"]:
        if info.get(field) is not True:
            pending.append(field)
    if not info.get("enunciado_original_conferido"):
        pending.append("enunciado_original_conferido")
    if args.online:
        by_url={item["url"]:item for item in checks["links_http"]}
        for required in [info["repositorio_rpa_url"],info["integracao_evidencia_url"],video]:
            if required and by_url.get(required,{}).get("status")!=200:
                pending.append("link_de_entrega_indisponivel:"+required)
    checks["pendencias_para_envio"]=pending
    checks["links_conferidos_nesta_execucao"]=args.online
    checks["pronto_para_envio"]=not pending and args.online
    # Manifesto das evidências: não inclui este arquivo para evitar hash circular.
    checks["sha256_evidencias"]={path.relative_to(ROOT).as_posix():sha(path) for path in sorted((ROOT/"docs/evidencias").rglob("*")) if path.is_file() and path.resolve()!=output}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(checks,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"suite_reexecutada":False,"testes_historicos":test_info["testes"],"cenarios":len(evidence),"pdf_paginas":checks["pdf"]["paginas"],"bpmn_xsd_revalidado":checks["bpmn_xsd_revalidado"],"saida":str(output),"links":checks.get("links_http","não consultados"),"pronto_para_envio":checks["pronto_para_envio"],"pendencias_para_envio":pending},ensure_ascii=False,indent=2))
    return 1 if args.final and pending else 0


if __name__=="__main__":
    raise SystemExit(main())
