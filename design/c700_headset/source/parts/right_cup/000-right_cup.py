# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup
# cell: right_cup

right_cup_diameter=param("right_cup_diameter",36.0)
right_cup_pad_thickness=param("right_cup_pad_thickness",6.0)
right_cup_shell_thickness=param("right_cup_shell_thickness",7.0)
right_cup_rounding=param("right_cup_rounding",2.0)
right_cup_clearance=param("right_cup_clearance",1.2)
right_cup_tilt_deg=param("right_cup_tilt_deg",-8.0)
right_cup_shell_cap_depth=param("right_cup_shell_cap_depth",2.6)
right_cup_shell_cap_margin=param("right_cup_shell_cap_margin",9.0)
depth=right_cup_diameter
height=depth
p=right_cup_pad_thickness
t=right_cup_shell_thickness
# User side-centre alignment. Local origin is assembled at X=+/-36,Y=0,Z=89.
# 41 mm sphere radius comes from the user-specified 82 mm camera head.
head_centre=Pos(-36,0,0)
r=41+right_cup_clearance
right_cup_axial_ratio=param("right_cup_axial_ratio",0.9)
# Axial compression about the unchanged radius-41 head pole (local X=5).
axial_ratio=right_cup_axial_ratio
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
right_cup_pad_diameter=param("right_cup_pad_diameter",42.0)
right_cup_shell_taper=param("right_cup_shell_taper",4.0)
right_cup_pad_roll=param("right_cup_pad_roll",3.2)
right_cup_pad_contact_diameter=param("right_cup_pad_contact_diameter",32.04)
# The sphere-facing face was 35.6 mm after the rolled edge in v8; reduce only that face by 10%.
right_cup_pad_inward_extension=param("right_cup_pad_inward_extension",2.5)
# Add foam toward the head, then subtract the exact 82 mm head sphere.
# Reference camera_head is a radius-41 sphere in this region; its lower trim is below the pad.
raw_pad=curved_disc(r-right_cup_pad_inward_extension,r+p,right_cup_pad_diameter/2,right_cup_pad_roll,soft=True,contact_q=right_cup_pad_contact_diameter/2)
raw_pad=raw_pad.transform_geometry(compression)
head_cutter=head_centre*Sphere(41)
pad=raw_pad-head_cutter
assert len(pad.solids())==1

print("contact_face_diameter",right_cup_pad_contact_diameter)
# Two tapered axial stages, with rounded perimeter edges.
base_d=depth-1
end_d=base_d-right_cup_shell_taper
face_x=r+p-36
start_x=sqrt((r+p)**2-(base_d/2)**2)-36-.2
body=loft([Pos(start_x,0,0)*(Plane.YZ*Circle(base_d/2)),Pos(face_x+t,0,0)*(Plane.YZ*Circle(end_d/2))],ruled=True)
# The small stage starts at exactly the large stage's end radius and plane.
cap_d=end_d-2*right_cup_shell_cap_margin
right_cup_shell_dome_height=param("right_cup_shell_dome_height",1.0)
# Shallow spherical crown replaces the flat end, then the outside rim is blended.
crown_q=cap_d/2
rise=right_cup_shell_dome_height
assert 0<rise<crown_q
end_x=face_x+t+right_cup_shell_cap_depth
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
right_cup_shell_join_radius=param("right_cup_shell_join_radius",1.3)
shell=fillet(join_edges,right_cup_shell_join_radius)
right_cup_shell_outer_radius=param("right_cup_shell_outer_radius",1.0)
outer_edges=[e for e in shell.edges().filter_by(GeomType.CIRCLE) if abs(e.center().X-(face_x+t+right_cup_shell_cap_depth))<.001]
assert len(outer_edges)==1, "Expected one outside rim"
shell=fillet(outer_edges,right_cup_shell_outer_radius)
print("stage_length",face_x+t-start_x,"taper_slope",(base_d-end_d)/(2*(face_x+t-start_x)),"cap_depth",right_cup_shell_cap_depth,"join_radius",right_cup_shell_join_radius)
before_axial=shell.bounding_box().size.X
shell=shell.transform_geometry(compression)
assert abs(shell.bounding_box().size.X/before_axial-axial_ratio)<0.00001
print('shell_axial_ratio',shell.bounding_box().size.X/before_axial)
shell=shell-pad
# Rotate about the camera sphere centre, then place on the corresponding lowered radial axis.
tilt=Rot(0,right_cup_tilt_deg,0)
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
rod_seat_diameter=param("right_cup_rod_seat_diameter",3.0)
# Matches the lowered cup's rotated boom root; mic end remains fixed.
rod_path=Bezier((13.371577124059122,-7,-14.187991690022514),(9.69532108863713,-17,-27.013167773103135),(1.7969208915605108,-43.96,-33.7486656039905),(-9.45307910843949,-49,-33.7486656039905))
rod_seat=sweep(Plane(origin=(13.371577124059122,-7,-14.187991690022514),z_dir=rod_path.tangent_at(0))*Circle(rod_seat_diameter/2),rod_path)
shell=shell-rod_seat

# Decorative root socket: short rounded sleeve aligned with the boom exit.
right_cup_boom_joint_diameter=param("right_cup_boom_joint_diameter",4.8)
right_cup_boom_joint_length=param("right_cup_boom_joint_length",6.5)
right_cup_boom_joint_embed=param("right_cup_boom_joint_embed",1.2)
right_cup_boom_joint_rounding=param("right_cup_boom_joint_rounding",0.45)
root_axis=rod_path.tangent_at(0)
root_origin=rod_path.position_at(0)
joint_centre=root_origin+root_axis*(right_cup_boom_joint_length/2-right_cup_boom_joint_embed)
boom_root_joint=Plane(origin=joint_centre,z_dir=root_axis)*Cylinder(right_cup_boom_joint_diameter/2,right_cup_boom_joint_length)
boom_root_joint=fillet(boom_root_joint.edges().filter_by(GeomType.CIRCLE),right_cup_boom_joint_rounding)
boom_root_joint=boom_root_joint-rod_seat-shell-pad
assert len(boom_root_joint.solids())==1
boom_root_joint.color=Color(.86,.87,.85)
publish("boom_root_joint",boom_root_joint,"麦杆根部连接座",material="petg")
shell.color=Color(.94,.94,.92)
pad.color=Color(.74,.75,.73)
publish("right_cup_shell",shell,"右耳罩外壳",material="petg")
publish("right_cup_pad",pad,"右耳罩软垫",material="tpu")
