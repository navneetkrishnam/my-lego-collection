"""Produce a deterministic PDF and inspectable PNGs from the saved model.

Dependencies: reportlab, pymupdf, pillow, numpy. All diagrams are construction schematics
derived from the exact instance coordinates; decorative shapes are simplified.
"""
from collections import Counter
import json
import math
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, white
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader
import pymupdf as fitz
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=ROOT/'output/pdf'
OUT.mkdir(parents=True,exist_ok=True)
MODEL=json.loads((HERE/'model.json').read_text())
PARTS=json.loads((HERE/'part-map.json').read_text())
BOM=json.loads((HERE/'bom.json').read_text())
REPORT=json.loads((HERE/'verification.json').read_text())
KEY={e:chr(65+i) for i,e in enumerate(sorted(PARTS))}
W,H=842,595
INK='#203C32'; MUTED='#61776C'; PAPER='#FAF8F1'; PALE='#E8EDE4'; ACCENT='#D26C55'

def rgb(s):
    return tuple(int(s[i:i+2],16)/255 for i in (1,3,5))

def shade(s,factor=1,fade=False):
    values=[min(1,v*factor) for v in rgb(s)]
    if fade: values=[v*.25+.75*.90 for v in values]
    return Color(*values)

def text(c,x,y,s,size=10,color=INK,bold=False):
    c.setFillColor(HexColor(color));c.setFont('Helvetica-Bold' if bold else 'Helvetica',size)
    c.drawString(x,y,str(s))

def wrap(c,s,x,y,width,size=10,leading=14,color=INK):
    words=s.split();line=''
    for word in words:
        candidate=(line+' '+word).strip()
        if stringWidth(candidate,'Helvetica',size)>width and line:
            text(c,x,y,line,size,color);y-=leading;line=word
        else:line=candidate
    if line:text(c,x,y,line,size,color);y-=leading
    return y

def polygon(c,points,fill,stroke=None,width=.35):
    c.setFillColor(fill)
    c.setStrokeColor(stroke or shade('#253E30',1))
    c.setLineWidth(width)
    path=c.beginPath();path.moveTo(*points[0])
    for point in points[1:]:path.lineTo(*point)
    path.close();c.drawPath(path,stroke=1,fill=1)

def project(x,y,z):
    return ((x-y)*.8660254,-(x+y)*.5+z*.4)

