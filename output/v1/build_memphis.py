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

def collection(name):
    c=bpy.data.collections.new(name); scene.collection.children.link(c); return c
stage=collection('05 • Studio (hide for fabrication)')
cols=[collection(n) for n in ['01 • ARCH / porcelain + petrol','02 • ZIGZAG / ochre + violet','03 • DISC / ultramarine','04 • STAIRS / vermilion']]

def mat(name,color,rough=.25,coat=.3):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough; p.inputs['Coat Weight'].default_value=coat; p.inputs['Coat Roughness'].default_value=.2
    return m
cream=mat('01 | Warm porcelain resin',(.87,.81,.61)); teal=mat('02 | Petrol teal resin',(.009,.34,.30))
red=mat('03 | Vermilion resin',(.72,.043,.016)); yellow=mat('04 | Golden ochre resin',(.91,.53,.015))
blue=mat('05 | Ultramarine resin',(.014,.073,.53)); violet=mat('06 | Lilac resin',(.40,.25,.69))
black=mat('07 | Carbon black',(.009,.013,.017),.34,.18); ground=mat('Studio | chalk',(.22,.24,.27),.8,0)
black.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.28

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

def rounded_ring(width,r,z):
    pts=[]
    for cx,cy,start in [(width/2-r,width/2-r,0),(-width/2+r,width/2-r,90),(-width/2+r,-width/2+r,180),(width/2-r,-width/2+r,270)]:
        for i in range(16):
            a=math.radians(start+i*90/16); pts.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
    return pts

