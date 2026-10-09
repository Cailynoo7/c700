
# User supplied C700 nominal dimensions; all unmeasured details are photo estimates.
camera_width = param("camera_width",82.0)
camera_height = param("camera_height",130.0)
camera_head_diameter = param("camera_head_diameter",82.0)
camera_head_join_z = param("camera_head_join_z",57.0)
head_z = camera_height-camera_head_diameter/2
base_waist_radius = param("camera_base_waist_radius",27.0)
base_shoulder_z = param("camera_base_shoulder_z",43.0)
base_bottom_lip = param("camera_base_bottom_lip",2.0)
with BuildPart() as base_builder:
    with BuildSketch(Plane.XZ):
        with BuildLine():
            Polyline((0,base_bottom_lip),(camera_width/2-1,base_bottom_lip))
            ThreePointArc((camera_width/2-1,base_bottom_lip),(camera_width/2-.25,base_bottom_lip+.4),(camera_width/2,base_bottom_lip+1))
            Polyline((camera_width/2,base_bottom_lip+1),(camera_width/2,base_shoulder_z*.56))
            Bezier((camera_width/2,base_shoulder_z*.56),(camera_width/2,base_shoulder_z),(camera_width*.41,camera_head_join_z-3),(base_waist_radius,camera_head_join_z))
            Polyline((base_waist_radius,camera_head_join_z),(0,camera_head_join_z),(0,base_bottom_lip))
        make_face()
    revolve(axis=Axis.Z)
base=base_builder.part
base.color=Color(.94,.94,.92)
publish("camera_base",base,"C700 底座",material="abs")
foot_diameter=param("camera_foot_diameter",80.0)
foot_height=param("camera_foot_height",2.0)
foot=Cylinder(foot_diameter/2,foot_height,align=(Align.CENTER,Align.CENTER,Align.MIN))
foot.color=Color(.69,.69,.68)
publish("camera_foot",foot,"底部圆盘",material="abs")
window_width=param("camera_window_width",39.0)
window_height=param("camera_window_height",65.0)
window_center_z=param("camera_window_center_z",92.0)
window_depth=param("camera_window_depth",18.0)
# Capsule sketch in XZ, extruded toward camera front (-Y).
capsule=RectangleRounded(window_width,window_height,window_width/2-.01)
prism=extrude(Plane.XZ*capsule,amount=window_depth)
prism=Pos(0,-25,window_center_z)*prism
ball=Pos(0,0,head_z)*Sphere(camera_head_diameter/2)
ball=ball & Pos(0,0,(camera_head_join_z+camera_height)/2)*Box(camera_width+2,camera_width+2,camera_height-camera_head_join_z)
lens_diameter=param("camera_lens_disk_diameter",34.0)
lens_depth=param("camera_lens_disk_depth",5.0)
lens_center_z=param("camera_lens_center_z",89.0)
lens_front_y=param("camera_lens_front_y",-40.5)
disk=Pos(0,lens_front_y+lens_depth/2,lens_center_z)*Rot(90,0,0)*Cylinder(lens_diameter/2,lens_depth)
glass_diameter=param("camera_glass_diameter",10.0)
glass_thickness=param("camera_glass_thickness",.5)
glass_y=param("camera_glass_front_y",-41.0)
glass=Pos(0,glass_y+glass_thickness/2,lens_center_z)*Rot(90,0,0)*Cylinder(glass_diameter/2,glass_thickness)
head=ball-prism-disk-glass
head.color=Color(.96,.96,.94)
publish("camera_head",head,"82 mm 球头",material="abs")
window=ball & prism
window=window-disk-glass
window.color=Color(.08,.085,.09)
publish("camera_window",window,"黑色镜头窗口",material="abs")
ring_od=param("camera_ring_outer_diameter",17.5)
ring_id=param("camera_ring_inner_diameter",14.6)
ring_depth=param("camera_ring_depth",1.0)
ring_y=param("camera_ring_front_y",-41.0)
ring=Pos(0,ring_y+ring_depth/2,lens_center_z)*Rot(90,0,0)*(Cylinder(ring_od/2,ring_depth)-Cylinder(ring_id/2,ring_depth+2))
lens_disk=disk-ring-glass
lens_disk.color=Color(.045,.048,.052)
publish("camera_lens_disk",lens_disk,"镜头转盘",material="abs")
ring.color=Color(.68,.53,.29)
publish("camera_lens_ring",ring,"金色镜头圈",material="brass")

# glass lies in the front recess in the lens disk.
lens_disk2=lens_disk # already separate from glass at a flush face
glass.color=Color(.055,.07,.1)
publish("camera_glass",glass,"镜头玻璃",material="glass")
