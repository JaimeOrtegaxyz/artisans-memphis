"""Rebuild with Blender 4.3+: blender -b --python build_memphis.py"""
import bpy, bmesh, math, random, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(ROOT,'output'); os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection': bpy.data.collections.remove(c)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=.001
scene.unit_settings.length_unit='MILLIMETERS'

# Match the plain deck to a near-10 mm Cherry R1 height target.
# Keep the physical switch seat fixed; do NOT count decorative relief as base height.
SKIRT_BOTTOM=.25
SHELL_HEIGHT=9.8
DECK_Z=SKIRT_BOTTOM+SHELL_HEIGHT
SOCKET_BOTTOM=.4
SOCKET_SEAT_Z=5.1
WALL_DRAFT=math.degrees(math.atan(1.2/(DECK_Z-.35-.7)))
scene['shell_height_mm']=SHELL_HEIGHT
scene['deck_z_mm']=DECK_Z
scene['wall_draft_deg']=WALL_DRAFT
scene['height_reference']='9.8 mm plain deck target, informed by GMK-based KeyV2 Cherry R1 and owner measurement; not a certified Cherry specification.'

def collection(name):
    c=bpy.data.collections.new(name); scene.collection.children.link(c); return c
stage=collection('05 • Studio (hide for fabrication)')
cols=[collection(n) for n in ['01 • ARCH / porcelain + petrol','02 • ZIGZAG / ochre + violet','03 • DISC / ultramarine','04 • STAIRS / vermilion']]

def mat(name,color,rough=.25,coat=.3):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough; p.inputs['Coat Weight'].default_value=coat; p.inputs['Coat Roughness'].default_value=.2
    return m
cream=mat('01 | Warm porcelain resin',(.87,.81,.61)); teal=mat('02 | Petrol teal resin',(.006,.235,.195))
red=mat('03 | Vermilion resin',(.72,.043,.016)); yellow=mat('04 | Golden ochre resin',(.91,.53,.015))
blue=mat('05 | Ultramarine resin',(.014,.073,.53)); violet=mat('06 | Lilac resin',(.40,.25,.69))
black=mat('07 | Carbon black',(.009,.013,.017),.25,.4); ground=mat('Studio | chalk',(.22,.24,.27),.8,0)
black.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.35
for m in (cream,teal,red,yellow,blue,violet):
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Roughness'].default_value=.23; p.inputs['Coat Weight'].default_value=.42
    p.inputs['Coat Roughness'].default_value=.16

# Volumetric glaze pigmentation wraps continuously over the deck, bevels and sides.
# Unlike raised decals, these patches remain flush even on the tapered walls.
spotted=cream.copy(); spotted.name='08 | Dalmatian porcelain • continuous 3D stains'
nodes=spotted.node_tree.nodes; links=spotted.node_tree.links
tex=nodes.new('ShaderNodeTexCoord'); tex.location=(-900,0)
noise=nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=.8; noise.inputs['Detail'].default_value=1.3; noise.location=(-720,-160)
# Normalize pigment coordinates to a fixed texture-space height.
rescale=nodes.new('ShaderNodeVectorMath'); rescale.operation='MULTIPLY'; rescale.inputs[1].default_value=(1,1,8.75/SHELL_HEIGHT)
links.new(tex.outputs['Object'],rescale.inputs[0])
remap=nodes.new('ShaderNodeVectorMath'); remap.operation='ADD'; remap.inputs[1].default_value=(0,0,SKIRT_BOTTOM*(1-8.75/SHELL_HEIGHT))
links.new(rescale.outputs['Vector'],remap.inputs[0])
links.new(remap.outputs['Vector'],noise.inputs['Vector'])
warp=nodes.new('ShaderNodeVectorMath'); warp.operation='SCALE'; warp.inputs[3].default_value=1.5; warp.location=(-520,-160)
links.new(noise.outputs['Color'],warp.inputs[0])
add=nodes.new('ShaderNodeVectorMath'); add.operation='ADD'; add.location=(-330,0)
links.new(remap.outputs['Vector'],add.inputs[0]); links.new(warp.outputs['Vector'],add.inputs[1])
cells=nodes.new('ShaderNodeTexVoronoi'); cells.inputs['Scale'].default_value=.28; cells.location=(-150,0)
links.new(add.outputs['Vector'],cells.inputs['Vector'])
ramp=nodes.new('ShaderNodeValToRGB'); ramp.location=(50,0); ramp.color_ramp.interpolation='EASE'
ramp.color_ramp.elements[0].position=.275; ramp.color_ramp.elements[0].color=(.006,.008,.009,1)
ramp.color_ramp.elements[1].position=.292; ramp.color_ramp.elements[1].color=(*cream.diffuse_color[:3],1)
links.new(cells.outputs['Distance'],ramp.inputs['Fac'])
links.new(ramp.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])

