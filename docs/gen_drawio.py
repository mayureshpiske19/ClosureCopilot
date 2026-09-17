"""draw.io: sequence Collaterals · PPA · Equivalence; Design Context right; modules vertical right."""
import html

NODES=[]
def add(nid,label,x,y,w,h,fill,stroke,fs=13): NODES.append((nid,label,x,y,w,h,fill,stroke,fs))

MC=620  # main-pipeline center x

# title
add("t","ClosureCopilot — Architecture &amp; Data Flow",300,14,740,40,"none","none",22)

# ---- input wrappers : Collaterals · PPA · Equivalence  (Design Context rightmost) ----
add("wcol","Collaterals&#10;UPF · Constraints (SDC)",194,90,270,74,"#DAE8FC","#6C8EBF",13)          # center 329
add("wppa","PPA Reports&#10;STA · Synthesis · RTLA (report + log)",500,90,290,74,"#DAE8FC","#6C8EBF",12)  # 645
add("wequ","Equivalence&#10;Formal / LEC (report + log)",826,90,220,74,"#DAE8FC","#6C8EBF",12)      # 936
add("wdc","Design Context&#10;RTL files · spec .md · micro-arch docs",1180,90,280,74,"#E6F8F7","#0E8088",12)  # 1320

# ---- ingestion (spans the 3 report wrappers) ----
add("parser","Ingestion / Parser Agent&#10;ingestion/parsers.py · detect_type() → Finding",
    194,212,852,58,"#D5E8D4","#82B366",14)   # center 620

# ---- supervisor + side ----
add("sup","Supervisor / Orchestrator&#10;orchestrator.py",440,316,360,64,"#E1D5E7","#9673A6",14)  # 620
add("az","Azure OpenAI&#10;llm.py · optional",60,318,200,60,"#F5F5F5","#999999",12)
add("kb","Grounded knowledge&#10;rag/ · design + global",1200,318,220,60,"#B0E3E6","#0E8088",12)  # 1310

# ---- grouping layer : Collaterals · PPA · Equivalence ----
add("gcol","Collaterals Check",119,436,422,52,"#DAE8FC","#6C8EBF",14)   # center 330
add("gppa","PPA Analysis",554,436,422,52,"#FFF2CC","#D6B656",14)        # 765
add("gequ","Equivalence Check",989,436,132,52,"#F8CECC","#B85450",12)   # 1055

# ---- leaf agents (7) : [Synthesis UPF Constraints] [Power Timing Area] [Formal] ----
leaves=["Synthesis","UPF","Constraints","Power","Timing","Area","Formal"]
aw,ag=132,13; ax0=119; atot=7*aw+6*ag
acx=[ax0 + i*(aw+ag) + aw/2 for i in range(7)]
for i,name in enumerate(leaves):
    add(f"a{i}",name, ax0+i*(aw+ag), 534, aw, 62, "#EEF1F6","#5B6570",12)

# ---- fix router (spans leaves) ----
add("fix","Fix-Routing / Diagnosis Engine&#10;fix_router.py · RTL | SDC | UPF | Synth  +  snippet + trade-off",
    ax0,646,atot,66,"#F8CECC","#B85450",14)

# ---- output ----
add("out","Ranked findings — AnalysisResult&#10;Streamlit app · HTML dashboard · CLI",
    340,754,560,64,"#D5E8D4","#82B366",13)   # center 620

# ---- closure modules : VERTICAL stack on the right (independent) ----
add("panel","CLOSURE MODULES&#10;reuse the Fix-Router",1180,548,280,290,"#FFFAF1","#E6C48A",12)
mboxes=[("Constraint Promotion","promotion.py"),("UPF Signoff","upf_signoff.py"),
        ("Regression Detective","regression.py")]
for i,(t,fn) in enumerate(mboxes):
    add(f"m{i}",f"{t}&#10;{fn}",1198,600+i*76,244,60,"#FFE6CC","#D79B00",12)


