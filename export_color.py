"""Export full-color OBJ+MTL+PNG print files (e.g. PolyJet) without modifying the source .blend.
Each cap is boolean-joined like the STL export, UV-unwrapped, and its material colors,
including the procedural porcelain stains, are baked into one PNG texture.
Run: blender -b output/Memphis_Artisans.blend --python export_color.py
"""
import bpy
import bmesh
import json
import math
import os
from mathutils import Matrix

ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(ROOT,'output','color'); os.makedirs(OUT,exist_ok=True)
TEXTURE=4096
DG=bpy.context.evaluated_depsgraph_get()
scene=bpy.context.scene
COLLECTION=bpy.data.collections.new('Temporary color export'); scene.collection.children.link(COLLECTION)
REPORT={'units':'mm','axes':'Z up, skirt bottom at Z=0 (same placement as the STLs)','texture_px':TEXTURE,'physical_fit_validated':False,
        'note':'Colors are baked from the Blender materials. Closed-mesh checks do not establish switch fit or printability.','files':[]}

scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=16
# Narrow pixel filter keeps the hard stain boundaries crisp in the baked texture.
scene.cycles.filter_width=.7
scene.render.bake.margin=8; scene.render.bake.margin_type='EXTEND'


def evaluated_copy(source,transform):
    ev=source.evaluated_get(DG)
    me=bpy.data.meshes.new_from_object(ev,depsgraph=DG)
    me.transform(transform@source.matrix_world)
    ob=bpy.data.objects.new('Color copy | '+source.name,me); COLLECTION.objects.link(ob)
    return ob


def select_only(ob):
    for o in bpy.context.view_layer.objects: o.select_set(False)
    ob.select_set(True); bpy.context.view_layer.objects.active=ob


def export_group(objects,stem):
    shell=next(o for o in objects if 'hollow' in o.name)
    # Join in the shell's object space so object-coordinate textures (the porcelain
    # stains) bake exactly as they render in the source scene.
    transform=shell.matrix_world.inverted()
    result=evaluated_copy(shell,transform)
    sources=sorted((o for o in objects if o!=shell),key=lambda o: (0 if 'MX socket' in o.name else 1 if 'roof buttress' in o.name else 2,o.name))
    for source in sources:
        operand=evaluated_copy(source,transform)
        mod=result.modifiers.new('Join '+source.name,'BOOLEAN'); mod.operation='UNION'; mod.solver='EXACT'; mod.object=operand
        mod.use_hole_tolerant=True; mod.material_mode='TRANSFER'
        select_only(result); bpy.ops.object.modifier_apply(modifier=mod.name)
        data=operand.data; bpy.data.objects.remove(operand,do_unlink=True); bpy.data.meshes.remove(data)
    bm=bmesh.new(); bm.from_mesh(result.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(result.data); bm.free()
    for p in result.data.polygons: p.use_smooth=False

    select_only(result)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.003)
    bpy.ops.object.mode_set(mode='OBJECT')

    image=bpy.data.images.new(stem,TEXTURE,TEXTURE,alpha=False)
    targets=[]
    for m in result.data.materials:
        node=m.node_tree.nodes.new('ShaderNodeTexImage'); node.image=image
        m.node_tree.nodes.active=node; targets.append((m,node))
    bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'},use_clear=True)
    for m,node in targets: m.node_tree.nodes.remove(node)
    png=os.path.join(OUT,stem+'.png')
    image.filepath_raw=png; image.file_format='PNG'; image.save()

    baked=bpy.data.materials.new('MEMPHIS '+stem); baked.use_nodes=True
    tex=baked.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=image
    bsdf=baked.node_tree.nodes.get('Principled BSDF')
    baked.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=.25
    result.data.materials.clear(); result.data.materials.append(baked)

    # Same placement as the STLs: centered in X/Y, skirt bottom at Z=0, millimeters.
    bottom=min(v.co.z for v in result.data.vertices)
    result.data.transform(Matrix.Translation((0,0,-bottom)))
    bm=bmesh.new(); bm.from_mesh(result.data)
    non_manifold=sum(not e.is_manifold for e in bm.edges)
    unseen=set(bm.verts); components=0
    while unseen:
        components+=1; pending=[unseen.pop()]
        while pending:
            v=pending.pop()
            for edge in v.link_edges:
                other=edge.other_vert(v)
                if other in unseen: unseen.remove(other); pending.append(other)
    volume=bm.calc_volume(signed=True)
    degenerate=sum(f.calc_area()<1e-12 for f in bm.faces)
    mins=[min(v.co[i] for v in bm.verts) for i in range(3)]
    maxs=[max(v.co[i] for v in bm.verts) for i in range(3)]
    bm.free()
    passed=not non_manifold and not degenerate and components==1 and volume>0 and abs(mins[2])<1e-4 and bool(result.data.uv_layers)
    audit={'file':stem+'.obj','material':stem+'.mtl','texture':stem+'.png','triangles':len(result.data.polygons),'non_manifold_edges':non_manifold,
           'connected_components':components,'degenerate_triangles':degenerate,'volume_mm3':round(volume,4),'dimensions_mm':[round(b-a,4) for a,b in zip(mins,maxs)],'pass':passed}
    REPORT['files'].append(audit)
    if passed:
        select_only(result)
        bpy.ops.wm.obj_export(filepath=os.path.join(OUT,stem+'.obj'),export_selected_objects=True,export_uv=True,export_normals=True,
                              export_materials=True,path_mode='STRIP',forward_axis='Y',up_axis='Z',global_scale=1.0,
                              apply_modifiers=False,export_triangulated_mesh=True)
    print('COLOR_AUDIT',audit,flush=True)
    return result


CAPS=[('01','01_ARCH_DOME'),('02','02_ZIGZAG_CYLINDER'),('03','03_DISC_RAILS'),('04','04_STAIR_SILHOUETTE')]
previews=[]
for number,stem in CAPS:
    col=next(c for c in bpy.data.collections if c.name.startswith(number+' '))
    objects=[o for o in col.objects if o.type=='MESH']
    if number=='01':
        structure=[o for o in objects if any(key in o.name for key in ('hollow','MX socket','roof buttress'))]
        fit=export_group(structure,'00_BASE_FIT_TEST'); fit.hide_render=True
    shell=next(o for o in objects if 'hollow' in o.name)
    ob=export_group(objects,stem)
    # Place the textured copy where the source cap sits for the comparison render.
    ob.location=shell.location; ob.location.z+=min((shell.matrix_world@v.co).z for v in shell.data.vertices)
    previews.append(ob)

REPORT['pass']=all(row['pass'] for row in REPORT['files']) and len(REPORT['files'])==5
with open(os.path.join(OUT,'Color_Check.json'),'w') as f: json.dump(REPORT,f,indent=2)
if not REPORT['pass']: raise RuntimeError('One or more color meshes failed validation; failed meshes were not exported.')

# Preview: the baked-texture copies from the hero camera, for comparison with Memphis_Artisans.png.
for c in bpy.data.collections:
    if c.name[:2] in ('01','02','03','04'): c.hide_render=True
scene.cycles.samples=32; scene.cycles.filter_width=1.5; scene.render.resolution_x=scene.render.resolution_y=1000
scene.render.filepath=os.path.join(OUT,'Color_Preview.png'); bpy.ops.render.render(write_still=True)
print('COLOR_EXPORT_PASS: 5 textured OBJ+MTL+PNG sets')
