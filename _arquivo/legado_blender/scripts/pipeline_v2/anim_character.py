"""Procedural keyframe animation for Nico and the Shoe Seller across the 15-second storyboard."""

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
        # Eyebrows slightly raised inner corners, small worried frown
        _key_transform(eb_l, frame, loc=(-0.115, -0.232, 0.365), rot=(0.0, rad(-12), 0.0))
        _key_transform(eb_r, frame, loc=(0.115, -0.232, 0.365), rot=(0.0, rad(12), 0.0))
        _key_transform(mouth, frame, scale=(0.95, 1.0, 0.85))
    elif state == "surprised":
        # Eyebrows shoot high up, mouth opens into an O
        _key_transform(eb_l, frame, loc=(-0.115, -0.232, 0.395), rot=(0.0, rad(8), 0.0))
        _key_transform(eb_r, frame, loc=(0.115, -0.232, 0.395), rot=(0.0, rad(-8), 0.0))
        _key_transform(mouth, frame, scale=(0.75, 1.1, 2.35))
    elif state == "happy_idea":
        # Eyebrows arched confidently, wide hopeful mouth
        _key_transform(eb_l, frame, loc=(-0.115, -0.232, 0.378), rot=(0.0, rad(5), 0.0))
        _key_transform(eb_r, frame, loc=(0.115, -0.232, 0.378), rot=(0.0, rad(-5), 0.0))
        _key_transform(mouth, frame, scale=(1.30, 1.0, 1.15))
    elif state == "effort_carry":
        # Focused carry expression
        _key_transform(eb_l, frame, loc=(-0.115, -0.232, 0.358), rot=(0.0, rad(6), 0.0))
        _key_transform(eb_r, frame, loc=(0.115, -0.232, 0.358), rot=(0.0, rad(-6), 0.0))
        _key_transform(mouth, frame, scale=(1.05, 1.0, 0.90))
    elif state == "frustrated":
        # Strong comic disappointment / frustration: brows angled down/in, mouth wide open frown
        _key_transform(eb_l, frame, loc=(-0.115, -0.232, 0.350), rot=(0.0, rad(-18), 0.0))
        _key_transform(eb_r, frame, loc=(0.115, -0.232, 0.350), rot=(0.0, rad(18), 0.0))
        _key_transform(mouth, frame, scale=(1.25, 1.1, 1.85))
    else:
        _key_transform(eb_l, frame, loc=(-0.115, -0.232, 0.360), rot=(0.0, 0.0, 0.0))
        _key_transform(eb_r, frame, loc=(0.115, -0.232, 0.360), rot=(0.0, 0.0, 0.0))
        _key_transform(mouth, frame, scale=(1.0, 1.0, 1.0))


