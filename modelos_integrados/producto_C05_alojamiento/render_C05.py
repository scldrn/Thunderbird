"""Render actual CAD mesh; translucent skin/door and red markers are aids."""
from pathlib import Path
import gzip,json
import bpy
from mathutils import Vector
H=Path(__file__).resolve().parent
with gzip.open(H/'vista_C05_malla.json.gz','rt') as f:data=json.load(f)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1300;s.render.resolution_y=900;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
s.world.color=(0.12,0.12,0.12)

def material(name,color,opacity=1,emission=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links
 p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
 p.inputs['Metallic'].default_value=.45;p.inputs['Roughness'].default_value=.32
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 if opacity<1:
  out=n.get('Material Output');mix=n.new('ShaderNodeMixShader');t=n.new('ShaderNodeBsdfTransparent')
  l.new(t.outputs[0],mix.inputs[1]);l.new(p.outputs[0],mix.inputs[2]);mix.inputs[0].default_value=opacity;l.new(mix.outputs[0],out.inputs['Surface'])
 return m
mats={'body':material('Carroceria recortada translúcida',(.24,.33,.42),.22),
      'door':material('Compuerta translúcida',(.40,.48,.53),.30),
      'ring':material('Aro',(.64,.72,.75)),
      'gasket':material('Junta',(.035,.04,.045)),
      'rotor':material('Rotor',(.30,.34,.36)),
      'hardware':material('Propuesta mecanismo',(.64,.34,.06)),
      'guide':material('Guias',(.42,.46,.50)),
      'marker':material('Marcador de interferencia',(.9,.03,.015),1,1.0)}
for it in data['items']:
 name=it['name'];vertices=[((v[0]+160)*.001,(v[1]+76)*.001,v[2]*.001) for v in it['vertices']]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],it['triangles']);mesh.update()
 for p in mesh.polygons:p.use_smooth=True
 o=bpy.data.objects.new(name,mesh);s.collection.objects.link(o)
 if name=='carroceria_recortada':k='body'
 elif name=='compuerta_C03':k='door'
 elif name=='aro_C03':k='ring'
 elif name=='junta_C03':k='gasket'
 elif name=='rotor_C03':k='rotor'
 elif name.startswith('guia_fija'):k='guide'
 else:k='hardware'
 o.data.materials.append(mats[k])
# A marker is an exaggerated overlay: mean of ring/gasket overlap centroids on each arm.
for arm in ('brazo_tapa_reserva','brazo_tapa_reserva001'):
 positions=[Vector(m['position_mm']) for m in data['markers'] if m['arm']==arm]
 if not positions:continue
 p=sum(positions,Vector())/len(positions)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=.0035,location=((p.x+160)*.001,(p.y+76)*.001,p.z*.001))
 bpy.context.object.data.materials.append(mats['marker'])

def look(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(.20,-.27,.23));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=.185;look(cam,(0,-.035,.073));s.camera=cam
for loc,energy,size in [((0,-.1,.4),2,.22),((.1,.18,.25),1.5,.20),((-.25,0,.12),1.0,.16)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;look(o,(0,-.02,.07))
s.render.filepath=str(H/'C05_inspeccion.png');bpy.ops.render.render(write_still=True)
print('RENDER_C05_OK',flush=True)
