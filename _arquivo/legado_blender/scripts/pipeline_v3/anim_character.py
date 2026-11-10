"""Procedural keyframe animation V3 for Nico and the Shoe Seller across the 15-second storyboard.

Implements:
- Cold Open: close-up step, thin front sole peeling open ('boca de jacaré'), snag on stone, and stumble recovery
- Reveal: glance from broken shoe to 40kg potato sack on handcart, 'Aha!' idea, anticipation squat & heavy lift
- Grounded Heavy Walk Cycle: heel-to-toe contact, knee flexion on weight acceptance, hip bounce, and sole flap
- Barter Offer: heavy heave onto counter ('PLOC!'), pointing from potatoes to new shoes
- Refusal & Milk Reveal: startled recoil at Red X, bewildered gaze at Milk Icon
- Final Reaction: look at milk -> look at potatoes -> comic shrug & frustrated slump
"""

import math
from . import config
from .scene_setup import set_interpolation

rad = math.radians


def _key_transform(obj, frame, loc=None, rot=None, scale=None):
    """Insert location, rotation_euler, and/or scale keyframes on an object."""
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert(data_path="location", frame=frame)
    if rot is not None:
        obj.rotation_euler = rot
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert(data_path="scale", frame=frame)


def _set_facial_expression(nico, frame, state="neutral"):
    """Keyframe Nico's eyebrows and mouth for clear visual emotion on mobile screens."""
    eb_l = nico["eyebrow_l"]
    eb_r = nico["eyebrow_r"]
    mouth = nico["mouth"]

    if state == "worried_shoe":
        # Inner eyebrow corners raised in worry, slight frown
        _key_transform(eb_l, frame, loc=(-0.102, -0.228, 0.348), rot=(rad(-10), rad(-14), 0.0))
        _key_transform(eb_r, frame, loc=(0.102, -0.228, 0.348), rot=(rad(-10), rad(14), 0.0))
        _key_transform(mouth, frame, scale=(0.92, 1.0, 0.85))
    elif state == "surprised":
        # Eyebrows shoot high up, mouth opens into a round O
        _key_transform(eb_l, frame, loc=(-0.102, -0.228, 0.368), rot=(rad(-10), rad(8), 0.0))
        _key_transform(eb_r, frame, loc=(0.102, -0.228, 0.368), rot=(rad(-10), rad(-8), 0.0))
        _key_transform(mouth, frame, scale=(0.76, 1.1, 2.25))
    elif state == "happy_idea":
        # Eyebrows arched confidently, wide optimistic smile
        _key_transform(eb_l, frame, loc=(-0.102, -0.228, 0.358), rot=(rad(-10), rad(6), 0.0))
        _key_transform(eb_r, frame, loc=(0.102, -0.228, 0.358), rot=(rad(-10), rad(-6), 0.0))
        _key_transform(mouth, frame, scale=(1.28, 1.0, 0.82))
    elif state == "effort":
        # Eyebrows lowered in physical effort while lifting/carrying 40kg
        _key_transform(eb_l, frame, loc=(-0.102, -0.228, 0.336), rot=(rad(-10), rad(10), 0.0))
        _key_transform(eb_r, frame, loc=(0.102, -0.228, 0.336), rot=(rad(-10), rad(-10), 0.0))
        _key_transform(mouth, frame, scale=(1.10, 1.0, 0.72))
    elif state == "frustrated":
        # Furrowed comic disbelief/frustration eyebrows, wide open mouth
        _key_transform(eb_l, frame, loc=(-0.102, -0.228, 0.338), rot=(rad(-10), rad(16), 0.0))
        _key_transform(eb_r, frame, loc=(0.102, -0.228, 0.338), rot=(rad(-10), rad(-16), 0.0))
        _key_transform(mouth, frame, scale=(1.22, 1.0, 1.38))
    else:
        _key_transform(eb_l, frame, loc=(-0.102, -0.228, 0.342), rot=(rad(-10), 0.0, 0.0))
        _key_transform(eb_r, frame, loc=(0.102, -0.228, 0.342), rot=(rad(-10), 0.0, 0.0))
        _key_transform(mouth, frame, scale=(1.0, 1.0, 1.0))


