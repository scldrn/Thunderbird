"""Native Blender presentation of existing C02 CAD; no geometry redesign."""
from pathlib import Path
import json
import bpy
from mathutils import Vector

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SOURCE = ROOT/'ejecucion/G3/C02/integracion_x160'

for mode, native in [('exterior','C02_cerrado_CANDIDATA.blend'),
                     ('interior','C02_inspeccion_CANDIDATA.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/native))
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 6
    scene.render.resolution_x = 2000
    scene.render.resolution_y = 1250
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    scene.camera.location = (-1.32,-1.65,1.48)
    scene.camera.rotation_euler = (Vector((0,0,0))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    scene.camera.data.lens = 55
    for obj in scene.objects:
        if obj.type == 'FONT':
            obj.data.body = ('C02 | CAD ACTUAL / EXTERIOR' if mode=='exterior' else 'C02 | CAD ACTUAL / CORTE INTERIOR') if obj.data.size>.003 else '5 kg objetivo | Integracion candidata | Equipos y prestaciones pendientes de validar'
        if obj.type == 'LIGHT':
            obj.data.energy *= .48
        if obj.name == 'Studio' and obj.active_material:
            node = obj.active_material.node_tree.nodes.get('Principled BSDF')
            node.inputs['Roughness'].default_value = .92
            node.inputs['Metallic'].default_value = 0
            node.inputs['Base Color'].default_value = (.028,.036,.048,1)
    scene['delivery_note'] = 'Same identified C02 geometry; cosmetic presentation only; research goal remains paused.'
    scene.render.filepath = str(OUT/f'C02_actual_{mode}.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'C02_actual_{mode}.blend'))
    bpy.ops.render.render(write_still=True)
    print('NATIVE_CAD_RENDER_COMPLETE', mode, flush=True)
