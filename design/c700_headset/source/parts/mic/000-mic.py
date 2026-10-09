# cell: mic

mic_width=param("mic_width",18.0)
mic_height=param("mic_height",14.0)
mic_depth=param("mic_depth",14.0)
# Rounded capsule along local X; spherical ends meet a short cylindrical middle.
capsule_radius=mic_height/2
capsule_middle=mic_width-mic_height
assert capsule_middle>0
left_tip=(-mic_width/2,0,0)
left_shoulder=(-capsule_middle/2,capsule_radius,0)
right_shoulder=(capsule_middle/2,capsule_radius,0)
right_tip=(mic_width/2,0,0)
q=2**-0.5
profile=Wire([ThreePointArc(left_tip,(-capsule_middle/2-capsule_radius*q,capsule_radius*q,0),left_shoulder),Line(left_shoulder,right_shoulder),ThreePointArc(right_shoulder,(capsule_middle/2+capsule_radius*q,capsule_radius*q,0),right_tip),Line(right_tip,left_tip)])
mic=revolve(Face(profile),axis=Axis.X)
if abs(mic_depth-mic_height)>1e-8:
    mic=mic.transform_geometry(Matrix([[1,0,0,0],[0,mic_depth/mic_height,0,0],[0,0,1,0],[0,0,0,1]]))
assert len(mic.solids())==1
capsule_reference=mic
# Blind decorative rod seat. Source dimensions match the boom photo reconstruction.
# Matches the cup-compressed boom root; mic position and end tangent stay fixed.
# Matches the lowered boom; mic end remains fixed.
rod_path=Bezier((22.82465623249861,42,19.56067391396799),(19.14840019707662,32,6.735497830887368),(11.25,5.039999999999999,0),(0,0,0))
seat=sweep(Plane(origin=(22.82465623249861,42,19.56067391396799),z_dir=rod_path.tangent_at(0))*Circle(param("mic_rod_seat_diameter",3.0)/2),rod_path)
# Align to the exposed ferrule instead of the buried boom endpoint.
mic_collar_distance=param("mic_collar_distance",10.1)
collar_t=1-mic_collar_distance/rod_path.length
collar_centre=rod_path.position_at(collar_t)
collar_axis=rod_path.tangent_at(collar_t)

from math import atan2,degrees
mic_volume_ratio=param("mic_volume_ratio",0.9)
end_direction=collar_axis
# Project capsule centre onto the ferrule centreline for exact coaxial alignment.
body_offset=collar_centre-collar_axis*collar_centre.dot(collar_axis)
body_frame=Plane(origin=body_offset,x_dir=collar_axis,z_dir=Vector(0,1,0).cross(collar_axis))
assert abs(abs(body_frame.x_dir.dot(collar_axis))-1)<1e-9
axis_angle=degrees(atan2(end_direction.Y,end_direction.X))
reference_volume=(capsule_reference-seat).volume
target_volume=reference_volume*mic_volume_ratio
scale_factor=mic_volume_ratio**(1/3)
for _ in range(6):
    mic_outer=body_frame*capsule_reference.scale(scale_factor)
    mic=mic_outer-seat
    scale_factor*= (target_volume/mic.volume)**(1/3)
mic_outer=body_frame*capsule_reference.scale(scale_factor)
mic=mic_outer-seat
assert len(mic.solids())==1
assert abs(mic.volume/reference_volume-mic_volume_ratio)<1e-5
print("Mic axis angle degrees:",axis_angle,"linear scale:",scale_factor,"before volume mm3:",reference_volume,"after volume mm3:",mic.volume,"volume ratio:",mic.volume/reference_volume)
mic.color=Color(.06,.06,.065)
publish("mic",mic,"黑色麦克风头",material="rubber")

# Short cylindrical ferrule at the foam boundary, centred on the actual rod.
mic_collar_diameter=param("mic_collar_diameter",3.9)
mic_collar_length=param("mic_collar_length",4.2)
mic_collar_rounding=param("mic_collar_rounding",0.25)
mic_collar=Plane(origin=collar_centre,z_dir=collar_axis)*Cylinder(mic_collar_diameter/2,mic_collar_length)
mic_collar=fillet(mic_collar.edges().filter_by(GeomType.CIRCLE),mic_collar_rounding)
mic_collar=mic_collar-seat-mic_outer
assert len(mic_collar.solids())==1
mic_collar.color=Color(.68,.7,.69)
publish("mic_collar",mic_collar,"麦头圆柱套筒",material="petg")
