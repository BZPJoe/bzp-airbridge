"""Render the supplied STL geometry without changing or exporting its mesh.
Run with Blender --background --python tools/render_makerworld_case.py.
"""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'makerworld'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.world.color = (0.12, 0.12, 0.12)

def material(name, color, roughness=.5, metallic=0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = roughness
    bs.inputs['Metallic'].default_value = metallic
    return m

base_mat = material('Neutral silver', (.42, .49, .53), .45)
lid_mat = material('Cyan accent', (.015, .45, .62), .45)
ground_mat = material('Charcoal', (.015, .022, .027), .65)
for filename, x, mat in [('Vornado Fan Controller Case.stl', -3.6, base_mat), ('Vornado Fan Controller Case Top.stl', 3.6, lid_mat)]:
    bpy.ops.wm.stl_import(filepath=str(ROOT/'hardware/enclosure/user-supplied'/filename))
    obj=bpy.context.object
    bounds=[Vector(v) for v in obj.bound_box]
    center=Vector(((min(v.x for v in bounds)+max(v.x for v in bounds))/2,
                   (min(v.y for v in bounds)+max(v.y for v in bounds))/2,
                   min(v.z for v in bounds)))
    obj.scale=(.1,.1,.1)
    obj.location=Vector((x,0,0))-center*.1
    obj.data.materials.clear()
    obj.data.materials.append(mat)

bpy.ops.mesh.primitive_plane_add(size=200)
bpy.context.object.data.materials.append(ground_mat)
for loc, energy, size in [((0,-5,12),2200,9), ((-9,3,8),1700,7), ((8,5,9),1800,6)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    lamp=bpy.context.object;lamp.data.energy=energy;lamp.data.shape='DISK';lamp.data.size=size
    lamp.rotation_euler=(Vector((0,0,1))-lamp.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(8,-15,15))
camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,.8))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=17
scene.camera=camera

def caption(body, y, size):
    bpy.ops.object.text_add()
    t=bpy.context.object;t.data.body=body;t.data.size=size;t.data.align_x='CENTER'
    q=camera.rotation_euler.to_quaternion()
    t.location=camera.location+q@Vector((0,y,-11))
    t.rotation_euler=camera.rotation_euler
    m=material('Caption '+body,(.72,.9,1),.8)
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Emission Color'].default_value=(.72,.9,1,1)
    bs.inputs['Emission Strength'].default_value=.7
    t.data.materials.append(m)
caption('BZP AIRBRIDGE',4.7,.6)
caption('CASE BASE + TOP',4.05,.28)
caption('ACTUAL STL GEOMETRY  /  RENDER, NOT A PRINT PHOTO',-4.9,.22)
scene.render.filepath=str(OUT/'case-parts-render.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'case-parts-render.blend'))
bpy.ops.render.render(write_still=True)
