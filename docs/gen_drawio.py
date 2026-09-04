"""Generate a draw.io (.drawio / mxGraph XML) architecture diagram for ClosureCopilot."""
import html

NODES = [
    # id, label, x, y, w, h, fill, font
    ("t", "ClosureCopilot — Multi-Agent Backend Closure Copilot for RTL",
     360, 30, 680, 40, "none", "#FFFFFF", 20),
    # inputs
    ("i1", "STA Timing", 80, 120, 160, 60, "#1F6FEB", "#FFFFFF", 12),
    ("i2", "Synthesis Log", 260, 120, 160, 60, "#1F6FEB", "#FFFFFF", 12),
    ("i3", "RTLA Power", 440, 120, 160, 60, "#1F6FEB", "#FFFFFF", 12),
    ("i4", "Area Report", 620, 120, 160, 60, "#1F6FEB", "#FFFFFF", 12),
    ("i5", "UPF", 800, 120, 160, 60, "#1F6FEB", "#FFFFFF", 12),
    ("i6", "SDC", 980, 120, 160, 60, "#1F6FEB", "#FFFFFF", 12),
    ("i7", "P&amp;R Congestion", 1160, 120, 160, 60, "#1F6FEB", "#FFFFFF", 12),
    # parser
    ("parser", "Ingestion / Parser Agent  —  tool-agnostic report normalizer",
     180, 235, 1040, 55, "#238636", "#FFFFFF", 14),
    # supervisor
    ("sup", "Supervisor / Orchestrator Agent", 520, 335, 360, 62, "#8957E5", "#FFFFFF", 15),
    # side panels
    ("azure", "Azure OpenAI\n(deterministic offline fallback)", 120, 333, 210, 66,
     "#30363D", "#FFFFFF", 11),
    ("rag", "Dual-RAG\nGlobal PPA KB + Design Context Memory", 930, 333, 300, 66,
     "#0E7490", "#FFFFFF", 11),
    # agents
    ("a1", "Power Agent", 80, 450, 190, 55, "#2D333B", "#FFFFFF", 12),
    ("a2", "Timing Agent", 290, 450, 190, 55, "#2D333B", "#FFFFFF", 12),
    ("a3", "Area Agent", 500, 450, 190, 55, "#2D333B", "#FFFFFF", 12),
    ("a4", "Synthesis Agent", 710, 450, 190, 55, "#2D333B", "#FFFFFF", 12),
    ("a5", "UPF Agent", 920, 450, 190, 55, "#2D333B", "#FFFFFF", 12),
    ("a6", "Constraints Agent", 1130, 450, 190, 55, "#2D333B", "#FFFFFF", 12),
    # modules
    ("m1", "PPA Analyzer", 75, 570, 230, 66, "#BB8009", "#FFFFFF", 12),
    ("m2", "Constraint Promotion", 330, 570, 230, 66, "#BB8009", "#FFFFFF", 12),
    ("m3", "UPF Signoff", 585, 570, 230, 66, "#BB8009", "#FFFFFF", 12),
    ("m4", "Regression Detective", 840, 570, 230, 66, "#BB8009", "#FFFFFF", 12),
    ("m5", "Physical-Aware Feedback", 1095, 570, 230, 66, "#BB8009", "#FFFFFF", 12),
    # fix routing
    ("fix", "Fix-Routing / Diagnosis Engine  —  RTL  vs  SDC  vs  UPF  vs  Synth-setup",
     300, 690, 800, 60, "#E5484D", "#FFFFFF", 13),
    # output
    ("out", "Ranked findings  +  corrected snippets (RTL / SDC / UPF)  +  cross-domain PPA trade-offs",
     180, 800, 1040, 60, "#3FB950", "#0D1117", 13),
    # designer
    ("des", "RTL Designer", 580, 910, 240, 55, "#57606A", "#FFFFFF", 13),
]

# edges: (source, target, dashed)
EDGES = [
    ("i1", "parser", 0), ("i2", "parser", 0), ("i3", "parser", 0), ("i4", "parser", 0),
    ("i5", "parser", 0), ("i6", "parser", 0), ("i7", "parser", 0),
    ("parser", "sup", 0),
    ("sup", "a1", 0), ("sup", "a2", 0), ("sup", "a3", 0),
    ("sup", "a4", 0), ("sup", "a5", 0), ("sup", "a6", 0),
    ("a1", "m1", 0), ("a2", "m1", 0), ("a3", "m1", 0), ("a4", "m1", 0),
    ("a6", "m2", 0), ("a5", "m3", 0),
    ("sup", "m4", 0), ("sup", "m5", 0),
    ("m1", "fix", 0), ("m2", "fix", 0), ("m3", "fix", 0), ("m4", "fix", 0), ("m5", "fix", 0),
    ("fix", "out", 0), ("out", "des", 0),
    ("rag", "sup", 1), ("azure", "sup", 1),
]


def node_xml(nid, label, x, y, w, h, fill, font, fs):
    label = html.escape(label).replace("\n", "&#10;")
    if fill == "none":
        style = f"text;html=1;fontSize={fs};fontColor={font};fontStyle=1;align=center;"
    else:
        style = (f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};fontColor={font};"
                 f"strokeColor=#8B949E;fontSize={fs};fontStyle=1;arcSize=18;")
    return (f'<mxCell id="{nid}" value="{label}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')


def edge_xml(eid, s, t, dashed):
    style = ("edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;"
             "strokeColor=#8B949E;strokeWidth=1.4;")
    if dashed:
        style += "dashed=1;strokeColor=#0E7490;endArrow=open;"
    return (f'<mxCell id="{eid}" style="{style}" edge="1" parent="1" '
            f'source="{s}" target="{t}"><mxGeometry relative="1" as="geometry"/></mxCell>')


cells = [node_xml(*n) for n in NODES]
cells += [edge_xml(f"e{i}", s, t, d) for i, (s, t, d) in enumerate(EDGES)]

xml = f'''<mxfile host="app.diagrams.net">
  <diagram name="ClosureCopilot" id="closurecopilot">
    <mxGraphModel dx="1400" dy="1000" grid="0" gridSize="10" guides="1" tooltips="1"
        connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1400"
        pageHeight="1000" background="#0D1117" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {"".join(cells)}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

with open("docs/architecture.drawio", "w", encoding="utf-8") as f:
    f.write(xml)
print("saved docs/architecture.drawio")