def animate_nico(nico):
    """Keyframe Nico V3 across all 450 frames (15s @ 30 FPS) of Storyboard V3."""
    root = nico["root"]
    pelvis = nico["pelvis"]
    torso = nico["torso"]
    head = nico["head"]
    arm_l = nico["arm_l"]
    forearm_l = nico["forearm_l"]
    arm_r = nico["arm_r"]
    forearm_r = nico["forearm_r"]
    leg_l = nico["leg_l"]
    knee_l = nico["knee_l"]
    foot_l = nico["foot_l"]
    leg_r = nico["leg_r"]
    knee_r = nico["knee_r"]
    foot_r = nico["foot_r"]
    sole_r = nico["damaged_sole"]

    # ==========================================================================
    # SHOT 1 (0.0-2.2s | Frames 1-66): COLD OPEN — STEP, SOLE PEELS OPEN & STUMBLE
    # ==========================================================================
    # Frame 1: Starting step on the path
    _key_transform(root, 1, loc=(-2.28, -0.62, 0.0), rot=(0.0, 0.0, rad(32)))
    _key_transform(pelvis, 1, loc=(0.0, 0.0, 0.78), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, 1, rot=(rad(6), 0.0, 0.0))
    _key_transform(head, 1, rot=(rad(10), 0.0, rad(-6)))
    _key_transform(arm_l, 1, rot=(rad(-14), rad(8), 0.0))
    _key_transform(forearm_l, 1, rot=(rad(-22), 0.0, 0.0))
    _key_transform(arm_r, 1, rot=(rad(12), rad(-8), 0.0))
    _key_transform(forearm_r, 1, rot=(rad(-20), 0.0, 0.0))
    _key_transform(leg_l, 1, rot=(rad(8), 0.0, 0.0))
    _key_transform(knee_l, 1, rot=(rad(6), 0.0, 0.0))
    _key_transform(foot_l, 1, rot=(rad(-8), 0.0, 0.0))
    _key_transform(leg_r, 1, rot=(rad(-12), 0.0, 0.0))
    _key_transform(knee_r, 1, rot=(rad(14), 0.0, 0.0))
    _key_transform(foot_r, 1, rot=(rad(-4), 0.0, 0.0))
    _key_transform(sole_r, 1, rot=(rad(12), 0.0, 0.0))
    _set_facial_expression(nico, 1, "neutral")

    # Frame 15 (0.5s): Right foot lifts high in step; detached front sole peels wide open ("boca de jacaré"!)
    _key_transform(root, 15, loc=(-2.16, -0.61, 0.0), rot=(0.0, 0.0, rad(34)))
    _key_transform(pelvis, 15, loc=(0.0, 0.0, 0.79), rot=(0.0, rad(-3), 0.0))
    _key_transform(torso, 15, rot=(rad(10), 0.0, rad(-4)))
    _key_transform(head, 15, rot=(rad(16), 0.0, rad(-8)))
    _key_transform(arm_l, 15, rot=(rad(-24), rad(12), 0.0))
    _key_transform(forearm_l, 15, rot=(rad(-35), 0.0, 0.0))
    _key_transform(arm_r, 15, rot=(rad(18), rad(-10), 0.0))
    _key_transform(forearm_r, 15, rot=(rad(-30), 0.0, 0.0))
    _key_transform(leg_l, 15, rot=(rad(4), 0.0, 0.0))
    _key_transform(knee_l, 15, rot=(rad(4), 0.0, 0.0))
    _key_transform(foot_l, 15, rot=(rad(-4), 0.0, 0.0))
    _key_transform(leg_r, 15, rot=(rad(-34), 0.0, 0.0))
    _key_transform(knee_r, 15, rot=(rad(28), 0.0, 0.0))
    _key_transform(foot_r, 15, rot=(rad(-10), 0.0, 0.0))
    _key_transform(sole_r, 15, rot=(rad(29), 0.0, 0.0))
    _set_facial_expression(nico, 15, "worried_shoe")

    # Frame 28 (~0.9s): Right foot comes down; hanging front sole catches on the stepping stone first!
    _key_transform(root, 28, loc=(-2.04, -0.60, 0.0), rot=(0.0, 0.0, rad(38)))
    _key_transform(pelvis, 28, loc=(0.0, 0.0, 0.76), rot=(0.0, rad(4), 0.0))
    _key_transform(torso, 28, rot=(rad(16), rad(4), rad(-6)))
    _key_transform(head, 28, rot=(rad(20), 0.0, rad(-10)))
    _key_transform(leg_r, 28, rot=(rad(-26), 0.0, 0.0))
    _key_transform(knee_r, 28, rot=(rad(22), 0.0, 0.0))
    _key_transform(foot_r, 28, rot=(rad(-8), 0.0, 0.0))
    _key_transform(sole_r, 28, rot=(rad(32), 0.0, 0.0))
    _set_facial_expression(nico, 28, "worried_shoe")

    # Frame 35: Upper shoe slams down onto the snagged sole as Nico's weight pitches forward
    _key_transform(sole_r, 35, rot=(rad(2), 0.0, 0.0))

    # Frame 45 (1.5s): Stumble Peak! Nico lurches forward, knees bend deeply, arms windmill out for balance
    _key_transform(root, 45, loc=(-1.90, -0.58, 0.0), rot=(0.0, 0.0, rad(42)))
    _key_transform(pelvis, 45, loc=(0.0, 0.0, 0.70), rot=(rad(8), rad(-5), 0.0))
    _key_transform(torso, 45, rot=(rad(26), rad(-6), rad(8)))
    _key_transform(head, 45, rot=(rad(12), rad(6), rad(-12)))
    _key_transform(arm_l, 45, rot=(rad(-62), rad(34), rad(-18)))
    _key_transform(forearm_l, 45, rot=(rad(-48), 0.0, 0.0))
    _key_transform(arm_r, 45, rot=(rad(-48), rad(-36), rad(16)))
    _key_transform(forearm_r, 45, rot=(rad(-42), 0.0, 0.0))
    _key_transform(leg_l, 45, rot=(rad(-28), 0.0, 0.0))
    _key_transform(knee_l, 45, rot=(rad(44), 0.0, 0.0))
    _key_transform(foot_l, 45, rot=(rad(-16), 0.0, 0.0))
    _key_transform(leg_r, 45, rot=(rad(16), 0.0, 0.0))
    _key_transform(knee_r, 45, rot=(rad(24), 0.0, 0.0))
    _key_transform(foot_r, 45, rot=(rad(-22), 0.0, 0.0))
    _key_transform(sole_r, 45, rot=(rad(26), 0.0, 0.0))
    _set_facial_expression(nico, 45, "surprised")

    # Frame 60-66 (2.0-2.2s): Nico regains balance and lifts the right toe slightly, looking down at the broken sole
    _key_transform(root, 62, loc=(-1.84, -0.56, 0.0), rot=(0.0, 0.0, rad(36)))
    _key_transform(pelvis, 62, loc=(0.0, 0.0, 0.77), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, 62, rot=(rad(14), 0.0, rad(-4)))
    _key_transform(head, 62, rot=(rad(20), 0.0, rad(-8)))
    _key_transform(arm_l, 62, rot=(rad(-18), rad(12), 0.0))
    _key_transform(forearm_l, 62, rot=(rad(-32), 0.0, 0.0))
    _key_transform(arm_r, 62, rot=(rad(-14), rad(-12), 0.0))
    _key_transform(forearm_r, 62, rot=(rad(-28), 0.0, 0.0))
    _key_transform(leg_l, 62, rot=(rad(0), 0.0, 0.0))
    _key_transform(knee_l, 62, rot=(rad(0), 0.0, 0.0))
    _key_transform(foot_l, 62, rot=(rad(0), 0.0, 0.0))
    _key_transform(leg_r, 62, rot=(rad(-26), 0.0, 0.0))
    _key_transform(knee_r, 62, rot=(rad(22), 0.0, 0.0))
    _key_transform(foot_r, 62, rot=(rad(-8), 0.0, 0.0))
    _key_transform(sole_r, 62, rot=(rad(26), 0.0, 0.0))
    _set_facial_expression(nico, 62, "worried_shoe")

    # ==========================================================================
    # SHOT 2 (2.2-4.5s | Frames 67-135): REVELAÇÃO — CART, 40KG POTATOES & IDEA
    # ==========================================================================
    # Frame 75: Nico glances from his broken shoe toward the 40kg potato sack on his wooden handcart
    _key_transform(root, 75, loc=(-1.80, -0.55, 0.0), rot=(0.0, 0.0, rad(28)))
    _key_transform(pelvis, 75, loc=(0.0, 0.0, 0.78), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, 75, rot=(rad(8), 0.0, rad(-8)))
    _key_transform(head, 75, rot=(rad(6), rad(-4), rad(-24)))
    _key_transform(leg_r, 75, rot=(rad(-18), 0.0, 0.0))
    _key_transform(knee_r, 75, rot=(rad(16), 0.0, 0.0))
    _key_transform(foot_r, 75, rot=(rad(-6), 0.0, 0.0))
    _key_transform(sole_r, 75, rot=(rad(22), 0.0, 0.0))
    _set_facial_expression(nico, 75, "worried_shoe")

    # Frame 105 (3.5s) & 112: "Aha!" Idea! Nico perks up with a confident grin, pointing from the potatoes to the stall
    for fr_idea in (102, 112):
        _key_transform(root, fr_idea, loc=(-1.72, -0.54, 0.0), rot=(0.0, 0.0, rad(32)))
        _key_transform(pelvis, fr_idea, loc=(0.0, 0.0, 0.80), rot=(0.0, 0.0, 0.0))
        _key_transform(torso, fr_idea, rot=(rad(-4), 0.0, rad(-6)))
        _key_transform(head, fr_idea, rot=(rad(-6), rad(4), rad(-14)))
        _key_transform(arm_l, fr_idea, rot=(rad(-26), rad(14), 0.0))
        _key_transform(forearm_l, fr_idea, rot=(rad(-42), 0.0, 0.0))
        _key_transform(arm_r, fr_idea, rot=(rad(-68), rad(-16), rad(12)))
        _key_transform(forearm_r, fr_idea, rot=(rad(-52), 0.0, 0.0))
        _key_transform(leg_l, fr_idea, rot=(rad(0), 0.0, 0.0))
        _key_transform(knee_l, fr_idea, rot=(rad(0), 0.0, 0.0))
        _key_transform(foot_l, fr_idea, rot=(rad(0), 0.0, 0.0))
        _key_transform(leg_r, fr_idea, rot=(rad(-12), 0.0, 0.0))
        _key_transform(knee_r, fr_idea, rot=(rad(12), 0.0, 0.0))
        _key_transform(foot_r, fr_idea, rot=(rad(-4), 0.0, 0.0))
        _key_transform(sole_r, fr_idea, rot=(rad(16), 0.0, 0.0))
        _set_facial_expression(nico, fr_idea, "happy_idea")

    # Frame 124: Anticipation Squat to grab the heavy 40kg sack off the wooden cart
    _key_transform(root, 124, loc=(-1.56, -0.34, 0.0), rot=(0.0, 0.0, rad(18)))
    _key_transform(pelvis, 124, loc=(0.0, 0.0, 0.67), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, 124, rot=(rad(24), 0.0, 0.0))
    _key_transform(head, 124, rot=(rad(-8), 0.0, 0.0))
    _key_transform(arm_l, 124, rot=(rad(-56), rad(-16), 0.0))
    _key_transform(forearm_l, 124, rot=(rad(-38), 0.0, 0.0))
    _key_transform(arm_r, 124, rot=(rad(-56), rad(16), 0.0))
    _key_transform(forearm_r, 124, rot=(rad(-38), 0.0, 0.0))
    _key_transform(leg_l, 124, rot=(rad(-28), 0.0, 0.0))
    _key_transform(knee_l, 124, rot=(rad(52), 0.0, 0.0))
    _key_transform(foot_l, 124, rot=(rad(-24), 0.0, 0.0))
    _key_transform(leg_r, 124, rot=(rad(-28), 0.0, 0.0))
    _key_transform(knee_r, 124, rot=(rad(52), 0.0, 0.0))
    _key_transform(foot_r, 124, rot=(rad(-24), 0.0, 0.0))
    _key_transform(sole_r, 124, rot=(rad(0), 0.0, 0.0))
    _set_facial_expression(nico, 124, "effort")

    # Frame 135: Heaves the 40kg sack against his chest (torso leans slightly back to counterbalance weight)
    _key_transform(root, 135, loc=(-1.42, -0.50, 0.0), rot=(0.0, 0.0, rad(78)))
    _key_transform(pelvis, 135, loc=(0.0, 0.0, 0.76), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, 135, rot=(rad(-8), 0.0, 0.0))
    _key_transform(head, 135, rot=(rad(8), 0.0, rad(-12)))
    _key_transform(arm_l, 135, rot=(rad(-54), rad(-20), 0.0))
    _key_transform(forearm_l, 135, rot=(rad(-62), 0.0, 0.0))
    _key_transform(arm_r, 135, rot=(rad(-54), rad(20), 0.0))
    _key_transform(forearm_r, 135, rot=(rad(-62), 0.0, 0.0))
    _key_transform(leg_l, 135, rot=(rad(0), 0.0, 0.0))
    _key_transform(knee_l, 135, rot=(rad(8), 0.0, 0.0))
    _key_transform(foot_l, 135, rot=(rad(-8), 0.0, 0.0))
    _key_transform(leg_r, 135, rot=(rad(0), 0.0, 0.0))
    _key_transform(knee_r, 135, rot=(rad(8), 0.0, 0.0))
    _key_transform(foot_r, 135, rot=(rad(-8), 0.0, 0.0))
    _key_transform(sole_r, 135, rot=(rad(0), 0.0, 0.0))
    _set_facial_expression(nico, 135, "effort")

    # ==========================================================================
    # SHOTS 3 & 4 (4.5-8.5s | Frames 136-255): GROUNDED WALK WITH HEAVY LOAD
    # ==========================================================================
    # 8 grounded steps from X = -1.42 to X = +0.06 (14 frames per step = 112 frames: 136 -> 248)
    walk_x_start = -1.42
    walk_x_end = 0.06
    num_steps = 8
    step_dur = 14

    for s in range(num_steps + 1):
        fr = 136 + s * step_dur
        t = s / num_steps
        wx = walk_x_start + (walk_x_end - walk_x_start) * t
        wy = -0.50 + 0.04 * t
        # Angle slightly toward camera (+72 deg) so both face, sack, and flapping right shoe read clearly
        yaw = rad(74) if s < num_steps else rad(52)

        _key_transform(root, fr, loc=(wx, wy, 0.0), rot=(0.0, 0.0, yaw))
        # Contact pose: pelvis at 0.775
        _key_transform(pelvis, fr, loc=(0.0, 0.0, 0.775), rot=(0.0, rad(3 if s % 2 == 0 else -3), 0.0))
        _key_transform(torso, fr, rot=(rad(-7), rad(-3 if s % 2 == 0 else 3), rad(4 if s % 2 == 0 else -4)))
        _key_transform(head, fr, rot=(rad(6), 0.0, rad(-16)))
        _key_transform(arm_l, fr, rot=(rad(-54), rad(-20), 0.0))
        _key_transform(forearm_l, fr, rot=(rad(-62), 0.0, 0.0))
        _key_transform(arm_r, fr, rot=(rad(-54), rad(20), 0.0))
        _key_transform(forearm_r, fr, rot=(rad(-62), 0.0, 0.0))

        if s == num_steps:
            # Final planted stop at counter (Frame 248)
            _key_transform(leg_l, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(knee_l, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(foot_l, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(leg_r, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(knee_r, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(foot_r, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(sole_r, fr, rot=(0.0, 0.0, 0.0))
        elif s % 2 == 0:
            # Left leg forward contact, Right leg back pushing off (sole starts peeling open)
            _key_transform(leg_l, fr, rot=(rad(-24), 0.0, 0.0))
            _key_transform(knee_l, fr, rot=(rad(10), 0.0, 0.0))
            _key_transform(foot_l, fr, rot=(rad(12), 0.0, 0.0))
            _key_transform(leg_r, fr, rot=(rad(22), 0.0, 0.0))
            _key_transform(knee_r, fr, rot=(rad(18), 0.0, 0.0))
            _key_transform(foot_r, fr, rot=(rad(-16), 0.0, 0.0))
            _key_transform(sole_r, fr, rot=(rad(20), 0.0, 0.0))
        else:
            # Right leg forward contact, Left leg back pushing off
            _key_transform(leg_l, fr, rot=(rad(22), 0.0, 0.0))
            _key_transform(knee_l, fr, rot=(rad(18), 0.0, 0.0))
            _key_transform(foot_l, fr, rot=(rad(-16), 0.0, 0.0))
            _key_transform(leg_r, fr, rot=(rad(-24), 0.0, 0.0))
            _key_transform(knee_r, fr, rot=(rad(10), 0.0, 0.0))
            _key_transform(foot_r, fr, rot=(rad(10), 0.0, 0.0))
            _key_transform(sole_r, fr, rot=(rad(4), 0.0, 0.0))

        # Mid-step passing/down pose (fr + 7): weight acceptance & swing leg knee flexion
        if s < num_steps:
            fr_mid = fr + step_dur // 2
            _key_transform(pelvis, fr_mid, loc=(0.0, 0.0, 0.735), rot=(0.0, 0.0, 0.0))
            if s % 2 == 0:
                # Right leg swinging forward high: knee flexed +36 deg, damaged sole wide open (+28 deg)!
                _key_transform(leg_l, fr_mid, rot=(rad(2), 0.0, 0.0))
                _key_transform(knee_l, fr_mid, rot=(rad(18), 0.0, 0.0))
                _key_transform(foot_l, fr_mid, rot=(rad(-16), 0.0, 0.0))
                _key_transform(leg_r, fr_mid, rot=(rad(-18), 0.0, 0.0))
                _key_transform(knee_r, fr_mid, rot=(rad(36), 0.0, 0.0))
                _key_transform(foot_r, fr_mid, rot=(rad(-10), 0.0, 0.0))
                _key_transform(sole_r, fr_mid, rot=(rad(28), 0.0, 0.0))
            else:
                # Right leg planted bearing full weight (sole pressed flat = 0 deg), Left leg swinging forward
                _key_transform(leg_l, fr_mid, rot=(rad(-18), 0.0, 0.0))
                _key_transform(knee_l, fr_mid, rot=(rad(36), 0.0, 0.0))
                _key_transform(foot_l, fr_mid, rot=(rad(-10), 0.0, 0.0))
                _key_transform(leg_r, fr_mid, rot=(rad(2), 0.0, 0.0))
                _key_transform(knee_r, fr_mid, rot=(rad(18), 0.0, 0.0))
                _key_transform(foot_r, fr_mid, rot=(rad(-16), 0.0, 0.0))
                _key_transform(sole_r, fr_mid, rot=(rad(0), 0.0, 0.0))

    # ==========================================================================
    # SHOT 5 (8.5-11.5s | Frames 256-345): A PROPOSTA DE TROCA NO BALCÃO
    # ==========================================================================
    # Frame 260: Effort heave lifting the 40kg sack onto the counter
    _key_transform(root, 260, loc=(0.06, -0.46, 0.0), rot=(0.0, 0.0, rad(46)))
    _key_transform(pelvis, 260, loc=(0.0, 0.0, 0.81), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, 260, rot=(rad(-12), 0.0, rad(-6)))
    _key_transform(head, 260, rot=(rad(-6), 0.0, rad(-10)))
    _key_transform(arm_l, 260, rot=(rad(-78), rad(-12), 0.0))
    _key_transform(forearm_l, 260, rot=(rad(-45), 0.0, 0.0))
    _key_transform(arm_r, 260, rot=(rad(-78), rad(12), 0.0))
    _key_transform(forearm_r, 260, rot=(rad(-45), 0.0, 0.0))
    _set_facial_expression(nico, 260, "effort")

    # Frame 268: Sack lands with "PLOC!" on counter; Nico's body settles down
    _key_transform(pelvis, 268, loc=(0.0, 0.0, 0.76), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, 268, rot=(rad(8), 0.0, rad(-4)))

    # Frames 282-335 (including Frame 285 = 9.5s): Nico proudly gestures from the potato sack to the new shoes
    for fr_offer in (282, 330):
        _key_transform(root, fr_offer, loc=(0.04, -0.48, 0.0), rot=(0.0, 0.0, rad(38)))
        _key_transform(pelvis, fr_offer, loc=(0.0, 0.0, 0.78), rot=(0.0, 0.0, 0.0))
        _key_transform(torso, fr_offer, rot=(rad(4), 0.0, rad(-10)))
        _key_transform(head, fr_offer, rot=(rad(-4), 0.0, rad(-16)))
        # Right arm (screen right, closer to counter) extends to point at the potatoes & new shoes
        _key_transform(arm_r, fr_offer, rot=(rad(-64), rad(-18), rad(-12)))
        _key_transform(forearm_r, fr_offer, rot=(rad(-28), 0.0, 0.0))
        # Left arm relaxed with elbow bent
        _key_transform(arm_l, fr_offer, rot=(rad(-22), rad(14), 0.0))
        _key_transform(forearm_l, fr_offer, rot=(rad(-46), 0.0, 0.0))
        # Slight lift of right toe so damaged sole stays subtly visible
        _key_transform(leg_r, fr_offer, rot=(rad(-10), 0.0, 0.0))
        _key_transform(knee_r, fr_offer, rot=(rad(10), 0.0, 0.0))
        _key_transform(foot_r, fr_offer, rot=(rad(-4), 0.0, 0.0))
        _key_transform(sole_r, fr_offer, rot=(rad(16), 0.0, 0.0))
        _set_facial_expression(nico, fr_offer, "happy_idea")

    # ==========================================================================
    # SHOT 6 (11.5-13.5s | Frames 346-405): A RECUSA (X VERMELHO -> LEITE)
    # ==========================================================================
    # Frame 352: Red X pops over the potatoes! Nico recoils in surprise
    _key_transform(root, 352, loc=(-0.05, -0.48, 0.0), rot=(0.0, 0.0, rad(28)))
    _key_transform(pelvis, 352, loc=(0.0, 0.0, 0.76), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, 352, rot=(rad(-8), 0.0, rad(6)))
    _key_transform(head, 352, rot=(rad(-10), 0.0, rad(-18)))
    _key_transform(arm_l, 352, rot=(rad(-52), rad(14), 0.0))
    _key_transform(forearm_l, 352, rot=(rad(-64), 0.0, 0.0))
    _key_transform(arm_r, 352, rot=(rad(-52), rad(-14), 0.0))
    _key_transform(forearm_r, 352, rot=(rad(-64), 0.0, 0.0))
    _set_facial_expression(nico, 352, "surprised")

    # Frames 375 (12.5s) & 382: Large Milk Icon pops in! Nico gazes up at the Milk sign in shock
    for fr_milk in (375, 392):
        _key_transform(root, fr_milk, loc=(-0.05, -0.48, 0.0), rot=(0.0, 0.0, rad(24)))
        _key_transform(pelvis, fr_milk, loc=(0.0, 0.0, 0.77), rot=(0.0, 0.0, 0.0))
        _key_transform(torso, fr_milk, rot=(rad(-6), 0.0, rad(4)))
        _key_transform(head, fr_milk, rot=(rad(-12), rad(4), rad(-22)))
        _key_transform(arm_l, fr_milk, rot=(rad(-58), rad(14), 0.0))
        _key_transform(forearm_l, fr_milk, rot=(rad(-68), 0.0, 0.0))
        _key_transform(arm_r, fr_milk, rot=(rad(-58), rad(-14), 0.0))
        _key_transform(forearm_r, fr_milk, rot=(rad(-68), 0.0, 0.0))
        _set_facial_expression(nico, fr_milk, "surprised")

    # ==========================================================================
    # SHOT 7 (13.5-15.0s | Frames 406-450): REAÇÃO CÔMICA FINAL
    # ==========================================================================
    # Frame 412: Looks up at the Milk sign
    _key_transform(root, 412, loc=(-0.05, -0.48, 0.0), rot=(0.0, 0.0, rad(20)))
    _key_transform(head, 412, rot=(rad(-12), rad(4), rad(-22)))
    _set_facial_expression(nico, 412, "surprised")

    # Frame 424: Looks down at his 40kg sack of potatoes on the counter
    _key_transform(head, 424, rot=(rad(12), rad(-4), rad(-26)))
    _set_facial_expression(nico, 424, "worried_shoe")

    # Frames 434-450 (including Frame 435 = 14.5s): Comic shrug & frustrated slump toward camera!
    for fr_end in (434, 450):
        _key_transform(root, fr_end, loc=(-0.05, -0.48, 0.0), rot=(0.0, 0.0, rad(18)))
        _key_transform(pelvis, fr_end, loc=(0.0, 0.0, 0.73), rot=(0.0, 0.0, 0.0))
        _key_transform(torso, fr_end, rot=(rad(8), rad(-3), 0.0))
        _key_transform(head, fr_end, rot=(rad(4), rad(8), rad(-8)))
        # Arms open outward organically in a helpless "What do I do with 40kg of potatoes?!" shrug
        _key_transform(arm_l, fr_end, rot=(rad(-20), rad(18), rad(-6)))
        _key_transform(forearm_l, fr_end, rot=(rad(-46), 0.0, 0.0))
        _key_transform(arm_r, fr_end, rot=(rad(-20), rad(-18), rad(6)))
        _key_transform(forearm_r, fr_end, rot=(rad(-46), 0.0, 0.0))
        _key_transform(leg_l, fr_end, rot=(rad(-6), 0.0, 0.0))
        _key_transform(knee_l, fr_end, rot=(rad(12), 0.0, 0.0))
        _key_transform(foot_l, fr_end, rot=(rad(-6), 0.0, 0.0))
        _key_transform(leg_r, fr_end, rot=(rad(-14), 0.0, 0.0))
        _key_transform(knee_r, fr_end, rot=(rad(16), 0.0, 0.0))
        _key_transform(foot_r, fr_end, rot=(rad(-6), 0.0, 0.0))
        _key_transform(sole_r, fr_end, rot=(rad(18), 0.0, 0.0))
        _set_facial_expression(nico, fr_end, "frustrated")

    # Apply smooth Bezier interpolation across all animated Nico controls
    for key_name, part in nico.items():
        if key_name != "armature" and part is not None:
            set_interpolation(part, interpolation="BEZIER")


def animate_seller(seller):
    """Animate the Cobbler / Shoe Seller watching Nico, inspecting the potatoes, and refusing the trade."""
    head = seller["head"]
    torso = seller["torso"]
    arm_l = seller["arm_l"]
    arm_r = seller["arm_r"]

    # Idle watching Nico approach (Frames 1-255)
    _key_transform(head, 1, rot=(0.0, 0.0, rad(-20)))
    _key_transform(torso, 1, rot=(0.0, 0.0, 0.0))
    _key_transform(arm_l, 1, rot=(rad(-10), rad(8), 0.0))
    _key_transform(arm_r, 1, rot=(rad(-10), rad(-8), 0.0))

    # Frame 272: Looks down surprised at the heavy 40kg potato sack landing on his counter
    _key_transform(head, 272, rot=(rad(22), 0.0, rad(-18)))
    _key_transform(torso, 272, rot=(rad(8), 0.0, 0.0))

    # Frames 315-360: Shakes head "NO" vigorously and gestures toward the Refusal X & Milk Sign
    _key_transform(head, 315, rot=(rad(10), 0.0, rad(-36)))
    _key_transform(head, 326, rot=(rad(10), 0.0, rad(6)))
    _key_transform(head, 337, rot=(rad(10), 0.0, rad(-36)))
    _key_transform(head, 350, rot=(rad(6), 0.0, rad(-14)))
    _key_transform(arm_l, 348, rot=(rad(-68), rad(16), 0.0))
    _key_transform(arm_r, 374, rot=(rad(-78), rad(-20), 0.0))
    _key_transform(head, 378, rot=(rad(-6), 0.0, rad(-8)))

    # Settle (Frames 410-450)
    _key_transform(arm_l, 412, rot=(rad(-18), rad(10), 0.0))
    _key_transform(arm_r, 412, rot=(rad(-18), rad(-10), 0.0))
    _key_transform(head, 450, rot=(rad(4), 0.0, rad(-15)))

    for part in seller.values():
        set_interpolation(part, interpolation="BEZIER")
