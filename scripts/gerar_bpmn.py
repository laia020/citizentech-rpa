"""Gera BPMN 2.0 editável com DI e renderiza as mesmas posições em SVG/PNG.

O processo é descritivo (isExecutable=false); a execução correspondente é Python.
"""

import math
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

import pymupdf
from reportlab.graphics import renderPDF, renderSVG
from reportlab.graphics.shapes import Circle, Drawing, Group, Line, Polygon, PolyLine, Rect, String
from reportlab.lib.colors import HexColor

ROOT = Path(__file__).resolve().parents[1]
NS = {
    "bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
    "bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
    "dc": "http://www.omg.org/spec/DD/20100524/DC",
    "di": "http://www.omg.org/spec/DD/20100524/DI",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)


def element(parent, kind, **attrs):
    prefix, tag = kind.split(":")
    return ET.SubElement(parent, f"{{{NS[prefix]}}}{tag}", {k: str(v) for k, v in attrs.items()})


def build_source():
    definitions = ET.Element(f"{{{NS['bpmn']}}}definitions", {
        "id": "Definitions_AkonaRPA", "targetNamespace": "https://example.invalid/akona/rpa",
        "exporter": "CitizenTech RPA", "exporterVersion": "0.1.0",
    })
    element(definitions, "bpmn:error", id="Error_API", name="Falha técnica de integração", errorCode="falha_api")
    process = element(definitions, "bpmn:process", id="Process_Lote", name="Akona Energy - lote fictício", isExecutable="false")
    nodes = {}

    def node(parent, kind, identifier, label, **attrs):
        value = element(parent, "bpmn:" + kind, id=identifier, name=label, **attrs)
        nodes[identifier] = (kind, label)
        return value

    node(process, "startEvent", "Start_Lote", "Iniciar lote")
    node(process, "scriptTask", "Task_Ler", "Ler CSV/JSON e validar arquivo")
    node(process, "exclusiveGateway", "Gate_Arquivo", "Arquivo válido?", default="Flow_ArquivoErro")
    sub = node(process, "subProcess", "Sub_Item", "Processar cada registro")
    node(sub, "startEvent", "Start_Item", "Próximo item")
    node(sub, "scriptTask", "Task_Validar", "Normalizar, validar e consultar estado")
    node(sub, "exclusiveGateway", "Gate_Rota", "Qual caminho?", default="Flow_Novo")
    node(sub, "scriptTask", "Task_Pendente", "Registrar pendência ou conflito")
    node(sub, "scriptTask", "Task_Duplicado", "Reutilizar sucesso anterior")
    node(sub, "serviceTask", "Task_API", "Consultar IA e validar resposta")
    boundary = node(sub, "boundaryEvent", "Boundary_API", "Erro técnico", attachedToRef="Task_API", cancelActivity="true")
    element(boundary, "bpmn:errorEventDefinition", id="ErrorDef_API", errorRef="Error_API")
    node(sub, "scriptTask", "Task_Salvar", "Salvar resultado e encaminhar revisão")
    node(sub, "scriptTask", "Task_Falha", "Salvar falha / resultado incerto")
    node(sub, "endEvent", "End_Item", "Item finalizado")
    loop = element(sub, "bpmn:multiInstanceLoopCharacteristics", isSequential="true")
    cardinality = element(loop, "bpmn:loopCardinality")
    cardinality.set(f"{{{NS['xsi']}}}type", "bpmn:tFormalExpression")
    cardinality.text = "len(registros)"
    sub.remove(loop)
    sub.insert(0, loop)  # tActivity exige loopCharacteristics antes dos flowElements.
    node(process, "scriptTask", "Task_Exportar", "Exportar resultados, pendências e resumo")
    node(process, "scriptTask", "Task_ArquivoErro", "Auditar arquivo e exportar resumo de erro")
    node(process, "endEvent", "End_Lote", "Lote finalizado")
    node(process, "endEvent", "End_ArquivoErro", "Arquivo rejeitado")

    def sequence(parent, identifier, source, target, label="", condition=None):
        flow = element(parent, "bpmn:sequenceFlow", id=identifier, sourceRef=source, targetRef=target)
        if label:
            flow.set("name", label)
        if condition:
            expr = element(flow, "bpmn:conditionExpression")
            expr.set(f"{{{NS['xsi']}}}type", "bpmn:tFormalExpression")
            expr.text = condition

    for flow in [
        ("Flow_Inicio", "Start_Lote", "Task_Ler"),
        ("Flow_Lido", "Task_Ler", "Gate_Arquivo"),
        ("Flow_ArquivoOK", "Gate_Arquivo", "Sub_Item", "Sim", "arquivo_valido"),
        ("Flow_ArquivoErro", "Gate_Arquivo", "Task_ArquivoErro", "Não"),
        ("Flow_Exportar", "Sub_Item", "Task_Exportar"),
        ("Flow_Final", "Task_Exportar", "End_Lote"),
        ("Flow_FimErro", "Task_ArquivoErro", "End_ArquivoErro"),
    ]:
        sequence(process, *flow)
    for flow in [
        ("Flow_ItemInicio", "Start_Item", "Task_Validar"),
        ("Flow_ItemValido", "Task_Validar", "Gate_Rota"),
        ("Flow_Pendente", "Gate_Rota", "Task_Pendente", "Pendente / conflito", "rota == pendente"),
        ("Flow_Duplicado", "Gate_Rota", "Task_Duplicado", "Sucesso idêntico", "rota == duplicado"),
        ("Flow_Novo", "Gate_Rota", "Task_API", "Novo / retomada permitida"),
        ("Flow_Resposta", "Task_API", "Task_Salvar", "200 válido"),
        ("Flow_Falha", "Boundary_API", "Task_Falha"),
        ("Flow_PendenteFim", "Task_Pendente", "End_Item"),
        ("Flow_DuplicadoFim", "Task_Duplicado", "End_Item"),
        ("Flow_SalvoFim", "Task_Salvar", "End_Item"),
        ("Flow_FalhaFim", "Task_Falha", "End_Item"),
    ]:
        sequence(sub, *flow)
    collaboration = element(definitions, "bpmn:collaboration", id="Collaboration_IA")
    element(collaboration, "bpmn:participant", id="Participant_RPA", name="RPA Akona Energy", processRef="Process_Lote")
    element(collaboration, "bpmn:participant", id="Participant_IA", name="IA CitizenTech - serviço público (modo real)")
    nodes["Participant_RPA"] = ("participant", "RPA Akona Energy - subprocesso por item")
    nodes["Participant_IA"] = ("participant", "IA CitizenTech - serviço público (modo real)")
    element(collaboration, "bpmn:messageFlow", id="Message_Request", name="Ocorrência fictícia mapeada", sourceRef="Task_API", targetRef="Participant_IA")
    element(collaboration, "bpmn:messageFlow", id="Message_Response", name="Análise ou erro HTTP", sourceRef="Participant_IA", targetRef="Task_API")

    macro_nodes = {
        "Start_Lote": (40, 128, 32, 32), "Task_Ler": (110, 110, 200, 70),
        "Gate_Arquivo": (355, 124, 40, 40), "Sub_Item": (450, 110, 205, 70),
        "Task_Exportar": (740, 110, 200, 70), "End_Lote": (1000, 128, 32, 32),
        "Task_ArquivoErro": (450, 235, 240, 70), "End_ArquivoErro": (775, 254, 32, 32),
    }
    macro_edges = {
        "Flow_Inicio": [(72, 144), (110, 144)], "Flow_Lido": [(310, 144), (355, 144)],
        "Flow_ArquivoOK": [(395, 144), (450, 144)],
        "Flow_ArquivoErro": [(375, 164), (375, 270), (450, 270)],
        "Flow_Exportar": [(655, 144), (740, 144)], "Flow_Final": [(940, 144), (1000, 144)],
        "Flow_FimErro": [(690, 270), (775, 270)],
    }
    item_nodes = {
        "Participant_RPA": (10, 10, 1080, 440), "Participant_IA": (380, 510, 460, 65),
        "Start_Item": (63, 219, 32, 32), "Task_Validar": (120, 200, 160, 70),
        "Gate_Rota": (320, 215, 40, 40), "Task_Pendente": (450, 65, 205, 65),
        "Task_Duplicado": (450, 355, 205, 65), "Task_API": (460, 200, 195, 70),
        "Boundary_API": (628, 254, 26, 26), "Task_Salvar": (755, 200, 180, 70),
        "Task_Falha": (760, 355, 180, 65), "End_Item": (1000, 219, 32, 32),
    }
    item_edges = {
        "Flow_ItemInicio": [(95, 235), (120, 235)], "Flow_ItemValido": [(280, 235), (320, 235)],
        "Flow_Pendente": [(340, 215), (340, 98), (450, 98)],
        "Flow_Duplicado": [(340, 255), (340, 388), (450, 388)],
        "Flow_Novo": [(360, 235), (460, 235)], "Flow_Resposta": [(655, 235), (755, 235)],
        "Flow_Falha": [(641, 280), (725, 280), (725, 388), (760, 388)],
        "Flow_PendenteFim": [(655, 98), (1016, 98), (1016, 219)],
        "Flow_DuplicadoFim": [(655, 388), (680, 388), (680, 435), (1016, 435), (1016, 251)],
        "Flow_SalvoFim": [(935, 235), (1000, 235)],
        "Flow_FalhaFim": [(940, 388), (1016, 388), (1016, 251)],
        "Message_Request": [(570, 270), (570, 310), (695, 310), (695, 510)],
        "Message_Response": [(710, 510), (710, 295), (610, 295), (610, 270)],
    }

    def diagram(identifier, plane_ref, positions, edges):
        diagram_node = element(definitions, "bpmndi:BPMNDiagram", id=identifier)
        plane = element(diagram_node, "bpmndi:BPMNPlane", id=identifier + "_Plane", bpmnElement=plane_ref)
        for key, (x, y, width, height) in positions.items():
            attrs = {"id": key + "_di_" + identifier, "bpmnElement": key}
            if key == "Sub_Item":
                attrs["isExpanded"] = "false"
            shape = element(plane, "bpmndi:BPMNShape", **attrs)
            element(shape, "dc:Bounds", x=x, y=y, width=width, height=height)
        for key, points in edges.items():
            edge = element(plane, "bpmndi:BPMNEdge", id=key + "_di_" + identifier, bpmnElement=key)
            for x, y in points:
                element(edge, "di:waypoint", x=x, y=y)

    diagram("Diagram_Macro", "Process_Lote", macro_nodes, macro_edges)
    diagram("Diagram_Item", "Collaboration_IA", item_nodes, item_edges)
    ET.indent(definitions)
    ET.ElementTree(definitions).write(ROOT / "docs/processo.bpmn", encoding="utf-8", xml_declaration=True)
    return definitions