current=cols[0]; origin=(0,0)
def finish(obj,name,material,bevel=0):
    obj.name=name
    for c in list(obj.users_collection): c.objects.unlink(obj)
    current.objects.link(obj)
    obj.location.x+=origin[0]; obj.location.y+=origin[1]
    if material: obj.data.materials.append(material)
    if bevel:
        mod=obj.modifiers.new('Soft molded edges','BEVEL'); mod.width=bevel; mod.segments=4
    for p in obj.data.polygons: p.use_smooth=True
    if obj.type=='MESH':
        mod=obj.modifiers.new('Face-weighted normals','WEIGHTED_NORMAL'); mod.keep_sharp=True; mod.weight=40
    return obj

def mesh(name,verts,faces,material,bevel=0):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); current.objects.link(ob)
    return finish(ob,name,material,bevel)

def prism(name,poly,z0,z1,material,bevel=.2):
    # Input polygon is counterclockwise.
    n=len(poly); vs=[(x,y,z) for z in (z0,z1) for x,y in poly]
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    fs += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vs,fs,material,bevel)

def cube(name,loc,scale,material,bevel=.2):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,material,bevel)

def cylinder(name,loc,r,depth,material,bevel=.15):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=r,depth=depth,location=loc)
    return finish(bpy.context.object,name,material,bevel)

def sphere(name,loc,r,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=r,location=loc)
    return finish(bpy.context.object,name,material)

def rounded_outline(poly,inset,radius,segments=8,balanced=False):
    """Offset a CCW outline, with tangent circular corners (including concave ones)."""
    out=[]
    for i,xy in enumerate(poly):
        p=Vector(xy); u=(p-Vector(poly[i-1])).normalized(); v=(Vector(poly[(i+1)%len(poly)])-p).normalized()
        turn=math.atan2(u.x*v.y-u.y*v.x,u.dot(v))
        if abs(turn)<1e-7: continue
        sign=1 if turn>0 else -1
        ni=Vector((-u.y,u.x)); no=Vector((-v.y,v.x))
        q=p+(ni+no)*(inset/(1+u.dot(v)))
        # Decouple plan corner radii from the shoulder roll so convex and concave
        # corners retain a consistent, blocky appearance.
        r=radius if balanced else radius-sign*inset
        tangent=r*math.tan(abs(turn)/2)
        start=q-u*tangent; center=start+ni*(sign*r)
        a=math.atan2(start.y-center.y,start.x-center.x)
        for j in range(segments+1):
            t=a+turn*j/segments
            out.append((center.x+r*math.cos(t),center.y+r*math.sin(t)))
    return out

