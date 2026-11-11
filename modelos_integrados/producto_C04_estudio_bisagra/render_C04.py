"""Render the actual tessellated C04 FreeCAD geometry; body is hidden."""
from pathlib import Path
import gzip
import json
import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=20
scene.cycles.use_denoising=True
scene.render.resolution_x=1100
scene.render.resolution_y=800
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world.color=(0.22,0.22,0.22)
scene.view_settings.view_transform='AgX'


def mat(color):
 m=bpy.data.materials.new('mat')
 m.diffuse_color=(*color,1)
 m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*color,1)
 p.inputs['Metallic'].default_value=0.55
 p.inputs['Roughness'].default_value=0.32
 return m


def look(obj, target):
 obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

bpy.ops.object.camera_add(location=(0.22,-0.28,0.25))
camera=bpy.context.object
camera.data.type='ORTHO'
camera.data.ortho_scale=0.21
look(camera,(0,0,0.045))
scene.camera=camera
for location,energy,size in [((0.0,-0.15,0.35),180,0.23),((0.1,0.2,0.25),150,0.20),((-0.25,0.0,0.12),90,0.16)]:
 bpy.ops.object.light_add(type='AREA',location=location)
 obj=bpy.context.object
 obj.data.energy=energy
 obj.data.shape='DISK'
 obj.data.size=size
 look(obj,(0,0,0.04))
for state in ('cerrado','elevado','abierto'):
 objs=[]
 with gzip.open(HERE/('C04_'+state+'_malla.json.gz'),'rt') as f:
  data=json.load(f)
 for part in data:
  mesh=bpy.data.meshes.new(part['name']+'_mesh')
  # Shift module centre to the origin; mm -> m.
  verts=[((v[0]+160)*.001,(v[1]+76)*.001,v[2]*.001) for v in part['vertices']]
  mesh.from_pydata(verts,[],part['faces'])
  mesh.update()
  for p in mesh.polygons:p.use_smooth=True
  ob=bpy.data.objects.new(part['name'],mesh)
  scene.collection.objects.link(ob)
  ob.data.materials.append(mat(part['rgb']))
  objs.append(ob)
 scene.render.filepath=str(HERE/('C04_'+state+'.png'))
 bpy.ops.render.render(write_still=True)
 for ob in objs:bpy.data.objects.remove(ob,do_unlink=True)
 print('RENDER_OK',state,flush=True)
