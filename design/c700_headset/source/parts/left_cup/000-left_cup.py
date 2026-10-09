# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup
# cell: left_cup

left_cup_diameter=param("left_cup_diameter",36.0)
left_cup_pad_thickness=param("left_cup_pad_thickness",6.0)
left_cup_shell_thickness=param("left_cup_shell_thickness",7.0)
left_cup_rounding=param("left_cup_rounding",2.0)
left_cup_clearance=param("left_cup_clearance",1.2)
left_cup_tilt_deg=param("left_cup_tilt_deg",-8.0)
left_cup_shell_cap_depth=param("left_cup_shell_cap_depth",2.6)
left_cup_shell_cap_margin=param("left_cup_shell_cap_margin",9.0)
depth=left_cup_diameter
height=depth
p=left_cup_pad_thickness
t=left_cup_shell_thickness
# User side-centre alignment. Local origin is assembled at X=+/-36,Y=0,Z=89.
# 41 mm sphere radius comes from the user-specified 82 mm camera head.
head_centre=Pos(-36,0,0)
r=41+left_cup_clearance
left_cup_axial_ratio=param("left_cup_axial_ratio",0.9)
# Axial compression about the unchanged radius-41 head pole (local X=5).
axial_ratio=left_cup_axial_ratio
compression=Matrix([[axial_ratio,0,0,5*(1-axial_ratio)],[0,1,0,0],[0,0,1,0]])
from math import sqrt
# Revolved meridian gives concentric spherical faces and a rounded circular lip.
def curved_disc(ri,ro,q,lip,soft=False,contact_q=None):
    lip=min(lip,(ro-ri)*(.5 if soft else .3),q*(.24 if soft else .15))
    v=q-lip
    vi=v if contact_q is None else contact_q
    def x(rad,y):
        return sqrt(rad*rad-y*y)-36
    k=lip*(4/3 if soft else 1.3)
    # Matching end tangents avoid a crease at the spherical face / rounded rim junction.
    rim=make_face([
      ThreePointArc((ri-36,0),(x(ri,vi*.5),vi*.5),(x(ri,vi),vi)),
      Bezier((x(ri,vi),vi),(x(ri,vi)-k*vi/sqrt(ri*ri-vi*vi),vi+k),(x(ro,v)-k*v/sqrt(ro*ro-v*v),v+k),(x(ro,v),v)),
      ThreePointArc((x(ro,v),v),(x(ro,v*.5),v*.5),(ro-36,0)),
      Line((ro-36,0),(ri-36,0))])
    return revolve(rim,axis=Axis.X)
left_cup_pad_diameter=param("left_cup_pad_diameter",42.0)
left_cup_shell_taper=param("left_cup_shell_taper",4.0)
left_cup_pad_roll=param("left_cup_pad_roll",3.2)
left_cup_pad_contact_diameter=param("left_cup_pad_contact_diameter",32.04)
# The sphere-facing face was 35.6 mm after the rolled edge in v8; reduce only that face by 10%.
left_cup_pad_inward_extension=param("left_cup_pad_inward_extension",2.5)
# Add foam toward the head, then subtract the exact 82 mm head sphere.
# Reference camera_head is a radius-41 sphere in this region; its lower trim is below the pad.
raw_pad=curved_disc(r-left_cup_pad_inward_extension,r+p,left_cup_pad_diameter/2,left_cup_pad_roll,soft=True,contact_q=left_cup_pad_contact_diameter/2)
raw_pad=raw_pad.transform_geometry(compression)
head_cutter=head_centre*Sphere(41)
pad=raw_pad-head_cutter
assert len(pad.solids())==1

print("contact_face_diameter",left_cup_pad_contact_diameter)
# Two tapered axial stages, with rounded perimeter edges.
base_d=depth-1
end_d=base_d-left_cup_shell_taper
face_x=r+p-36
start_x=sqrt((r+p)**2-(base_d/2)**2)-36-.2
body=loft([Pos(start_x,0,0)*(Plane.YZ*Circle(base_d/2)),Pos(face_x+t,0,0)*(Plane.YZ*Circle(end_d/2))],ruled=True)
# The small stage starts at exactly the large stage's end radius and plane.
cap_d=end_d-2*left_cup_shell_cap_margin
left_cup_shell_dome_height=param("left_cup_shell_dome_height",1.0)
# Shallow spherical crown replaces the flat end, then the outside rim is blended.
crown_q=cap_d/2
rise=left_cup_shell_dome_height
assert 0<rise<crown_q
end_x=face_x+t+left_cup_shell_cap_depth
crown_R=(crown_q*crown_q+rise*rise)/(2*rise)
crown_c=end_x+rise-crown_R
crown=make_face([
 Line((face_x+t,0),(face_x+t,end_d/2)),
 Line((face_x+t,end_d/2),(end_x,crown_q)),
 ThreePointArc((end_x,crown_q),(crown_c+sqrt(crown_R*crown_R-(crown_q*.5)**2),crown_q*.5),(end_x+rise,0)),
 Line((end_x+rise,0),(face_x+t,0))])
cap=revolve(crown,axis=Axis.X)
shell=body+cap
join_edges=[e for e in shell.edges().filter_by(GeomType.CIRCLE) if abs(e.center().X-(face_x+t))<.001]
assert len(join_edges)==1, "Expected one continuous stage junction"
left_cup_shell_join_radius=param("left_cup_shell_join_radius",1.3)
shell=fillet(join_edges,left_cup_shell_join_radius)
left_cup_shell_outer_radius=param("left_cup_shell_outer_radius",1.0)
outer_edges=[e for e in shell.edges().filter_by(GeomType.CIRCLE) if abs(e.center().X-(face_x+t+left_cup_shell_cap_depth))<.001]
assert len(outer_edges)==1, "Expected one outside rim"
shell=fillet(outer_edges,left_cup_shell_outer_radius)
print("stage_length",face_x+t-start_x,"taper_slope",(base_d-end_d)/(2*(face_x+t-start_x)),"cap_depth",left_cup_shell_cap_depth,"join_radius",left_cup_shell_join_radius)
before_axial=shell.bounding_box().size.X
shell=shell.transform_geometry(compression)
assert abs(shell.bounding_box().size.X/before_axial-axial_ratio)<0.00001
print('shell_axial_ratio',shell.bounding_box().size.X/before_axial)
shell=shell-pad
# Rotate about the camera sphere centre, then place on the corresponding lowered radial axis.
tilt=Rot(0,left_cup_tilt_deg,0)
pad=tilt*pad
shell=tilt*shell
# Seat follows the v14 headband's varying rounded section.
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
band_solid=seat
band_solid=Pos(-35.45307910843949,0,6.251334396009497)*band_solid
shell=shell-band_solid
pad=pad-band_solid
shell.color=Color(.94,.94,.92)
pad.color=Color(.74,.75,.73)
publish("left_cup_shell",shell,"左耳罩外壳",material="petg")
publish("left_cup_pad",pad,"左耳罩软垫",material="tpu")
