"""Centralized configuration and constants for the Nico 15s Low-Poly Animation (Blender 5.2 LTS)."""

import math

# ==============================================================================
# 1. RENDER & TIMELINE SETTINGS
# ==============================================================================
FPS = 30
DURATION_SECONDS = 15
FRAME_START = 1
FRAME_END = FPS * DURATION_SECONDS  # 450 frames

RES_X = 1080
RES_Y = 1920

# Presets for preview vs final rendering
RENDER_PRESETS = {
    "preview_stills": {
        "resolution_percentage": 50,
        "taa_render_samples": 24,
    },
    "preview_video": {
        "resolution_percentage": 50,
        "taa_render_samples": 16,
    },
    "final_video": {
        "resolution_percentage": 100,
        "taa_render_samples": 32,
    },
}

# ==============================================================================
# 2. STORYBOARD KEY FRAMES (AT 30 FPS)
# ==============================================================================
BEATS = {
    # 0-2s (Frames 1-60): The Problem (damaged shoe)
    "problem_start": 1,
    "problem_end": 60,
    # 2-4s (Frames 60-120): The Potato Sack Falls
    "sack_drop_start": 62,
    "sack_impact": 74,
    "sack_settle": 92,
    "sack_beat_end": 120,
    # 4-8s (Frames 120-240): Nico Walks to the Stall with the Sack
    "pickup_reach": 135,
    "pickup_lift": 148,
    "walk_start": 148,
    "walk_end": 236,
    # 8-11s (Frames 240-330): The Barter Attempt
    "place_sack_on_counter": 258,
    "barter_offer_end": 330,
    # 11-13s (Frames 330-390): The Refusal (Red X -> Milk Symbol)
    "refusal_x_start": 332,
    "refusal_x_peak": 340,
    "refusal_x_settle": 348,
    "milk_sign_start": 360,
    "milk_sign_peak": 368,
    "milk_sign_settle": 376,
    "refusal_end": 390,
    # 13-15s (Frames 390-450): Comic Frustration Reaction
    "reaction_start": 390,
    "reaction_slump": 412,
    "scene_end": 450,
}

# Representative frames to render for visual inspection and deliverables
REPRESENTATIVE_FRAMES = [
    (28, "01_sapato_danificado"),
    (75, "02_queda_saco_batatas"),
    (112, "03_nico_ideia_saco"),
    (190, "04_caminhada_feira"),
    (285, "05_tentativa_troca_balcao"),
    (352, "06_recusa_placa_x"),
    (382, "07_desejo_simbolo_leite"),
    (430, "08_reacao_comica_final"),
]

# ==============================================================================
# 3. SPATIAL STAGE POSITIONS (WORLD COORDINATES, Z = 0.0 IS GROUND)
# ==============================================================================
POSITIONS = {
    "nico_start": (-2.25, -0.65, 0.0),
    "sack_drop_xy": (-1.42, -0.58),
    "sack_start_z": 5.60,
    "nico_pickup": (-1.78, -0.62, 0.0),
    "nico_at_counter": (0.02, -0.52, 0.0),
    "stall_center": (1.35, 0.35, 0.0),
    "counter_center": (0.98, -0.15, 0.0),
    "counter_top_z": 0.96,
    "sack_on_counter": (0.76, -0.22, 0.96),
    "shoes_on_counter": (1.32, -0.10, 0.96),
    "seller_pos": (1.42, 0.48, 0.08),
    # Positioned clearly below the awning valance (Z=2.92) and above seller's eyes
    "sign_x_pos": (0.66, -0.35, 2.20),
    "sign_milk_pos": (1.44, -0.25, 2.20),
}


def _srgb_to_linear(r, g, b):
    """Convert perceptual sRGB (0..1) tuple to Blender Scene Linear RGBA."""
    def conv(c):
        return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92
    return (conv(r), conv(g), conv(b), 1.0)