def base(label,material):
    # Continuous manifold shell, including underside cavity and 1.65 mm roof.
    rings=[(14.7,1.05,.25),(13.5,1.3,6.85),(13.1,1.4,7.15),
           (16.0,1.65,9.0),(16.6,1.75,8.65),(18,1.5,.7),(17.8,1.45,.25)]
    # Separate top exterior and cavity ceiling connected through walls, not through roof sides.
    order=[rings[i] for i in [2,1,0,6,5,4,3]]
    vs=sum([rounded_ring(*r) for r in order],[]); n=64
    fs=[tuple(reversed(range(n)))]
    for k in range(len(order)-1):
        fs += [(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for i in range(n)]
    fs.append(tuple(range((len(order)-1)*n,len(order)*n)))
    shell=mesh(label+' | hollow 1u shell',vs,fs,material,.16)
    stem=cylinder(label+' | MX socket (prototype)',(0,0,3.8),2.8,6.8,material,.12)
    # Apply bevel before cross subtraction, leaving the nominal slot dimensions precise.
    bpy.context.view_layer.objects.active=stem
    for m in list(stem.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
    # One plus-shaped cutter avoids coplanar sequential cuts.
    a=2.10; b=.65
    plus=[(-b,-a),(b,-a),(b,-b),(a,-b),(a,b),(b,b),(b,a),(-b,a),(-b,b),(-a,b),(-a,-b),(-b,-b)]
    cut=prism('temporary cross cutter',plus,-.2,5.1,None,0)
    mod=stem.modifiers.new('MX cross • 4.20 × 1.30 mm • depth 4.70','BOOLEAN'); mod.operation='DIFFERENCE'; mod.object=cut
    bpy.context.view_layer.objects.active=stem; bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(cut,do_unlink=True)
    stem.data.update()
    for p in stem.data.polygons:
        p.use_smooth=(abs(p.normal.z)<.5 and math.hypot(p.center.x,p.center.y)>2.6)
    stem['fit_note']='Nominal prototype only. Print fit coupon; compensate for resin shrinkage. Cross 4.20 x 1.30 mm.'
    shell['dimensions_mm']='18 x 18; deck Z=9; 19.05 mm pitch; open underside'
    return shell

pitch=19.05
origins=[(-pitch/2,pitch/2),(pitch/2,pitch/2),(-pitch/2,-pitch/2),(pitch/2,-pitch/2)]
for i in range(4):
    current=cols[i]; origin=origins[i]; base(['ARCH','ZIGZAG','DISC','STAIRS'][i],[cream,yellow,blue,red][i])
    if i==0:
        # Arch lies in the deck plane as in the reference, with short squared legs.
        poly=[(6,-3.6),(6,-.8)]
        poly += [(6*math.cos(t*math.pi/64),-.8+6*math.sin(t*math.pi/64)) for t in range(1,65)]
        poly += [(-6,-3.6),(-3.3,-3.6),(-3.3,-.8)]
        poly += [(3.3*math.cos(t*math.pi/64),-.8+3.3*math.sin(t*math.pi/64)) for t in range(63,-1,-1)]
        poly += [(3.3,-3.6)]
        prism('ARCH | solid teal horseshoe',poly,8.86,11.8,teal,.32)
        sphere('ARCH | orange bead',(0,-1.6,10.12),1.95,red)
        random.seed(19)
        # Tiny physically modeled, near-flush irregular terrazzo inlays, not shader noise.
        for j in range(48):
            x=random.uniform(-7.25,7.25); y=random.uniform(-7.25,7.25)
            if abs(x)>6.6 and abs(y)>6.6: continue
            r=random.uniform(.085,.22)
            p=[]
            for k in range(5):
                a=2*math.pi*k/5; rr=r*random.uniform(.65,1.25); p.append((x+rr*math.cos(a),y+rr*math.sin(a)))
            prism('ARCH | terrazzo %02d'%j,p,8.985,9.018,black,.015)
    elif i==1:
        poly=[(-5,4.7),(-3,4.7),(-3,1.1),(.9,1.1),(.9,-2.5),(4.8,-2.5),(4.8,-4.6),(-1.2,-4.6),(-1.2,-1),(-5,-1)]
        # Reverse clockwise outline.
        poly.reverse(); prism('ZIGZAG | black stepped beam',poly,8.87,11.3,black,.24)
        sphere('ZIGZAG | violet bead',(3.5,3.5,10.2),2.5,violet)
    elif i==2:
        cylinder('DISC | porcelain medallion',(-3.6,2.65,9.83),2.75,1.95,cream,.28)
        for j,y in enumerate([.6,-1.95,-4.5]):
            cube('DISC | black rail %d'%(j+1),(2.55,y,9.85),(6.35,1.35,1.95),black,.3)
    else:
        # Four contiguous broad terraces; rise in X and extend rearward in Y.
        stairs=None
        for j in range(4):
            x0=-5.3+j*2.65; x1=x0+2.65
            y0=-4.8; y1=-2.25+j*2.45
            block=prism('STAIRS | lavender terrace %d'%(j+1),[(x0-(.03 if j else 0),y0),(x1,y0),(x1,y1),(x0-(.03 if j else 0),y1)],8.87,10.25+j*.68,violet,0)
            block.modifiers.clear()
            if stairs is None: stairs=block
            else:
                mod=stairs.modifiers.new('Fuse terrace','BOOLEAN'); mod.operation='UNION'; mod.object=block
                bpy.context.view_layer.objects.active=stairs; bpy.ops.object.modifier_apply(modifier=mod.name)
                bpy.data.objects.remove(block,do_unlink=True)
        stairs.name='STAIRS | continuous lavender staircase'
        bm=bmesh.new(); bm.from_mesh(stairs.data)
        bmesh.ops.dissolve_limit(bm,angle_limit=.001,verts=list(bm.verts),edges=list(bm.edges))
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(stairs.data); bm.free()
        mod=stairs.modifiers.new('Rounded stair nosings','BEVEL'); mod.width=.19; mod.segments=4
        mod=stairs.modifiers.new('Face-weighted normals','WEIGHTED_NORMAL'); mod.keep_sharp=True

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
scene.render.engine='CYCLES'; scene.cycles.samples=96; scene.cycles.use_denoising=True
scene.world.color=(.25,.25,.25)
scene.render.resolution_x=1600; scene.render.resolution_y=1600; scene.render.resolution_percentage=100
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
bpy.ops.object.select_all(action='DESELECT')
scene['README']='MEMPHIS / four 1u resin artisan concepts. Model units mm. Separate editable colored parts; studio in collection 05. Prototype MX mounts, not validated for production. See MODEL_NOTES.md.'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Memphis_Artisans.blend'))
scene.render.filepath=os.path.join(OUT,'Memphis_Artisans.png'); bpy.ops.render.render(write_still=True)
# Second orthographic underside inspection, without changing the saved hero scene.
for ob in stage.objects:
    if ob.type=='MESH': ob.hide_render=True
cam.location=(28,-40,-65); aim(cam,(0,0,3)); camdata.ortho_scale=60
area('Underside inspection',(-20,-30,-50),26000,45,(1,1,1),target=(0,0,3))
scene.render.resolution_x=1200; scene.render.resolution_y=1200; scene.cycles.samples=48
scene.render.filepath=os.path.join(OUT,'Memphis_Underside.png'); bpy.ops.render.render(write_still=True)
print('MEMPHIS_COMPLETE')
