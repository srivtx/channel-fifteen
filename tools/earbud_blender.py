# Builds the field manual's earbud and charging case in Blender and renders the plates' artwork.
#
# Run inside Blender (Scripting tab, or through the Blender MCP add-on):
#     exec(open("/path/to/earshot-field-manual/tools/earbud_blender.py").read())
#
# Everything lives in its own scene, "Earshot Manual", so the open file is left alone.
# Writes renders/assembled.png, renders/exploded.png, renders/case.png and
# renders/exploded.json (each part's position in the exploded render, for the SVG callouts).

import json
import math
import os

import bpy
import bmesh
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in globals() else os.environ.get(
    "FIELD_MANUAL", os.path.expanduser("~/Desktop/new/earshot-field-manual"))
OUT = os.path.join(ROOT, "renders")
os.makedirs(OUT, exist_ok=True)

# The manual's palette: bone paper, ink, and three riso inks.
PALETTE = {
    "shell": "#E6DFCF",
    "shell_dark": "#CFC6B2",
    "tip": "#9FB8A6",
    "ink": "#1B1A17",
    "vermilion": "#E0462F",
    "cobalt": "#2C4FA3",
    "green": "#2E8B57",
    "ochre": "#D9A441",
    "steel": "#A9ADB0",
    "gold": "#C9A227",
}


def rgba(hex_):
    h = hex_.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*lin, 1.0)


def material(name):
    mat = bpy.data.materials.get("fm_" + name) or bpy.data.materials.new("fm_" + name)
    mat.diffuse_color = rgba(PALETTE[name])
    return mat


# ---------------------------------------------------------------- scene

scene = bpy.data.scenes.get("Earshot Manual") or bpy.data.scenes.new("Earshot Manual")
(bpy.context.window or bpy.context.window_manager.windows[0]).scene = scene
for obj in list(scene.collection.all_objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for coll in list(scene.collection.children):
    bpy.data.collections.remove(coll)


def collection(name):
    coll = bpy.data.collections.new(name)
    scene.collection.children.link(coll)
    return coll


def link(obj, coll, name, mat):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    coll.objects.link(obj)
    obj.name = name
    obj.data.materials.clear()
    obj.data.materials.append(material(mat))
    return obj


def smooth(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True


def add(kind, coll, name, mat, loc, rot=(0, 0, 0), scale=(1, 1, 1), **kw):
    ops = {
        "cyl": bpy.ops.mesh.primitive_cylinder_add,
        "cone": bpy.ops.mesh.primitive_cone_add,
        "cube": bpy.ops.mesh.primitive_cube_add,
        "sphere": bpy.ops.mesh.primitive_uv_sphere_add,
        "torus": bpy.ops.mesh.primitive_torus_add,
    }
    if kind in ("cyl", "cone"):
        kw.setdefault("vertices", 64)
    if kind == "sphere":
        kw.setdefault("segments", 64)
        kw.setdefault("ring_count", 32)
    ops[kind](location=loc, rotation=rot, **kw)
    obj = bpy.context.active_object
    obj.scale = scale
    if kind != "cube":
        smooth(obj)
    return link(obj, coll, name, mat)


def half_shell(coll, name, front):
    """One half of the bud's body: an ellipsoid cut at x = 0, hollowed with a solidify."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1, location=(0, 0, 0))
    obj = bpy.context.active_object
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # Poles along X, so the cut falls exactly on a ring of vertices and the rim is clean.
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "Y"))
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, 0), plane_no=(1, 0, 0),
                           clear_outer=front, clear_inner=not front)
    bm.to_mesh(obj.data)
    bm.free()
    obj.scale = (1.0, 0.84, 0.9)
    smooth(obj)
    mod = obj.modifiers.new("shell", "SOLIDIFY")
    mod.thickness = 0.06
    mod.offset = -1
    # A hair of a gap between the halves reads as a real seam instead of z-fighting.
    obj.location.x = -0.006 if front else 0.006
    return link(obj, coll, name, "shell")


Y90 = (0, math.radians(90), 0)


def dome(coll):
    """A mushroom ear tip: half an ellipsoid, hollow, opening toward the nozzle."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1, location=(0, 0, 0))
    obj = bpy.context.active_object
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # Poles along X, so the cut falls exactly on a ring of vertices and the rim is clean.
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "Y"))
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, 0), plane_no=(1, 0, 0), clear_outer=True)
    bm.to_mesh(obj.data)
    bm.free()
    obj.scale = (0.36, 0.48, 0.48)
    obj.location = (-1.16, 0, 0)
    smooth(obj)
    obj.modifiers.new("shell", "SOLIDIFY").thickness = 0.12
    return link(obj, coll, "Ear tip", "tip")


