"""Render C06 meshes. Cropped transparent skin and duct are visual aids."""
from pathlib import Path
import gzip,json
import bpy
from mathutils import Vector
H=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1300;s.render.resolution_y=900;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.world.color=(.10,.10,.10)

def mat(name,color,opacity=1):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links
 p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=.5;p.inputs['Roughness'].default_value=.34
 if opacity<1:
  mix=n.new('ShaderNodeMixShader');t=n.new('ShaderNodeBsdfTransparent');mix.inputs[0].default_value=opacity
  l.new(t.outputs[0],mix.inputs[1]);l.new(p.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],n.get('Material Output').inputs['Surface'])
 return m
mats={'skin':mat('Carroceria translúcida',(.28,.35,.40),.20),'duct':mat('Camisa translúcida',(.19,.29,.32),.15),
      'door':mat('Compuerta',(.075,.095,.12)),'rotor':mat('Rotor interior',(.32,.38,.41)),
      'ring':mat('Aro',(.65,.72,.75)),'seal':mat('Junta',(.045,.05,.055)),
      'collision':mat('Interferencia',(.8,.03,.01)),'guide':mat('Reserva de guia',(.8,.42,.08))}

def look(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(.34,-.38,.32));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=.36;look(cam,(0,0,.07));s.camera=cam
for loc,energy,size in [((0,-.2,.45),3,.30),((.25,.2,.30),2,.28),((-.3,.02,.20),1.5,.20)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;look(o,(0,0,.07))
for state in ('cerrado','abierto'):
 with gzip.open(H/f'C08_local_{state}_mallas.json.gz','rt') as f:data=json.load(f)
 objs=[]
 for it in data['items']:
  name=it['name'];vs=[((v[0]+200)*.001,(v[1]+76)*.001,v[2]*.001) for v in it['vertices']]
  mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],it['triangles']);mesh.update()
  for face in mesh.polygons:face.use_smooth=True
  ob=bpy.data.objects.new(name,mesh);s.collection.objects.link(ob);objs.append(ob)
  k={'carroceria_C03':'skin','piel_superior_C03':'skin','camisa_C03':'duct','compuerta_C03':'door','rotor_C03':'rotor','aro_C03':'ring','junta_C03':'seal','interseccion':'collision','reserva_guia_0':'guide','reserva_guia_1':'guide'}[name]
  ob.data.materials.append(mats[k])
 s.render.filepath=str(H/f'C08_local_{state}.png');bpy.ops.render.render(write_still=True)
 for o in objs:bpy.data.objects.remove(o,do_unlink=True)
 print('RENDER_C08',state,flush=True)
