# Renders every earbud part on its own, for the parts catalogue plate.
# Run after earbud_blender.py, in the same Blender:
#     exec(open("/path/to/earshot-field-manual/tools/parts_blender.py").read())

import os

import bpy
from mathutils import Vector

ROOT = os.environ.get("FIELD_MANUAL", os.path.expanduser("~/Desktop/new/earshot-field-manual"))
OUT = os.path.join(ROOT, "renders", "parts")
os.makedirs(OUT, exist_ok=True)

scene = bpy.data.scenes["Earshot Manual"]
cam = scene.camera
source = bpy.data.collections["Bud exploded"]

PARTS = [
    ("01-ear-tip", ["Ear tip"]), ("02-acoustic-mesh", ["Acoustic mesh"]),
    ("03-front-shell", ["Front shell", "Nozzle"]), ("04-ir-wear-sensor", ["IR wear sensor"]),
    ("05-diaphragm", ["Diaphragm"]), ("06-voice-coil", ["Voice coil"]), ("07-magnet", ["Magnet"]),
    ("08-feedback-mic", ["Feedback mic"]), ("09-pcb", ["PCB", "Bluetooth SoC", "Flash", "PMIC"]),
    ("10-li-ion-cell", ["Li-ion cell", "Cell label"]), ("11-back-shell", ["Back shell"]),
    ("12-touch-pad", ["Touch pad"]), ("13-feed-forward-mic", ["Feed-forward mic"]),
    ("14-stem", ["Stem", "Stem cap"]), ("15-antenna", ["Antenna"]), ("16-case-magnet", ["Case magnet"]),
    ("17-talk-mic", ["Talk mic"]), ("18-pogo-contacts", ["Pogo contact 0", "Pogo contact 1"]),
]

for c in scene.collection.children:
    c.hide_render = c is not source
scene.render.resolution_x = scene.render.resolution_y = 420
direction = Vector((0.5, -1, 0.42)).normalized()
names = {o.name.split(".")[0]: o for o in source.objects}

for slug, members in PARTS:
    show = [names[m] for m in members]
    for o in source.objects:
        o.hide_render = o not in show
    pts = [o.matrix_world @ Vector(c) for o in show for c in o.bound_box]
    centre = sum(pts, Vector()) / len(pts)
    size = max((p - centre).length for p in pts)
    cam.location = centre + direction * 30
    cam.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    cam.data.ortho_scale = size * 2.3
    scene.render.filepath = os.path.join(OUT, slug + ".png")
    bpy.ops.render.render(write_still=True)

for o in source.objects:
    o.hide_render = False
result = {"parts": sorted(os.listdir(OUT))}