def build_bud(coll, explode):
    """Adds one earbud's parts. `explode` moves each part out along the bud's axis.

    The bud points its nozzle down -X (into the ear); the stem hangs down -Z.
    Returns {part key: [objects]} for the callouts.
    """
    parts = {}

    def put(key, objs, offset):
        objs = objs if isinstance(objs, list) else [objs]
        if explode:
            for o in objs:
                o.location += Vector(offset)
        parts[key] = objs

    put("ear_tip", dome(coll), (-3.1, 0, 0))
    put("mesh", add("cyl", coll, "Acoustic mesh", "ink", (-1.2, 0, 0), Y90, radius=0.26, depth=0.03),
        (-2.55, 0, 0))
    put("front_shell", [half_shell(coll, "Front shell", True),
                        add("cyl", coll, "Nozzle", "shell", (-0.98, 0, 0), Y90, radius=0.28, depth=0.45)],
        (-1.75, 0, 0))
    put("wear_sensor", add("cube", coll, "IR wear sensor", "vermilion", (-0.62, 0, 0.6), scale=(0.1, 0.16, 0.06)),
        (-1.75, 0, 1.05))
    put("diaphragm", add("cone", coll, "Diaphragm", "ochre", (-0.66, 0, 0), Y90, radius1=0.56, radius2=0.14, depth=0.16),
        (-0.95, 0, 0))
    put("voice_coil", add("torus", coll, "Voice coil", "vermilion", (-0.52, 0, 0), Y90, major_radius=0.17,
                          minor_radius=0.035, major_segments=48, minor_segments=12),
        (-0.62, 0, 0))
    put("magnet", add("cyl", coll, "Magnet", "steel", (-0.4, 0, 0), Y90, radius=0.36, depth=0.2),
        (-0.3, 0, 0))
    put("fb_mic", add("cube", coll, "Feedback mic", "cobalt", (-0.82, 0, -0.42), scale=(0.07, 0.1, 0.05)),
        (-0.95, 0, -1.05))
    pcb = add("cyl", coll, "PCB", "green", (-0.08, 0, 0), Y90, radius=0.72, depth=0.05)
    soc = add("cube", coll, "Bluetooth SoC", "ink", (-0.03, 0.12, 0.08), scale=(0.03, 0.22, 0.22))
    flash = add("cube", coll, "Flash", "ink", (-0.03, -0.3, 0.12), scale=(0.025, 0.1, 0.14))
    pmic = add("cube", coll, "PMIC", "ink", (-0.03, -0.18, -0.34), scale=(0.025, 0.12, 0.1))
    for key, obj in (("pcb", pcb), ("soc", soc), ("flash", flash), ("pmic", pmic)):
        put(key, obj, (0.55, 0, 0))
    battery = add("cyl", coll, "Li-ion cell", "steel", (0.3, 0, 0), Y90, radius=0.56, depth=0.3)
    band = add("cyl", coll, "Cell label", "vermilion", (0.3, 0, 0), Y90, radius=0.565, depth=0.12)
    put("battery", [battery, band], (1.45, 0, 0))
    put("back_shell", half_shell(coll, "Back shell", False), (2.45, 0, 0))
    put("ff_mic", add("cyl", coll, "Feed-forward mic", "cobalt", (0.78, 0, 0.5), Y90, radius=0.07, depth=0.08),
        (3.1, 0, 0.9))
    # The stem hangs from the back of the head and sweeps forward under it, like most stem buds.
    stem_parts = {
        "stem": [add("cone", coll, "Stem", "shell", (0.42, 0, -1.25), scale=(1, 0.72, 1), radius1=0.21,
                     radius2=0.29, depth=1.5),
                 add("sphere", coll, "Stem cap", "shell", (0.42, 0, -2.0), scale=(1, 0.72, 0.8), radius=0.21)],
        "touch_pad": [add("cyl", coll, "Touch pad", "gold", (0.42, -0.2, -0.82), (math.radians(90), 0, 0),
                          scale=(0.85, 2.0, 1), radius=0.16, depth=0.03)],
        "antenna": [add("cube", coll, "Antenna", "cobalt", (0.42, 0.06, -1.2), scale=(0.03, 0.04, 0.5))],
        "case_magnet": [add("cyl", coll, "Case magnet", "steel", (0.42, 0, -1.6), radius=0.12, depth=0.2)],
        "talk_mic": [add("cyl", coll, "Talk mic", "cobalt", (0.42, -0.15, -1.9), (math.radians(90), 0, 0),
                         radius=0.06, depth=0.05)],
        "pogo": [add("cyl", coll, f"Pogo contact {i}", "gold", (0.42 + dx, 0, -2.16), radius=0.05, depth=0.06)
                 for i, dx in enumerate((-0.09, 0.09))],
    }
    pivot, tilt = Vector((0.42, 0, -0.5)), math.radians(14)
    for objs in stem_parts.values():
        for o in objs:
            rel = o.location - pivot
            o.location = pivot + Vector((rel.x * math.cos(tilt) + rel.z * math.sin(tilt), rel.y,
                                         -rel.x * math.sin(tilt) + rel.z * math.cos(tilt)))
            o.rotation_euler.y += tilt
    offsets = {"stem": (2.45, 0, -0.75), "touch_pad": (3.35, 0, -0.35), "antenna": (3.45, 0, -0.75),
               "case_magnet": (1.3, 0, -0.8), "talk_mic": (1.3, 0, -1.0), "pogo": (2.45, 0, -1.35)}
    for key, objs in stem_parts.items():
        put(key, objs, offsets[key])
    return parts


