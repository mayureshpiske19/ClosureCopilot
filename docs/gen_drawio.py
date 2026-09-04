"""Generate a clean white-theme draw.io architecture diagram for ClosureCopilot."""
import html

# id, label, x, y, w, h, fill, stroke
NODES = [
    ("t", "ClosureCopilot  —  Multi-Agent Backend Closure Copilot for RTL",
     380, 30, 740, 40, "none", "none"),
    # inputs (fill light blue)
    ("i1", "STA Timing", 101, 110, 170, 60, "#DAE8FC", "#6C8EBF"),
    ("i2", "Synthesis Log", 289, 110, 170, 60, "#DAE8FC", "#6C8EBF"),
    ("i3", "RTLA Power", 477, 110, 170, 60, "#DAE8FC", "#6C8EBF"),
    ("i4", "Area Report", 665, 110, 170, 60, "#DAE8FC", "#6C8EBF"),
    ("i5", "UPF", 853, 110, 170, 60, "#DAE8FC", "#6C8EBF"),
    ("i6", "SDC", 1041, 110, 170, 60, "#DAE8FC", "#6C8EBF"),
    ("i7", "P&amp;R Congestion", 1229, 110, 170, 60, "#DAE8FC", "#6C8EBF"),
    # parser
    ("parser", "Ingestion / Parser Agent  —  tool-agnostic report normalizer",
     230, 220, 1040, 55, "#D5E8D4", "#82B366"),
    # supervisor + side panels
    ("sup", "Supervisor / Orchestrator", 570, 325, 360, 62, "#E1D5E7", "#9673A6"),
    ("azure", "Azure OpenAI\n(deterministic offline fallback)", 150, 328, 210, 56,
     "#F5F5F5", "#999999"),
    ("rag", "Dual-RAG\nGlobal PPA KB + Design Context Memory", 1140, 328, 210, 56,
     "#B0E3E6", "#0E8088"),
    # agents
    ("a1", "Power Agent", 105, 445, 200, 55, "#F5F5F5", "#666666"),
    ("a2", "Timing Agent", 323, 445, 200, 55, "#F5F5F5", "#666666"),
    ("a3", "Area Agent", 541, 445, 200, 55, "#F5F5F5", "#666666"),
    ("a4", "Synthesis Agent", 759, 445, 200, 55, "#F5F5F5", "#666666"),
    ("a5", "UPF Agent", 977, 445, 200, 55, "#F5F5F5", "#666666"),
    ("a6", "Constraints Agent", 1195, 445, 200, 55, "#F5F5F5", "#666666"),
    # fix engine
    ("fix", "Fix-Routing / Diagnosis Engine  —  RTL | SDC | UPF | Synth-setup",
     350, 560, 800, 58, "#F8CECC", "#B85450"),
    # modules
    ("m1", "PPA Analyzer", 135, 670, 230, 66, "#FFE6CC", "#D79B00"),
    ("m2", "Constraint Promotion", 385, 670, 230, 66, "#FFE6CC", "#D79B00"),
    ("m3", "UPF Signoff", 635, 670, 230, 66, "#FFE6CC", "#D79B00"),
    ("m4", "Regression Detective", 885, 670, 230, 66, "#FFE6CC", "#D79B00"),
    ("m5", "Physical-Aware Feedback", 1135, 670, 230, 66, "#FFE6CC", "#D79B00"),
    # output + designer
    ("out", "Ranked findings  +  corrected snippets (RTL / SDC / UPF)  +  PPA trade-offs",
     230, 785, 1040, 58, "#D5E8D4", "#82B366"),
    ("des", "RTL Designer", 620, 895, 260, 55, "#FFF2CC", "#D6B656"),
]

# edges: (source, target, exitX, entryX, dashed)   exitY=1, entryY=0 for vertical flow
EDGES = []
for i in range(1, 8):                       # inputs -> parser (spread entry)
    EDGES.append((f"i{i}", "parser", 0.5, (i - 0.5) / 7, 0))
EDGES.append(("parser", "sup", 0.5, 0.5, 0))
for j in range(1, 7):                        # supervisor -> agents (spread exit)
    EDGES.append(("sup", f"a{j}", (j - 0.5) / 6, 0.5, 0))
for j in range(1, 7):                        # agents -> fix (spread entry)
    EDGES.append((f"a{j}", "fix", 0.5, (j - 0.5) / 6, 0))
for k in range(1, 6):                        # fix -> modules (spread exit)
    EDGES.append(("fix", f"m{k}", (k - 0.5) / 5, 0.5, 0))
for k in range(1, 6):                        # modules -> output (spread entry)
    EDGES.append((f"m{k}", "out", 0.5, (k - 0.5) / 5, 0))
EDGES.append(("out", "des", 0.5, 0.5, 0))


def node_xml(nid, label, x, y, w, h, fill, stroke):
    label = html.escape(label).replace("\n", "&#10;")
    if fill == "none":
        style = "text;html=1;fontSize=20;fontColor=#1A1A1A;fontStyle=1;align=center;"
    else:
        style = (f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
                 f"fontColor=#1A1A1A;fontSize=13;fontStyle=1;arcSize=14;")
    return (f'<mxCell id="{nid}" value="{label}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')


def edge_xml(eid, s, t, ex, en, dashed):
    style = ("edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;jettySize=auto;"
             f"exitX={ex:.3f};exitY=1;exitDx=0;exitDy=0;entryX={en:.3f};entryY=0;"
             "entryDx=0;entryDy=0;endArrow=block;strokeColor=#8A94A0;strokeWidth=1.5;")
    return (f'<mxCell id="{eid}" style="{style}" edge="1" parent="1" '
            f'source="{s}" target="{t}"><mxGeometry relative="1" as="geometry"/></mxCell>')


def side_edge_xml(eid, s, t, exx, exy, enx, eny):
    style = ("edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;dashed=1;"
             f"exitX={exx};exitY={exy};entryX={enx};entryY={eny};"
             "endArrow=open;strokeColor=#0E8088;strokeWidth=1.4;")
    return (f'<mxCell id="{eid}" style="{style}" edge="1" parent="1" '
            f'source="{s}" target="{t}"><mxGeometry relative="1" as="geometry"/></mxCell>')


cells = [node_xml(*n) for n in NODES]
cells += [edge_xml(f"e{i}", s, t, ex, en, d) for i, (s, t, ex, en, d) in enumerate(EDGES)]
# dashed side links
cells.append(side_edge_xml("eaz", "azure", "sup", 1, 0.5, 0, 0.5))
cells.append(side_edge_xml("erag", "rag", "sup", 0, 0.5, 1, 0.5))

xml = f'''<mxfile host="app.diagrams.net">
  <diagram name="ClosureCopilot" id="closurecopilot">
    <mxGraphModel dx="1500" dy="1000" grid="0" gridSize="10" guides="1" tooltips="1"
        connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1500"
        pageHeight="1000" background="#FFFFFF" math="0" shadow="0">
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
