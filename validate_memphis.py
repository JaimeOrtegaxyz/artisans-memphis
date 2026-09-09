"""Validate evaluated design meshes; run after opening the generated blend in background."""
import bpy, bmesh, json, os, math
from mathutils import Vector
report={'units':'millimeters','note':'Topology checks do not establish switch fit or manufacturability. Separate intersecting colored parts are intentional.','objects':[],'engineering_checks':[]}
dg=bpy.context.evaluated_depsgraph_get()
for col in bpy.data.collections:
    if not col.name[:2] in ('01','02','03','04'): continue
    for ob in col.objects:
        if ob.type!='MESH': continue
        ev=ob.evaluated_get(dg); me=ev.to_mesh(); bm=bmesh.new(); bm.from_mesh(me)
        report['objects'].append({'name':ob.name,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_mm3':round(bm.calc_volume(signed=True),5),'dimensions_mm':[round(v,4) for v in ob.dimensions]})
        bm.free(); ev.to_mesh_clear()
    if bpy.context.scene.get('design_revision',0)>=4:
        shell=next(o for o in col.objects if 'hollow' in o.name)
        stem=next(o for o in col.objects if 'MX socket' in o.name)
        ev=shell.evaluated_get(dg)
        shell_z=[(ev.matrix_world@Vector(p)).z for p in ev.bound_box]
        # Cross-boundary vertices are inside R=2.5; outer boss vertices are not.
        slot_z=[(stem.matrix_world@v.co).z for v in stem.data.vertices if math.hypot(v.co.x,v.co.y)<2.5]
        check={'cap':col.name,'base_height_mm':round(max(shell_z)-min(shell_z),4),'socket_seat_z_mm':round(max(slot_z),4),'socket_mouth_z_mm':round(min(slot_z),4),'roof_rib_count':sum('roof buttress' in o.name for o in col.objects)}
        check['pass']=abs(check['base_height_mm']-9.8)<.001 and abs(check['socket_seat_z_mm']-5.1)<.001 and abs(check['socket_mouth_z_mm']-.4)<.001 and check['roof_rib_count']==4
        report['engineering_checks'].append(check)
report['pass']=all(o['non_manifold_edges']==0 and o['volume_mm3']>0 for o in report['objects']) and all(c['pass'] for c in report['engineering_checks'])
path=os.path.join(os.path.dirname(bpy.data.filepath),'Geometry_Check.json')
with open(path,'w') as f: json.dump(report,f,indent=2)
print('GEOMETRY_PASS',report['pass'],'OBJECTS',len(report['objects']))
for check in report['engineering_checks']: print('BASE_AND_SOCKET_CHECK',check)
for o in report['objects']:
    if o['non_manifold_edges'] or o['volume_mm3']<=0: print('ISSUE',o)
