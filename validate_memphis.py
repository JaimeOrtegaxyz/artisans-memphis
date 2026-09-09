"""Validate evaluated design meshes; run after opening the generated blend in background."""
import bpy, bmesh, json, os
report={'units':'millimeters','note':'Topology checks do not establish switch fit or manufacturability. Separate intersecting colored parts are intentional.','objects':[]}
dg=bpy.context.evaluated_depsgraph_get()
for col in bpy.data.collections:
    if not col.name[:2] in ('01','02','03','04'): continue
    for ob in col.objects:
        if ob.type!='MESH': continue
        ev=ob.evaluated_get(dg); me=ev.to_mesh(); bm=bmesh.new(); bm.from_mesh(me)
        report['objects'].append({'name':ob.name,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_mm3':round(bm.calc_volume(signed=True),5),'dimensions_mm':[round(v,4) for v in ob.dimensions]})
        bm.free(); ev.to_mesh_clear()
report['pass']=all(o['non_manifold_edges']==0 and o['volume_mm3']>0 for o in report['objects'])
path=os.path.join(os.path.dirname(bpy.data.filepath),'Geometry_Check.json')
with open(path,'w') as f: json.dump(report,f,indent=2)
print('GEOMETRY_PASS',report['pass'],'OBJECTS',len(report['objects']))
for o in report['objects']:
    if o['non_manifold_edges'] or o['volume_mm3']<=0: print('ISSUE',o)
