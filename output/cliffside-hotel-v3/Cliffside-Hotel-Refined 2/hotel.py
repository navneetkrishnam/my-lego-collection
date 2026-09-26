"""Refine the checked architecture's roofs, terrain and circulation."""
from pathlib import Path
from baseline import author as previous_author
from facade import export
from site_refined import build as site
from roof_wings import roof as wing_roof
from engine import rect
HERE=Path(__file__).resolve().parent

def author():
    m,_=previous_author()
    replaced={'site-foundation','terrace-supports','broad-staircase','layered-rock','terrace-deck','pool','waterfront','main-roof','guest-wing-roof','connector-roof'}
    for q in m.pieces[:]:
        if q['module'] in replaced:m.pieces.remove(q);m.remaining[q['element']]+=1
        else:
            q['origin'][1]-=144
            if not q.get('pose_type') and q['kind']!='insert':q['z']+=18
    from roof_refined import roof
    for name,x,y,z in [('guest-wing-roof',45,15,97),('connector-roof',32,7,71)]:
        m.module=name;m.step=55
        m.fill(rect(x,y,4,2),z,['tile'],[70,308],8,color_first=True)
    report=roof(m,x=3,y=3,w=26,d=16,base=111)
    m.module='guest-roof-cornice';m.step=50
    for q in m.pieces[:]:
        if q['module']=='guest-wing-floor' and q['z']==87:m.pieces.remove(q);m.remaining[q['element']]+=1
    m.fill(rect(39,9,16,14),87,['plate'],[15],32)
    wing_roof(m,'guest-wing-roof',39,9,16,14,88,3)
    m.module='connector-roof-cornice';m.step=50
    for q in m.pieces[:]:
        if q['module']=='connector-floor' and q['z']==64:m.pieces.remove(q);m.remaining[q['element']]+=1
    m.fill(rect(28,3,12,10),64,['plate'],[15],32)
    wing_roof(m,'connector-roof',28,3,12,10,65,2)
    report['site']=site(m)
    m.pieces.sort(key=lambda q:(q['step'],q['key']))
    return m,report

if __name__=='__main__':
    m,report=author();export(m,report,stem='hotel',title=f'Cliffside Hotel — {len(m.pieces):,}-piece refined coastal draft')
