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
    "navy": "#1B2F63",
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


def rounded_box(name, loc, size, bevel, mat, coll):
    obj = add("cube", coll, name, mat, loc, scale=(size[0] / 2, size[1] / 2, size[2] / 2))
    mod = obj.modifiers.new("round", "BEVEL")
    mod.width = bevel
    mod.segments = 8
    mod.limit_method = "NONE"
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


# The case: a pebble split into a body and a hinged lid. The buds stand stem-down in wells
# cut to their shape, nozzles toward the hinge. Everything is in the case's own units, the
# same as the bud's, so the website can drop the bud model straight into a well.
CASE_HALF = (2.85, 1.95, 2.15)
CASE_MID = -0.45
SPLIT = -0.35
HINGE = Vector((0, 1.82, SPLIT))
DOCKS = {"L": Vector((-1.3, -0.22, 0)), "R": Vector((1.3, -0.22, 0))}
DOCK_ROT = (0, math.radians(-14), math.radians(-90))  # stem straight down, nozzle to the hinge
case_body = collection("Case body")
case_lid = collection("Case lid")
case_buds = collection("Case buds")


def baked(obj):
    """Applies an object's modifiers to its mesh."""
    deps = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(deps))
    obj.modifiers.clear()
    old, obj.data = obj.data, mesh
    bpy.data.meshes.remove(old)
    return obj