# ---------------------------------------------------------------- the three set-ups

assembled = collection("Bud assembled")
assembled_parts = build_bud(assembled, explode=False)
exploded = collection("Bud exploded")
parts = build_bud(exploded, explode=True)
case = collection("Case with buds")


def rounded_box(name, loc, size, bevel, mat, coll):
    obj = add("cube", coll, name, mat, loc, scale=(size[0] / 2, size[1] / 2, size[2] / 2))
    mod = obj.modifiers.new("round", "BEVEL")
    mod.width = bevel
    mod.segments = 8
    mod.limit_method = "NONE"
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


rounded_box("Case base", (0, 0, -0.75), (6.2, 3.2, 1.9), 0.75, "shell_dark", case)
rounded_box("Case well", (0, -0.15, 0.16), (4.8, 1.9, 0.12), 0.08, "ink", case)
lid = rounded_box("Case lid", (0, 1.55, 1.15), (6.2, 0.9, 2.8), 0.42, "shell", case)
lid.rotation_euler = (math.radians(-18), 0, 0)
rounded_box("Hall sensor", (0, -0.9, 0.24), (0.36, 0.2, 0.06), 0.02, "vermilion", case)
rounded_box("Case LED", (0, -1.62, -0.6), (0.18, 0.04, 0.18), 0.02, "green", case)
# Two buds standing stem-down in the case, nozzles toward the hinge.
for side, x in (("L", -1.3), ("R", 1.3)):
    bud = collection(f"Case bud {side}")
    build_bud(bud, explode=False)
    holder = bpy.data.objects.new(f"Case bud {side}", None)
    case.objects.link(holder)
    for obj in list(bud.objects):
        bud.objects.unlink(obj)
        case.objects.link(obj)
        obj.parent = holder
    bpy.data.collections.remove(bud)
    holder.location = (x, -0.1, 1.55)
    holder.rotation_euler = (0, 0, math.radians(-90 if side == "R" else -90))
    if side == "L":
        holder.scale = (1, -1, 1)

# ---------------------------------------------------------------- camera and look

cam_data = bpy.data.cameras.new("Plate camera")
cam_data.type = "ORTHO"
cam = bpy.data.objects.new("Plate camera", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.engine = "BLENDER_WORKBENCH"
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.display.render_aa = "16"
shading = scene.display.shading
shading.light = "STUDIO"
shading.color_type = "MATERIAL"
shading.show_object_outline = True
shading.object_outline_color = rgba(PALETTE["ink"])[:3]
shading.show_cavity = True
shading.cavity_type = "BOTH"
shading.show_specular_highlight = False
shading.show_shadows = True
shading.shadow_intensity = 0.35
scene.display.light_direction = (0.45, -0.35, 0.82)
scene.view_settings.view_transform = "Standard"


def aim(direction, target, scale):
    d = Vector(direction).normalized()
    cam.location = Vector(target) + d * 30
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    cam_data.ortho_scale = scale


def only(coll):
    for c in scene.collection.children:
        c.hide_render = c is not coll
        c.hide_viewport = c is not coll


def anchors(parts, name):
    """Where each part landed in the last render, in pixels from the top left."""
    bpy.context.view_layer.update()
    w, h = scene.render.resolution_x, scene.render.resolution_y
    out = {}
    for key, objs in parts.items():
        pts = [o.matrix_world @ Vector(corner) for o in objs for corner in o.bound_box]
        p = world_to_camera_view(scene, cam, sum(pts, Vector()) / len(pts))
        out[key] = [round(p.x * w, 1), round((1 - p.y) * h, 1)]
    with open(os.path.join(OUT, name + ".json"), "w") as f:
        json.dump({"size": [w, h], "parts": out}, f, indent=1)
    return out


def render(name, coll, size, direction, target, scale):
    only(coll)
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    aim(direction, target, scale)
    scene.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)


render("assembled", assembled, (1200, 1200), (0.3, -1, 0.3), (-0.1, 0, -0.6), 4.0)
anchors(assembled_parts, "assembled")
render("case", case, (1600, 1200), (0.25, -1, 0.7), (0, 0.3, 0.6), 8.8)
render("exploded", exploded, (2400, 1500), (0.5, -1, 0.42), (0.2, 0, -0.75), 11.2)
exploded_anchors = anchors(parts, "exploded")

# Leave the exploded bud on screen for whoever is watching.
only(exploded)
result = {"renders": sorted(os.listdir(OUT)), "anchors": exploded_anchors}
