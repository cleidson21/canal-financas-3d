"""Localization-safe material library and 4-point cinematic lighting setup for Pipeline V3."""

import math
import bpy
from . import config
from .scene_setup import link_to_collection


def create_stylized_material(
    name,
    rgba,
    roughness=0.68,
    metallic=0.0,
    specular=0.38,
    coat_weight=0.0,
    emission_strength=0.0,
):
    """Create a Principled BSDF material safely across any Blender language localization."""
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)

    mat.diffuse_color = rgba
    if mat.node_tree is None:
        mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    bsdf = next((n for n in nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)
    output = next((n for n in nodes if n.bl_idname == "ShaderNodeOutputMaterial"), None)

    if not bsdf:
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    if not output:
        output = nodes.new(type="ShaderNodeOutputMaterial")
        links.new(bsdf.outputs[0], output.inputs[0])

    if "Base Color" in bsdf.inputs:
        bsdf.inputs["Base Color"].default_value = rgba
    else:
        bsdf.inputs[0].default_value = rgba

    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = roughness
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = specular
    if coat_weight > 0.0 and "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = coat_weight

    if emission_strength > 0.0:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = rgba
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength

    return mat


def build_material_library():
    """Build and return a dictionary of all stylized materials for the V3 scene."""
    pal = config.PALETTE
    mats = {}

    roughness_map = {
        "eye_dark": 0.12,
        "eye_white": 0.18,
        "new_shoe_gold": 0.28,
        "new_shoe_red": 0.34,
        "sign_x_red": 0.35,
        "sign_check_green": 0.35,
        "milk_white": 0.32,
        "milk_blue": 0.36,
        "nico_cap_blue": 0.56,
        "nico_shirt": 0.62,
        "nico_shorts_blue": 0.65,
        "nico_skin": 0.58,
        "nico_cheeks": 0.62,
        "nico_shoe_body": 0.72,
        "nico_shoe_sole": 0.64,
        "nico_shoe_inside": 0.92,
        "grass_base": 0.86,
        "dirt_path": 0.88,
        "burlap_sack": 0.86,
        "wood_warm": 0.72,
        "wood_light": 0.68,
        "wood_dark": 0.76,
    }
    emission_map = {
        "eye_white": 0.10,
        "sign_board": 0.10,
        "sign_x_red": 0.22,
        "sign_check_green": 0.22,
        "milk_white": 0.15,
        "new_shoe_gold": 0.12,
    }
    coat_map = {
        "new_shoe_red": 0.35,
        "new_shoe_gold": 0.40,
        "nico_cap_blue": 0.15,
    }

    for key, rgba in pal.items():
        r = roughness_map.get(key, 0.70)
        em = emission_map.get(key, 0.0)
        ct = coat_map.get(key, 0.0)
        mats[key] = create_stylized_material(
            f"Mat_{key}", rgba, roughness=r, coat_weight=ct, emission_strength=em
        )

    return mats


def setup_world_and_lighting(scene, col_lights):
    """Configure a bright sky world and 4-point cinematic lighting for crisp depth & character silhouette."""
    world = bpy.data.worlds.get("World_Vila_V3")
    if not world:
        world = bpy.data.worlds.new("World_Vila_V3")
    scene.world = world
    if world.node_tree is None:
        world.use_nodes = True

    wnodes = world.node_tree.nodes
    bg = next((n for n in wnodes if n.bl_idname == "ShaderNodeBackground"), None)
    if bg:
        bg.inputs[0].default_value = config.PALETTE["sky_warm"]
        bg.inputs[1].default_value = 0.82

    # 1. Key Light: Warm golden morning sun angled to sculpt facial features and cast clear ground shadows
    sun_data = bpy.data.lights.new(name="Sol_Principal", type="SUN")
    sun_data.energy = 3.35
    sun_data.color = (1.0, 0.95, 0.86)
    if hasattr(sun_data, "angle"):
        sun_data.angle = math.radians(5.5)
    sun_obj = bpy.data.objects.new(name="Sol_Principal", object_data=sun_data)
    sun_obj.location = (-4.0, -6.0, 8.0)
    sun_obj.rotation_euler = (math.radians(48), math.radians(-20), math.radians(-26))
    link_to_collection(sun_obj, col_lights)

    # 2. Fill Light: Soft sky-blue area light from front-right to keep shadows clean and mobile-friendly
    fill_data = bpy.data.lights.new(name="Luz_Preenchimento", type="AREA")
    fill_data.energy = 82.0
    fill_data.color = (0.86, 0.93, 1.0)
    if hasattr(fill_data, "size"):
        fill_data.size = 7.5
    fill_obj = bpy.data.objects.new(name="Luz_Preenchimento", object_data=fill_data)
    fill_obj.location = (4.5, -5.5, 4.0)
    fill_obj.rotation_euler = (math.radians(56), math.radians(14), math.radians(32))
    link_to_collection(fill_obj, col_lights)

    # 3. Rim Light: Back-top warm highlight to separate Nico's head, cap, and shoulders from the background
    rim_data = bpy.data.lights.new(name="Luz_Recorte_Rim", type="SUN")
    rim_data.energy = 1.25
    rim_data.color = (1.0, 0.89, 0.72)
    if hasattr(rim_data, "angle"):
        rim_data.angle = math.radians(10.0)
    rim_obj = bpy.data.objects.new(name="Luz_Recorte_Rim", object_data=rim_data)
    rim_obj.location = (0.0, 5.0, 5.5)
    rim_obj.rotation_euler = (math.radians(-46), math.radians(10), math.radians(156))
    link_to_collection(rim_obj, col_lights)

    # 4. Stall Interior Warm Light: Illuminates the cobbler counter and makes the new shoes gleam
    stall_light_data = bpy.data.lights.new(name="Luz_Barraca_Interna", type="POINT")
    stall_light_data.energy = 68.0
    stall_light_data.color = (1.0, 0.88, 0.65)
    if hasattr(stall_light_data, "shadow_soft_size"):
        stall_light_data.shadow_soft_size = 0.45
    stall_light_obj = bpy.data.objects.new(name="Luz_Barraca_Interna", object_data=stall_light_data)
    stall_light_obj.location = (1.28, 0.02, 2.22)
    link_to_collection(stall_light_obj, col_lights)

    # 5. Low Front Shoe Fill Light: Ensures the gap under the damaged shoe sole is 100% crisp during the Cold Open
    shoe_fill_data = bpy.data.lights.new(name="Luz_Destaque_Sapato", type="AREA")
    shoe_fill_data.energy = 24.0
    shoe_fill_data.color = (1.0, 0.96, 0.90)
    if hasattr(shoe_fill_data, "size"):
        shoe_fill_data.size = 1.6
    shoe_fill_obj = bpy.data.objects.new(name="Luz_Destaque_Sapato", object_data=shoe_fill_data)
    shoe_fill_obj.location = (-1.85, -2.25, 0.55)
    shoe_fill_obj.rotation_euler = (math.radians(74), 0.0, math.radians(-12))
    link_to_collection(shoe_fill_obj, col_lights)

    return {
        "sun": sun_obj,
        "fill": fill_obj,
        "rim": rim_obj,
        "stall_light": stall_light_obj,
        "shoe_fill": shoe_fill_obj,
    }

