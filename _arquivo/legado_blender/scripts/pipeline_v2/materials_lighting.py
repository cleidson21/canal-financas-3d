"""Localization-safe material library and warm cinematic low-poly lighting setup."""

import math
import bpy
from . import config
from .scene_setup import link_to_collection


def create_stylized_material(name, rgba, roughness=0.72, metallic=0.0, emission_strength=0.0):
    """Create a Principled BSDF material safely across any Blender language localization."""
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)

    # Set viewport solid color as well
    mat.diffuse_color = rgba

    # In Blender 5.0+, node_tree is created by default; avoid deprecated use_nodes setter if possible
    if mat.node_tree is None:
        mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Locate Principled BSDF by bl_idname (avoids pt_BR 'BSDF - Pré-fundamentado' lookup bug)
    bsdf = next((n for n in nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)
    output = next((n for n in nodes if n.bl_idname == "ShaderNodeOutputMaterial"), None)

    if not bsdf:
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    if not output:
        output = nodes.new(type="ShaderNodeOutputMaterial")
        links.new(bsdf.outputs[0], output.inputs[0])

    # Set shader parameters by input identifier/name
    if "Base Color" in bsdf.inputs:
        bsdf.inputs["Base Color"].default_value = rgba
    else:
        bsdf.inputs[0].default_value = rgba

    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = roughness
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.35

    if emission_strength > 0.0:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = rgba
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength

    return mat


def build_material_library():
    """Build all palette materials and return a dictionary keyed by palette name."""
    mats = {}
    p = config.PALETTE

    roughness_overrides = {
        "new_shoe_gold": (0.32, 0.25, 0.05),
        "new_shoe_red": (0.38, 0.05, 0.0),
        "eye_white": (0.25, 0.0, 0.08),
        "eye_dark": (0.15, 0.0, 0.0),
        "sign_x_red": (0.35, 0.0, 0.22),
        "milk_white": (0.35, 0.0, 0.12),
        "milk_blue": (0.35, 0.0, 0.12),
        "sign_board": (0.45, 0.0, 0.08),
        "cloud_white": (0.85, 0.0, 0.15),
    }

    for key, rgba in p.items():
        rough, metal, emis = roughness_overrides.get(key, (0.74, 0.0, 0.0))
        mats[key] = create_stylized_material(
            name=f"Mat_{key}",
            rgba=rgba,
            roughness=rough,
            metallic=metal,
            emission_strength=emis,
        )

    return mats


def setup_world_and_lighting(scene, col_lights):
    """Configure warm sky world shader and 3-point + stall fill lighting with soft shadows."""
    world = bpy.data.worlds.get("Ceu_Vila_LowPoly")
    if not world:
        world = bpy.data.worlds.new("Ceu_Vila_LowPoly")
    scene.world = world

    if world.node_tree is None:
        world.use_nodes = True

    wnodes = world.node_tree.nodes
    wlinks = world.node_tree.links
    bg = next((n for n in wnodes if n.bl_idname == "ShaderNodeBackground"), None)
    wout = next((n for n in wnodes if n.bl_idname == "ShaderNodeOutputWorld"), None)
    if not bg:
        bg = wnodes.new(type="ShaderNodeBackground")
    if not wout:
        wout = wnodes.new(type="ShaderNodeOutputWorld")
        wlinks.new(bg.outputs[0], wout.inputs[0])

    bg.inputs[0].default_value = config.PALETTE["sky_warm"]
    bg.inputs[1].default_value = 0.48

    # 1. Key Light: Warm Golden Sun with soft shadow angle
    sun_data = bpy.data.lights.new(name="Sol_Principal", type="SUN")
    sun_data.energy = 3.8
    sun_data.color = (1.0, 0.94, 0.82)
    if hasattr(sun_data, "angle"):
        sun_data.angle = math.radians(6.5)  # Soft shadows
    sun_obj = bpy.data.objects.new(name="Sol_Principal", object_data=sun_data)
    sun_obj.location = (-3.0, -4.0, 6.0)
    sun_obj.rotation_euler = (math.radians(44), math.radians(-18), math.radians(-26))
    link_to_collection(sun_obj, col_lights)

    # 2. Fill Light: Large soft area light from front-right to lift dark shadows without washing out contrast
    fill_data = bpy.data.lights.new(name="Luz_Preenchimento", type="AREA")
    fill_data.energy = 75.0
    fill_data.color = (0.85, 0.92, 1.0)
    if hasattr(fill_data, "size"):
        fill_data.size = 7.0
    fill_obj = bpy.data.objects.new(name="Luz_Preenchimento", object_data=fill_data)
    fill_obj.location = (4.5, -5.5, 4.2)
    fill_obj.rotation_euler = (math.radians(55), math.radians(15), math.radians(32))
    link_to_collection(fill_obj, col_lights)

    # 3. Rim Light: Back-top warm highlight for character silhouette separation
    rim_data = bpy.data.lights.new(name="Luz_Recorte_Rim", type="SUN")
    rim_data.energy = 1.15
    rim_data.color = (1.0, 0.88, 0.70)
    if hasattr(rim_data, "angle"):
        rim_data.angle = math.radians(12.0)
    rim_obj = bpy.data.objects.new(name="Luz_Recorte_Rim", object_data=rim_data)
    rim_obj.location = (0.0, 5.0, 5.0)
    rim_obj.rotation_euler = (math.radians(-45), math.radians(10), math.radians(155))
    link_to_collection(rim_obj, col_lights)

    # 4. Stall Interior Warm Point Light: Highlights the counter and new shoes
    stall_light_data = bpy.data.lights.new(name="Luz_Barraca_Interna", type="POINT")
    stall_light_data.energy = 55.0
    stall_light_data.color = (1.0, 0.86, 0.62)
    if hasattr(stall_light_data, "shadow_soft_size"):
        stall_light_data.shadow_soft_size = 0.45
    stall_light_obj = bpy.data.objects.new(name="Luz_Barraca_Interna", object_data=stall_light_data)
    stall_light_obj.location = (1.25, 0.05, 2.25)
    link_to_collection(stall_light_obj, col_lights)

    return {
        "sun": sun_obj,
        "fill": fill_obj,
        "rim": rim_obj,
        "stall_light": stall_light_obj,
    }

