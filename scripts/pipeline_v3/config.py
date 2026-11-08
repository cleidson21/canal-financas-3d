"""Centralized configuration, paths, storyboard beats, and Scene-Linear palette for Pipeline V3."""

from pathlib import Path


def get_project_root() -> Path:
    """Resolve the repository root directory using pathlib.Path without hardcoded machine paths."""
    here = Path(__file__).resolve()
    # scripts/pipeline_v3/config.py -> parent is pipeline_v3, parent.parent is scripts, parent.parent.parent is root
    return here.parent.parent.parent


PROJECT_ROOT = get_project_root()
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
PERSONAGENS_DIR = PROJECT_ROOT / "personagens"
CENARIOS_DIR = PROJECT_ROOT / "cenarios"
OBJETOS_DIR = PROJECT_ROOT / "objetos"
EPISODIOS_DIR = PROJECT_ROOT / "episodios"
EP001_DIR = EPISODIOS_DIR / "EP001_dinheiro"
EP001_DELIVERIES_DIR = EP001_DIR / "ENTREGAS"
EP001_ARCHIVE_DIR = PROJECT_ROOT / "arquivo" / "EP001"
EP001_PILOT_DIR = EP001_ARCHIVE_DIR / "piloto"
PROJECT_CACHE_DIR = PROJECT_ROOT / ".cache"
DOCUMENTOS_DIR = PROJECT_ROOT / "documentos"
REFERENCIAS_DIR = PROJECT_ROOT / "referencias"
BACKUPS_DIR = PROJECT_ROOT / "backups" / "legado"

# ==============================================================================
# 1. RENDER & TIMELINE SETTINGS (VERTICAL SHORTS 9:16, 30 FPS, 15.0 SECONDS)
# ==============================================================================
FPS = 30
DURATION_SECONDS = 15
FRAME_START = 1
FRAME_END = FPS * DURATION_SECONDS  # 450 frames

RES_X = 1080
RES_Y = 1920

RENDER_PRESETS = {
    "preview_stills": {
        "resolution_percentage": 50,
        "taa_render_samples": 24,
    },
    "high_stills": {
        "resolution_percentage": 100,
        "taa_render_samples": 32,
    },
    "preview_video": {
        "resolution_percentage": 50,
        "taa_render_samples": 16,
    },
    "final_video": {
        "resolution_percentage": 100,
        "taa_render_samples": 20,
    },
}

# ==============================================================================
# 2. STORYBOARD V3 TIMING & SHOT CUTS (30 FPS, 450 FRAMES)
# ==============================================================================
BEATS = {
    # Shot 1 (0.0-2.2s | Frames 1-66): Cold Open — Close-up of damaged shoe opening & stumble
    "cold_open_start": 1,
    "step_lift": 14,          # ~0.5s: Foot lifts, sole peels open ("boca de jacaré")
    "step_snag": 26,          # ~0.85s: Detached sole catches on stone
    "stumble_peak": 38,       # ~1.25s: Nico stumbles forward, arms flail for balance
    "stumble_recover": 52,    # ~1.7s: Nico regains balance and looks down at his shoe
    "cold_open_end": 66,      # 2.2s: End of Shot 1

    # Shot 2 (2.2-4.5s | Frames 67-135): Revelação — Nico, damaged shoe & 40kg potatoes on cart
    "reveal_cut": 67,         # Hard cut to Medium-Full shot showing Nico + Cart with 40kg potatoes
    "look_at_sack": 88,       # ~2.9s: Nico turns head from shoe to the 40kg potato sack
    "idea_spark": 105,        # 3.5s: "Aha!" expression, finger raised, confident smile
    "grab_sack_Squat": 120,   # 4.0s: Anticipation squat to grab the heavy sack from the cart
    "lift_sack_ready": 135,   # 4.5s: Sack lifted against torso with heavy posture

    # Shot 3 (4.5-6.8s | Frames 136-205) & Shot 4 (6.8-8.5s | Frames 206-255): A Tentativa
    "walk_cut": 136,          # Cut to dynamic tracking angle of grounded heavy walk
    "walk_mid": 180,          # 6.0s: Mid-stride grounded step with sole flapping
    "arrival_cut": 206,       # Cut to stall arrival angle as Nico approaches the counter
    "walk_end": 248,          # 8.25s: Nico stops in front of the cobbler counter

    # Shot 5 (8.5-11.5s | Frames 256-345): A Proposta de Troca
    "barter_cut": 256,        # Cut to clear negotiation framing (Nico, Sack, New Shoes, Seller)
    "sack_counter_ploc": 268, # ~8.9s: Heavy sack lands on counter with squash & stretch ("PLOC!")
    "sack_counter_settle": 280,
    "offer_gesture": 295,     # ~9.8s: Nico points proudly from potatoes to the gleaming new shoes
    "seller_inspect": 318,    # Seller looks down at potatoes and starts shaking head NO
    "barter_end": 345,

    # Shot 6 (11.5-13.5s | Frames 346-405): A Recusa (X sobre as Batatas -> Ícone Grande de Leite)
    "refusal_cut": 346,       # Cut to tighter framing of counter + refusal icons
    "red_x_start": 348,
    "red_x_peak": 356,
    "red_x_settle": 364,
    "milk_icon_start": 370,
    "milk_icon_peak": 378,    # ~12.6s: Large Milk icon pops in with elastic overshoot
    "milk_icon_settle": 386,
    "refusal_end": 405,

    # Shot 7 (13.5-15.0s | Frames 406-450): Reação Cômica Final
    "reaction_cut": 406,      # Cut to Close-Up / Medium Close-Up of Nico's reaction
    "look_at_milk": 412,      # Looks up at Milk icon in disbelief
    "look_at_potatoes": 426,  # Looks back at his 40kg potato sack on the counter
    "comic_shrug": 436,       # 14.5s: Shoulders slump/shrug + head tilt + frustrated frown
    "scene_end": 450,         # 15.0s
}

