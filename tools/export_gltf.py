# Exports the earbud and the case as glTF for the website's 3D story, plus each part's
# explode offset. Run in Blender after earbud_blender.py:
#     exec(open("/path/to/earshot-field-manual/tools/export_gltf.py").read())

import json
import os

import bpy

ROOT = os.environ.get("FIELD_MANUAL", os.path.expanduser("~/Desktop/new/earshot-field-manual"))
OUT = os.path.join(ROOT, "site", "public", "models")
os.makedirs(OUT, exist_ok=True)
scene = bpy.data.scenes["Earshot Manual"]

# glTF wants a Principled BSDF; copy each flat colour into one.
for mat in bpy.data.materials:
    if not mat.name.startswith("fm_"):
        continue
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = mat.diffuse_color
        bsdf.inputs["Roughness"].default_value = 0.55


def base(name):
    return name.split(".")[0]


def export(collection, filename):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.data.collections[collection].all_objects:
        obj.hide_set(False)
        obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, filename), export_format="GLB", use_selection=True,
                              export_apply=True, export_yup=True)


for c in scene.collection.children:
    c.hide_viewport = False
export("Bud assembled", "bud.glb")
export("Case with buds", "case.glb")

assembled = {base(o.name): o.location.copy() for o in bpy.data.collections["Bud assembled"].objects}
offsets = {}
for o in bpy.data.collections["Bud exploded"].objects:
    a = assembled.get(base(o.name))
    if a is not None:
        d = o.location - a
        offsets[base(o.name)] = [round(d.x, 4), round(d.z, 4), round(-d.y, 4)]  # Blender Z-up → glTF Y-up
with open(os.path.join(OUT, "explode.json"), "w") as f:
    json.dump(offsets, f, indent=1)
result = {"files": sorted(os.listdir(OUT)), "parts": len(offsets)}
