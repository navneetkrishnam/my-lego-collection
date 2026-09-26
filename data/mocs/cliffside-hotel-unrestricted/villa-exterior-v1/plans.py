"""Native vector and raster floor-plan drawings from the same authored layout."""
from pathlib import Path
import html,json,hashlib
from PIL import Image,ImageDraw,ImageFont
import layout as l
HERE=Path(__file__).resolve().parent
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
COLORS=dict(guest='#eee1c4',bath='#d5e8eb',circulation='#f1ece2',stair='#dcdce7',
            lobby='#f0dbc5',lounge='#e8dfcf',service='#e2e4e0',garden='#dce8d0',
            pool='#d8e9e7',dining='#f4dfc6',salon='#e4def0',spa='#d8e8e0',shared='#eee8df',private='#eee1c4')
class Canvas:
 def __init__(self,w,h):
  self.im=Image.new('RGB',(w,h),'#faf8f3');self.d=ImageDraw.Draw(self.im);self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="#faf8f3"/>']
 def rect(self,b,fill,stroke=None,width=1):
  self.d.rectangle(b,fill=fill,outline=stroke,width=width)
  x,y,xx,yy=b;self.svg.append(f'<rect x="{x}" y="{y}" width="{xx-x}" height="{yy-y}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{width}"/>')
 def line(self,pts,fill,width=2):
  self.d.line(pts,fill=fill,width=width)
  self.svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{fill}" stroke-width="{width}"/>')
 def text(self,p,s,size=18,color='#343c3d',center=False):
  font=ImageFont.truetype(FONT,size)
  self.d.text(p,s,font=font,fill=color,anchor='mm' if center else 'lt')
  anchor='middle' if center else 'start';baseline='central' if center else 'hanging'
  self.svg.append(f'<text x="{p[0]}" y="{p[1]}" font-family="Arial, sans-serif" font-size="{size}" fill="{color}" text-anchor="{anchor}" dominant-baseline="{baseline}">{html.escape(s)}</text>')
 def save(self,name):
  self.im.save(HERE/(name+'.png'));(HERE/(name+'.svg')).write_text('\n'.join(self.svg)+ '</svg>')

def panel(c,floors,bounds,origin,scale,labels=True):
 ox,oy=origin;bx,by,bw,bh=bounds
 pt=lambda x,y:(round(ox+(x-bx)*scale),round(oy+(y-by)*scale))
 rr=lambda r:(*pt(r[0],r[1]),*pt(r[0]+r[2],r[1]+r[3]))
 for f in floors:
  for r in f['rects']:c.rect(rr(r),'#fffefa','#bcb6aa')
  for b in f['balconies']:c.rect(rr(b['rect']),'#f2e7d1','#c7bda8')
 for f in floors:
  for s in f['spaces']:c.rect(rr(s['rect']),COLORS.get(s['kind'],'#ece9e2'))
  for h in f['holes']:c.rect(rr(h),'#cfced5','#888494')
  for item in f['furniture']:c.rect(rr(item['rect']),'#95ab82' if item['name'].startswith(('Side garden','Cottage garden')) else '#aba59a','#817c73')
 # Stairs occupy floor shafts, not room footprints. Show flight direction.
 for f in floors:
  if f['id'].startswith('main'):
   x,y=45,11
  elif f['id'] in ('dining','salon','spa'):x,y=115,41
  else:continue
  for i in range(10):
   c.line([pt(x,y+3+i*.9),pt(x+4,y+3+i*.9)],'#8d8997',1)
   c.line([pt(x+6,y+3+i*.9),pt(x+10,y+3+i*.9)],'#8d8997',1)
  c.line([pt(x+2,y+11),pt(x+2,y+4),pt(x+1,y+5)],'#666275',2)
  c.line([pt(x+8,y+4),pt(x+8,y+11),pt(x+9,y+10)],'#666275',2)
 for f in floors:
  for w in f['walls']:
   axis,at,a,b,t=w['axis'],w['c'],w['a'],w['b'],w['thickness']
   r=(a,at-t/2,b-a,t) if axis=='x' else (at-t/2,a,t,b-a)
   c.rect(rr(r),'#44494a')
   for o in w['opens']:
    q=(o['a'],at-t/2,o['w'],t) if axis=='x' else (at-t/2,o['a'],t,o['w'])
    c.rect(rr(q),'#faf8f3' if o['kind']=='door' else '#86afb9')
    if o['kind']=='door':
     ends=[pt(o['a'],at),pt(o['a']+o['w'],at)] if axis=='x' else [pt(at,o['a']),pt(at,o['a']+o['w'])]
     c.line(ends,'#4f9478',2)
 if labels:
  for f in floors:
   for s in f['spaces']:
    text=s['name'];x,y=s['node'];sz=15 if scale<14 else 17
    if s['kind']=='bath' and 'Changing' not in text:text='Bath / WC';sz=12
    elif s['kind']=='stair':text='Landing';sz=12
    elif s['kind']=='circulation':sz=12
    if 'Corner room' in text:y+=3
    if 'Treatment' in text:y+=2
    if f['id']=='site' and 'Common side' in text:x=10
    if f['id']=='site' and 'Arrival court' in text:x,y=61,41
    if f['id']=='site' and text=='Cottage private garden':x,y=88,43.5;text='Private garden';sz=12
    if scale<14 and text=='Service corridor':y=58
    if text=='Restaurant / pool bar':text='Restaurant: 8 seats';x,y=111,75.5
    if text=='Salon / quiet lounge':x,y=112,74
    if 'Garden room —' in text:text='Room 101\nNo balcony'
    if 'Corner room —' in text:text='Room 102\nPrivate balcony'
    if 'Extended suite —' in text:text='Suite 103\nExtended room'
    if text=='Cottage 01 private room':text='Cottage 01\nPrivate room'
    if text=='Private sitting area':text='Private sitting area';sz=12
    if text=='Lobby lounge / library':text='Lobby lounge\nLibrary'
    if text=='Common corridor' and scale<14:y=29.5
    if text=='Cottage foyer':sz=11
    if text=='Lobby / front desk':text='Lobby\nFront desk'
    if 'bath' in s['name'].lower():text='Bath'
    for i,line in enumerate(text.split('\n')):
     xp,yp=pt(x,y);c.text((xp,yp+i*(sz+3)),line,sz,center=True)
   for b in f['balconies']:
    text='Suite balcony' if 'Extended' in b['name'] else 'Private balcony' if 'Corner' in b['name'] else 'Lounge terrace'
    c.text(pt(*b['node']),text,12,center=True)
 return pt

