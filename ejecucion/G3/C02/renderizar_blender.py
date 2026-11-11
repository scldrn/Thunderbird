"""Closed/cut views of identified CAD. Cosmetic materials only."""
from pathlib import Path
import gzip
import json
import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
DEST=HERE/'integracion_x160'
with gzip.open(DEST/'mallas_C02.json.gz','rt') as f:data=json.load(f)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='METERS'
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
materials={}

def material(rgb):
    key=tuple(rgb)
    if key in materials:return materials[key]
    m=bpy.data.materials.new('Cosmetic_'+str(len(materials)));m.use_nodes=True
    linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    node=m.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value=(*linear,1)
    node.inputs['Metallic'].default_value=.6 if rgb[0]>.3 else .35
    node.inputs['Roughness'].default_value=.24
    node.inputs['Coat Weight'].default_value=.2
    materials[key]=m
    return m

def make_mesh(name,record):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(record['vertices_m'],[],record['triangles']);mesh.update()
    for face in mesh.polygons:face.use_smooth=True
    return mesh

objects={}
for p in data['parts']:
    mesh=make_mesh(p['name']+'_mesh',p)
    obj=bpy.data.objects.new(p['name'],mesh);scene.collection.objects.link(obj)
    n=p['name']
    if p['hardware_reserve']:rgb=[.07,.27,.36]
    elif n.startswith(('carroceria_C02_','compuerta_C02_')):rgb=[.045,.055,.065]
    elif n.startswith('aro_C02_'):rgb=[.63,.27,.10]
    elif n.startswith(('junta_C02_','sculpture_','epaule_','lame_','signature_','carenado_raiz_')):rgb=[.018,.025,.032]
    elif n.startswith('aleta_movil_'):rgb=[.055,.062,.070]
    else:rgb=p['color']
    obj.data.materials.append(material(rgb))
    if n.startswith(('carroceria_C02_','compuerta_C02_')):
        node=obj.data.materials[0].node_tree.nodes.get('Principled BSDF')
        node.inputs['Metallic'].default_value=.15;node.inputs['Roughness'].default_value=.30
    obj['hardware_reserve_not_selected']=p['hardware_reserve']
    obj['source_STEP_SHA256']=data['closed_STEP_sha256']
    obj['performance_validated']=False
    objects[p['name']]=obj
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.165))
bpy.context.object.name='Studio';bpy.context.object.data.materials.append(material([.025,.030,.040]))
node=bpy.context.object.data.materials[0].node_tree.nodes.get('Principled BSDF')
node.inputs['Metallic'].default_value=0;node.inputs['Roughness'].default_value=.65
world=bpy.data.worlds.new('World_C02');scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.08,.105,.14,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.35
for name,loc,power,size in [('Key',(-1.1,-1.7,2.2),450,2),('Rim',(1.4,1.2,1.8),650,1.6),('Fill',(-1,1.3,1.4),280,1.4)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name
    o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(-1.45,-1.8,1.25));camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=55;scene.camera=camera

def label(body,x,y,size):
    curve=bpy.data.curves.new('Engineering note','FONT');curve.body=body;curve.size=size
    obj=bpy.data.objects.new('Engineering note',curve);scene.collection.objects.link(obj);obj.parent=camera
    obj.location=(x,y,-.2)
    m=bpy.data.materials.get('Engineering note emission')
    if m is None:
        m=bpy.data.materials.new('Engineering note emission');m.use_nodes=True;nodes=m.node_tree.nodes;nodes.clear()
        emission=nodes.new('ShaderNodeEmission');emission.inputs[0].default_value=(.85,.90,.95,1)
        output=nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
    curve.materials.append(m)
    return curve

title=label('C02 | INTEGRACION INTERNA',-.059,.034,.0036)
note=label('5 kg objetivo - CAD candidato - motor, materiales y prestaciones sin validar',-.059,-.036,.00165)
# Dark camera-facing caption panel keeps the engineering scope legible.
panel_mesh=bpy.data.meshes.new('Caption panel')
panel_mesh.from_pydata([(-.062,-.039,0),(.062,-.039,0),(.062,-.032,0),(-.062,-.032,0)],[],[(0,1,2,3)])
panel_mesh.update();panel=bpy.data.objects.new('Caption panel',panel_mesh);scene.collection.objects.link(panel)
panel.parent=camera;panel.location=(0,0,-.201)
pm=bpy.data.materials.new('Caption background');pm.use_nodes=True;nodes=pm.node_tree.nodes;nodes.clear()
e=nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(.01,.014,.02,1)
o=nodes.new('ShaderNodeOutputMaterial');pm.node_tree.links.new(e.outputs[0],o.inputs['Surface']);panel_mesh.materials.append(pm)
scene['geometry_source_sha256']=data['closed_STEP_sha256'];scene['scope']=data['scope']
bpy.data.texts.new('ALCANCE').write(data['scope'])
bpy.ops.wm.save_as_mainfile(filepath=str(DEST/'C02_cerrado_CANDIDATA.blend'))
scene.render.filepath=str(DEST/'C02_cerrado.png');bpy.ops.render.render(write_still=True)
for p in data['parts']:
    obj=objects[p['name']]
    if p['hidden_in_cut']:obj.hide_render=True;obj.hide_viewport=True
    if p['name'] in data['cut_overrides']:
        mats=list(obj.data.materials);obj.data=make_mesh(p['name']+'_cut',data['cut_overrides'][p['name']])
        for m in mats:obj.data.materials.append(m)
title.body='C02 | CORTE DE INSPECCION'
note.body='Azul: reservas de equipos. Corte de CAD; no representa vuelo o fabricacion aprobados.'
bpy.ops.wm.save_as_mainfile(filepath=str(DEST/'C02_inspeccion_CANDIDATA.blend'))
scene.render.filepath=str(DEST/'C02_inspeccion.png');bpy.ops.render.render(write_still=True)
print('C02_NATIVE_CAD_RENDER_OK',flush=True)
