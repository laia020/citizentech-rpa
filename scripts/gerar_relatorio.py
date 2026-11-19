"""Relatório técnico e painel visual, gerados somente de evidências preservadas."""

import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import pymupdf
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Paragraph, Preformatted, Spacer, Table, TableStyle

from gerar_bpmn import render_diagram
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
INK = colors.HexColor("#153238")
TEAL = colors.HexColor("#167b80")
MUTED = colors.HexColor("#52686b")
LIGHT = colors.HexColor("#edf6f4")
AMBER = colors.HexColor("#fff2d8")
BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=10.2, leading=14.1,
                      textColor=INK, spaceAfter=9, alignment=TA_LEFT)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=9.1, leading=12, spaceAfter=3)
HEADING = ParagraphStyle("heading", parent=BODY, fontName="Helvetica-Bold", fontSize=13,
                         leading=17, spaceBefore=9, spaceAfter=6)
CODE = ParagraphStyle("code", fontName="Courier", fontSize=8.3, leading=11.4,
                      backColor=LIGHT, borderPadding=8, textColor=INK, spaceAfter=12)
CAPTION = ParagraphStyle("caption", parent=SMALL, textColor=MUTED, spaceAfter=8)


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def p(text, style=BODY):
    return Paragraph(text, style)


def h(text):
    return p(text, HEADING)


def link(label, url):
    return f'<link href="{escape(url, {chr(34): "&quot;"})}" color="#167b80"><u>{escape(label)}</u></link>'


def table(rows, widths, header=True, font_style=SMALL):
    rendered = [[p(str(cell), font_style) for cell in row] for row in rows]
    value = Table(rendered, colWidths=widths, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), .4, colors.HexColor("#d3e0df")),
    ]
    if header:
        commands.append(("BACKGROUND", (0, 0), (-1, 0), LIGHT))
    value.setStyle(TableStyle(commands))
    return value


def scaled(drawing, width):
    factor = width / drawing.width
    drawing.scale(factor, factor)
    drawing.width *= factor
    drawing.height *= factor
    return drawing


def evidence_panel():
    first = read_json("docs/evidencias/simulado/resumo.json")
    unavailable = read_json("docs/evidencias/real-indisponibilidade/resumo.json")
    real = read_json("docs/evidencias/nuvem-real/resumo.json")
    repeat = read_json("docs/evidencias/simulado-repeticao/resumo.json")
    tests = read_json("docs/evidencias/testes.json")
    drawing = Drawing(1000, 430)
    drawing.add(Rect(0,0,1000,430,fillColor=colors.white,strokeColor=colors.HexColor("#ccdedd")))
    drawing.add(Rect(0,372,1000,58,fillColor=INK,strokeColor=None))

    def text(x,y,value,size=17,color=INK,bold=False):
        drawing.add(String(x,y,value,fontName="Helvetica-Bold" if bold else "Helvetica",fontSize=size,fillColor=color))

    text(24,392,"REGISTRO VISUAL DE EXECUÇÕES - 18/11/2026",19,colors.white,True)
    text(24,344,"Painel gerado dos JSON e logs preservados. Não é screenshot do Akona.",15,MUTED)
    labels=["Cenário", "Entradas", "Processados", "Duplicados", "Pendências", "Falhas"]
    xs=[24,385,490,625,755,890]
    for x,label in zip(xs,labels):
        text(x,300,label,15,INK,True)
    for y,name,summary in [(255,"SIMULADOR - sem IA",first),(210,"REPETIÇÃO - sem nova consulta",repeat),(165,"HISTÓRICO - HTTP 503",unavailable),(120,"IA REAL - HTTP 200",real)]:
        text(24,y,name,16,TEAL if "HTTP" not in name else INK,True)
        for x,key in zip(xs[1:],["entradas","processados","duplicados","pendencias","falhas"]):
            text(x+10,y,str(summary["contagens"][key]),20)
    text(24,70,f"Suíte histórica: {tests['testes']} testes aprovados; rede da IA simulada.",17,TEAL,True)
    text(24,35,"Integração real: 2 chamadas HTTP 200. Não houve criação de chamado ou reparo.",16,MUTED)
    return drawing


