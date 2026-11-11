"""Native CAD presentation; cosmetic material, not manufacturing specification."""
from pathlib import Path
import gzip
import json
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
OUT = HERE/'modulo_preliminar/CAD'
with gzip.open(OUT/'mallas_render.json.gz','rt') as f:
    data=json.load(f)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene.unit_settings.length_unit='METERS'
scene.render.engine='CYCLES'
scene.cycles.device='CPU'
scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.render.resolution_x=1600
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'

def material(name,color,metallic=0):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    node=m.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value=(*color,1)
    node.inputs['Metallic'].default_value=metallic
    node.inputs['Roughness'].default_value=.28
    return m

surface=material('Cosmetic graphite - material unapproved',(.16,.19,.22),.65)
for index,p in enumerate(data['parts']):
    mesh=bpy.data.meshes.new(p['name']+'_CAD_mesh')
    mesh.from_pydata(p['vertices_m'],[],p['triangles'])
    mesh.update()
    obj=bpy.data.objects.new(p['name'],mesh)
    scene.collection.objects.link(obj)
    obj.location=(-.078 if index==0 else .078,0,0)
    obj.data.materials.append(surface)
    obj['source_STEP_sha256']=p['sha256']
    obj['physical_performance_approved']=False
    for face in mesh.polygons:
        face.use_smooth=True
bpy.ops.mesh.primitive_plane_add(size=20,location=(0,0,-.012))
bpy.context.object.data.materials.append(material('Studio',(.022,.028,.039)))
world=bpy.data.worlds.new('Studio')
scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.15,.20,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.2
for name,loc,energy,size in [('Key',(-.2,-.1,.3),2,.25),('Rim',(.12,.15,.25),3,.2),('Fill',(.25,-.2,.15),1,.2)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    light=bpy.context.object
    light.name=name
    light.data.energy=energy
    light.data.size=size
    light.rotation_euler=(Vector((0,0,0))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-.28,.32))
camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'
camera.data.ortho_scale=.33
scene.camera=camera

def label(text,x,y,size):
    curve=bpy.data.curves.new(text,'FONT')
    curve.body=text
    curve.size=size
    obj=bpy.data.objects.new(text,curve)
    scene.collection.objects.link(obj)
    obj.parent=camera
    obj.location=(x,y,-.2)
    m=bpy.data.materials.get('Lettering')
    if m is None:
        m=bpy.data.materials.new('Lettering')
        m.use_nodes=True
        nodes=m.node_tree.nodes
        nodes.clear()
        emission=nodes.new('ShaderNodeEmission')
        emission.inputs[0].default_value=(.78,.84,.92,1)
        output=nodes.new('ShaderNodeOutputMaterial')
        m.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
    curve.materials.append(m)

def label_panel(x):
    mesh=bpy.data.meshes.new('Label panel')
    mesh.from_pydata([(-.055,-.011,0),(.055,-.011,0),(.055,.011,0),(-.055,.011,0)],[],[(0,1,2,3)])
    mesh.update()
    obj=bpy.data.objects.new('Label panel',mesh)
    scene.collection.objects.link(obj)
    obj.parent=camera
    obj.location=(x,-.063,-.201)
    m=bpy.data.materials.new('Panel background')
    m.use_nodes=True
    nodes=m.node_tree.nodes
    nodes.clear()
    emission=nodes.new('ShaderNodeEmission')
    emission.inputs[0].default_value=(.012,.018,.028,1)
    output=nodes.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
    mesh.materials.append(m)

label_panel(-.078)
label_panel(.078)
label('ROTORES INTERNOS | ESTUDIO C01',-.153,.080,.008)
label('CAD calculado - ocho palas - dos escalas de referencia',-.153,.066,.0045)
label('D 82 mm',-.113,-.066,.0065)
label('D 102,5 mm',.035,-.066,.0065)
label('Geometria preliminar. Alojamiento, material y RPM sin aprobar.',-.153,-.088,.0042)
scene['scope']='Computed rotor component geometry; not installed, manufacturing or performance approval'
bpy.data.texts.new('ALCANCE').write(scene['scope'])
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'comparacion_rotores.blend'))
scene.render.filepath=str(OUT/'comparacion_rotores.png')
bpy.ops.render.render(write_still=True)
print('ROTOR_CAD_RENDER_OK',flush=True)