def draw_iso(c,pieces,box,active=None):
    # Identical framing for every step makes the build's orientation stable.
    x0,y0,bw,bh=box
    bounds=[project(x,y,z) for x in (0,16) for y in (0,16) for z in (0,20)]
    loX=min(p[0] for p in bounds);hiX=max(p[0] for p in bounds)
    loY=min(p[1] for p in bounds);hiY=max(p[1] for p in bounds)
    scale=min((bw-12)/(hiX-loX),(bh-12)/(hiY-loY))
    ox=x0+bw/2;oy=y0+bh/2-(hiY+loY)/2*scale
    def pp(p):
        sx,sy=project(*p);return ox+sx*scale,oy+sy*scale
    faces=[]
    def face(vertices,col,factor=1,fade=False):
        depth=sum(v[0]+v[1]+v[2]*.4 for v in vertices)/len(vertices)
        faces.append((depth,vertices,shade(col,factor,fade),fade))
    def cylinder(cx,cy,z,r,height,col,fade=False,segments=12):
        ring=[(cx+math.cos(i*2*math.pi/segments)*r,cy+math.sin(i*2*math.pi/segments)*r) for i in range(segments)]
        for i in range(segments):
            a,b=ring[i],ring[(i+1)%segments]
            face([(a[0],a[1],z),(b[0],b[1],z),(b[0],b[1],z+height),(a[0],a[1],z+height)],col,.86,fade)
        face([(x,y,z+height) for x,y in ring],col,1,fade)
    for p in pieces:
        x,y,z,w,d,h=[p[k] for k in ('x','y','z','w','d','h')]
        top=z+h;col=p['rgb'];fade=active is not None and p['step']!=active
        if p['kind']=='box':
            face([(x,y,z),(x+w,y,z),(x+w,y,top),(x,y,top)],col,.75,fade)
            face([(x,y,z),(x,y+d,z),(x,y+d,top),(x,y,top)],col,.85,fade)
            face([(x+w,y,z),(x+w,y+d,z),(x+w,y+d,top),(x+w,y,top)],col,.77,fade)
            face([(x,y+d,z),(x+w,y+d,z),(x+w,y+d,top),(x,y+d,top)],col,.9,fade)
            face([(x,y,top),(x+w,y,top),(x+w,y+d,top),(x,y+d,top)],col,1,fade)
            if p['studded']:
                for i in range(int(w)):
                    for j in range(int(d)):cylinder(x+i+.5,y+j+.5,top,.23,.18,col,fade,8)
        elif p['kind']=='leaf':
            cx,cy=x+.5,y+.5
            for angle in (-math.pi/4,5*math.pi/4,math.pi/2):
                ux,uy=math.cos(angle),math.sin(angle);vx,vy=-uy,ux
                vertices=[(cx,cy,top),(cx+ux*.65+vx*.35,cy+uy*.65+vy*.35,top+.25),
                    (cx+ux*1.25,cy+uy*1.25,top+.2),
                    (cx+ux*.65-vx*.35,cy+uy*.65-vy*.35,top+.25)]
                face(vertices,col,1,fade)
            cylinder(cx,cy,top,.22,.1,col,fade)
        elif p['kind']=='flower':
            cx,cy=x+.5,y+.5
            for i in range(5):
                a=2*math.pi*i/5;cylinder(cx+.22*math.cos(a),cy+.22*math.sin(a),top,.19,.06,col,fade,8)
            cylinder(cx,cy,top,.14,.11,col,fade,8)
        elif p['kind']=='mug':
            cylinder(x+.5,y+.5,z,.43,h,col,fade)
            # Schematic open top and oriented handle, not a substitute mesh.
            cylinder(x+.5,y+.5,top+.01,.30,.01,'#806925',fade)
            sign=-1 if p.get('rotation')==180 else 1
            near=y+.5+sign*.4;far=y+.5+sign*1.1;mid=y+.5+sign*.9
            face([(x+.37,near,z+.4),(x+.63,near,z+.4),(x+.63,far,z+.4),(x+.37,far,z+.4)],col,.9,fade)
            face([(x+.37,mid,z+.4),(x+.63,mid,z+.4),(x+.63,mid,z+1.7),(x+.37,mid,z+1.7)],col,.9,fade)
    # A true per-pixel depth buffer prevents large lower plates from painting
    # over smaller upper parts, which a centroid-sorted vector drawing cannot.
    resolution=2
    width,height=int(bw*resolution),int(bh*resolution)
    pixels=np.full((height,width,3),rgb(PAPER),dtype=np.float32)
    depths=np.full((height,width),-np.inf,dtype=np.float64)
    edges=[]
    for _,vs,col,fade in faces:
        vertices=[]
        for v in vs:
            xx,yy=pp(v)
            vertices.append(((xx-x0)*resolution,(y0+bh-yy)*resolution,v[0]+v[1]+v[2]*.4))
        fill=np.array([col.red,col.green,col.blue],dtype=np.float32)
        for j in range(1,len(vertices)-1):
            a,b,d=np.array([vertices[0],vertices[j],vertices[j+1]])
            den=(b[1]-d[1])*(a[0]-d[0])+(d[0]-b[0])*(a[1]-d[1])
            if abs(den)<1e-8:continue
            minx=max(0,int(math.floor(min(a[0],b[0],d[0]))));maxx=min(width-1,int(math.ceil(max(a[0],b[0],d[0]))))
            miny=max(0,int(math.floor(min(a[1],b[1],d[1]))));maxy=min(height-1,int(math.ceil(max(a[1],b[1],d[1]))))
            if maxx<minx or maxy<miny:continue
            xx,yy=np.meshgrid(np.arange(minx,maxx+1)+.5,np.arange(miny,maxy+1)+.5)
            wa=((b[1]-d[1])*(xx-d[0])+(d[0]-b[0])*(yy-d[1]))/den
            wb=((d[1]-a[1])*(xx-d[0])+(a[0]-d[0])*(yy-d[1]))/den
            wc=1-wa-wb;zz=wa*a[2]+wb*b[2]+wc*d[2]
            section=depths[miny:maxy+1,minx:maxx+1]
            mask=(wa>=-1e-6)&(wb>=-1e-6)&(wc>=-1e-6)&(zz>=section)
            section[mask]=zz[mask];pixels[miny:maxy+1,minx:maxx+1][mask]=fill
        for j in range(len(vertices)):
            edges.append((vertices[j],vertices[(j+1)%len(vertices)],fill*.65+.15))
    for a,b,col in edges:
        a=np.array(a);b=np.array(b);n=max(2,int(np.max(np.abs(b[:2]-a[:2]))*1.5)+1)
        line=a[None,:]+np.linspace(0,1,n)[:,None]*(b-a)[None,:]
        xx=np.floor(line[:,0]).astype(int);yy=np.floor(line[:,1]).astype(int)
        valid=(xx>=0)&(xx<width)&(yy>=0)&(yy<height)
        xx=xx[valid];yy=yy[valid];zz=line[valid,2]
        visible=zz>=depths[yy,xx]-.06
        pixels[yy[visible],xx[visible]]=col
    img=Image.fromarray(np.clip(pixels*255,0,255).astype('uint8'))
    c.drawImage(ImageReader(img),x0,y0,bw,bh,mask='auto')

