# cell: headband
# cell: headband
# cell: headband
# cell: headband
# cell: headband
headband_inner_radius=param("headband_inner_radius",41.0)
headband_thickness=param("headband_thickness",6.0)
headband_depth=param("headband_depth",14.0)
headband_end_height=param("headband_end_height",8.0)
headband_edge_radius=param("headband_edge_radius",1.0)
headband_side_spread=param("headband_side_spread",8.0)
headband_end_thickness=param("headband_end_thickness",2.0)
headband_arch_rise=param("headband_arch_rise",11.0)
headband_end_width_ratio=param("headband_end_width_ratio",0.9)
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

band=tapered_band(headband_inner_radius+headband_side_spread,headband_inner_radius+headband_arch_rise,headband_thickness,headband_end_thickness,headband_depth,headband_end_height,headband_edge_radius,headband_arch_rise,headband_end_width_ratio)
band.color=Color(.93,.93,.91)
publish("headband",band,"Headband",material="petg")
