"""Render isolated orthographic views from the saved model; does not modify the .blend.
Run: blender -b output/Memphis_Artisans.blend --python render_drawings.py
Then: python3 compose_drawings.py (requires Pillow)
"""
import bpy, math, os, json
from mathutils import Vector
ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(ROOT,'output','drawings'); RAW=os.path.join(OUT,'_views')
os.makedirs(RAW,exist_ok=True)
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=800; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'
scene.render.film_transparent=True
s=scene.display.shading
s.light='STUDIO'; s.studio_light='paint.sl'; s.color_type='MATERIAL'
s.show_shadows=False; s.show_cavity=True; s.cavity_type='BOTH'
s.curvature_ridge_factor=1.2; s.curvature_valley_factor=1.0
s.cavity_ridge_factor=1.0; s.cavity_valley_factor=1.0
s.show_object_outline=True; s.object_outline_color=(.12,.14,.16)
s.show_specular_highlight=False; s.show_xray=False
scene.display.render_aa='32'
scene.view_settings.view_transform='Standard'
scene.view_settings.look='None'
scene.view_settings.exposure=0; scene.view_settings.gamma=1
camera_data=bpy.data.cameras.new('Drawing orthographic camera'); camera_data.type='ORTHO'; camera_data.ortho_scale=24
camera=bpy.data.objects.new('Drawing orthographic camera',camera_data); scene.collection.objects.link(camera); scene.camera=camera
camera_data.clip_start=.1; camera_data.clip_end=500
caps=[('01','Arch + dome','ARCH_DOME'),('02','Zigzag + cylinder','ZIGZAG_CYLINDER'),('03','Disc + rails','DISC_RAILS'),('04','Stair silhouette','STAIR_SILHOUETTE')]
metadata=[]
for number,title,slug in caps:
    col=next(c for c in bpy.data.collections if c.name.startswith(number+' '))
    objects=[o for o in col.objects if o.type=='MESH']
    for o in scene.objects:
        if o.type=='MESH': o.hide_render=o not in objects
    shell=next(o for o in objects if 'hollow' in o.name)
    # A schematic cavity tint makes the cross recess readable in a straight-on
    # workbench view, where parallel floor faces would otherwise look identical.
    stem=next(o for o in objects if 'MX socket' in o.name)
    cavity=bpy.data.materials.new('Drawing only | recessed socket '+number)
    base_color=stem.data.materials[0].diffuse_color
    cavity.diffuse_color=(*(v*.38 for v in base_color[:3]),1)
    stem.data.materials.append(cavity)
    for p in stem.data.polygons:
        if math.hypot(p.center.x,p.center.y)<2.5 and p.center.z>-3.3:
            p.material_index=len(stem.data.materials)-1
    x,y=shell.location.x,shell.location.y
    dg=bpy.context.evaluated_depsgraph_get()
    pts=[]
    for o in objects:
        ev=o.evaluated_get(dg)
        pts.extend(ev.matrix_world@Vector(p) for p in ev.bound_box)
    zmin=min(p.z for p in pts); zmax=max(p.z for p in pts); mid=(zmin+zmax)/2
    row={'number':number,'title':title,'slug':slug,'ortho_scale_mm':24,'view_pixels':800,'overall_height_mm':round(zmax-zmin,2),'shell_height_mm':round(9-zmin,2),'footprint_mm':18,'deck_mm':15,'views':{}}
    views={
        'top':((x,y,100),(0,0,0)),
        'front':((x,y-100,mid),(math.pi/2,0,0)),
        'right':((x+100,y,mid),(math.pi/2,0,math.pi/2)),
        'underside':((x,y,-100),(math.pi,0,0)),
    }
    for name,(loc,rot) in views.items():
        camera.location=loc; camera.rotation_euler=rot
        file=os.path.join(RAW,slug+'_'+name+'.png')
        scene.render.filepath=file; bpy.ops.render.render(write_still=True)
        row['views'][name]=os.path.relpath(file,OUT)
    metadata.append(row)
with open(os.path.join(OUT,'dimensions.json'),'w') as f: json.dump(metadata,f,indent=2)
print('ORTHOGRAPHIC_VIEWS_COMPLETE')
