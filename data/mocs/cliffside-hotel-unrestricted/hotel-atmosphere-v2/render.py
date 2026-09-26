#!/usr/bin/env python3
"""Render authored massing geometry, with no generated-image substitution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
from PIL import Image
import mitsuba as mi

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('mesh_utils',HERE.parents[1]/'fern-and-steam-v2/render_model.py')
util=importlib.util.module_from_spec(spec)
spec.loader.exec_module(util)


def render(view, samples, width, model):
    mi.set_variant('scalar_rgb')
    T=mi.ScalarTransform4f
    src=HERE/(model+'.ldr')
    groups=util.Library(Path('/Applications/Studio 2.0/ldraw')).parse(src.read_text())
    folder=Path('/private/tmp/hotel-composition-mesh')/(hashlib.sha256(src.read_bytes()).hexdigest()[:12]+'-'+view)
    folder.mkdir(parents=True,exist_ok=True)
    meshes={}
    all_points=[]
    for color,tris in groups.items():
        tris=(tris*np.array([.05,-.05,.05]))[:,[0,2,1]]
        all_points.append(tris.reshape(-1,3))
        p=folder/f'{color}.ply'
        util.write_ply(p,tris)
        rgb=np.array([(color >> n)&255 for n in (16,8,0)])/255
        linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
        meshes[f'material_{color}']={'type':'ply','filename':str(p),'face_normals':True,
            'bsdf':{'type':'twosided','nested':{'type':'diffuse',
                'reflectance':{'type':'rgb','value':linear.tolist()}}}}
    points=np.concatenate(all_points)
    lo,hi=points.min(0),points.max(0)
    center=(lo+hi)/2
    directions={'concept':[-.72,.66,1.0],'front':[0,.28,1],
                'rear':[.72,.66,-1],'plan':[0,1,.0001],'villa':[.8,.48,1]}
    direction=np.array(directions[view],dtype=float)
    direction/=np.linalg.norm(direction)
    right=np.cross(direction,[0,1,0]);right/=np.linalg.norm(right)
    up=np.cross(right,direction)
    projected_x=(points-center)@right
    projected_y=(points-center)@up
    # Fit actual silhouette, not a bounding box containing empty roof corners.
    center+=right*(projected_x.min()+projected_x.max())/2
    center+=up*(projected_y.min()+projected_y.max())/2
    aspect=1.06 if view!='plan' else 1.10
    half_w=max(np.ptp(projected_x)/2,np.ptp(projected_y)/2*aspect)*1.09
    origin=center+direction*450
    scene={'type':'scene','integrator':{'type':'path','max_depth':10,'hide_emitters':True},
        'sensor':{'type':'orthographic',
            'to_world':T().look_at(origin=origin.tolist(),target=center.tolist(),up=[0,1,0])@T().scale([half_w,half_w,1]),
            'sampler':{'type':'independent','sample_count':samples},
            'film':{'type':'hdrfilm','width':width,'height':round(width/aspect),
                'rfilter':{'type':'tent'},'pixel_format':'rgb'}},
        'environment':{'type':'constant','radiance':{'type':'rgb','value':[.38,.38,.38]}},
        'floor':{'type':'rectangle','to_world':T().translate([48,float(lo[1])-.05,44])@T().rotate([1,0,0],-90)@T().scale(500),
            'bsdf':{'type':'diffuse','reflectance':{'type':'rgb','value':[.78,.76,.72]}}},**meshes}
    for name,pos,power,size in [('key',[-70,180,90],[6,5.7,5.2],65),
                              ('fill',[140,110,90],[2.3,2.4,2.6],60),
                              ('rim',[40,150,-80],[3,2.9,2.7],50)]:
        scene[name]={'type':'rectangle','to_world':T().look_at(origin=pos,target=center.tolist(),up=[0,1,0])@T().scale(size),
            'emitter':{'type':'area','radiance':{'type':'rgb','value':power}}}
    print(f'Rendering {view} at {width}px / {samples} spp',flush=True)
    a=np.maximum(0,np.array(mi.render(mi.load_dict(scene),seed=42)))
    a=a/(1+.2*a)
    a=np.where(a<=.0031308,a*12.92,1.055*a**(1/2.4)-.055)
    out=HERE/f'{model}-{view}.png'
    Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(out)
    meta={'view':view,'model_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
          'render_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
          'generator_sha256':hashlib.sha256((HERE/'build.py').read_bytes()).hexdigest(),
          'renderer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'camera_direction':direction.tolist(),'samples':samples,'seed':42,
          'layout_sha256':hashlib.sha256((HERE/'layout.py').read_bytes()).hexdigest(),
          'geometry_sha256':hashlib.sha256((HERE/'geometry.py').read_bytes()).hexdigest(),
          'exterior_sha256':hashlib.sha256((HERE/'exterior.py').read_bytes()).hexdigest(),
          'annex_exterior_sha256':hashlib.sha256((HERE/'annex_exterior.py').read_bytes()).hexdigest(),
          'atmosphere_sha256':hashlib.sha256((HERE/'atmosphere.py').read_bytes()).hexdigest(),
          'status':'proxy geometry; not a LEGO parts model'}
    out.with_suffix('.render.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(out,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--view',choices=['concept','front','rear','plan','villa'],default='concept')
    p.add_argument('--samples',type=int,default=64)
    p.add_argument('--width',type=int,default=1440)
    p.add_argument('--model',default='blockout')
    a=p.parse_args()
    render(a.view,a.samples,a.width,a.model)
