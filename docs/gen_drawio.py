"""Generate an accurate white-theme draw.io architecture diagram for ClosureCopilot."""
import html

# id, label, x, y, w, h, fill, stroke
NODES = [
    ("t", "ClosureCopilot — Architecture &amp; Data Flow", 380, 24, 740, 40, "none", "none"),
    # inputs
    ("i1","STA Timing",101,100,168,58,"#DAE8FC","#6C8EBF"),
    ("i2","Synthesis log",287,100,168,58,"#DAE8FC","#6C8EBF"),
    ("i3","RTLA power",473,100,168,58,"#DAE8FC","#6C8EBF"),
    ("i4","Area",659,100,168,58,"#DAE8FC","#6C8EBF"),
    ("i5","UPF",845,100,168,58,"#DAE8FC","#6C8EBF"),
    ("i6","SDC",1031,100,168,58,"#DAE8FC","#6C8EBF"),
    ("i7","P&amp;R congestion",1217,100,168,58,"#DAE8FC","#6C8EBF"),
    # parser
    ("parser","Ingestion / Parser Agent&#10;ingestion/parsers.py · detect_type() → Finding objects",
     230,205,1040,58,"#D5E8D4","#82B366"),
    # supervisor + side
    ("sup","Supervisor / Orchestrator&#10;orchestrator.py",560,310,360,64,"#E1D5E7","#9673A6"),
    ("az","Azure OpenAI&#10;llm.py · optional",120,312,210,60,"#F5F5F5","#999999"),
    ("kb","Grounded knowledge&#10;rag/ · design + global",1150,312,210,60,"#B0E3E6","#0E8088"),
    # agents
    ("a1","Power",130,430,190,54,"#EEF0F4","#666666"),
    ("a2","Timing",345,430,190,54,"#EEF0F4","#666666"),
    ("a3","Area",560,430,190,54,"#EEF0F4","#666666"),
    ("a4","Synthesis",775,430,190,54,"#EEF0F4","#666666"),
    ("a5","UPF",990,430,190,54,"#EEF0F4","#666666"),
    ("a6","Constraints",1205,430,190,54,"#EEF0F4","#666666"),
    # fix router
    ("fix","Fix-Routing / Diagnosis Engine&#10;fix_router.py · RTL | SDC | UPF | Synth  +  snippet + trade-off",
     360,540,800,60,"#F8CECC","#B85450"),
    # output
    ("out","Ranked findings (AnalysisResult)&#10;Streamlit app · HTML dashboard · CLI",
     440,650,640,58,"#D5E8D4","#82B366"),
    # module lane
    ("m1","Constraint Promotion&#10;promotion.py",180,780,250,60,"#FFE6CC","#D79B00"),
    ("m2","UPF Signoff&#10;upf_signoff.py",470,780,250,60,"#FFE6CC","#D79B00"),
    ("m3","Regression Detective&#10;regression.py",760,780,250,60,"#FFE6CC","#D79B00"),
    ("m4","Physical-Aware&#10;physical.py",1050,780,250,60,"#FFE6CC","#D79B00"),
]

# solid main-pipeline edges (source, target)
SOLID = [("i1","parser"),("i2","parser"),("i3","parser"),("i4","parser"),
         ("i5","parser"),("i6","parser"),("i7","parser"),
         ("parser","sup"),
         ("sup","a1"),("sup","a2"),("sup","a3"),("sup","a4"),("sup","a5"),("sup","a6"),
         ("a1","fix"),("a2","fix"),("a3","fix"),("a4","fix"),("a5","fix"),("a6","fix"),
         ("fix","out")]
# dashed (optional / grounding / module reuse)
DASHED = [("az","sup","enrich"),("kb","sup","ground"),
          ("m1","fix","reuse"),("m2","fix","reuse"),("m3","fix","reuse"),("m4","fix","reuse")]


def node_xml(nid,label,x,y,w,h,fill,stroke):
    if fill=="none":
        style="text;html=1;fontSize=20;fontColor=#1A1A1A;fontStyle=1;align=center;"
    else:
        style=(f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
               f"fontColor=#1A1A1A;fontSize=12;fontStyle=1;arcSize=12;")
    return (f'<mxCell id="{nid}" value="{label}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')


def edge_xml(eid,s,t,dashed=False,label=""):
    base=("edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;"
          "strokeColor=#8A94A0;strokeWidth=1.5;")
    if dashed: base+="dashed=1;endArrow=open;strokeColor=#0E8088;"
    lbl=f' value="{label}"' if label else ""
    return (f'<mxCell id="{eid}"{lbl} style="{base}" edge="1" parent="1" source="{s}" target="{t}">'
            f'<mxGeometry relative="1" as="geometry"/></mxCell>')


cells=[node_xml(*n) for n in NODES]
cells+=[edge_xml(f"s{i}",s,t) for i,(s,t) in enumerate(SOLID)]
cells+=[edge_xml(f"d{i}",s,t,True,lab) for i,(s,t,lab) in enumerate(DASHED)]

xml=f'''<mxfile host="app.diagrams.net">
  <diagram name="ClosureCopilot" id="closurecopilot">
    <mxGraphModel dx="1500" dy="1000" grid="0" gridSize="10" guides="1" tooltips="1"
        connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1500"
        pageHeight="920" background="#FFFFFF" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {"".join(cells)}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

open("docs/architecture.drawio","w",encoding="utf-8").write(xml)
print("saved docs/architecture.drawio")
