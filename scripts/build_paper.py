from __future__ import annotations
import re
from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"paper"/"EPV_M8_MANUSCRIPT.md"
OUTPUT=ROOT/"output"/"pdf"/"EPV_M8_MANUSCRIPT.pdf"

def esc(text):
    return text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def footer(canvas, doc):
    canvas.saveState(); canvas.setFont("Helvetica",8); canvas.setFillColor(HexColor("#52606d"))
    canvas.drawString(0.72*inch,0.48*inch,"EPV 0.1.0 research release candidate - not published")
    canvas.drawRightString(7.78*inch,0.48*inch,f"{doc.page}"); canvas.restoreState()

def build():
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name="PaperTitle",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=20,leading=24,textColor=HexColor("#102a43"),spaceAfter=16))
    styles.add(ParagraphStyle(name="Author",parent=styles["Normal"],alignment=TA_CENTER,fontSize=11,spaceAfter=22))
    styles.add(ParagraphStyle(name="H1x",parent=styles["Heading1"],fontName="Helvetica-Bold",fontSize=14,leading=17,textColor=HexColor("#0b7285"),spaceBefore=14,spaceAfter=7,keepWithNext=True))
    styles.add(ParagraphStyle(name="Bodyx",parent=styles["BodyText"],fontName="Times-Roman",fontSize=9.5,leading=13,spaceAfter=7,alignment=4))
    styles.add(ParagraphStyle(name="Ref",parent=styles["BodyText"],fontName="Times-Roman",fontSize=8.5,leading=11,spaceAfter=5))
    story=[]
    for i,line in enumerate(SOURCE.read_text(encoding="utf-8").splitlines()):
        line=line.strip()
        if not line: continue
        if line.startswith("# "):
            story.append(Paragraph(esc(line[2:]),styles["PaperTitle"])); continue
        if line.startswith("**") and line.endswith("**"):
            story.append(Paragraph(esc(line.strip("*")),styles["Author"])); continue
        if line.startswith("## "):
            if line=="## References": story.append(PageBreak())
            story.append(Paragraph(esc(line[3:]),styles["H1x"])); continue
        text=esc(line)
        text=re.sub(r"`([^`]+)`",r"<font name='Courier'>\1</font>",text)
        story.append(Paragraph(text,styles["Ref"] if "References" in [getattr(x,"text","") for x in story[-1:]] else styles["Bodyx"]))
    doc=SimpleDocTemplate(str(OUTPUT),pagesize=LETTER,rightMargin=.72*inch,leftMargin=.72*inch,topMargin=.65*inch,bottomMargin=.7*inch,title="EPV: An Assurance-Oriented Framework",author="Aayush Kadam")
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print(OUTPUT)

if __name__=="__main__": build()
