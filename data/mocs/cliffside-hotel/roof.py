"""Pitched plate roofs using owned bar/clip hinges; actual rigid transforms.

Roof angle is a proposed 30 degrees. Physical hinge friction/load not tested.
Fixed bars face outward from the ridge and are staggered along X.
"""
import math
from engine import rect,transform,rotation

def multiply(a,b):return [sum(a[3*i+k]*b[3*k+j] for k in range(3)) for i in range(3) for j in range(3)]
def pitch(a):
 c=math.cos(math.radians(a));s=math.sin(math.radians(a));return [1,0,0,0,c,-s,0,s,c]

def roof(m,name,x,y,w,building_depth,base,step):
 oldmodule,oldstep=m.module,m.step;m.module=name;m.step=step
 center_y=y+building_depth/2;depth=6 if building_depth==12 else 4
 # Gable masonry under the sloping panels, stepped safely below their underside.
 heights=[1,2,4,5,7,8,8,7,5,4,2,1] if building_depth==12 else [3,4,6,8,8,6,4,3]
 for xx in (x,x+w-1):
  vox={(xx,yy,base+zz) for yy,h in zip(range(y,y+building_depth),heights) for zz in range(h)}
  m.volume(vox,[15,19],8)
 # Central ridge support: concealed under the roof.
 for zz in (0,3):m.part('3003',15,x+w//2-1,int(center_y)-1,base+zz)
 for zz in (6,7):m.part('3022',15,x+w//2-1,int(center_y)-1,base+zz)
 m.fill(rect(x,int(center_y)-1,w,2),base+8,['plate'],[0,72,15])
 fixed={}
 positions=([3,w-5],[5,w-3]) if w==16 else ([2,w-4],[4,w-2])
 for side in (0,1):
  for hx in positions[side]:
   # Handles face away from the ridge to clear the opposite skin and ridge plates.
   q=m.part('48336',0 if m.remaining.get(m.element('48336',0),0)>0 else 70,x+hx-1,center_y+(-1 if side==0 else 0),base+9,angle=0 if side==0 else 180)
   fixed[side,hx]=q
 # Ridge cover above hinge bodies. A four-stud cap covers the roof-panel gap.
 for zz in (10,11):m.fill(rect(x,int(center_y)-1,w,2),base+zz,['plate'],[0,72])
 m.fill(rect(x,int(center_y)-2,w,4),base+12,['plate'],[308,70])
 for side in (0,1):
  start=len(m.pieces)
  clips=[]
  for hx in positions[side]:
   local_x=w-hx if side==0 else hx
   q=m.part('60470b',0,local_x-1,0,-1);q['hinge_parent']=fixed[side,hx]['key'];clips.append((q,hx))
  # Overlapping underside braces tie both the skin's X and Z seams.
  for bx in ([1,w//2-1,w-3] if w==16 else [1,7]):
   m.fill(rect(bx,1,2,depth-1),-1,['plate'],[0,72],12)
  if building_depth==8:m.fill(rect(9,2,3,2),-1,['plate'],[0,72],6)
  m.fill(rect(0,0,w,depth),0,['plate'],[308,70],32)
  m.fill(rect(0,0,w,depth),1,['tile'],[308,70],8)
  R=multiply(pitch(30),rotation(180)) if side==0 else pitch(-30)
  clip,hx=clips[0];fixed_part=fixed[side,hx]
  local_pivot=[clip['origin'][0],2,-10]
  fixed_offset=transform(fixed_part['matrix'],[0,2,-20])
  world_pivot=[a+b for a,b in zip(fixed_part['origin'],fixed_offset)]
  rotated_pivot=transform(R,local_pivot);T=[a-b for a,b in zip(world_pivot,rotated_pivot)]
  for q in m.pieces[start:]:
   q['local_pose']={'origin':q['origin'][:],'matrix':q['matrix'][:],'x':q['x'],'y':q['y'],'z':q['z']}
   q['pose_type']='pitched_roof_panel';q['panel']=name+('-front' if side==0 else '-rear');q['panel_matrix']=R;q['panel_translation']=T
   q['origin']=[a+b for a,b in zip(transform(R,q['origin']),T)];q['matrix']=multiply(R,q['matrix'])
 m.module,m.step=oldmodule,oldstep
