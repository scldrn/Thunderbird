"""Render C07 directly from meshes tessellated from the FreeCAD assemblies.

Run in Blender background mode with `-- abierto` or `-- cerrado` after the
generator. Materials and lighting are cosmetic; no geometry is invented here.
"""

from pathlib import Path
import gzip
import json
import math
import os
import sys

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
if "--" not in sys.argv:
    raise ValueError("Provide 'abierto' or 'cerrado' after --")
STATE = sys.argv[sys.argv.index("--") + 1]
PREVIEW = os.environ.get("C07_PREVIEW") == "1"
if STATE not in ("abierto", "cerrado"):
    raise ValueError("Unknown door state")
with gzip.open(HERE / "5kg" / f"C07_5kg_mallas_caras.json.gz", "rt") as stream:
    DATA = json.load(stream)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 8 if PREVIEW else 24
scene.cycles.use_denoising = True
scene.render.resolution_x = 960 if PREVIEW else 1600
scene.render.resolution_y = 600 if PREVIEW else 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "METERS"
scene.view_settings.view_transform = "AgX"


def material(name, color, metallic=0.0, roughness=0.35, coat=0.0, emission=0.0):
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    node = result.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = (*color, 1)
    node.inputs["Metallic"].default_value = metallic
    node.inputs["Roughness"].default_value = roughness
    node.inputs["Coat Weight"].default_value = coat
    if emission:
        node.inputs["Emission Color"].default_value = (*color, 1)
        node.inputs["Emission Strength"].default_value = emission
    return result


materials = {
    "shell": material("Obsidian lacquer", (0.006, 0.009, 0.014), 0.14, 0.32, 0.25),
    "panel": material("Satin graphite", (0.012, 0.017, 0.024), 0.25, 0.35, 0.12),
    "trim": material("Dark titanium", (0.028, 0.034, 0.041), 0.65, 0.32),
    "rubber": material("Seal black", (0.006, 0.008, 0.010), 0.05, 0.55),
    "rotor": material("Internal rotor graphite", (0.07, 0.09, 0.11), 0.55, 0.35),
    "hardware": material("Illustrative metal", (0.12, 0.14, 0.16), 0.65, 0.34),
    "reserve": material("Unspecified hardware envelope", (0.035, 0.085, 0.10), 0.35, 0.38),
    "light": material("Cosmetic light accent", (0.60, 0.80, 0.95), 0.1, 0.25, emission=1.4),
    "floor": material("Studio charcoal", (0.012, 0.016, 0.023), 0.08, 0.48),
}


def choose_material(name):
    if name.startswith(("carroceria_C02_", "compuerta_C02_")):
        return materials["shell"]
    if name.startswith(("panel_sensor_", "cubierta_lateral_", "signature_dorsale_")):
        return materials["panel"]
    if name.startswith(("signature_optique", "signature_arriere")):
        return materials["light"]
    if name.startswith("junta_"):
        return materials["rubber"]
    if name.startswith("aro_"):
        return materials["trim"]
    if "rotor_copa" in name:
        return materials["rotor"]
    if "reserva_" in name:
        return materials["reserve"]
    if name.startswith(("sculpture_", "epaule_", "lame_", "aleta_movil_", "carenado_raiz_")):
        return materials["panel"]
    return materials["hardware"]


body = bpy.data.objects.new("CAD_C07", None)
scene.collection.objects.link(body)
model_objects = []
for part in DATA["parts"]:
    mesh = bpy.data.meshes.new(part["name"] + "_mesh")
    mesh.from_pydata(part["vertices_m"], [], part["triangles"])
    mesh.update()
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    obj = bpy.data.objects.new(part["name"], mesh)
    scene.collection.objects.link(obj)
    obj.parent = body
    obj.data.materials.append(choose_material(part["name"]))
    obj["fuente_geometria"] = "C07 FreeCAD, tessellation 0.30 mm"
    model_objects.append(obj)

bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.215))
floor = bpy.context.object
floor.name = "Studio floor"
floor.data.materials.append(materials["floor"])

world = bpy.data.worlds.new("Studio world")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.055, 0.070, 0.090, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.12


def area_light(name, location, power, size, size_y, target=(0, 0, 0)):
    bpy.ops.object.light_add(type="AREA", location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.energy = power
    obj.data.shape = "RECTANGLE"
    obj.data.size = size
    obj.data.size_y = size_y
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj


lights = [
    area_light("Long white key", (-0.7, -1.2, 1.8), 22, 2.4, 0.55),
    area_light("Cool upper rim", (0.9, 1.4, 1.35), 32, 2.0, 0.35),
    area_light("Front softbox", (-1.5, 0.5, 0.8), 18, 1.2, 0.75),
    area_light("Broad front fill", (0.2, -2.0, 0.9), 13, 1.9, 1.0),
]

base_camera = Vector((-1.45, -1.70, 1.23 if STATE == "abierto" else 1.02))
bpy.ops.object.camera_add(location=base_camera)
camera = bpy.context.object
camera.name = "Camera_C07"
camera.data.lens = 52
scene.camera = camera


def look_at(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()


for mass_kg in ((5,) if PREVIEW else (5, 10)):
    factor = (mass_kg / 5.0) ** (1.0 / 3.0)
    body.scale = (factor, factor, factor)
    floor.location.z = -0.215 * factor
    camera.location = base_camera * factor
    look_at(camera, (0, 0, 0))
    for lamp, original in zip(lights, ((-0.7, -1.2, 1.8), (0.9, 1.4, 1.35),
                                       (-1.5, 0.5, 0.8), (0.2, -2.0, 0.9))):
        lamp.location = Vector(original) * factor
        look_at(lamp, (0, 0, 0))
    scene["alcance"] = "C07 conceptual; tapas deslizantes sin accionamiento ni prestaciones validadas"
    scene["native_fuente_sha256"] = DATA["source_native_sha256"]
    output = (Path("/private/tmp") / f"C07_preview_{STATE}.png" if PREVIEW
              else HERE / f"{mass_kg}kg" / f"C07_{mass_kg}kg_{STATE}.png")
    scene.render.filepath = str(output)
    if mass_kg == 5 and not PREVIEW:
        bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "5kg" / f"C07_5kg_{STATE}.blend"))
    bpy.ops.render.render(write_still=True)
    print("C07_RENDER_OK", output, flush=True)


if STATE == "abierto" and not PREVIEW:
    # A visual inspection cutaway hides CAD parts; it does not alter the model.
    for obj in model_objects:
        name = obj.name
        near_module = name.startswith(("modulo_C02_0_", "modulo_C02_2_"))
        if (name.startswith(("carroceria_C02_superior", "compuerta_C02_", "aro_C02_", "junta_C02_"))
                or (near_module and ("camisa_cuna_y_soportes" in name or "superior_" in name))):
            obj.hide_render = True
    for mass_kg in (5, 10):
        factor = (mass_kg / 5.0) ** (1.0 / 3.0)
        body.scale = (factor, factor, factor)
        floor.location.z = -0.215 * factor
        camera.location = Vector((-1.35, -1.45, 1.60)) * factor
        look_at(camera, (0, 0, 0))
        for lamp, original in zip(lights, ((-0.7, -1.2, 1.8), (0.9, 1.4, 1.35),
                                           (-1.5, 0.5, 0.8), (0.2, -2.0, 0.9))):
            lamp.location = Vector(original) * factor
            look_at(lamp, (0, 0, 0))
        scene["alcance"] = "Vista de inspeccion: piezas ocultas, no corte estructural"
        output = HERE / f"{mass_kg}kg" / f"C07_{mass_kg}kg_interior.png"
        scene.render.filepath = str(output)
        if mass_kg == 5:
            bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "5kg" / "C07_5kg_interior.blend"))
        bpy.ops.render.render(write_still=True)
        print("C07_INSPECCION_OK", output, flush=True)