def draw_plan(c,pieces,box,active):
    bx,by,size=box;s=size/16
    c.setFillColor(HexColor('#EEECE2'));c.rect(bx,by,size,size,stroke=0,fill=1)
    visible=sorted(pieces,key=lambda p:(p['z']+p['h'],p['key']))
    for p in visible:
        x=bx+p['x']*s;y=by+(16-p['y']-p['d'])*s
        c.setFillColor(shade(p['rgb'],1,p['step']!=active));c.setStrokeColor(HexColor('#A6B0A5'));c.setLineWidth(.3)
        c.rect(x,y,p['w']*s,p['d']*s,stroke=1,fill=1)
        if p['step']==active:
            c.setStrokeColor(HexColor(INK));c.setLineWidth(.85)
            c.rect(x,y,p['w']*s,p['d']*s,stroke=1,fill=0)
            color='#FFFFFF' if sum(rgb(p['rgb']))<1.5 else INK
            text(c,x+p['w']*s/2-2.4,y+p['d']*s/2-2.2,KEY[p['element']],6.5,color,True)
    for i in range(17):
        c.setStrokeColor(HexColor('#BEC6B8'));c.setLineWidth(.16)
        c.line(bx+i*s,by,bx+i*s,by+size);c.line(bx,by+i*s,bx+size,by+i*s)
    for i in range(16):
        text(c,bx+(i+.5)*s-3,by+size+5,str(i),6.5,MUTED)
        text(c,bx-14,by+(15.5-i)*s-2,str(i),6.5,MUTED)
    text(c,bx+size/2-21,by-14,'FRONT',8,INK,True)

def page(c,number,kicker,title,subtitle=''):
    c.setFillColor(HexColor(PAPER));c.rect(0,0,W,H,fill=1,stroke=0)
    text(c,32,H-30,kicker.upper(),9,MUTED,True)
    text(c,32,H-66,title,27,INK,True)
    if subtitle:wrap(c,subtitle,32,H-88,W-64,10,14,MUTED)
    c.setStrokeColor(HexColor('#D4DCCD'));c.setLineWidth(.5);c.line(32,30,W-32,30)
    text(c,32,17,'FERN & STEAM  /  REVISION 1  /  INVENTORY-CHECKED PROTOTYPE',7,MUTED)
    text(c,W-48,17,str(number),8,MUTED)

