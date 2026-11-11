"""C04: one exploratory C03 door guide/hinge layout, dimensions in mm.

Run with FreeCAD's freecadcmd. Output is a mechanism envelope study, not a
manufacturing design. The actual C03 door, ring and rotor are preserved.
"""
from pathlib import Path
import gzip
import hashlib
import json
import math
import FreeCAD as App
import Part
import Import

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'producto_C03/5kg/C03_5kg_cerrado.FCStd'
RULES = HERE.parent.parent / 'ejecucion/G3/C02/integracion_x160/REGLAS_TAPAS_CONCEPTUALES.json'
AXIS = App.Vector(-160, -124, 67.9767683408146)
STATES = (('cerrado', 0.0, 0.0), ('elevado', 10.0, 0.0), ('abierto', 10.0, 110.0))


def file_hash(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def cylinder(rad, length, base, direction):
    return Part.makeCylinder(rad, length, base, direction)


def add(doc, group, label, shape, color):
    obj = doc.addObject('Part::Feature', 'Pieza')
    obj.Label = label
    obj.Shape = shape
    group.addObject(obj)
    if obj.ViewObject:
        obj.ViewObject.ShapeColor = color
    return obj


def transform(shape, lift, angle):
    shape = shape.copy()
    shape.translate(App.Vector(0, 0, lift))
    shape.rotate(AXIS + App.Vector(0, 0, lift), App.Vector(1, 0, 0), angle)
    return shape


def measured_pair(a, b):
    try:
        return {'distancia_mm': a.distToShape(b)[0], 'interseccion_mm3': a.common(b).Volume}
    except Exception as exc:
        return {'error': str(exc)}


def mesh(shape):
    vertices, faces = shape.tessellate(0.35)
    return {'vertices': [[v.x, v.y, v.z] for v in vertices], 'faces': [list(f) for f in faces]}


def main():
    rules = json.loads(RULES.read_text())
    rule = next(r for r in rules if r['name'] == 'compuerta_C02_0_superior')
    assert abs(rule['lift_mm'] - 10) < 1e-9 and abs(rule['angle_deg'] - 110) < 1e-9
    assert all(abs(a-b) < 1e-8 for a,b in zip(rule['axis_closed'], (AXIS.x, AXIS.y, AXIS.z)))
    source = App.openDocument(str(SOURCE))
    parts = {o.Label: o.Shape.copy() for o in source.Objects if o.Name.startswith('pieza_')}
    wanted = ['compuerta_C02_0_superior', 'aro_C02_0_superior', 'modulo_C02_0_rotor_copa',
              'carroceria_C02_superior004', 'modulo_C02_0_camisa_cuna_y_soportes']
    assert all(x in parts for x in wanted), [x for x in wanted if x not in parts]
    door, ring, rotor, body, duct = [parts[x] for x in wanted]
    # Two conceptual linear guides and sliders. Rail positions and all hardware
    # sizes are proposals, not selected commercial hardware.
    fixed = []
    slider = []
    arms = []
    for x in (-185.0, -135.0):
        rail = cylinder(1.5, 33, App.Vector(x, -140, 49), App.Vector(0,0,1))
        fixed.append(('guia_fija', rail))
        outer = cylinder(3.2, 7, App.Vector(x, -140, 64.5), App.Vector(0,0,1))
        bore = cylinder(1.7, 7.2, App.Vector(x, -140, 64.4), App.Vector(0,0,1))
        slide = outer.cut(bore)
        # A bridge and bearing are modeled separately; their attachment to the
        # real airframe and actuator is deliberately not assumed.
        bridge = Part.makeBox(5, 16, 4, App.Vector(x-2.5, -140, AXIS.z-2))
        bearing = cylinder(3.0, 5, App.Vector(x-2.5,-124,AXIS.z), App.Vector(1,0,0)).cut(
            cylinder(1.2, 5.2, App.Vector(x-2.6,-124,AXIS.z), App.Vector(1,0,0)))
        slider.extend([('patin_movil',slide), ('puente_reserva',bridge), ('cojinete_reserva',bearing)])
    pin = cylinder(1.0, 56, App.Vector(-188,-124,AXIS.z), App.Vector(1,0,0))
    slider.append(('pasador',pin))
    for x in (-176.0, -144.0):
        # Exploratory tabs intended to connect the cover to the common pin.
        # Actual contact is measured below, not asserted.
        a=App.Vector(x-1.5,-124,AXIS.z)
        b=App.Vector(x-1.5,-116,80)
        vec=b-a
        arm=cylinder(2.0,vec.Length,a,vec.normalize())
        arms.append(('brazo_tapa_reserva',arm))
    result = {'revision':'C04_estudio_local_v2', 'source':str(SOURCE), 'source_sha256':file_hash(SOURCE),
              'scope':'Una compuerta, disposicion mecanica exploratoria; no demuestra integracion, cargas ni vuelo',
              'door':rule['name'], 'axis_mm':[AXIS.x,AXIS.y,AXIS.z], 'states':[]}
    for name, lift, angle in STATES:
        doc=App.newDocument('C04_'+name)
        group=doc.addObject('App::Part','Estudio_C04')
        note=doc.addObject('App::FeaturePython','Alcance')
        note.addProperty('App::PropertyString','Advertencia','Proyecto')
        note.Advertencia='ESTUDIO LOCAL: piezas de guia y brazos son reservas no validadas; sin actuador ni fijaciones.'
        shapes=[]
        shapes.append(('compuerta_C03', transform(door,lift,angle), (0.19,0.22,0.27)))
        shapes.append(('aro_C03', ring, (0.45,0.47,0.50)))
        shapes.append(('rotor_C03', rotor, (0.20,0.22,0.24)))
        for n,s in fixed: shapes.append((n,s,(0.7,0.70,0.72)))
        for n,s in slider: shapes.append((n,transform(s,lift,0),(0.80,0.50,0.12)))
        for n,s in arms: shapes.append((n,transform(s,lift,angle),(0.95,0.35,0.08)))
        items=[]
        meshes=[]
        for label,shape,color in shapes:
            if shape.isNull() or not shape.isValid() or not shape.Solids:
                raise RuntimeError('Forma invalida '+name+' '+label)
            items.append(add(doc,group,label,shape,color))
            meshes.append({'name':label,'rgb':color,**mesh(shape)})
        doc.recompute()
        fc=HERE / ('C04_'+name+'.FCStd')
        step=HERE / ('C04_'+name+'.step')
        doc.saveAs(str(fc))
        Import.export([group],str(step))
        with gzip.open(HERE / ('C04_'+name+'_malla.json.gz'),'wt',encoding='utf8') as f:
            json.dump(meshes,f,separators=(',',':'))
        # Evaluate a sample at each endpoint, and specifically whether the
        # proposed connecting arms meet the physical cover.
        actual_door=transform(door,lift,angle)
        checks=[]
        for j,(label,s) in enumerate(fixed + [(n,transform(v,lift,0)) for n,v in slider] + [(n,transform(v,lift,angle)) for n,v in arms]):
            for obs_name,obs in [('rotor_C03',rotor),('carroceria_superior_C03',body),('camisa_C03',duct)]:
                checks.append({'elemento':label+'_'+str(j), 'obstaculo':obs_name, **measured_pair(s,obs)})
            if label=='brazo_tapa_reserva':
                checks.append({'elemento':label+'_'+str(j), 'obstaculo':'compuerta', **measured_pair(s,actual_door)})
        entry={'estado':name,'elevacion_mm':lift,'angulo_deg':angle,'partes':len(shapes),'comprobaciones':checks,
               'fcstd':fc.name,'fcstd_sha256':file_hash(fc),'step':step.name,'step_sha256':file_hash(step)}
        result['states'].append(entry)
        (HERE/'RESULTADOS_PARCIALES.json').write_text(json.dumps(result,indent=2)+'\n')
        App.closeDocument(doc.Name)
        print('ESTADO_COMPLETADO',name,flush=True)
    App.closeDocument(source.Name)
    (HERE/'RESULTADOS.json').write_text(json.dumps(result,indent=2)+'\n')
    print('C04_GENERADO',flush=True)

main()