def draw():
 c=Canvas(1560,1330)
 c.text((45,26),'HOTEL PLAN | courtyard level',30)
 c.text((45,68),'Library returns to the villa; Cottage 01 is entirely private and extends to the right edge of the service building.',19)
 fs=[f for f in l.FLOORS if f['z']==40]
 # Paint site first, then rooms, so circulation rectangles never hide the buildings.
 fs=sorted(fs,key=lambda f:f['id']!='site')
 pt=panel(c,fs,(0,5,128,85),(55,115),11.3)
 c.rect((*pt(66,64),*pt(88,76)),'#75b8c5','#427d89',2)
 c.text(pt(77,70),'POOL · 22 × 12',18,center=True)
 routes=[[(51,55),(51,43),(43.5,43),(35,43),(35,40)],
         [(51,43),(76,43),(76,57.5),(96.5,57.5),(120,57.5),(120,54)],
         [(35,40),(35,28),(59,28),(62,28),(62,22)],
         [(35,40),(35,42),(17,42),(17,40)],
         [(76,57.5),(62,60),(62,78),(91,78),(91,60),(76,60)]]
 for path in routes:c.line([pt(*p) for p in path],'#347e9b',3)
 # Private cottage approach is a different color from public through-routes.
 c.line([pt(*p) for p in [(76,43),(81,43),(81,38),(89,38),(89,33),(90,33),(90,28)]],'#a66e41',3)
 c.line([pt(127,8),pt(127,78)],'#a66e41',2)
 c.text((45,1080),'Cottage: 44 × 28 studs. Both right-hand exterior walls align at x = 126; roof eaves also align.',18)
 c.text((45,1110),'Blue routes: public access. Brown route: private cottage access. Green wall gaps: doors. Blue inserts: windows.',18)
 c.text((45,1144),'The cottage foyer and private garden remain. The shared promenade reaches services without crossing either.',18)
 c.text((45,1178),'Pool deck: 7 studs clear at both sides; 9.5 behind and 11 in front, between coping and guards.',18)
 c.text((45,1212),'Loungers occupy the front band; a 4.5-stud strip between coping and loungers stays clear.',18)
 c.text((45,1256),'Architectural proxy plan · not LEGO connection verification or real-building certification',16,'#77756d')
 c.save('plan-arrival')
 c=Canvas(1340,1150)
 c.text((45,28),'MAIN VILLA | guest floor',30)
 c.text((45,71),'Identical layout at +54 and +68: rooms 101–103 / 201–203. Six rooms total.',19)
 panel(c,[f for f in l.FLOORS if f['id']=='main-1'],(18,8,62,50),(80,130),19)
 c.text((45,1050),'Two rooms in the long arm: one with a balcony, one without. The extended suite has its own balcony.',18)
 c.text((45,1088),'Each room has its own corridor door and bathroom. The stair core has an actual opening in the floor.',18)
 c.save('plan-guest-floor')
 c=Canvas(1740,1030)
 c.text((40,25),'SERVICE BUILDING | three connected levels',30)
 c.text((40,66),'Public stairs open onto shared corridors. Guests do not pass through kitchens or treatment rooms.',19)
 for i,(key,title) in enumerate([('dining','+40 · Dining / pool bar'),('salon','+26 · Salon / lounge'),('spa','+12 · Spa / changing')]):
  c.text((45+i*575,128),title,24)
  panel(c,[f for f in l.FLOORS if f['id']==key],(95,39,32,44),(45+i*575,184),16)
 c.text((40,930),'Service floors align vertically. Stair cores stay in the same position on every floor.',19)
 c.text((40,966),'Donor-inspired furniture envelopes: dining tables, kitchen island, two styling chairs and one wash station.',18)
 c.save('plan-services')
 meta=dict(layout_sha256=hashlib.sha256((HERE/'layout.py').read_bytes()).hexdigest(),
           drawings={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob('plan-*.*')) if p.suffix in ('.svg','.png')})
 (HERE/'plans-provenance.json').write_text(json.dumps(meta,indent=2)+'\n')
 print('Saved 3 native SVG + PNG floor-plan sheets')
if __name__=='__main__':draw()
