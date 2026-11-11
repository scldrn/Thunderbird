from pathlib import Path
import bpy,json,gzip,math
from mathutils import Vector
P=Path(__file__).resolve().parent
with gzip.open(P/'cad_A07.json.gz','rt') as f:data=json.load(f)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='METERS';scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1280;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.fps=24;scene.frame_start=1;scene.frame_end=100
collections={}
for name in ('Exterior','Interior','Compuertas','Aletas','Estudio'):
 c=bpy.data.collections.new(name);scene.collection.children.link(c);collections[name]=c
materials={}
def material(rgb):
 key=tuple(rgb)
 if key in materials:return materials[key]
 m=bpy.data.materials.new('Material_'+str(len(materials)));linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb];m.diffuse_color=(*linear,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*linear,1);n.inputs['Metallic'].default_value=.65 if rgb[0]>.3 else .25;n.inputs['Roughness'].default_value=.22 if rgb[0]>.03 else .3;n.inputs['Coat Weight'].default_value=.25;materials[key]=m;return m
def empty(name,collection):
 o=bpy.data.objects.new(name,None);collection.objects.link(o);return o
root=empty('A07_internal_fans_5kg_TARGET',collections['Estudio']);rules={r['name']:r for r in data['rules']}
for p in data['parts']:
 name=p['name'];cover=name in rules;verts=p['vertices_m']
 if cover:
  r=rules[name];axis=[a/1000 for a in r['axis_closed']];verts=[[v[i]-axis[i] for i in range(3)] for v in verts]
 mesh=bpy.data.meshes.new(name+'_mesh');mesh.from_pydata(verts,[],p['triangles']);mesh.update()
 obj=bpy.data.objects.new(name,mesh);group='Compuertas' if cover else ('Aletas' if name.startswith(('aleta_','carenado_raiz_','eje_control','cojinete','actuador_reserva')) else ('Exterior' if p['exterior'] else 'Interior'));collections[group].objects.link(obj);obj.data.materials.append(material(p['color']));obj['scope']=p['scope'];obj['source_STEP']=data['source_sha256']
 if cover:
  lift=empty(name+'_ELEVACION_CONCEPTUAL',collections['Compuertas']);lift.parent=root
  hinge=empty(name+'_EJE_CONCEPTUAL',collections['Compuertas']);hinge.parent=lift;hinge.location=axis;obj.parent=hinge
  for frame,z in ((1,0),(40,r['out']*.01),(100,r['out']*.01)):
   lift.location.z=z;lift.keyframe_insert(data_path='location',frame=frame)
  for frame,angle in ((1,0),(40,0),(100,math.radians(r['sign']*110))):
   hinge.rotation_euler.x=angle;hinge.keyframe_insert(data_path='rotation_euler',frame=frame)
 else:obj.parent=root
# Neutral studio; all lighting and assets embedded, no external textures.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.165));floor=bpy.context.object;floor.name='Studio_floor';floor.data.materials.append(material([.025,.03,.04]))
world=bpy.data.worlds.new('Studio_world');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.08,.105,.14,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35
for name,loc,power,size in [('Key',(-1.1,-1.7,2.2),450,2),('Rim',(1.4,1.2,1.8),650,1.6),('Fill',(-1,1.3,1.4),280,1.4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(-1.45,-1.8,1.25));cam=bpy.context.object;cam.name='Camera_producto';cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=55;scene.camera=cam
text=bpy.data.texts.new('LEEME — alcance');text.write('A07: ventiladores internos. 208 piezas importadas de STEP. Frames 1/40/100: cerrado/elevado/abierto. Solo estudio de trayectoria de tapas; bisagras y actuadores NO dimensionados. NO simulación CFD ni vuelo validado. Masa 5 kg OBJETIVO. Fotogramas intermedios Blender no equivalen al cribado geométrico de 61 posiciones.\n')
scene['geometry_source_sha256']=data['source_sha256'];scene['physical_performance_validated']=False;scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'A07_ventiladores_internos.blend'))
(P/'IMPORTACION.json').write_text(json.dumps(dict(blender_version=bpy.app.version_string,source=data['source'],source_sha256=data['source_sha256'],mesh_parts=len(data['parts']),units='m',frames={'closed':1,'lifted':40,'open':100},render_engine=scene.render.engine,render_device=scene.cycles.device,scope='CAD import and conceptual cover animation; no flight/CFD validation'),indent=2))
scene.render.filepath=str(P/'prueba_blender.png');bpy.ops.render.render(write_still=True)
print('BLENDER_IMPORT_RENDER_OK',flush=True)
