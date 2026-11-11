"""Render C10 diagnostic mesh; red marker is exaggerated for visibility."""
from pathlib import Path
import gzip,json
import bpy
from mathutils import Vector
H=Path(__file__).resolve().parent
with gzip.open(H/'C11_elevado_60_mallas.json.gz','rt') as f:data=json.load(f)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1300;s.render.resolution_y=900;s.render.resolution_percentage=100;s.world.color=(.10,.10,.10)

def mat(name,color,opacity=1,emit=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links
 p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=.45;p.inputs['Roughness'].default_value=.35
 if emit:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
 if opacity<1:
  mix=n.new('ShaderNodeMixShader');t=n.new('ShaderNodeBsdfTransparent');mix.inputs[0].default_value=opacity
  l.new(t.outputs[0],mix.inputs[1]);l.new(p.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],n.get('Material Output').inputs['Surface'])
 return m
mats={'piel':mat('Piel transparente',(.28,.35,.40),.18),'camisa':mat('Camisa transparente',(.19,.29,.32),.15),
      'compuerta':mat('Compuerta',(.075,.095,.12)),'rotor':mat('Rotor',(.32,.38,.41)),
      'aro':mat('Aro',(.65,.72,.75)),'junta':mat('Junta',(.045,.05,.055)),
      'lamina_0':mat('Lamina0',(.075,.095,.12)), 'lamina_1':mat('Lamina1',(.075,.095,.12)), 'lamina_2':mat('Lamina2',(.075,.095,.12)), 'lamina_3':mat('Lamina3',(.075,.095,.12))}
for it in data['items']:
 name=it['name'];vs=[((v[0]+160)*.001,(v[1]+76)*.001,v[2]*.001) for v in it['vertices']]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],it['triangles']);mesh.update()
 for face in mesh.polygons:face.use_smooth=True
 ob=bpy.data.objects.new(name,mesh);s.collection.objects.link(ob);ob.data.materials.append(mats[name])

def look(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(.34,-.38,.32));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=.28;look(cam,(0,0,.07));s.camera=cam
for loc,energy,size in [((0,-.2,.45),3,.30),((.25,.2,.30),2,.28),((-.3,.02,.20),1.5,.20)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;look(o,(0,0,.07))
s.render.filepath=str(H/'C11_elevado_60.png');bpy.ops.render.render(write_still=True)
print('RENDER_C11_COMPLETO',flush=True)
