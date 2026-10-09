# cell: right_ear
# cell: right_ear
# cell: right_ear
# cell: right_ear

right_ear_width=param("right_ear_width",26.0)
right_ear_height=param("right_ear_height",25.0)
right_ear_depth=param("right_ear_depth",8.0)
right_ear_tip_shift=param("right_ear_tip_shift",9.0)
right_ear_rim=param("right_ear_rim",3.0)
right_ear_recess_depth=param("right_ear_recess_depth",2.5)
right_ear_rounding=param("right_ear_rounding",2.5)
right_ear_bulge=param("right_ear_bulge",2.0)
right_ear_root_drop=param("right_ear_root_drop",0.8)
right_ear_scale=param("right_ear_scale",1.1)
size_scale=right_ear_scale
root_drop=right_ear_root_drop*size_scale
w=right_ear_width*size_scale
h=right_ear_height*size_scale
d=right_ear_depth*size_scale
tip=right_ear_tip_shift*size_scale
# Outline landmarks transcribed from headset_photo, normalized to an 82 mm head:
# inner root ~X19,Z134; tip ~X39,Z146; outer flank ~X43,Z133; outer root ~X41,Z121.
edges=[
 Bezier((-w*.42,h*.5-root_drop),(-w*.25,h*.82),(tip-w*.15,h*.98),(tip,h)),
 Bezier((tip,h),(tip+right_ear_rounding*size_scale*1.5,h*1.015),(w*.56,h*.77),(w/2+right_ear_bulge*size_scale*.45,h*.44)),
 Bezier((w/2+right_ear_bulge*size_scale*.45,h*.44),(w/2+right_ear_bulge*size_scale*.45+(w/2+right_ear_bulge*size_scale*.45-w*.56)*.55,h*.44+(h*.44-h*.77)*.55),(w*.48,h*.02-root_drop),(w*.42,-h*.05-root_drop)),
 Bezier((w*.42,-h*.05-root_drop),(w*.42+(w*.42-w*.48)*1.6,-h*.05-root_drop+(-h*.05-h*.02)*1.6),(-w*.42-(-w*.25+w*.42)*.4,h*.5-root_drop-(h*.82-h*.5+root_drop)*.4),(-w*.42,h*.5-root_drop))]
outline=make_face(edges)
if 1<0:
    outline=mirror(outline,about=Plane.YZ)
# Rounded auricle, broad bowl tapering smoothly inward like the reference.
c=outline.center()
def ear_section(s):
    return Pos(c.X,c.Y,0)*((Pos(-c.X,-c.Y,0)*outline).scale(s))
right_ear_back_extension=param("right_ear_back_extension",1.3)
back_depth=d/2+right_ear_back_extension
right_ear_side_taper=param("right_ear_side_taper",0.08)
# Thicker front rim and a smoothly converging, domed rear surface.
outer_sections=[Pos(0,-d/2,0)*(Plane.XZ*ear_section(.94)),Pos(0,-d*.34,0)*(Plane.XZ*ear_section(.985)),Plane.XZ*outline]
from math import sqrt
for s in [.98,.93,.84,.7,.5,.25,.05,.015]:
    yy=back_depth*(1-s*s)**(.5+right_ear_side_taper)
    outer_sections.append(Pos(0,yy,0)*(Plane.XZ*ear_section(s)))
ear=loft(outer_sections)
right_ear_side_round=param("right_ear_side_round",0.65)
front_outer_edges=[e for e in ear.edges() if abs(e.center().Y+d/2)<1e-5]
assert len(front_outer_edges)>0
# Round the front outer perimeter before forming bowl and root seats.
ear=fillet(front_outer_edges,right_ear_side_round)

bowl_depth=right_ear_recess_depth*size_scale
opening_scale=1-1.5*right_ear_rim*size_scale/w
# Elliptic depth law prevents a ring-shaped depression or abrupt bottom.
from math import sqrt
bowl_sections=[Pos(0,-d/2-.8,0)*(Plane.XZ*ear_section(opening_scale))]
for s in [1,.985,.94,.86,.75,.6,.43,.25,.1,.025]:
    yy=-d/2+bowl_depth*sqrt(1-s*s)
    bowl_sections.append(Pos(0,yy,0)*(Plane.XZ*ear_section(opening_scale*s)))
recess=loft(bowl_sections)
right_ear_root_land=param("right_ear_root_land",1.2)
root_land=Pos(-30,30,-30.3)*extrude(Plane.XZ*Ellipse(55+right_ear_root_land*size_scale,47+right_ear_root_land*size_scale),amount=60)
recess=recess-root_land
ear=ear-recess
# Root seat follows the rounded headband in its assembled position.
from math import sin,cos,acos,sqrt
def tapered_band(a,b,top_t,end_t,width,end_h,edge,rise=0,end_w_ratio=1):
    limit=acos((end_h+rise)/b)
    sections=[]
    for i in range(41):
        theta=-limit+2*limit*i/40
        s=sin(theta); c=cos(theta)
        nx=s/a; nz=c/b
        norm=sqrt(nx*nx+nz*nz)
        nx/=norm; nz/=norm
        weight=((c-cos(limit))/(1-cos(limit)))**1.5
        thick=end_t+(top_t-end_t)*weight
        centre=(a*s+nx*thick/2,0,b*c-rise+nz*thick/2)
        plane=Plane(origin=centre,x_dir=(nx,0,nz),z_dir=(nz,0,-nx))
        section_width=width*(end_w_ratio+(1-end_w_ratio)*weight)
        section=plane*Ellipse(thick/2,section_width/2)
        sections.append(section)
    band=loft(sections)
    end_faces=band.faces().filter_by(GeomType.PLANE)
    end_edges=[e for f in end_faces for e in f.edges()]
    assert len(end_edges)==2, 'Expected two planar-cap terminal rims'
    band=fillet(end_edges,min(edge*.15,end_t*.08))
    return band

seat=tapered_band(47.8,36.3,7.8,4.14,14,5,1,-4.7,0.9)
ear=ear-Pos(-30,0,-30.3)*seat
ear=ear-Pos(-30,0,-30.3)*Sphere(41)
# Keep the upper connected ear after trimming its root to the band.
ear=max(ear.solids(),key=lambda s:s.volume)

ear.color=Color(.95,.95,.93)
publish("right_ear",ear,"右猫耳",material="petg")