def animate_nico(nico):
    """Animate Nico through all 6 storyboard beats (Frames 1 to 450 at 30 FPS)."""
    root = nico["root"]
    pelvis = nico["pelvis"]
    torso = nico["torso"]
    head = nico["head"]
    arm_l, forearm_l = nico["arm_l"], nico["forearm_l"]
    arm_r, forearm_r = nico["arm_r"], nico["forearm_r"]
    leg_l, knee_l, foot_l = nico["leg_l"], nico["knee_l"], nico["foot_l"]
    leg_r, knee_r, foot_r = nico["leg_r"], nico["knee_r"], nico["foot_r"]
    sole_r = nico["damaged_sole"]

    sx, sy, sz = config.POSITIONS["nico_start"]

    # ==========================================================================
    # BEAT 1 (0-2s, Frames 1-60): Inspecting the Damaged Right Sneaker
    # ==========================================================================
    # Nico lifts his damaged right foot forward (-X rotation on leg_r), looking down at it
    # while the detached front sole flaps open and closed twice.
    _key_transform(root, 1, loc=(sx, sy, 0.015), rot=(0.0, 0.0, rad(35)))
    _key_transform(pelvis, 1, loc=(0.0, 0.0, 0.78), rot=(0.0, rad(-4), 0.0))
    _key_transform(torso, 1, rot=(rad(14), 0.0, 0.0))
    _key_transform(head, 1, rot=(rad(24), rad(-6), rad(-10)))
    _key_transform(arm_l, 1, rot=(rad(-15), rad(18), 0.0))
    _key_transform(forearm_l, 1, rot=(rad(-35), 0.0, 0.0))
    _key_transform(arm_r, 1, rot=(rad(-28), rad(-12), 0.0))
    _key_transform(forearm_r, 1, rot=(rad(-42), 0.0, 0.0))
    _key_transform(leg_l, 1, rot=(0.0, 0.0, 0.0))
    _key_transform(knee_l, 1, rot=(0.0, 0.0, 0.0))
    _key_transform(foot_l, 1, rot=(0.0, 0.0, 0.0))
    _key_transform(leg_r, 1, rot=(rad(-28), 0.0, 0.0))
    _key_transform(knee_r, 1, rot=(rad(18), 0.0, 0.0))
    _key_transform(foot_r, 1, rot=(rad(-16), 0.0, 0.0))
    _key_transform(sole_r, 1, rot=(rad(12), 0.0, 0.0))
    _set_facial_expression(nico, 1, "worried_shoe")

    # Lift right foot higher and flap the broken sole open/shut (frames 12, 20, 28, 38, 48, 58)
    shoe_inspect_frames = [
        (12, rad(-38), rad(20), rad(-18), rad(38), rad(24)),
        (20, rad(-32), rad(18), rad(-12), rad(10), rad(20)),
        (28, rad(-44), rad(22), rad(-26), rad(44), rad(26)),
        (38, rad(-34), rad(18), rad(-12), rad(12), rad(20)),
        (48, rad(-42), rad(22), rad(-24), rad(40), rad(24)),
        (60, rad(-12), rad(8), rad(-4), rad(4), rad(16)),
    ]
    for fr, lr_rx, kr_rx, fr_rx, sole_rx, hd_rx in shoe_inspect_frames:
        _key_transform(leg_r, fr, rot=(lr_rx, 0.0, 0.0))
        _key_transform(knee_r, fr, rot=(kr_rx, 0.0, 0.0))
        _key_transform(foot_r, fr, rot=(fr_rx, 0.0, 0.0))
        _key_transform(sole_r, fr, rot=(sole_rx, 0.0, 0.0))
        _key_transform(head, fr, rot=(hd_rx, rad(-5), rad(-8)))

    _key_transform(root, 60, loc=(sx, sy, 0.015), rot=(0.0, 0.0, rad(42)))
    _key_transform(pelvis, 60, loc=(0.0, 0.0, 0.78), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, 60, rot=(rad(8), 0.0, 0.0))
    _set_facial_expression(nico, 60, "worried_shoe")

    # ==========================================================================
    # BEAT 2 (2-4s, Frames 60-120): Startled by Falling Potato Sack, Then Idea!
    # ==========================================================================
    # Frame 73: Just before sack lands, foot touches down
    _key_transform(leg_r, 72, rot=(0.0, 0.0, 0.0))
    _key_transform(knee_r, 72, rot=(0.0, 0.0, 0.0))
    _key_transform(foot_r, 72, rot=(0.0, 0.0, 0.0))
    _key_transform(sole_r, 72, rot=(0.0, 0.0, 0.0))
    _key_transform(pelvis, 72, loc=(0.0, 0.0, 0.78), rot=(0.0, 0.0, 0.0))

    # Frame 75-79: Sack hits ground ("PLOC!") -> Nico jumps up in surprise!
    _key_transform(root, 78, loc=(sx - 0.04, sy, 0.015), rot=(0.0, 0.0, rad(62)))
    _key_transform(pelvis, 78, loc=(0.0, 0.0, 0.92), rot=(rad(-6), 0.0, 0.0))
    _key_transform(torso, 78, rot=(rad(-10), 0.0, 0.0))
    _key_transform(head, 78, rot=(rad(10), 0.0, rad(-12)))
    _key_transform(arm_l, 78, rot=(rad(-65), rad(35), 0.0))
    _key_transform(forearm_l, 78, rot=(rad(-45), 0.0, 0.0))
    _key_transform(arm_r, 78, rot=(rad(-65), rad(-35), 0.0))
    _key_transform(forearm_r, 78, rot=(rad(-45), 0.0, 0.0))
    _key_transform(leg_l, 78, rot=(rad(-15), 0.0, 0.0))
    _key_transform(knee_l, 78, rot=(rad(25), 0.0, 0.0))
    _key_transform(leg_r, 78, rot=(rad(12), 0.0, 0.0))
    _key_transform(knee_r, 78, rot=(rad(22), 0.0, 0.0))
    _set_facial_expression(nico, 76, "surprised")

    # Frame 85: Lands from jump with slight knee bend
    _key_transform(pelvis, 85, loc=(0.0, 0.0, 0.72), rot=(rad(4), 0.0, 0.0))
    _key_transform(leg_l, 85, rot=(rad(-16), 0.0, 0.0))
    _key_transform(knee_l, 85, rot=(rad(32), 0.0, 0.0))
    _key_transform(foot_l, 85, rot=(rad(-16), 0.0, 0.0))
    _key_transform(leg_r, 85, rot=(rad(-16), 0.0, 0.0))
    _key_transform(knee_r, 85, rot=(rad(32), 0.0, 0.0))
    _key_transform(foot_r, 85, rot=(rad(-16), 0.0, 0.0))

    # Frame 94: Stands up and inspects the potato sack closely
    _key_transform(root, 95, loc=(sx, sy, 0.015), rot=(0.0, 0.0, rad(72)))
    _key_transform(pelvis, 95, loc=(0.0, 0.0, 0.78), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, 95, rot=(rad(12), 0.0, 0.0))
    _key_transform(head, 95, rot=(rad(22), 0.0, 0.0))
    _key_transform(arm_l, 95, rot=(rad(-20), rad(12), 0.0))
    _key_transform(forearm_l, 95, rot=(rad(-30), 0.0, 0.0))
    _key_transform(arm_r, 95, rot=(rad(-20), rad(-12), 0.0))
    _key_transform(forearm_r, 95, rot=(rad(-30), 0.0, 0.0))
    _key_transform(leg_l, 95, rot=(0.0, 0.0, 0.0))
    _key_transform(knee_l, 95, rot=(0.0, 0.0, 0.0))
    _key_transform(foot_l, 95, rot=(0.0, 0.0, 0.0))
    _key_transform(leg_r, 95, rot=(0.0, 0.0, 0.0))
    _key_transform(knee_r, 95, rot=(0.0, 0.0, 0.0))
    _key_transform(foot_r, 95, rot=(0.0, 0.0, 0.0))

    # Frame 112-120: Looks up toward the shoe stall with an excited "Eureka!" gesture
    _key_transform(torso, 112, rot=(rad(-4), 0.0, 0.0))
    _key_transform(head, 112, rot=(rad(-6), 0.0, rad(-12)))
    _key_transform(arm_r, 112, rot=(rad(-75), rad(-15), 0.0))
    _key_transform(forearm_r, 112, rot=(rad(-55), 0.0, 0.0))
    _set_facial_expression(nico, 110, "happy_idea")

    # ==========================================================================
    # BEAT 3 (4-8s, Frames 120-240): Picking Up Sack & Walking to the Counter
    # ==========================================================================
    px, py, pz = config.POSITIONS["nico_pickup"]
    # Step up to the sack (Frames 120-132)
    _key_transform(root, 120, loc=(sx, sy, 0.015), rot=(0.0, 0.0, rad(78)))
    _key_transform(root, 126, loc=((sx + px) * 0.5, (sy + py) * 0.5, 0.015), rot=(0.0, 0.0, rad(82)))
    _key_transform(pelvis, 126, loc=(0.0, 0.0, 0.81), rot=(0.0, 0.0, 0.0))
    _key_transform(leg_l, 126, rot=(rad(-28), 0.0, 0.0))
    _key_transform(knee_l, 126, rot=(rad(22), 0.0, 0.0))
    _key_transform(leg_r, 126, rot=(rad(22), 0.0, 0.0))
    _key_transform(knee_r, 126, rot=(rad(10), 0.0, 0.0))

    # Frame 136: Squat down and reach both arms forward to grab the potato sack
    _key_transform(root, 136, loc=(px, py, 0.015), rot=(0.0, 0.0, rad(84)))
    _key_transform(pelvis, 136, loc=(0.0, 0.0, 0.62), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, 136, rot=(rad(32), 0.0, 0.0))
    _key_transform(head, 136, rot=(rad(10), 0.0, 0.0))
    _key_transform(arm_l, 136, rot=(rad(-68), rad(-10), 0.0))
    _key_transform(forearm_l, 136, rot=(rad(-28), 0.0, 0.0))
    _key_transform(arm_r, 136, rot=(rad(-68), rad(10), 0.0))
    _key_transform(forearm_r, 136, rot=(rad(-28), 0.0, 0.0))
    _key_transform(leg_l, 136, rot=(rad(-38), 0.0, 0.0))
    _key_transform(knee_l, 136, rot=(rad(68), 0.0, 0.0))
    _key_transform(foot_l, 136, rot=(rad(-30), 0.0, 0.0))
    _key_transform(leg_r, 136, rot=(rad(-38), 0.0, 0.0))
    _key_transform(knee_r, 136, rot=(rad(68), 0.0, 0.0))
    _key_transform(foot_r, 136, rot=(rad(-30), 0.0, 0.0))
    _set_facial_expression(nico, 136, "effort_carry")

    # Frame 148: Stand up holding the sack in front of his torso
    _key_transform(root, 148, loc=(px, py, 0.015), rot=(0.0, 0.0, rad(84)))
    _key_transform(pelvis, 148, loc=(0.0, 0.0, 0.77), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, 148, rot=(rad(-7), 0.0, 0.0))
    _key_transform(head, 148, rot=(rad(6), 0.0, rad(-8)))
    _key_transform(arm_l, 148, rot=(rad(-52), rad(-14), 0.0))
    _key_transform(forearm_l, 148, rot=(rad(-48), 0.0, 0.0))
    _key_transform(arm_r, 148, rot=(rad(-52), rad(14), 0.0))
    _key_transform(forearm_r, 148, rot=(rad(-48), 0.0, 0.0))
    _key_transform(leg_l, 148, rot=(0.0, 0.0, 0.0))
    _key_transform(knee_l, 148, rot=(0.0, 0.0, 0.0))
    _key_transform(foot_l, 148, rot=(0.0, 0.0, 0.0))
    _key_transform(leg_r, 148, rot=(0.0, 0.0, 0.0))
    _key_transform(knee_r, 148, rot=(0.0, 0.0, 0.0))
    _key_transform(foot_r, 148, rot=(0.0, 0.0, 0.0))

    # Frames 148-236: 6-Step Articulated Walk Cycle from (-1.78, -0.62) to (0.18, -0.52)
    walk_start_f = config.BEATS["walk_start"]
    walk_end_f = config.BEATS["walk_end"]
    cx_end, cy_end, _ = config.POSITIONS["nico_at_counter"]
    num_half_steps = 12

    for step_i in range(1, num_half_steps + 1):
        t = step_i / num_half_steps
        fr = round(walk_start_f + t * (walk_end_f - walk_start_f))
        fr_mid = round(fr - (walk_end_f - walk_start_f) / (2.0 * num_half_steps))
        nx = px + t * (cx_end - px)
        ny = py + t * (cy_end - py)
        nx_mid = px + ((step_i - 0.5) / num_half_steps) * (cx_end - px)
        ny_mid = py + ((step_i - 0.5) / num_half_steps) * (cy_end - py)

        # Passing pose at mid-step (pelvis high, swinging leg knee bent high so foot clears ground)
        left_swinging = (step_i % 2 == 1)
        _key_transform(root, fr_mid, loc=(nx_mid, ny_mid, 0.015), rot=(0.0, 0.0, rad(82)))
        _key_transform(
            pelvis,
            fr_mid,
            loc=(0.0, 0.0, 0.805),
            rot=(0.0, rad(4 if left_swinging else -4), 0.0),
        )
        if left_swinging:
            _key_transform(leg_l, fr_mid, rot=(rad(-24), 0.0, 0.0))
            _key_transform(knee_l, fr_mid, rot=(rad(44), 0.0, 0.0))
            _key_transform(foot_l, fr_mid, rot=(rad(-12), 0.0, 0.0))
            _key_transform(leg_r, fr_mid, rot=(rad(6), 0.0, 0.0))
            _key_transform(knee_r, fr_mid, rot=(rad(6), 0.0, 0.0))
            _key_transform(foot_r, fr_mid, rot=(rad(-6), 0.0, 0.0))
        else:
            _key_transform(leg_r, fr_mid, rot=(rad(-24), 0.0, 0.0))
            _key_transform(knee_r, fr_mid, rot=(rad(44), 0.0, 0.0))
            _key_transform(foot_r, fr_mid, rot=(rad(-12), 0.0, 0.0))
            _key_transform(leg_l, fr_mid, rot=(rad(6), 0.0, 0.0))
            _key_transform(knee_l, fr_mid, rot=(rad(6), 0.0, 0.0))
            _key_transform(foot_l, fr_mid, rot=(rad(-6), 0.0, 0.0))
            # Subtle flap of damaged right sole during right leg swing
            _key_transform(sole_r, fr_mid, rot=(rad(22), 0.0, 0.0))

        # Contact pose at full half-step
        _key_transform(root, fr, loc=(nx, ny, 0.015), rot=(0.0, 0.0, rad(80)))
        _key_transform(
            pelvis,
            fr,
            loc=(0.0, 0.0, 0.755),
            rot=(0.0, 0.0, rad(-5 if left_swinging else 5)),
        )
        _key_transform(
            torso,
            fr,
            rot=(rad(-7), rad(3 if left_swinging else -3), rad(4 if left_swinging else -4)),
        )
        # Arms bob slightly while holding the sack
        arm_bob = rad(-55 if left_swinging else -49)
        _key_transform(arm_l, fr, rot=(arm_bob, rad(-14), 0.0))
        _key_transform(arm_r, fr, rot=(arm_bob, rad(14), 0.0))

        if step_i < num_half_steps:
            if left_swinging:
                # Left foot forward (-X rot), Right foot back (+X rot)
                _key_transform(leg_l, fr, rot=(rad(-28), 0.0, 0.0))
                _key_transform(knee_l, fr, rot=(rad(10), 0.0, 0.0))
                _key_transform(foot_l, fr, rot=(rad(14), 0.0, 0.0))
                _key_transform(leg_r, fr, rot=(rad(26), 0.0, 0.0))
                _key_transform(knee_r, fr, rot=(rad(14), 0.0, 0.0))
                _key_transform(foot_r, fr, rot=(rad(-18), 0.0, 0.0))
            else:
                # Right foot forward, Left foot back
                _key_transform(leg_r, fr, rot=(rad(-28), 0.0, 0.0))
                _key_transform(knee_r, fr, rot=(rad(10), 0.0, 0.0))
                _key_transform(foot_r, fr, rot=(rad(14), 0.0, 0.0))
                _key_transform(sole_r, fr, rot=(rad(4), 0.0, 0.0))
                _key_transform(leg_l, fr, rot=(rad(26), 0.0, 0.0))
                _key_transform(knee_l, fr, rot=(rad(14), 0.0, 0.0))
                _key_transform(foot_l, fr, rot=(rad(-18), 0.0, 0.0))
        else:
            # Final step (frame 236): feet come together at counter
            _key_transform(pelvis, fr, loc=(0.0, 0.0, 0.78), rot=(0.0, 0.0, 0.0))
            _key_transform(leg_l, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(knee_l, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(foot_l, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(leg_r, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(knee_r, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(foot_r, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(sole_r, fr, rot=(0.0, 0.0, 0.0))

    # ==========================================================================
    # BEAT 4 (8-11s, Frames 240-330): Placing Sack on Counter & Offering Trade
    # ==========================================================================
    # Frame 248: Lift arms up to place the potato sack over the counter edge
    _key_transform(root, 248, loc=(cx_end, cy_end, 0.015), rot=(0.0, 0.0, rad(72)))
    _key_transform(torso, 248, rot=(rad(10), 0.0, 0.0))
    _key_transform(head, 248, rot=(rad(-4), 0.0, rad(-6)))
    _key_transform(arm_l, 248, rot=(rad(-85), rad(-10), 0.0))
    _key_transform(forearm_l, 248, rot=(rad(-30), 0.0, 0.0))
    _key_transform(arm_r, 248, rot=(rad(-85), rad(10), 0.0))
    _key_transform(forearm_r, 248, rot=(rad(-30), 0.0, 0.0))

    # Frame 260: Hands release the sack onto the counter (Z = 0.96)
    _key_transform(torso, 260, rot=(rad(6), 0.0, 0.0))
    _key_transform(arm_l, 260, rot=(rad(-62), rad(8), 0.0))
    _key_transform(forearm_l, 260, rot=(rad(-25), 0.0, 0.0))
    _key_transform(arm_r, 260, rot=(rad(-62), rad(-8), 0.0))
    _key_transform(forearm_r, 260, rot=(rad(-25), 0.0, 0.0))
    _set_facial_expression(nico, 260, "happy_idea")

    # Frames 275-325: Nico gestures enthusiastically from the potato sack to the new shoes!
    _key_transform(root, 278, loc=(cx_end, cy_end, 0.015), rot=(0.0, 0.0, rad(60)))
    _key_transform(torso, 278, rot=(0.0, 0.0, rad(-8)))
    _key_transform(head, 278, rot=(rad(-6), 0.0, rad(-12)))
    _key_transform(arm_l, 278, rot=(rad(-25), rad(18), 0.0))
    _key_transform(forearm_l, 278, rot=(rad(-35), 0.0, 0.0))
    _key_transform(arm_r, 278, rot=(rad(-78), rad(-18), 0.0))
    _key_transform(forearm_r, 278, rot=(rad(-20), 0.0, 0.0))

    _key_transform(arm_r, 302, rot=(rad(-62), rad(-32), 0.0))
    _key_transform(forearm_r, 302, rot=(rad(-40), 0.0, 0.0))
    _key_transform(head, 302, rot=(rad(-4), rad(5), rad(-16)))

    _key_transform(arm_r, 325, rot=(rad(-50), rad(-16), 0.0))
    _key_transform(forearm_r, 325, rot=(rad(-32), 0.0, 0.0))
    _set_facial_expression(nico, 325, "happy_idea")

    # ==========================================================================
    # BEAT 5 (11-13s, Frames 330-390): Watching the Refusal X and Milk Sign Pop Up
    # ==========================================================================
    # Frame 340: Red X pops up -> Nico startled, looks up at the Red X
    _key_transform(root, 342, loc=(cx_end, cy_end, 0.015), rot=(0.0, 0.0, rad(52)))
    _key_transform(pelvis, 342, loc=(0.0, 0.0, 0.81), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, 342, rot=(rad(-8), 0.0, 0.0))
    _key_transform(head, 342, rot=(rad(-24), rad(-6), rad(-8)))
    _key_transform(arm_l, 342, rot=(rad(-42), rad(24), 0.0))
    _key_transform(forearm_l, 342, rot=(rad(-55), 0.0, 0.0))
    _key_transform(arm_r, 342, rot=(rad(-42), rad(-24), 0.0))
    _key_transform(forearm_r, 342, rot=(rad(-55), 0.0, 0.0))
    _set_facial_expression(nico, 340, "surprised")

    # Frame 370: Milk sign pops up -> Nico turns head slightly right to read the Milk symbol
    _key_transform(pelvis, 370, loc=(0.0, 0.0, 0.78), rot=(0.0, 0.0, 0.0))
    _key_transform(head, 370, rot=(rad(-22), rad(6), rad(-22)))
    _set_facial_expression(nico, 370, "surprised")

    # ==========================================================================
    # BEAT 6 (13-15s, Frames 390-450): Comic Frustration & Deflated Slump
    # ==========================================================================
    # Frame 398: Hands to head in disbelief ("Leite?!")
    _key_transform(root, 398, loc=(cx_end, cy_end, 0.015), rot=(0.0, 0.0, rad(24)))
    _key_transform(pelvis, 398, loc=(0.0, 0.0, 0.79), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, 398, rot=(rad(-6), 0.0, 0.0))
    _key_transform(head, 398, rot=(rad(-10), rad(-6), rad(-4)))
    _key_transform(arm_l, 398, rot=(rad(-105), rad(24), 0.0))
    _key_transform(forearm_l, 398, rot=(rad(-85), 0.0, 0.0))
    _key_transform(arm_r, 398, rot=(rad(-105), rad(-24), 0.0))
    _key_transform(forearm_r, 398, rot=(rad(-85), 0.0, 0.0))
    _set_facial_expression(nico, 396, "frustrated")

    # Frame 418-450: Shoulders & pelvis slump down while face remains clearly visible toward camera!
    _key_transform(root, 418, loc=(cx_end, cy_end, 0.015), rot=(0.0, 0.0, rad(18)))
    _key_transform(pelvis, 418, loc=(0.0, 0.0, 0.71), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, 418, rot=(rad(10), rad(-4), 0.0))
    _key_transform(head, 418, rot=(rad(-4), rad(-8), rad(-4)))
    _key_transform(arm_l, 418, rot=(rad(-16), rad(14), 0.0))
    _key_transform(forearm_l, 418, rot=(rad(-18), 0.0, 0.0))
    _key_transform(arm_r, 418, rot=(rad(-16), rad(-14), 0.0))
    _key_transform(forearm_r, 418, rot=(rad(-18), 0.0, 0.0))
    _key_transform(leg_l, 418, rot=(rad(-16), 0.0, 0.0))
    _key_transform(knee_l, 418, rot=(rad(32), 0.0, 0.0))
    _key_transform(foot_l, 418, rot=(rad(-16), 0.0, 0.0))
    _key_transform(leg_r, 418, rot=(rad(-16), 0.0, 0.0))
    _key_transform(knee_r, 418, rot=(rad(32), 0.0, 0.0))
    _key_transform(foot_r, 418, rot=(rad(-16), 0.0, 0.0))
    # Broken shoe sole flops open one last time for comic punctuation!
    _key_transform(sole_r, 418, rot=(rad(36), 0.0, 0.0))

    # Subtle head shake of frustration between 424 and 450 (keeping chin up so face is 100% readable)
    _key_transform(head, 430, rot=(rad(-3), rad(7), rad(6)))
    _key_transform(head, 440, rot=(rad(-4), rad(-7), rad(-6)))
    _key_transform(head, 450, rot=(rad(-3), rad(-4), rad(-3)))
    _key_transform(torso, 450, rot=(rad(10), rad(-3), 0.0))
    _key_transform(pelvis, 450, loc=(0.0, 0.0, 0.71), rot=(0.0, 0.0, 0.0))
    _set_facial_expression(nico, 450, "frustrated")

    # Apply smooth Bezier interpolation across all animated Nico controls
    for part in nico.values():
        set_interpolation(part, interpolation="BEZIER")


def animate_seller(seller):
    """Animate the Shoe Seller watching Nico and shaking his head NO when offered potatoes."""
    head = seller["head"]
    torso = seller["torso"]
    arm_l = seller["arm_l"]
    arm_r = seller["arm_r"]

    # Idle watching Nico approach (Frames 1-250)
    _key_transform(head, 1, rot=(0.0, 0.0, rad(-20)))
    _key_transform(torso, 1, rot=(0.0, 0.0, 0.0))
    _key_transform(arm_l, 1, rot=(rad(-10), rad(8), 0.0))
    _key_transform(arm_r, 1, rot=(rad(-10), rad(-8), 0.0))

    # Frame 265: Looks down at the potato sack placed on the counter
    _key_transform(head, 265, rot=(rad(22), 0.0, rad(-18)))
    _key_transform(torso, 265, rot=(rad(8), 0.0, 0.0))

    # Frames 305-355: Shakes head "NO" and raises hand toward the Refusal / Milk signs
    _key_transform(head, 305, rot=(rad(10), 0.0, rad(-35)))
    _key_transform(head, 316, rot=(rad(10), 0.0, rad(5)))
    _key_transform(head, 327, rot=(rad(10), 0.0, rad(-35)))
    _key_transform(head, 338, rot=(rad(6), 0.0, rad(-12)))
    _key_transform(arm_l, 335, rot=(rad(-65), rad(15), 0.0))
    _key_transform(arm_r, 365, rot=(rad(-75), rad(-20), 0.0))
    _key_transform(head, 370, rot=(rad(-6), 0.0, rad(-8)))

    # Settle (Frames 400-450)
    _key_transform(arm_l, 410, rot=(rad(-20), rad(10), 0.0))
    _key_transform(arm_r, 410, rot=(rad(-20), rad(-10), 0.0))
    _key_transform(head, 450, rot=(rad(4), 0.0, rad(-15)))

    for part in seller.values():
        set_interpolation(part, interpolation="BEZIER")

