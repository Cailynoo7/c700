# cell: boom
# cell: boom
# cell: boom

boom_diameter=param("boom_diameter",2.8)
boom_end_x=param("boom_end_x",-21.0)
boom_end_y=param("boom_end_y",-31.0)
boom_end_z=param("boom_end_z",-18.0)
boom_bend_x=param("boom_bend_x",-3.0)
boom_bend_drop=param("boom_bend_drop",13.0)
boom_root_inset=param("boom_root_inset",1.1813501915000082)
from math import cos,sin,radians
root_dx=-boom_root_inset*cos(radians(7))
root_dz=boom_root_inset*sin(radians(7))
boom_cup_tilt_delta=param("boom_cup_tilt_delta",3.0)
angle=radians(boom_cup_tilt_delta)
def lowered_point(x,y,z):
    wx=51+x
    wz=71+z-89
    return (cos(angle)*wx+sin(angle)*wz-51,y,89-sin(angle)*wx+cos(angle)*wz-71)
root=lowered_point(root_dx,0,root_dz)
bend=lowered_point(boom_bend_x+root_dx,-10,-boom_bend_drop+root_dz)
path=Bezier(root,bend,(boom_end_x*.55,boom_end_y*.88,boom_end_z),(boom_end_x,boom_end_y,boom_end_z))
section=Plane(origin=root,z_dir=path.tangent_at(0))*Circle(boom_diameter/2)
rod=sweep(section,path)
rod.color=Color(.74,.76,.74)
publish("boom",rod,"弯曲麦杆",material="petg")