def inventory_page(c,number,rows):
    page(c,number,'Parts / exact IDs','Your picking palette',
         'Required quantities are counted from the model. Minimum quantities assume complete, accessible donor sets.')
    cols=[40,76,160,385,538,642,736]
    for x,s in zip(cols,['KEY','ELEMENT ID','DESCRIPTION','COLOR','NEED','MINIMUM','LEFT*']):text(c,x,470,s,8,MUTED,True)
    for i,p in enumerate(rows):
        y=443-i*27
        c.setFillColor(shade(p['rgb']));c.setStrokeColor(HexColor('#839489'));c.rect(cols[0],y-3,13,13,fill=1,stroke=1)
        text(c,cols[0]+18,y,KEY[p['element']],10,INK,True)
        text(c,cols[1],y,p['element'],10)
        text(c,cols[2],y,p['name'],10)
        text(c,cols[3],y,p['color'],10)
        text(c,cols[4]+10,y,p['required'],10,INK,True)
        text(c,cols[5]+12,y,p['minimum'],10)
        text(c,cols[6]+7,y,p['minimum']-p['required'],10)
    wrap(c,'*Remaining conservative budget after this model. It is not an exact physical stock count. Part color labels are normalized from the repo enrichment cache; physically compare the piece against its exact element ID.',40,65,760,9,12,MUTED)
    c.showPage()