def arch_outline(inset):
    # Concentric curved crown with 2.15 mm straight legs and rounded terminals.
    outer=7.0; inner=3.35; corner=.8; cy=-4.15; leg=2.15
    yo=cy-leg+corner; ro=outer-inset; ri=inner+inset
    r=corner-inset; pts=[]
    def arc(x,y,rad,a,b,count,skip=False):
        pts.extend((x+rad*math.cos(a+(b-a)*j/count),y+rad*math.sin(a+(b-a)*j/count)) for j in range(1 if skip else 0,count+1))
    arc(outer-corner,yo,r,-math.pi/2,0,12)
    pts.append((ro,cy))
    arc(0,cy,ro,0,math.pi,64,True)
    pts.append((-ro,yo))
    arc(-outer+corner,yo,r,math.pi,3*math.pi/2,12,True)
    arc(-inner-corner,yo,r,-math.pi/2,0,12)
    pts.append((-ri,cy))
    arc(0,cy,ri,math.pi,0,64,True)
    pts.append((ri,yo))
    arc(inner+corner,yo,r,math.pi,3*math.pi/2,12,True)
    return pts

def glazed_prism(name,poly,material,height=1.65,corner=.85,roll=.6,paired_cap=False,outline_fn=None,balanced=False):
    """Broad top roll plus a small outward foot: a glazed-on, rather than glued-on, edge."""
    top=DECK_Z+height
    profile=[(-.12,DECK_Z-.12),(-.12,DECK_Z-.02),(-.07,DECK_Z+.055),(-.025,DECK_Z+.13),(0,DECK_Z+.23),(0,top-roll)]
    for j in range(1,13):
        a=math.pi*j/24; profile.append((roll*(1-math.cos(a)),top-roll+roll*math.sin(a)))
    vs=[]
    for inset,z in profile:
        outline=outline_fn(inset) if outline_fn else rounded_outline(poly,inset,corner,balanced=balanced)
        vs.extend((x,y,z) for x,y in outline)
    n=len(vs)//len(profile)
    # The annular arch uses an explicit quad-strip cap, avoiding an ill-conditioned
    # concave n-gon tessellation across the opening.
    cap=[(j,j+1,n-2-j,n-1-j) for j in range(n//2-1)] if paired_cap else [tuple(range(n))]
    fs=[tuple(reversed(f)) for f in cap]
    for k in range(len(profile)-1):
        fs.extend((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for j in range(n))
    last=(len(profile)-1)*n
    fs.extend(tuple(last+j for j in f) for f in cap)
    ob=mesh(name,vs,fs,material)
    ob.modifiers.clear()
    for p in list(ob.data.polygons)[:len(cap)]+list(ob.data.polygons)[-len(cap):]: p.use_smooth=False
    ob['edge_treatment']=f'Explicit outline; {roll:.2f} mm shoulder roll; {corner:.2f} mm plan corners; balanced={balanced}; flared glazed foot'
    return ob

def hemisphere(name,x,y,r,material):
    n=96; vs=[]
    for j in range(25):
        a=(math.pi/2)*j/25
        vs.extend((x+r*math.cos(a)*math.cos(2*math.pi*k/n),y+r*math.cos(a)*math.sin(2*math.pi*k/n),DECK_Z+r*math.sin(a)) for k in range(n))
    fs=[tuple(reversed(range(n)))]
    for j in range(24): fs.extend((j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for k in range(n))
    pole=len(vs); vs.append((x,y,DECK_Z+r))
    fs.extend((24*n+k,24*n+(k+1)%n,pole) for k in range(n))
    ob=mesh(name,vs,fs,material); ob.modifiers.clear(); ob.data.polygons[0].use_smooth=False
    return ob

def rounded_ring(width,r,z):
    pts=[]
    for cx,cy,start in [(width/2-r,width/2-r,0),(-width/2+r,width/2-r,90),(-width/2+r,-width/2+r,180),(width/2-r,-width/2+r,270)]:
        for i in range(16):
            a=math.radians(start+i*90/16); pts.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
    return pts

def base(label,material):
    # Raise the roof/cavity ceiling together, maintaining the 1.85 mm roof.
    rings=[(14.7,1.05,SKIRT_BOTTOM),(13.5,1.3,DECK_Z-2.15),(13.1,1.4,DECK_Z-1.85),
           (15.0,1.65,DECK_Z),(15.6,1.75,DECK_Z-.35),(18,1.5,.7),(17.8,1.45,SKIRT_BOTTOM)]
    # Separate top exterior and cavity ceiling connected through walls, not through roof sides.
    order=[rings[i] for i in [2,1,0,6,5,4,3]]
    vs=sum([rounded_ring(*r) for r in order],[]); n=64
    fs=[tuple(reversed(range(n)))]
    for k in range(len(order)-1):
        fs += [(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for i in range(n)]
    fs.append(tuple(range((len(order)-1)*n,len(order)*n)))
    shell=mesh(label+' | hollow 1u shell',vs,fs,material,.16)
    boss_top=DECK_Z-1.8
    stem=cylinder(label+' | MX socket (prototype)',(0,0,(SOCKET_BOTTOM+boss_top)/2),2.8,boss_top-SOCKET_BOTTOM,material,.12)
    # Apply bevel before cross subtraction, leaving the nominal slot dimensions precise.
    bpy.context.view_layer.objects.active=stem
    for m in list(stem.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
    # A short 0.10 mm / 45-degree entry lead-in eases alignment without changing
    # the nominal 4.20 x 1.30 mm engagement section or the fixed seating depth.
    def plus(a,b):
        return [(-b,-a),(b,-a),(b,-b),(a,-b),(a,b),(b,b),(b,a),(-b,a),(-b,b),(-a,b),(-a,-b),(-b,-b)]
    cut_rings=[(-.2,2.20,.75),(SOCKET_BOTTOM,2.20,.75),(SOCKET_BOTTOM+.10,2.10,.65),(SOCKET_SEAT_Z,2.10,.65)]
    cv=[(x,y,z) for z,a,b in cut_rings for x,y in plus(a,b)]
    cf=[tuple(reversed(range(12))),tuple(range(36,48))]
    for k in range(3): cf.extend((k*12+j,k*12+(j+1)%12,(k+1)*12+(j+1)%12,(k+1)*12+j) for j in range(12))
    cut=mesh('temporary cross cutter',cv,cf,None)
    cut.modifiers.clear()
    mod=stem.modifiers.new('MX cross • 4.20 × 1.30 mm • depth 4.70','BOOLEAN'); mod.operation='DIFFERENCE'; mod.object=cut
    bpy.context.view_layer.objects.active=stem; bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(cut,do_unlink=True)
    stem.data.update()
    for p in stem.data.polygons:
        p.use_smooth=(abs(p.normal.z)<.5 and math.hypot(p.center.x,p.center.y)>2.6)
    stem['fit_note']='Nominal prototype only. Print fit coupon; compensate for resin shrinkage. Cross 4.20 x 1.30 mm.'
    stem['socket_bottom_z_mm']=SOCKET_BOTTOM; stem['socket_seat_z_mm']=SOCKET_SEAT_Z
    stem['entry_lead_in_mm']=.10
    # Four short, high-set radial buttresses spread loads from the mounting boss
    # into the roof and inner walls. Their sloped lower edges leave the lower
    # switch-housing cavity open. Keep editable overlaps for fabrication planning.
    profile=[(2.4,DECK_Z-4.0),(7.1,DECK_Z-2.35),(7.1,DECK_Z-1.7),(2.4,DECK_Z-1.7)]
    rv=[(x,y,z) for y in (-.55,.55) for x,z in profile]
    rf=[tuple(range(4)),tuple(reversed(range(4,8)))]
    rf.extend((j,j+4,(j+1)%4+4,(j+1)%4) for j in range(4))
    for angle,direction in [(0,'+X'),(math.pi/2,'+Y'),(math.pi,'-X'),(3*math.pi/2,'-Y')]:
        rib=mesh(label+' | roof buttress '+direction,rv,rf,material,.14)
        rib.rotation_euler.z=angle
        rib['engineering_note']='1.10 mm nominal rib; overlaps boss, roof and inner wall. Sloped underside; lowest Z=6.05 mm. Validate full switch travel before fabrication.'
    shell['shell_height_mm']=SHELL_HEIGHT; shell['deck_z_mm']=DECK_Z; shell['wall_draft_deg']=WALL_DRAFT
    shell['dimensions_mm']=f'18 x 18 skirt; 15 x 15 deck; physical base height {SHELL_HEIGHT} mm; deck Z={DECK_Z}; wall draft {WALL_DRAFT:.1f} degrees; 19.05 mm pitch; open underside'
    return shell

pitch=19.05
origins=[(-pitch/2,pitch/2),(pitch/2,pitch/2),(-pitch/2,-pitch/2),(pitch/2,-pitch/2)]
for i in range(4):
    current=cols[i]; origin=origins[i]; shell=base(['ARCH','ZIGZAG','DISC','STAIRS'][i],[cream,yellow,blue,red][i])
    if i==0:
        # Concentric semicircular crown with short straight legs.
        cy=-4.15; outer=7.0; inner=3.35
        poly=[(outer*math.cos(t*math.pi/64),cy+outer*math.sin(t*math.pi/64)) for t in range(65)]
        poly += [(inner*math.cos(t*math.pi/64),cy+inner*math.sin(t*math.pi/64)) for t in range(64,-1,-1)]
        glazed_prism('ARCH | concentric teal arch with short legs',poly,teal,height=1.6,corner=.8,roll=.6,paired_cap=True,outline_fn=arch_outline)
        hemisphere('ARCH | orange hemisphere',0,cy,2.5,red)
        shell.data.materials[0]=spotted; shell.data.materials.append(cream)
        # Keep the internal cavity and bottom lip clean porcelain; exterior stains
        # continue seamlessly over the top shoulder and tapered outer walls.
        for p in list(shell.data.polygons)[:193]: p.material_index=1
        shell['pigmentation']='Continuous object-space Dalmatian glaze on top AND exterior side walls; clean underside; not raised geometry'
        shell['arch_layout']='Arch and dome share center (0,-4.15) in plan. Inner R3.35, outer R7.0, dome R2.5: nominal radial gap .85 on curved crown, band width 3.65. Short legs 2.15 mm; terminals Y=-6.3.'
    elif i==1:
        # 2.85 mm beam with matched small inner/outer plan corners.
        poly=[(-6.65,4.3),(-3.8,4.3),(-3.8,.05),(-.15,.05),(-.15,-3.8),(4.7,-3.8),(4.7,-6.65),(-3,-6.65),(-3,-2.8),(-6.65,-2.8)]
        poly.reverse(); glazed_prism('ZIGZAG | low rounded black beam',poly,black,height=1.55,corner=.28,roll=.45,balanced=True)
        # Nominal sharp-corner-to-disc gap .96 mm, about one third of beam width.
        disc=[(3.45+3.45*math.cos(2*math.pi*k/96),2.6+3.45*math.sin(2*math.pi*k/96)) for k in range(96)]
        glazed_prism('ZIGZAG | lilac glazed cylinder',disc,violet,height=1.65,corner=.8,roll=.6)
    elif i==2:
        disc=[(-3.8+3.55*math.cos(2*math.pi*k/96),2.45+3.55*math.sin(2*math.pi*k/96)) for k in range(96)]
        glazed_prism('DISC | broad porcelain medallion',disc,cream,height=1.5,corner=.8,roll=.6)
        for j,y in enumerate([-.1,-2.95,-5.8]):
            # Buried lower half and generous radius produce almost half-cylinder rails.
            ob=cube('DISC | pill rail %d'%(j+1),(3.35,y,DECK_Z+.3),(8.3,2.35,2.35),black,1.12)
            ob.modifiers['Soft molded edges'].segments=10
    else:
        # Side-elevation icon, one flat top at a single Z, NOT a physical staircase.
        poly=[(-7.1,-7.1),(7.1,-7.1),(7.1,7.1),(3.55,7.1),(3.55,3.55),(0,3.55),(0,0),(-3.55,0),(-3.55,-3.55),(-7.1,-3.55)]
        poly=[(x*5.25/7.1,y*5.25/7.1) for x,y in poly]
        glazed_prism('STAIRS | planar lilac stair silhouette',poly,violet,height=1.65,corner=.28,roll=.45,balanced=True)

# Studio is separate from all fabrication geometry.
current=stage; origin=(0,0)
cube('Infinite matte backdrop',(0,0,-.65),(2000,2000,1.2),ground,.1)

def aim(o,target): o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size,color,target=(0,0,3)):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size; data.color=color
    o=bpy.data.objects.new(name,data); stage.objects.link(o); o.location=loc; aim(o,target)
# Blender units are mm, so compensate inverse-square light falloff.
area('Key • large silk',(-35,-25,65),26000,45,(1,.91,.79))
area('Fill • cool softbox',(45,-5,45),14000,35,(.78,.87,1))
area('Rim • strip',(0,45,55),28000,30,(1,1,1))
camdata=bpy.data.cameras.new('Camera'); cam=bpy.data.objects.new('Camera',camdata); stage.objects.link(cam)
cam.location=(32,-49,83); aim(cam,(0,0,5)); camdata.type='ORTHO'; camdata.ortho_scale=61; camdata.lens=55; scene.camera=cam
draft=os.environ.get('MEMPHIS_DRAFT')=='1'
scene.render.engine='CYCLES'; scene.cycles.samples=24 if draft else 64; scene.cycles.use_denoising=True
scene.world.color=(.25,.25,.25)
scene.render.resolution_x=900 if draft else 1600; scene.render.resolution_y=scene.render.resolution_x; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG'
# Useful opening view, cleanly framed without camera/light overlays.
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            a.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
            a.spaces.active.region_3d.view_distance=75
            a.spaces.active.region_3d.view_location=(0,0,5)
            a.spaces.active.clip_end=3000
            a.spaces.active.shading.type='MATERIAL'
            a.spaces.active.overlay.show_extras=False
# Do not publish local home directories saved by the default file-browser UI.
for screen in bpy.data.screens:
    for area in screen.areas:
        for space in area.spaces:
            if space.type=='FILE_BROWSER' and getattr(space,'params',None):
                space.params.directory=b'//'
bpy.ops.object.select_all(action='DESELECT')
scene['README']='MEMPHIS / four 1u resin artisan concepts. Model units mm. Separate editable colored parts; studio in collection 05. Prototype MX mounts, not validated for production. See MODEL_NOTES.md.'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Memphis_Artisans.blend'))
scene.render.filepath=os.path.join(OUT,'Memphis_Artisans.png'); bpy.ops.render.render(write_still=True)
# Straight-on view makes silhouette, alignment and edge clearances easy to review.
cam.location=(0,0,100); aim(cam,(0,0,0)); camdata.ortho_scale=44
scene.render.resolution_x=900 if draft else 1200; scene.render.resolution_y=scene.render.resolution_x
scene.cycles.samples=16 if draft else 40
scene.render.filepath=os.path.join(OUT,'Memphis_Top.png'); bpy.ops.render.render(write_still=True)
# Second orthographic underside inspection, without changing the saved hero scene.
for ob in stage.objects:
    if ob.type=='MESH': ob.hide_render=True
cam.location=(28,-40,-65); aim(cam,(0,0,3)); camdata.ortho_scale=60
area('Underside inspection',(-20,-30,-50),26000,45,(1,1,1),target=(0,0,3))
scene.render.resolution_x=900 if draft else 1600; scene.render.resolution_y=scene.render.resolution_x; scene.cycles.samples=16 if draft else 64
scene.render.filepath=os.path.join(OUT,'Memphis_Underside.png'); bpy.ops.render.render(write_still=True)
print('MEMPHIS_COMPLETE')