def node_xml(nid,label,x,y,w,h,fill,stroke,fs):
    if fill=="none":
        style=f"text;html=1;fontSize={fs};fontColor=#1A1A1A;fontStyle=1;align=center;"
    elif nid=="panel":
        style=(f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
               f"fontColor=#B5791F;fontSize={fs};fontStyle=1;arcSize=6;verticalAlign=top;spacingTop=8;")
    else:
        style=(f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
               f"fontColor=#1A1A1A;fontSize={fs};fontStyle=1;arcSize=10;")
    return (f'<mxCell id="{nid}" value="{label}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" as="geometry"/></mxCell>')

def sv(eid,s,t,exx,enx,color="#5B6570"):
    style=(f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;"
           f"exitX={exx:.4f};exitY=1;exitDx=0;exitDy=0;entryX={enx:.4f};entryY=0;entryDx=0;entryDy=0;"
           f"strokeColor={color};strokeWidth=1.7;endArrow=block;endFill=1;")
    return (f'<mxCell id="{eid}" style="{style}" edge="1" parent="1" source="{s}" target="{t}">'
            f'<mxGeometry relative="1" as="geometry"/></mxCell>')

def hz(eid,s,t,color,label,exx,exy,enx,eny,dashed=True):
    style=(f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;"
           f"exitX={exx};exitY={exy};entryX={enx};entryY={eny};"
           f"strokeColor={color};strokeWidth=1.6;endArrow={'open' if dashed else 'block'};endFill={'0' if dashed else '1'};")
    if dashed: style+="dashed=1;"
    lbl=f' value="{html.escape(label)}"' if label else ""
    return (f'<mxCell id="{eid}"{lbl} style="{style}" edge="1" parent="1" source="{s}" target="{t}">'
            f'<mxGeometry relative="1" as="geometry"/></mxCell>')

PPX0,PW=194,852
E=[]
# report wrappers -> parser
for wid,cx in [("wcol",329),("wppa",645),("wequ",936)]:
    E.append(sv(f"e_{wid}",wid,"parser",0.5,(cx-PPX0)/PW))
# design context -> grounded knowledge
E.append(sv("edc","wdc","kb",0.5,0.5,color="#0E8088"))
# parser -> supervisor
E.append(sv("eps","parser","sup",0.5,0.5))
# az/kb -> supervisor
E.append(hz("eaz","az","sup","#0E8088","enrich",1,0.5,0,0.5))
E.append(hz("ekb","kb","sup","#0E8088","ground",0,0.5,1,0.5))
# supervisor -> groups
for g in ("gcol","gppa","gequ"): E.append(sv(f"eg_{g}","sup",g,0.5,0.5))
# groups -> leaves  (Collaterals: 0,1,2 | PPA: 3,4,5 | Equivalence: 6)
gpar={"gcol":[0,1,2],"gppa":[3,4,5],"gequ":[6]}
for g,idxs in gpar.items():
    for j in idxs: E.append(sv(f"e{g}{j}",g,f"a{j}",0.5,0.5))
# leaves -> fix
for i in range(7): E.append(sv(f"ef{i}",f"a{i}","fix",0.5,(acx[i]-ax0)/atot))
# fix -> output
E.append(sv("efo","fix","out",0.5,0.5))
# closure modules (panel) -> fix : reuse (horizontal dashed on the right)
E.append(hz("ereuse","panel","fix","#D79B00","reuse",0,0.5,1,0.5,dashed=True))

cells=[node_xml(*n) for n in NODES]+E
xml=f'''<mxfile host="app.diagrams.net">
  <diagram name="ClosureCopilot" id="closurecopilot">
    <mxGraphModel dx="1500" dy="950" grid="0" gridSize="10" guides="1" tooltips="1"
        connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1500"
        pageHeight="880" background="#FFFFFF" math="0" shadow="0">
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