def main():
    target=OUT/'fern-and-steam-build-guide.pdf'
    c=canvas.Canvas(str(target),pagesize=(W,H),invariant=1,pageCompression=1)
    c.setTitle('Fern & Steam - Inventory-checked prototype build guide')
    c.setAuthor('Navneet / Codex')
    page(c,1,'Original custom model / designed from your collection','Fern & Steam',
         'A little tea counter, an airy pergola and a courtyard full of plants.')
    draw_iso(c,MODEL['pieces'],(90,118,670,370))
    for x,value,label in [(45,str(REPORT['piece_count']),'PIECES'),(220,'16 x 16','STUD FOOTPRINT'),(440,str(REPORT['unique_elements']),'EXACT ELEMENTS'),(655,'12','BUILD STEPS')]:
        text(c,x,95,value,22,INK,True);text(c,x,78,label,8,MUTED,True)
    text(c,45,49,'Model-derived schematic. Foliage and mugs are simplified. Digital fine-fit and physical build remain to be tested.',9,MUTED)
    c.showPage()
    page(c,2,'Read before building','What has been checked',
         'Use this as a first physical prototype. A passing inventory calculation is not a completed physical test.')
    checks=[('PASS','115 pieces fit the conservative exact-ID inventory.'),
            ('PASS','Structural boxes have no body overlaps or out-of-bounds placements.'),
            ('PASS','Every elevated instance has a prior stud support in the simplified model.'),
            ('PASS','The final simplified connection graph is one connected assembly.'),
            ('PASS','No earlier structural box blocks the stated downward placement order.'),
            ('REVIEW','15 decorative instances use mounting abstractions; detailed mesh fit is not tested.'),
            ('REVIEW','Element-to-LDraw mappings and cached colors need visual confirmation.'),
            ('PENDING','Physical fit, stability, clutch strength and a complete trial build.')]
    for i,(label,s) in enumerate(checks):
        y=459-i*31;text(c,40,y,label,9,ACCENT if label!='PASS' else INK,True);text(c,112,y,s,10)
    wrap(c,'The donor allocation takes at most one of each listed element from each set copy. It currently spans 26 sets. This is a reproducible conservative allocation, not the smallest possible donor selection. Check familiar sets for extra copies first if you want to reduce disassembly.',40,184,752,11,16)
    wrap(c,'Build on a flat surface. Finish the two-layer base before lifting it. Attach the furniture, flowers and mugs before closing the pergola. If a piece does not seat naturally, stop and record the exact instance and step instead of forcing the connection.',40,104,752,11,16)
    c.showPage()
    page(c,3,'How to read the steps','A precise position for every piece',
         'Keep the front edge toward you. Each step includes a shaded model, a top view and an ordered placement table.')
    draw_plan(c,MODEL['pieces'][:23],(60,117,285),2)
    yy=458
    notes=[('X / Y','X runs left to right. Y runs from the rear toward the front. Both start at 0 and describe the rear-left corner of a part footprint.'),
           ('Z','Z is the bottom elevation measured in plate heights. A plate is 1 unit; an ordinary brick is 3. The finished tan base surface is Z = 2.'),
           ('FOOTPRINT','Width x depth describes how the part lies in the top view. For example 8 x 1 means a long horizontal beam; 1 x 6 runs front to back.'),
           ('KEY / ID','Letters A-Y identify exact elements in the parts palette. P001 etc. identify individual placements. Follow placement rows from top to bottom.'),
           ('DECORATIONS','Leaf Z is its underside mounting plane. A leaf adds 0.375 plate units before its flower; this is intentional. Leaf/flower shapes in the schematic are simplified.'),
           ('SHADING','Current-step pieces keep their colors. Earlier pieces are muted. The top view shows the uppermost footprint when several pieces share a position.')]
    for title,body in notes:
        text(c,405,yy,title,9,INK,True);yy=wrap(c,body,405,yy-17,387,10,14,MUTED)-15
    c.showPage()
    inventory_page(c,4,BOM[:13]);inventory_page(c,5,BOM[13:])
    for step in MODEL['steps']:
        n=step['number'];current=[p for p in MODEL['pieces'] if p['step']==n]
        sofar=[p for p in MODEL['pieces'] if p['step']<=n]
        page(c,n+5,f"Build / step {n:02} of 12",step['title'],step['description'])
        draw_iso(c,sofar,(30,145,468,320),active=n)
        text(c,40,128,f"ADD {len(current)} PIECES  /  TOTAL {len(sofar)}",10,INK,True)
        counts=Counter(p['element'] for p in current)
        line='   '.join(f'{KEY[e]} x{count}' for e,count in sorted(counts.items()))
        wrap(c,line,40,109,440,10,14,MUTED)
        text(c,40,65,'Assembly schematic; use the coordinates for exact placement.',9,MUTED)
        text(c,522,473,'INSTANCE  KEY     X    Y      Z       FOOTPRINT',8,INK,True)
        for i,p in enumerate(current):
            yy=455-i*12
            text(c,522,yy,p['key'],8.5)
            text(c,576,yy,KEY[p['element']],8.5,INK,True)
            text(c,613,yy,p['x'],8.5);text(c,638,yy,p['y'],8.5)
            text(c,668,yy,f"{p['z']:g}",8.5)
            text(c,737,yy,f"{p['w']} x {p['d']}",8.5)
        draw_plan(c,sofar,(563,58,192),n)
        c.showPage()
    page(c,18,'After the build','Record the physical result',
         'This revision is ready for a careful trial assembly. Keep a short record so the next revision improves on evidence.')
    text(c,42,449,'CHECK',9,MUTED,True);text(c,408,449,'RESULT / NOTES',9,MUTED,True)
    for i,s in enumerate(['All exact elements picked and visually matched','Two-layer base holds together when lifted','Counter, wall and posts seat without forcing','Bench seat and backrest attach securely','Leaf-to-flower connections seat correctly','Mug handles clear surrounding pieces','Both beams connect to all four posts','Slats fit without bending posts or beams','Completed model stays stable on a level surface']):
        yy=419-i*31;text(c,42,yy,s,10)
        c.setStrokeColor(HexColor('#CAD2C5'));c.line(408,yy-2,796,yy-2)
    wrap(c,'Companion files: fern-and-steam.ldr opens in an LDraw-compatible editor; model.json records every placement; picking-list.md groups the exact IDs by donor set; inventory-snapshot.json and verification.json preserve the inventory assumptions and checks.',42,109,754,10,14)
    text(c,42,55,'Geometry references: library.ldraw.org/library/official/parts/  |  File format: ldraw.org/article/218.html',8,MUTED)
    c.showPage();c.save()
    render_dir=ROOT/'tmp/pdfs/fern-and-steam';render_dir.mkdir(parents=True,exist_ok=True)
    doc=fitz.open(target)
    for i,p in enumerate(doc):
        p.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False).save(render_dir/f'page-{i+1:02}.png')
    doc[0].get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).save(HERE/'preview.png')
    print(f'{target}\n{len(doc)} pages rendered to {render_dir}')

if __name__=='__main__':main()