def pebble_half(name, coll, mat, below):
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.data.transform(Matrix.Diagonal(Vector((*CASE_HALF, 1))))
    bev = obj.modifiers.new("round", "BEVEL")
    bev.width, bev.segments, bev.limit_method = 1.15, 6, "NONE"
    obj.modifiers.new("smooth", "SUBSURF").levels = 2
    baked(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(Matrix.Translation((0, 0, CASE_MID)))
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    cut = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, SPLIT), plane_no=(0, 0, 1),
                                 clear_outer=below, clear_inner=not below)
    rim = [e for e in cut["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=True, edges=rim)
    bm.to_mesh(obj.data)
    bm.free()
    smooth(obj)
    obj.data.polygons.foreach_set("use_smooth", [abs(p.normal.z) < 0.999 for p in obj.data.polygons])
    return link(obj, coll, name, mat)


body = pebble_half("Case body", case_body, "cobalt", True)
# One bud per well, posed exactly where it docks; its shape is what the wells are cut from.
for side, at in DOCKS.items():
    holder = bpy.data.objects.new(f"Case bud {side}", None)
    case_buds.objects.link(holder)
    tmp = collection("tmp bud")
    build_bud(tmp, explode=False)
    for obj in list(tmp.objects):
        tmp.objects.unlink(obj)
        case_buds.objects.link(obj)
        obj.parent = holder
    bpy.data.collections.remove(tmp)
    holder.location, holder.rotation_euler = at, DOCK_ROT
    dock = bpy.data.objects.new(f"Dock {side}", None)
    case_body.objects.link(dock)
    dock.location, dock.rotation_euler = at, DOCK_ROT
bpy.context.view_layer.update()


def base_name(o):
    return o.name.split(".")[0]


cutters = []
for side in DOCKS:
    kids = {o for o in case_buds.objects if o.parent and o.parent.name == f"Case bud {side}"}
    for o in case_buds.objects:
        o.select_set(False)
    head = [o for o in kids if base_name(o) in ("Front shell", "Back shell", "Nozzle", "Ear tip")]
    stem = [o for o in kids if base_name(o) in ("Stem", "Stem cap")]
    for group, kind in ((head, "head"), (stem, "stem")):
        pts = [o.matrix_world @ Vector(c) for o in group for c in o.bound_box]
        lo = Vector([min(p[i] for p in pts) for i in range(3)])
        hi = Vector([max(p[i] for p in pts) for i in range(3)])
        mid, size = (lo + hi) / 2, hi - lo
        if kind == "head":
            c = add("sphere", case_body, "cutter", "navy", mid, scale=(size.x / 2 + 0.035, size.y / 2 + 0.035, size.z / 2 + 0.035))
        else:
            top = SPLIT + 0.6
            c = add("cyl", case_body, "cutter", "navy", (mid.x, mid.y, (lo.z - 0.06 + top) / 2),
                    scale=(size.x / 2 + 0.05, size.y / 2 + 0.05, (top - lo.z + 0.06) / 2), radius=1, depth=2)
        cutters.append(c)
for c in cutters:
    mod = body.modifiers.new("well", "BOOLEAN")
    mod.operation, mod.solver, mod.object = "DIFFERENCE", "EXACT", c
    mod.material_mode = "TRANSFER"
baked(body)
for c in cutters:
    bpy.data.objects.remove(c, do_unlink=True)

# Charging pads at the bottom of each stem well, the Hall sensor, the LED and the hinge barrel.
for o in [o for o in case_buds.objects if base_name(o).startswith("Pogo contact")]:
    p = o.matrix_world.translation
    add("cyl", case_body, "Charge pad", "gold", (p.x, p.y, p.z - 0.07), radius=0.07, depth=0.04)
rounded_box("Hall sensor", (0, -1.05, SPLIT + 0.01), (0.34, 0.2, 0.05), 0.02, "vermilion", case_body)
rounded_box("Case LED", (0, -CASE_HALF[1] - 0.005, -1.15), (0.22, 0.05, 0.22), 0.03, "green", case_body)
add("cyl", case_body, "Hinge", "steel", HINGE + Vector((0, 0.06, -0.02)), (0, math.radians(90), 0), radius=0.09, depth=1.6)

lid = pebble_half("Case lid", case_lid, "shell", False)
lid.data.transform(Matrix.Translation((0, 0, 0.012)))  # a hair of a seam
# "15" in a 5x7 pixel face on top of the lid: the channel the whole story is about.
GLYPHS = {"1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
          "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"]}
px = 0.085
top = CASE_MID + CASE_HALF[2]
for gi, ch in enumerate("15"):
    for r, row in enumerate(GLYPHS[ch]):
        for c, bit in enumerate(row):
            if bit == "1":
                x = (gi * 6 + c - 5) * px
                y = (3 - r) * px
                add("cube", case_lid, "Lid pixel", "vermilion", (x, y, top + 0.005), scale=(px * 0.46, px * 0.46, 0.02))
# Inside the lid, a recessed panel and the magnet that holds it shut; seen only while it's open.
rounded_box("Lid liner", (0, -0.1, SPLIT + 0.005), (4.7, 2.7, 0.03), 0.4, "shell_dark", case_lid)
rounded_box("Lid magnet", (0, -1.45, SPLIT + 0.02), (0.6, 0.18, 0.04), 0.03, "steel", case_lid)
# The lid turns about the hinge: its pixels and shell share one origin there.
lid_parts = list(case_lid.objects)
pivot = bpy.data.objects.new("Lid hinge", None)
case_lid.objects.link(pivot)
pivot.location = HINGE
for o in lid_parts:
    o.parent = pivot
    o.matrix_parent_inverse = Matrix.Translation(-HINGE)
pivot.rotation_euler.x = math.radians(-105)  # open for the plate; the website closes it

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


def only(*colls):
    for c in scene.collection.children:
        c.hide_render = c not in colls
        c.hide_viewport = c not in colls


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
    only(*(coll if isinstance(coll, tuple) else (coll,)))
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    aim(direction, target, scale)
    scene.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)


render("assembled", assembled, (1200, 1200), (0.3, -1, 0.3), (-0.1, 0, -0.6), 4.0)
anchors(assembled_parts, "assembled")
render("case", (case_body, case_lid, case_buds), (1600, 1200), (0.3, -1, 0.75), (0, 0.6, 0.2), 9.4)
anchors({"lid": [lid], "bud": [o for o in case_buds.objects if o.name.startswith("Back shell")][:1],
         "hall": [bpy.data.objects["Hall sensor"]], "led": [bpy.data.objects["Case LED"]], "body": [body]}, "case")
render("exploded", exploded, (2400, 1500), (0.5, -1, 0.42), (0.2, 0, -0.75), 11.2)
exploded_anchors = anchors(parts, "exploded")

# Leave the exploded bud on screen for whoever is watching.
only(exploded)
result = {"renders": sorted(os.listdir(OUT)), "anchors": exploded_anchors}
