"""Ordinary-stud hip approximations for the smaller hotel volumes."""
from engine import rect
def roof(m,name,x,y,w,d,base,courses):
    m.module=name;m.step=55;warm=[70,308];used=0
    ridge=rect(x+2*courses,y+2*courses,w-4*courses,d-4*courses)
    for c in range(courses):
        xx,yy=x+2*c,y+2*c;ww,dd=w-4*c,d-4*c;z=base+3*c
        for sx in range(xx,xx+ww,2):
            m.part('3039',70,sx,yy,z)
            m.part('3039',70,sx,yy+dd-2,z,angle=180);used+=2
        m.fill(rect(xx+2,yy+2,ww-4,dd-4),z,['brick'],[0,1,4,14,25,322,326,71,72],32)
        ends=rect(xx,yy+2,2,dd-4)|rect(xx+ww-2,yy+2,2,dd-4)
        for dz in (0,1):m.fill(ends,z+dz,['plate'],warm,16,color_first=True)
        m.fill(ends,z+2,['tile','plate'],warm,8,color_first=True)
    return dict(slope_count=used,hinges=False)