# Mandatory audit timestamps from Section 17 (at 30 FPS):
# 0.5s (15), 1.5s (45), 3.5s (105), 6.0s (180), 9.5s (285), 12.5s (375), 14.5s (435)
MANDATORY_AUDIT_FRAMES = [
    (15, "00_5s_close_sapato_abrindo"),
    (45, "01_5s_tropeco_sapato"),
    (105, "03_5s_revelacao_carrinho_batatas"),
    (180, "06_0s_caminhada_com_peso"),
    (285, "09_5s_proposta_troca_balcao"),
    (375, "12_5s_recusa_x_e_leite"),
    (435, "14_5s_reacao_final_nico"),
]

# V2-equivalent frames for 1:1 contact sheet comparison
V2_EQUIVALENT_FRAMES = [
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
    "nico_start": (-2.30, -0.62, 0.0),
    "nico_stumble": (-1.92, -0.60, 0.0),
    "cart_pos": (-1.62, 0.26, 0.0),
    "sack_on_cart": (-1.62, 0.26, 0.34),
    "nico_pickup": (-1.56, -0.34, 0.0),
    "nico_at_counter": (0.08, -0.48, 0.0),
    "stall_center": (1.35, 0.35, 0.0),
    "counter_center": (0.98, -0.15, 0.0),
    "counter_top_z": 0.96,
    "sack_on_counter": (0.64, -0.20, 0.96),
    "shoes_on_counter": (1.30, -0.12, 1.02),
    "seller_pos": (1.38, 0.50, 0.08),
    # Positioned clearly above the potato sack & shoes for immediate mobile readability
    "sign_x_pos": (0.62, -0.26, 1.78),
    "sign_milk_pos": (1.22, -0.22, 1.92),
}


def _srgb_to_linear(r: float, g: float, b: float) -> tuple[float, float, float, float]:
    """Convert perceptual sRGB (0..1) tuple to Blender Scene Linear RGBA."""
    def conv(c: float) -> float:
        return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92
    return (conv(r), conv(g), conv(b), 1.0)