def render_diagram(source, diagram_id):
    diagram = source.find(f"bpmndi:BPMNDiagram[@id='{diagram_id}']", NS)
    width, height = (1100, 355) if diagram_id == "Diagram_Macro" else (1100, 600)
    drawing = Drawing(width, height)
    drawing.add(Rect(0, 0, width, height, fillColor=HexColor("#ffffff"), strokeColor=None))
    semantics = {node.get("id"): node for node in source.iter() if node.get("id")}
    ink = HexColor("#153238")

    def label(text, x, y, size=14, anchor="middle", color=ink):
        drawing.add(String(x, height-y, text, fontName="Helvetica", fontSize=size,
                           textAnchor=anchor, fillColor=color))

    def multiline(text, x, y, limit, font=14):
        lines = textwrap.wrap(text, width=limit)
        for i, line in enumerate(lines):
            label(line, x, y + (i-(len(lines)-1)/2) * (font+3), font)

    def shape(shape_node):
        semantic = semantics[shape_node.get("bpmnElement")]
        kind = semantic.tag.split("}")[-1]
        x, y, w, h = [float(shape_node.find("dc:Bounds", NS).get(key)) for key in ("x", "y", "width", "height")]
        bottom = height - y - h
        name = semantic.get("name", "")
        if kind == "participant":
            drawing.add(Rect(x, bottom, w, h, fillColor=HexColor("#f7faf9"), strokeColor=HexColor("#9bb3b5"), strokeWidth=1.3))
            if semantic.get("id") == "Participant_IA":
                multiline(name, x+w/2, y+h/2+4, 56, 15)
            else:
                drawing.add(Line(x+30, bottom, x+30, bottom+h, strokeColor=HexColor("#9bb3b5")))
                text = Group(String(0, 0, "RPA - item", fontName="Helvetica", fontSize=13, fillColor=ink, textAnchor="middle"))
                text.translate(x+19, bottom+h/2)
                text.rotate(90)
                drawing.add(text)
        elif kind in {"startEvent", "endEvent", "boundaryEvent"}:
            drawing.add(Circle(x+w/2, bottom+h/2, w/2, fillColor=HexColor("#ffffff"), strokeColor=ink, strokeWidth=3.5 if kind=="endEvent" else 1.7))
            if kind == "boundaryEvent":
                drawing.add(Circle(x+w/2, bottom+h/2, w/2-3, fillColor=None, strokeColor=ink))
                drawing.add(PolyLine([x+9,bottom+19,x+15,bottom+14,x+11,bottom+12,x+17,bottom+7], strokeColor=ink, strokeWidth=2))
            else:
                multiline(name, x+w/2, y+h+23, 20, 12)
        elif kind == "exclusiveGateway":
            drawing.add(Polygon([x+w/2,bottom+h,x+w,bottom+h/2,x+w/2,bottom,x,bottom+h/2], fillColor=HexColor("#fff2d8"), strokeColor=ink, strokeWidth=1.5))
            drawing.add(Line(x+14,bottom+14,x+w-14,bottom+h-14,strokeColor=ink,strokeWidth=2))
            drawing.add(Line(x+14,bottom+h-14,x+w-14,bottom+14,strokeColor=ink,strokeWidth=2))
            multiline(name, x+w/2, y-15, 25, 12)
        else:
            drawing.add(Rect(x,bottom,w,h,rx=9,ry=9,fillColor=HexColor("#edf6f4"),strokeColor=ink,strokeWidth=1.5))
            if kind == "scriptTask":
                drawing.add(Rect(x+9,bottom+h-22,11,14,fillColor=None,strokeColor=ink))
                for offset in [11,15,19]:
                    drawing.add(Line(x+12,bottom+h-offset,x+18,bottom+h-offset,strokeColor=ink,strokeWidth=.7))
            elif kind == "serviceTask":
                cx, cy = x+17, bottom+h-17
                drawing.add(Circle(cx,cy,5,fillColor=None,strokeColor=ink))
                for angle in range(0,360,45):
                    dx,dy=math.cos(math.radians(angle)),math.sin(math.radians(angle))
                    drawing.add(Line(cx+dx*5,cy+dy*5,cx+dx*8,cy+dy*8,strokeColor=ink,strokeWidth=2))
            multiline(name, x+w/2+4, y+h/2+(7 if kind != "subProcess" else 1), int(w/7.5), 14)
            if kind == "subProcess":
                for offset in [8,12,16]:
                    drawing.add(Line(x+w/2-24,bottom+offset,x+w/2-11,bottom+offset,strokeColor=ink,strokeWidth=1.4))
                drawing.add(Rect(x+w/2+4,bottom+6,12,12,fillColor=HexColor("#ffffff"),strokeColor=ink))
                drawing.add(Line(x+w/2+6,bottom+12,x+w/2+14,bottom+12,strokeColor=ink))
                drawing.add(Line(x+w/2+10,bottom+8,x+w/2+10,bottom+16,strokeColor=ink))

    plane=diagram.find("bpmndi:BPMNPlane",NS)
    shapes=plane.findall("bpmndi:BPMNShape",NS)
    for item in shapes:
        if semantics[item.get("bpmnElement")].tag.endswith("participant"):
            shape(item)
    for edge in plane.findall("bpmndi:BPMNEdge",NS):
        semantic=semantics[edge.get("bpmnElement")]
        message=semantic.tag.endswith("messageFlow")
        points=[(float(p.get("x")),height-float(p.get("y"))) for p in edge.findall("di:waypoint",NS)]
        line=PolyLine([coord for point in points for coord in point],strokeColor=HexColor("#327a83") if message else ink,strokeWidth=1.3)
        if message:
            line.strokeDashArray=[5,4]
        drawing.add(line)
        (x0,y0),(x1,y1)=points[-2:]
        angle=math.atan2(y1-y0,x1-x0)
        p1=(x1-8*math.cos(angle-.45),y1-8*math.sin(angle-.45))
        p2=(x1-8*math.cos(angle+.45),y1-8*math.sin(angle+.45))
        drawing.add(Polygon([x1,y1,*p1,*p2],fillColor=HexColor("#ffffff") if message else ink,strokeColor=HexColor("#327a83") if message else ink))
        if message:
            drawing.add(Circle(*points[0],3,fillColor=HexColor("#ffffff"),strokeColor=HexColor("#327a83")))
        # Labels posicionados em DI-independent layout; sem cruzar texto das tarefas.
    labels = {
        "Diagram_Macro": [(420,132,"Sim"),(399,214,"Não")],
        "Diagram_Item": [(395,85,"Pendência"),(400,375,"Duplicata"),(409,273,"Novo / retomar"),(706,219,"200 válido"),(850,70,"Sem nova consulta"),(661,476,"Envio"),(746,476,"Resposta")],
    }
    for x,y,text in labels[diagram_id]:
        label(text,x,y,11)
    for item in shapes:
        if not semantics[item.get("bpmnElement")].tag.endswith("participant"):
            shape(item)
    return drawing


def main():
    source = build_source()
    for identifier, stem in [("Diagram_Macro","bpmn-macro"),("Diagram_Item","bpmn-item")]:
        drawing=render_diagram(source,identifier)
        renderSVG.drawToFile(drawing,str(ROOT/"assets"/(stem+".svg")))
        pdf=renderPDF.drawToString(drawing)
        with pymupdf.open(stream=pdf,filetype="pdf") as doc:
            doc[0].get_pixmap(matrix=pymupdf.Matrix(1.7,1.7)).save(ROOT/"assets"/(stem+".png"))
    print("BPMN editável e duas vistas gerados.")


if __name__ == "__main__":
    main()