class Report:
    def __init__(self, path, revision_date):
        self.canvas = canvas.Canvas(str(path), pagesize=A4, pageCompression=1)
        self.canvas.setTitle("Akona Energy - Relatório técnico RPA CitizenTech")
        self.canvas.setAuthor("Equipe CitizenTech - FIAP 4ES")
        self.canvas.setSubject("POC de lote fictício, BPMN, auditoria e estado real da entrega")
        self.number = 0
        self.revision_date = revision_date

    def page(self, title, subtitle, blocks, *, wide=False):
        self.number += 1
        width,height=landscape(A4) if wide else A4
        c=self.canvas
        c.setPageSize((width,height))
        c.setFillColor(TEAL)
        c.rect(0,height-10,width,10,fill=1,stroke=0)
        c.setFillColor(MUTED)
        c.setFont("Helvetica-Bold",8.8)
        c.drawString(46,height-37,"AKONA ENERGY  /  CITIZENTECH FIAP 4ES  /  RPA")
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold",22)
        c.drawString(46,height-67,title)
        c.setFillColor(MUTED)
        c.setFont("Helvetica",9.2)
        c.drawString(46,height-87,subtitle)
        frame=Frame(46,50,width-92,height-159,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
        remaining=list(blocks)
        frame.addFromList(remaining,c)
        if remaining:
            raise ValueError(f"Conteúdo excede a página {self.number}: {title}")
        c.setStrokeColor(colors.HexColor("#ccdedd"))
        c.line(46,38,width-46,38)
        c.setFont("Helvetica",8)
        c.setFillColor(MUTED)
        c.drawString(46,24,f"{self.revision_date}  |  Dados fictícios  |  Relatório técnico RPA")
        c.drawRightString(width-46,24,str(self.number))
        c.showPage()

    def save(self):
        self.canvas.save()


def main():
    info=read_json("docs/entrega.json")
    tests=read_json("docs/evidencias/testes.json")
    source=ET.parse(ROOT/"docs/processo.bpmn").getroot()
    destination=ROOT/"output/pdf/relatorio-tecnico-rpa.pdf"
    destination.parent.mkdir(parents=True,exist_ok=True)
    report=Report(destination,"/".join(info["data_revisao"].split("-")[::-1]))
    w=A4[0]-92
    mw=landscape(A4)[0]-92
    ia="https://laia020-citizentech-iluminacao-ia.hf.space"
    mvp="https://ca-akona-energy-prod.salmoncoast-770d275b.eastus2.azurecontainerapps.io/"
    repo_ia="https://github.com/laia020/citizentech-iluminacao-ia"
    repo_rpa=info.get("repositorio_rpa_url")
    workflow=info.get("workflow_publico_url")
    real_workflow=info["integracao_evidencia_url"]
    repo_label=link("GitHub do RPA",repo_rpa) if repo_rpa else "GitHub do RPA: pendente"
    ficha=[
        ["Campo", "Ficha Técnica comum - versão do componente"],
        ["Produto", "Akona Energy - automação de ocorrências de iluminação pública."],
        ["Cidadão / território", "Pessoas que relatam problemas e equipes de triagem. Osasco/SP demonstrativo, a alinhar com o grupo. Sem operação municipal comprovada."],
        ["Problema", "Recepção individual de relatos exige validar campos, conferir duplicidades e organizar encaminhamentos manualmente."],
        ["Proposta de valor", "Organizar lotes e pendências para triagem humana rastreável. Benefício esperado ao cidadão; não há ganho de tempo ou custo medido em campo."],
        ["Arquitetura", "CSV/JSON → Python RPA → validação + SQLite → cliente IA → JSON e auditoria → revisão humana. Workflow hospedado com simulação e integração real comprovadas; Akona não conectado."],
        ["Fontes de dados", "Lotes fictícios autorais, escritos manualmente para testar decisões e falhas; geração em docs/dados-demonstracao.md. Contrato OpenAPI público. Sem dados municipais ou sensores reais."],
        ["Modelos de IA", "Serviço existente: Qwen2.5-1.5B-Instruct + RAG + LoRA r1, PyTorch FP32, conforme projeto da IA. RPA não baixa pesos nem treina. Simulador não executa modelo."],
        ["MVP / repositórios", link("MVP informado",mvp)+" · "+link("IA pública",ia+"/demo")+" · "+link("Repositório da IA",repo_ia)+".<br/>"+repo_label+". Repositório do Akona: não fornecido."],
        ["Indicadores", "Medidos: contagens por execução e testes. Propostos: completude, tempo de triagem e revisão humana. Sem impacto municipal/energético comprovado."],
        ["ODS", "ODS 11: relatos de infraestrutura urbana; ODS 7: apoio proposto à gestão da iluminação. Alinhamento sem impacto de campo demonstrado."],
    ]
    team=[["Nome completo", "RM"]]+[[person["nome"],person["rm"]] for person in info["equipe"]]
    report.page("Ficha Técnica e equipe","Relatório técnico - Do Processo Manual à Automação Inteligente",[
        table(ficha,[117,w-117]),Spacer(1,10),table(team,[w-75,75]),
        Spacer(1,7),p("Disciplina: Robotic Process Automation. Professores: Bruno Diniz e Cibele Ribeiro.",CAPTION),
    ])
    report.page("Processo e implementação","Objetivo, decisões de negócio e limites da POC",[
        h("Objetivo e processo manual"),
        p("Automatizar a recepção e a conferência de ocorrências fictícias em lote. No processo manual proposto, um operador lê cada relato, confere dados e repetições e separa o que precisa de complementação. Essa descrição não é um levantamento municipal nem uma medição de atendimento real."),
        h("Fluxo implementado"),
        p("Uma ação do operador inicia o lote. A aplicação abre auditoria, lê CSV/JSON, valida a coleção e adquire o lock do SQLite. Percorre os itens sequencialmente, normaliza texto e defaults, valida o contrato e consulta o estado. Registros aptos são enviados ao cliente real da IA ou ao simulador identificado. Exporta resultados, pendências e resumo em diretório novo por UUID."),
        table([
            ["Condição", "Comportamento"],
            ["Novo e válido", "Grava marcador antes do POST, valida resposta e correlação, persiste e encaminha para revisão humana."],
            ["Incompleto / incoerente", "Pendência com motivo sanitizado; não inventa dados nem envia o corpo à IA."],
            ["Sucesso idêntico", "Reutiliza análise anterior sem nova chamada; mantém referência à execução original."],
            ["Mesmo ID, conteúdo diferente", "Conflito; não sobrescreve silenciosamente o registro original."],
            ["Recusa válida da IA", "Processado, com status_ia separado: complementar informações ou revisar escopo."],
            ["Falha técnica", "Registra o erro e continua os demais itens. Retomada não repete um ID falho duas vezes no mesmo lote."],
        ],[145,w-145]),
        h("Tecnologias e justificativa"),
        p("Python 3.12, uv e .venv exclusiva; CLI evita servidor permanente. jsonschema valida o contrato público congelado. SQLite mantém estado entre reinícios, se o arquivo for preservado. urllib/HTTPS faz a consulta sequencial; unittest usa falhas simuladas. ReportLab e PyMuPDF são dependências opcionais de documentação. Nenhuma biblioteca de IA foi instalada."),
        p("Escopo da entrega: RPA integrado à IA existente do mesmo produto. Esta disciplina demonstra o processo automatizado; treinamento e avaliação do modelo pertencem à entrega de IA. Relatório, BPMN e vídeo de RPA são específicos. Importação no backend do Akona fica como evolução futura.",CAPTION),
    ])
    report.page("BPMN 2.0 - processo do lote","Fonte editável: docs/processo.bpmn | processo descritivo, execução em Python",[
        scaled(render_diagram(source,"Diagram_Macro"),mw),
        Spacer(1,12),p("O subprocesso tem marcador de múltiplas instâncias sequenciais: cada registro da coleção é percorrido uma vez pelo fluxo. O sinal de expansão indica o detalhamento da página seguinte. Arquivo inválido produz auditoria e resumo de erro, sem consulta à IA."),
        p("Notação: círculo fino = início; círculo espesso = fim; losango com X = gateway exclusivo; retângulo arredondado = tarefa/subprocesso; três traços horizontais = múltiplas instâncias sequenciais. XML validado contra o XSD BPMN 2.0 oficial da OMG.",CAPTION),
    ],wide=True)
    report.page("BPMN 2.0 - decisão por item","Detalhamento do subprocesso; mensagens à IA existem somente no modo real",[
        scaled(render_diagram(source,"Diagram_Item"),mw-12),
        p("Evento de erro de borda captura falha técnica da tarefa de serviço. Linhas tracejadas representam mensagens entre participantes. Timeout e tentativas limitadas são tratados dentro dessa tarefa; o modo simulado não envia mensagens ao serviço público.",CAPTION),
    ],wide=True)
    report.page("Integração real e histórico","Duas respostas HTTP 200 validadas; falhas anteriores preservadas",[
        p("O RPA valida e organiza o lote; o serviço de IA existente analisa cada ocorrência apta. O payload normalizado segue para "+link("POST /v1/analisar",ia+"/docs")+". Os metadados tipo, bairro e ponto ficam no RPA. Uma resposta 200 precisa cumprir AnalysisResponse e corresponder ao ID enviado; a análise, a recusa e o request_id são preservados."),
        scaled(evidence_panel(),w),Spacer(1,10),
        table([
            ["Ocorrência / request_id", "Resposta de negócio preservada"],
            ["RPA-LIVE-20261118-001<br/>333fecbe-114f-4603-824e-43b7fa8dd2d6", "analise_preliminar; revisão humana. A repetição reutilizou a mesma resposta, sem outra chamada."],
            ["RPA-LIVE-20261118-002<br/>5e25fa23-6c84-423e-87f8-9a1fb4e849d3", "informacao_insuficiente; complementar informações. É sucesso operacional, sem conversão ADC/lux inventada."],
        ],[240,w-240]),
        h("Execução e correlação"),
        p(link("Run real 44327757282",real_workflow)+", 18/11 às 11:45 (Brasília), restaurou o estado 44296159102. Execução dd5f0bb6ea1f4cd6bd39db4fa78b0385. Quatro entradas: duas processadas, uma duplicada, uma pendência e zero falhas. Duas chamadas HTTP 200, uma tentativa por ID. Dados fictícios, simulada: true; cliente real. Evidências em docs/evidencias/nuvem-real/."),
        p("Histórico preservado: seis chamadas 503 em duas execuções às 08:14 e 08:24 (Brasília). A causa não foi determinada; /ready pronto: true não garantia inferência. Com o lote novo são oito chamadas reais documentadas, duas bem-sucedidas. Não houve teste de carga.",CAPTION),
        p("Item 6, página 48 do enunciado: outro componente deve consumir o resultado, inclusive via API. Nossa evidência é a ocorrência validada e normalizada pelo RPA, consumida pela IA. O arquivo final não foi importado pelo backend do Akona; nenhum chamado foi criado ou serviço de IA alterado.",CAPTION),
    ])
    report.page("Testes, resiliência e auditoria","Cenários automatizados separados da execução remota",[
        p(f"<b>{tests['testes']} testes aprovados no registro histórico</b>, com {tests['falhas']} falhas e {tests['erros']} erros, Python {tests['python']}. A suíte usa rede de IA simulada. A conferência documental local não reexecutou a suíte; a CI do GitHub roda na publicação. A primeira execução antes do código e a regressão estão em docs/evidencias/. O lote real HTTP 200 é evidência separada de integração."),
        table([
            ["Cenário executado", "Evidência / resultado"],
            ["Lote e contrato", "Dois itens válidos e mapeamento sem metadados extras; correlação da resposta verificada."],
            ["Decisão de negócio", "Incompleto não chama IA; informação insuficiente é sucesso operacional com revisão."],
            ["Duplicata / conflito / reinício", "Resposta reutilizada sem chamada; divergência fica pendente; mesmo SQLite preserva estado."],
            ["Arquivo ausente / inválido / CSV", "Erro explícito, zero chamadas; CSV booleano interpretado; rejeita NaN e chaves repetidas."],
            ["API 429/503 e Retry-After", "Tentativas limitadas; espera respeitada ou chamada adiada; sem repetir duplicata falha no mesmo lote."],
            ["413/422/502 e JSON inválido", "Sem reparo de JSON nem repetição de geração rejeitada."],
            ["Timeout / envio interrompido / lock", "Resultado incerto exige revisão; concorrência com mesma base é recusada."],
            ["Estado de nuvem", "Restauração inválida aborta; novo estado exige confirmação. Entrada do workflow testada localmente."],
        ],[160,w-160]),
        h("Auditoria e contagens"),
        p("auditoria.jsonl registra data_hora UTC com fuso, execucao_id, linha, item_ref hash, etapa, resultado, tentativa e código sanitizado. Não contém relato, corpo arbitrário de erro, token ou traceback. Resultados válidos preservam o conteúdo fictício e a resposta. O SHA-256 do arquivo de entrada consta no resumo."),
        Preformatted('entradas = processados + duplicados + pendencias + falhas\nTentativas HTTP não contam como novos itens.\nExit 0: lote concluído (pode haver pendências).\nExit 1: falha em item. Exit 2: arquivo/infraestrutura.',CODE),
        p("Em falha de infraestrutura, o resumo sinaliza interrupção e as contagens podem abranger somente itens finalizados. Resumos, respostas e logs reais estão em docs/evidencias/ e logs/. O painel anterior foi gerado desses arquivos; não é captura de tela do MVP.",CAPTION),
    ])
    report.page("Execução, estado e segurança","Processamento em Mac/Linux ou runner Ubuntu; documentação também no Windows",[
        h("Reprodução local em Mac/Linux"),
        Preformatted('cd ~/Projects/citizentech-rpa\n# Somente se .venv ainda não existir:\nuv venv --python 3.12 --prompt "venv-citizentech-rpa"\nuv sync --locked --no-default-groups\nuv run --no-sync python -m unittest discover -s tests -v\nuv run --no-sync citizentech-rpa examples/lote-demo.json',CODE),
        p("O RPA usa fcntl e não tem suporte nativo a Windows. Neste computador, apenas os scripts de documentação foram executados. O lote real já tem sucessos: preservar o estado, sem repetir inferência para filmar. Falhas 429/503 só são retomadas explicitamente, após revisão."),
        h("Persistência e recuperação"),
        p("Estado em state/ocorrencias.sqlite3, fora do Git, chave (modo, ID), fingerprint do conteúdo canônico completo. Simulação e real são separados. O arquivo deve ser preservado entre reinicializações. Antes do POST, grava em_envio; interrupção/timeout não autoriza replay, pois a API não fornece consulta por chave idempotente. Resultados incertos ficam para revisão humana."),
        h("Workflow hospedado e estado mais recente"),
        p("GitHub Actions com workflow_dispatch e ubuntu-latest. "+link("Primeiro lote simulado",workflow)+": 1 processada, 1 duplicada, 2 pendências. A repetição restaurou o estado: 0 novos processamentos, 2 duplicatas. O "+link("lote real posterior",real_workflow)+" teve 2 processadas, 1 duplicada, 1 pendência e 0 falhas. Estado de referência: <b>44327757282</b>; conferir runs posteriores antes de restaurar rpa-state. Não iniciar base nova nem voltar a ancestral. Restauração ausente/inválida aborta; resultados são arquivados inclusive em erro de API."),
        p("Artifacts configurados por 14 dias, sujeitos à política da conta. São armazenamento temporário, não banco permanente. Cancelamento ou falha antes do upload exige reconciliação; não continuar a partir de estado antigo cegamente. A base usada no Mac não é transferida automaticamente. Baixar artefatos exige login e leitura no GitHub."),
        h("Segurança e LGPD"),
        p("Whitelist, limites de tamanho, HTTPS e sem redirecionamentos; credenciais fora do código. simulada: true é declaração, não detector de dados pessoais. Revisar os lotes antes do envio. Auditoria minimizada; arquivos 0600 e diretórios de execução 0700 no Mac/Linux, sem criptografia do SQLite. Retenção e acesso para uso real exigem definição do responsável. Não há diagnóstico elétrico, conversão ADC/lux, reparo ou mensagem automática a terceiros."),
        p("Documentação oficial consultada: "+link("uv em Actions","https://docs.astral.sh/uv/guides/integration/github/")+" e "+link("download e retenção de artefatos","https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts")+". Nenhum serviço pago foi contratado.",CAPTION),
    ])
    report.page("Requisitos e entrega","Matriz obrigatória, pendências e links verificáveis",[
        table([
            ["Etapa obrigatória", "Evidência", "Estado"],
            ["1. Mapeamento", "PDD, BPMN editável e vistas neste PDF.", "Concluído"],
            ["2. Desenvolvimento", "Código versionado e público; CI aprovada em Ubuntu.", "Concluído"],
            ["3. Decisão e lote", "Lote de quatro itens, regras e laço sequencial.", "Concluído"],
            ["4. Exceções", "Falhas simuladas e HTTP 503 real preservado.", "Concluído"],
            ["5. Logs e auditoria", "UTC, itens, tentativas e códigos sanitizados.", "Concluído"],
            ["6. Integração", "Duas respostas HTTP 200 validadas; consumo pela IA. Akona sem importação.", "Via IA"],
            ["7. Testes", f"{tests['testes']} aprovados: sucesso, decisão e falha.", "Concluído"],
            ["8. Documentação/publicação", "Código e evidências públicos; link do vídeo incluído no relatório." if info["video_url"] else "README, PDD e código públicos; falta vídeo/link final.", "Ver notas"],
        ],[147,w-224,77]),
        h("Vídeo e situação da entrega"),
        p("O autor disponibilizou o vídeo demonstrativo no Google Drive; o link está na tabela abaixo. O relatório e o README incluem o link informado pelo autor. Código e evidências reais continuam públicos no GitHub. A Ficha Técnica comum permanece PENDENTE de confirmação com o grupo; o envio ao Teams é realizado por um integrante." if info["video_url"] else "Código e evidências reais publicados no GitHub. Falta confirmar a Ficha Técnica comum, disponibilizar o vídeo e inserir seu link no relatório."),
        p("A demonstração apresenta a execução registrada de 18/11/2026 e suas evidências autênticas. A integração RPA-IA está comprovada no run 44327757282. A página de apresentação permite consultar o fluxo, os resultados e a auditoria sem executar outro lote. A importação no backend do Akona não foi implementada."),
        table([
            ["Link de entrega", "Estado"],
            ["GitHub do RPA", link("Abrir repositório",info["repositorio_rpa_url"]) if info["repositorio_rpa_url"] else "PENDENTE - não publicado/autorizado nesta etapa."],
            ["Integração real", link("Run 44327757282 - duas respostas HTTP 200",real_workflow)],
            ["Vídeo demonstrativo", link("Abrir vídeo",info["video_url"]) if info["video_url"] else "PENDENTE - vídeo não gravado e URL não fornecida."],
            ["Página de RPA", link("Abrir apresentação e evidências",ia+"/rpa")],
            ["MVP informado", link("Abrir Akona Energy",mvp)+". Não recebeu registros deste RPA."],
            ["IA / contrato", link("Demonstração",ia+"/demo")+" · "+link("API/OpenAPI",ia+"/openapi.json")+" · "+link("GitHub da IA",repo_ia)],
        ],[147,w-147]),
        h("Prazo e avaliação"),
        p("19/11/2026 às 23h55, tarefa de RPA no Teams; um integrante envia pela equipe. Rubrica: integração 1, documentação 2, desenvolvimento 5, vídeo 2 pontos. Manter aplicações, repositórios e vídeo públicos durante a correção, até uma semana após o encerramento. Fonte: PDF FIAP CitizenTech 4ES, páginas 24 e 45–50."),
        p("Original conferido: páginas 18-24 e 45-50. A página 48 aceita consumo via API e não determina um backend ou arquivo final específico. Justificativa e limites em docs/auditoria-entrega.md. A aceitação depende da avaliação. A confirmação da ficha comum e o envio ao Teams permanecem sob responsabilidade da equipe.",CAPTION),
    ])
    report.save()
    panel=evidence_panel()
    with pymupdf.open(stream=renderPDF.drawToString(panel),filetype="pdf") as doc:
        doc[0].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(ROOT/"assets/execucao-evidencia.png")
    print(f"Relatório gerado: {destination.relative_to(ROOT)} ({report.number} páginas)")


if __name__ == "__main__":
    main()
