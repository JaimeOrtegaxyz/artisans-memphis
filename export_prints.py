"""Export joined, topology-checked millimeter STLs without modifying the source .blend.
Run: blender -b output/Memphis_Artisans.blend --python export_prints.py
"""
import bpy
import bmesh
import json
import math
import os
import struct
from mathutils import Matrix, Vector

ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(ROOT,'output','print'); os.makedirs(OUT,exist_ok=True)
DG=bpy.context.evaluated_depsgraph_get()
COLLECTION=bpy.data.collections.new('Temporary print export'); bpy.context.scene.collection.children.link(COLLECTION)
REPORT={'units':'mm','physical_fit_validated':False,'note':'Single-material prototypes. Closed-mesh checks do not establish switch fit, full travel, material strength, or printability on a particular machine.','files':[]}


def evaluated_copy(source,transform):
    ev=source.evaluated_get(DG)
    me=bpy.data.meshes.new_from_object(ev,depsgraph=DG)
    me.transform(transform@source.matrix_world)
    ob=bpy.data.objects.new('Print copy | '+source.name,me); COLLECTION.objects.link(ob)
    return ob


def export_group(objects,filename):
    shell=next(o for o in objects if 'hollow' in o.name)
    shell_ev=shell.evaluated_get(DG)
    bottom=min((shell_ev.matrix_world@Vector(p)).z for p in shell_ev.bound_box)
    transform=Matrix.Translation((-shell.location.x,-shell.location.y,-bottom))
    result=evaluated_copy(shell,transform)
    # Start with the mounting structure; append relief only after the base is joined.
    sources=sorted((o for o in objects if o!=shell),key=lambda o: (0 if 'MX socket' in o.name else 1 if 'roof buttress' in o.name else 2,o.name))
    for source in sources:
        operand=evaluated_copy(source,transform)
        mod=result.modifiers.new('Join '+source.name,'BOOLEAN'); mod.operation='UNION'; mod.solver='EXACT'; mod.object=operand
        mod.use_hole_tolerant=True
        bpy.context.view_layer.objects.active=result
        bpy.ops.object.modifier_apply(modifier=mod.name)
        data=operand.data; bpy.data.objects.remove(operand,do_unlink=True); bpy.data.meshes.remove(data)
    bm=bmesh.new(); bm.from_mesh(result.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.normal_update()
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
    finite=all(math.isfinite(c) for v in bm.verts for c in v.co)
    mins=[min(v.co[i] for v in bm.verts) for i in range(3)]
    maxs=[max(v.co[i] for v in bm.verts) for i in range(3)]
    passed=not non_manifold and components==1 and volume>0 and not degenerate and finite and abs(mins[2])<1e-4
    audit={'file':filename,'triangles':len(bm.faces),'non_manifold_edges':non_manifold,'connected_components':components,'degenerate_triangles':degenerate,'volume_mm3':round(volume,4),'dimensions_mm':[round(b-a,4) for a,b in zip(mins,maxs)],'bottom_z_mm':round(mins[2],6),'pass':passed}
    REPORT['files'].append(audit)
    if passed:
        # STL has no unit field: write unscaled model coordinates in millimeters.
        with open(os.path.join(OUT,filename),'wb') as f:
            f.write(('MEMPHIS | millimeters | prototype | '+filename).encode('ascii')[:80].ljust(80,b' '))
            f.write(struct.pack('<I',len(bm.faces)))
            for face in bm.faces:
                values=list(face.normal)
                for v in face.verts: values.extend(v.co)
                f.write(struct.pack('<12fH',*values,0))
    bm.free(); data=result.data; bpy.data.objects.remove(result,do_unlink=True); bpy.data.meshes.remove(data)
    print('PRINT_AUDIT',audit,flush=True)


CAPS=[('01','01_ARCH_DOME.stl'),('02','02_ZIGZAG_CYLINDER.stl'),('03','03_DISC_RAILS.stl'),('04','04_STAIR_SILHOUETTE.stl')]
for number,filename in CAPS:
    col=next(c for c in bpy.data.collections if c.name.startswith(number+' '))
    objects=[o for o in col.objects if o.type=='MESH']
    if number=='01':
        structure=[o for o in objects if any(key in o.name for key in ('hollow','MX socket','roof buttress'))]
        export_group(structure,'00_BASE_FIT_TEST.stl')
    export_group(objects,filename)
REPORT['pass']=all(row['pass'] for row in REPORT['files']) and len(REPORT['files'])==5
with open(os.path.join(OUT,'Print_Check.json'),'w') as f: json.dump(REPORT,f,indent=2)
if not REPORT['pass']: raise RuntimeError('One or more print meshes failed validation; failed meshes were not exported.')
print('PRINT_EXPORT_PASS: 5 single-component, closed millimeter STLs')