# ==============================================================================
# 4. SCENE-LINEAR COLOR PALETTE (REFINED FOR MOBILE CONTRAST & CHARM)
# ==============================================================================
PALETTE = {
    # Environment
    "grass_base": _srgb_to_linear(0.35, 0.65, 0.27),
    "grass_accent": _srgb_to_linear(0.27, 0.55, 0.21),
    "dirt_path": _srgb_to_linear(0.72, 0.57, 0.40),
    "stone_grey": _srgb_to_linear(0.68, 0.66, 0.62),
    "stone_warm": _srgb_to_linear(0.77, 0.71, 0.61),
    "sky_warm": _srgb_to_linear(0.52, 0.77, 0.96),
    "cloud_white": _srgb_to_linear(0.98, 0.99, 1.00),
    # Market Stall & Village
    "wood_warm": _srgb_to_linear(0.56, 0.34, 0.16),
    "wood_light": _srgb_to_linear(0.80, 0.59, 0.37),
    "wood_dark": _srgb_to_linear(0.32, 0.18, 0.09),
    "stall_wall": _srgb_to_linear(0.96, 0.89, 0.73),
    "awning_red": _srgb_to_linear(0.88, 0.19, 0.15),
    "awning_cream": _srgb_to_linear(0.98, 0.95, 0.86),
    "awning_teal": _srgb_to_linear(0.15, 0.56, 0.66),
    "tree_trunk": _srgb_to_linear(0.45, 0.27, 0.13),
    "foliage_light": _srgb_to_linear(0.36, 0.70, 0.26),
    "foliage_dark": _srgb_to_linear(0.22, 0.52, 0.18),
    "house_wall_1": _srgb_to_linear(0.95, 0.88, 0.76),
    "house_wall_2": _srgb_to_linear(0.90, 0.79, 0.67),
    "house_roof_1": _srgb_to_linear(0.82, 0.32, 0.20),
    "house_roof_2": _srgb_to_linear(0.28, 0.48, 0.68),
    # Character Nico V3
    "nico_skin": _srgb_to_linear(0.94, 0.70, 0.52),
    "nico_cheeks": _srgb_to_linear(0.94, 0.52, 0.42),
    "nico_hair": _srgb_to_linear(0.22, 0.14, 0.09),
    "nico_shirt": _srgb_to_linear(0.98, 0.45, 0.09),
    "nico_cap_blue": _srgb_to_linear(0.14, 0.44, 0.88),
    "nico_shorts_blue": _srgb_to_linear(0.14, 0.30, 0.62),
    "nico_shoe_body": _srgb_to_linear(0.22, 0.23, 0.26),
    "nico_shoe_inside": _srgb_to_linear(0.10, 0.08, 0.08),
    "nico_shoe_sole": _srgb_to_linear(0.95, 0.93, 0.89),
    "nico_sock_white": _srgb_to_linear(0.95, 0.95, 0.96),
    "nico_sock_red": _srgb_to_linear(0.84, 0.20, 0.20),
    "eye_white": _srgb_to_linear(0.99, 0.99, 0.99),
    "eye_dark": _srgb_to_linear(0.05, 0.05, 0.07),
    "eyebrow_dark": _srgb_to_linear(0.18, 0.11, 0.07),
    "mouth_dark": _srgb_to_linear(0.36, 0.10, 0.10),
    "tongue_pink": _srgb_to_linear(0.86, 0.38, 0.38),
    # Seller & Props
    "seller_shirt": _srgb_to_linear(0.95, 0.93, 0.88),
    "seller_apron": _srgb_to_linear(0.16, 0.48, 0.34),
    "new_shoe_gold": _srgb_to_linear(0.98, 0.78, 0.16),
    "new_shoe_red": _srgb_to_linear(0.88, 0.16, 0.16),
    "burlap_sack": _srgb_to_linear(0.68, 0.48, 0.26),
    "burlap_rope": _srgb_to_linear(0.86, 0.72, 0.44),
    "potato_gold": _srgb_to_linear(0.94, 0.76, 0.32),
    "iron_dark": _srgb_to_linear(0.24, 0.25, 0.27),
    # UI / Story Symbols
    "sign_board": _srgb_to_linear(0.98, 0.97, 0.92),
    "sign_milk_bg": _srgb_to_linear(0.10, 0.22, 0.40),
    "sign_border_red": _srgb_to_linear(0.86, 0.14, 0.14),
    "sign_x_red": _srgb_to_linear(0.96, 0.10, 0.10),
    "sign_border_blue": _srgb_to_linear(0.18, 0.58, 0.92),
    "sign_check_green": _srgb_to_linear(0.16, 0.84, 0.32),
    "milk_white": _srgb_to_linear(0.99, 0.99, 1.00),
    "milk_blue": _srgb_to_linear(0.15, 0.56, 0.94),
    "dust_puff": _srgb_to_linear(0.88, 0.83, 0.75),
}
