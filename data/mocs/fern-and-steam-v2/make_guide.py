"""Generate a coordinate-based digital build draft from the exact model."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=ROOT/'output/pdf/fern-and-steam-courtyard-build-draft.pdf'
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='SmallText',fontName='Helvetica',fontSize=8,leading=10,spaceAfter=5))
styles.add(ParagraphStyle(name='Deck',fontName='Helvetica',fontSize=11,leading=16,textColor=colors.HexColor('#45594a'),spaceAfter=12))
styles['Title'].textColor=colors.HexColor('#244233')
styles['Heading1'].textColor=colors.HexColor('#244233')
styles['Heading2'].textColor=colors.HexColor('#244233')

def para(s,style='BodyText'):return Paragraph(escape(s),styles[style])
def table(rows,widths):
    data=[[para(str(c),'SmallText') for c in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e3ebe4')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#90a394')),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#d6ddd8')),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2)]))
    return t

def footer(canvas,doc):
    canvas.saveState();canvas.setStrokeColor(colors.HexColor('#bdc8bf'));canvas.line(38,35,557,35)
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#637469'))
    canvas.drawString(38,23,'FERN & STEAM / DIGITAL BUILD DRAFT / physical build not tested')
    canvas.drawRightString(557,23,str(doc.page));canvas.restoreState()

def make():
    model=json.loads((HERE/'model.json').read_text());snap=json.loads((HERE/'inventory-snapshot.json').read_text())
    bom=json.loads((HERE/'bom.json').read_text());pieces=model['pieces'];spec=snap['parts']
    digest=hashlib.sha256((HERE/'fern-and-steam-v2.ldr').read_bytes()).hexdigest()
    if json.loads((HERE/'preview.render.json').read_text())['input_sha256']!=digest:
        raise ValueError('Preview is stale; render the current LDraw model before creating the guide')
    cache=ROOT/'tmp/pdfs/fern-steam-v2'/digest[:12];cache.mkdir(parents=True,exist_ok=True)
    story=[para('FERN & STEAM','Title'),para('Courtyard Edition','Heading1'),para(f"{len(pieces)} pieces / 24 x 24 studs / arched conservatory cafe",'Deck'),Image(str(HERE/'preview.png'),width=515,height=429),Spacer(1,12),para('Actual LDraw geometry render','Heading2'),para('A translation of the approved design concept using exact elements listed in the donor collection. This is a digital construction draft for review and a trial build, not physically tested instructions. The editable LDraw file is the authoritative placement reference.'),PageBreak()]
    story += [para('Before you build','Heading1'),para('What has been checked','Heading2'),para('The combined bill of materials fits the conservative donor allowance. Ordinary brick, plate and tile bodies have no nominal box overlaps. The stud attachment graph is connected, and compatible window inserts use the documented frame transforms. Actual mesh bounds have been checked against the authored placements.'),Spacer(1,9),para('What remains to be checked','Heading2'),para('A physical trial build, clutch strength, load stability, insertion access, and a complete solid collision check remain outstanding. The targeted accessory mesh probe is additional evidence, not a general collision certification. Studio may prompt you to update newer parts.'),Spacer(1,9),para('Inventory assumption','Heading2'),para('Each exact element ID counts once per owned donor-set copy. This is a conservative allowance from set membership, assuming complete accessible sets and no other reservations. Actual set quantities may be higher. The donor list is a reproducible allocation under this rule, not a requirement to dismantle that many sets.'),Spacer(1,9),para('How to read the coordinates','Heading2'),para('Face the cafe from the bench side. The rear-left base corner is (0,0). X runs left to right and Y runs rear to front, both in studs; the base occupies X=0..24 and Y=0..24. Z is upward in plate heights, measured at the bottom of the part body. One brick is 3 plates. For ordinary parts X/Y marks the lower-left footprint corner, not its center.'),Spacer(1,7),para('Yaw is the absolute LDraw rotation about its downward Y axis, viewed from above. The footprint column gives the final X by Y size, making rectangular-part orientation unambiguous. Round-mounted plants may use 45-degree yaw increments. For panes, attach to the named parent frame with the listed local LDraw offset instead of using footprint coordinates. 20 LDraw units = 1 stud; 8 units = 1 plate.'),Spacer(1,9),para('Assembly notes','Heading2'),para('Build the counter before fitting the arches and roof. Insert panes into their frames before the cornice. Assemble the lantern support rails and eaves as a small subassembly, then lower it onto the cornice; do not expect every loose rail to stand on its own. Hold the model by the base. Inspect the first trial assembly before applying force to any uncertain connection.'),PageBreak()]
    for step in model['steps']:
        n=step['number'];new=[p for p in pieces if p['step']==n];image=cache/f'step-{n:02}.png'
        if not image.exists():
            subprocess.run([sys.executable,str(HERE/'render_model.py'),'--step',str(n),'--output',str(image),'--width','900','--height','650','--samples','32'],check=True)
        story += [para(f"{n:02} / {step['title']}",'Heading1'),para(step['note'],'Deck'),Image(str(image),width=515,height=372),Spacer(1,8),para(f"Add {len(new)} pieces in this stage",'Heading2')]
        count=Counter(p['element'] for p in new)
        story += [table([['Element','Color / geometry','Qty']]+[[e,f"{spec[e]['color']} / {spec[e]['ldraw']}",k] for e,k in sorted(count.items())],[80,385,50]),PageBreak(),para(f"{n:02} / Placement schedule",'Heading1'),para('Place the pieces listed below; frame inserts identify their matching parent. Within a stage, assemble lower levels before higher levels unless the stage explicitly describes a subassembly.','SmallText')]
        rows=[['Instance','Element','X, Y, Z','Footprint','Yaw / insert']]
        for p in new:
            if p['kind']=='insert':
                coord='Frame '+p['parent'];foot='Insert';orient='offset '+', '.join(f'{v:g}' for v in p['offset'])
            else:
                coord=', '.join(f"{p[a]:g}" for a in ('x','y','z'));foot=f"{p['w']:g} x {p['d']:g}";orient=f"{round(math.degrees(math.atan2(p['matrix'][2],p['matrix'][0])))%360} deg"
            rows.append([p['key'],p['element'],coord,foot,orient])
        story += [table(rows,[55,70,125,65,200]),PageBreak()]
    story += [para('Combined bill of materials','Heading1'),para('Exact element IDs distinguish both shape and color. Available means the conservative set-membership allowance. See picking-list.md and allocation.json for donor boxes.','Deck')]
    story += [table([['Element','Color / geometry','Need','Available']]+[[b['element'],f"{b['color']} / {b['ldraw']}",b['required'],b['conservative_available']] for b in bom],[75,320,50,70]),Spacer(1,14),para('Provenance','Heading2'),para('Inventory: repo data/owned-sets.csv and public/data/parts/*.json, frozen with input hashes. Exact part/color mapping: installed BrickLink Studio elementInfoList.json, StudioPartDefinition2.txt and StudioColorDefinition.txt. Geometry: Studio LDraw library plus the attributed official primitive included under ldraw/. Architecture and roof research notes accompany the model.','SmallText'),para('LDraw SHA-256: '+digest,'SmallText')]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=38,leftMargin=38,topMargin=42,bottomMargin=47,title='Fern & Steam - Courtyard Edition - Digital Build Draft',author='LEGO Tracker',invariant=1)
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print('Created',OUT,flush=True)

if __name__=='__main__':make()