# ==============================================================================
# 4. COLOR PALETTE (CONVERTED TO SCENE LINEAR RGBA FOR RICH, VIBRANT RENDERING)
# ==============================================================================
PALETTE = {
    # Environment
    "grass_base": _srgb_to_linear(0.36, 0.66, 0.28),
    "grass_accent": _srgb_to_linear(0.28, 0.56, 0.22),
    "dirt_path": _srgb_to_linear(0.68, 0.52, 0.35),
    "stone_grey": _srgb_to_linear(0.66, 0.64, 0.60),
    "stone_warm": _srgb_to_linear(0.74, 0.68, 0.58),
    "sky_warm": _srgb_to_linear(0.55, 0.78, 0.96),
    "cloud_white": _srgb_to_linear(0.97, 0.98, 1.00),
    # Market Stall & Village
    "wood_warm": _srgb_to_linear(0.58, 0.35, 0.17),
    "wood_light": _srgb_to_linear(0.78, 0.56, 0.34),
    "wood_dark": _srgb_to_linear(0.38, 0.22, 0.11),
    "stall_wall": _srgb_to_linear(0.95, 0.86, 0.68),
    "awning_red": _srgb_to_linear(0.88, 0.18, 0.15),
    "awning_cream": _srgb_to_linear(0.98, 0.94, 0.84),
    "awning_teal": _srgb_to_linear(0.16, 0.58, 0.68),
    "tree_trunk": _srgb_to_linear(0.46, 0.28, 0.14),
    "foliage_light": _srgb_to_linear(0.38, 0.72, 0.28),
    "foliage_dark": _srgb_to_linear(0.24, 0.54, 0.20),
    "house_wall_1": _srgb_to_linear(0.95, 0.88, 0.75),
    "house_wall_2": _srgb_to_linear(0.90, 0.78, 0.66),
    "house_roof_1": _srgb_to_linear(0.82, 0.32, 0.20),
    "house_roof_2": _srgb_to_linear(0.28, 0.48, 0.68),
    # Character Nico
    "nico_skin": _srgb_to_linear(0.92, 0.68, 0.50),
    "nico_shirt": _srgb_to_linear(0.98, 0.44, 0.08),
    "nico_cap_blue": _srgb_to_linear(0.14, 0.42, 0.85),
    "nico_shorts_blue": _srgb_to_linear(0.15, 0.32, 0.66),
    "nico_shoe_body": _srgb_to_linear(0.26, 0.24, 0.23),
    "nico_shoe_sole": _srgb_to_linear(0.94, 0.92, 0.88),
    "nico_sock_red": _srgb_to_linear(0.92, 0.16, 0.16),
    "eye_white": _srgb_to_linear(0.99, 0.99, 0.99),
    "eye_dark": _srgb_to_linear(0.06, 0.06, 0.08),
    "eyebrow_dark": _srgb_to_linear(0.20, 0.13, 0.08),
    "mouth_dark": _srgb_to_linear(0.42, 0.12, 0.12),
    # Seller & Props
    "seller_shirt": _srgb_to_linear(0.94, 0.92, 0.86),
    "seller_apron": _srgb_to_linear(0.18, 0.50, 0.36),
    "new_shoe_gold": _srgb_to_linear(0.98, 0.76, 0.15),
    "new_shoe_red": _srgb_to_linear(0.90, 0.16, 0.16),
    "burlap_sack": _srgb_to_linear(0.68, 0.48, 0.26),
    "burlap_rope": _srgb_to_linear(0.86, 0.72, 0.44),
    "potato_gold": _srgb_to_linear(0.94, 0.76, 0.32),
    # UI / Story Symbols
    "sign_board": _srgb_to_linear(0.98, 0.96, 0.90),
    "sign_milk_bg": _srgb_to_linear(0.12, 0.24, 0.42),
    "sign_border_red": _srgb_to_linear(0.85, 0.14, 0.14),
    "sign_x_red": _srgb_to_linear(0.96, 0.10, 0.10),
    "sign_border_blue": _srgb_to_linear(0.18, 0.58, 0.90),
    "sign_check_green": _srgb_to_linear(0.18, 0.82, 0.32),
    "milk_white": _srgb_to_linear(0.99, 0.99, 1.00),
    "milk_blue": _srgb_to_linear(0.15, 0.56, 0.94),
    "dust_puff": _srgb_to_linear(0.88, 0.83, 0.75),
}
