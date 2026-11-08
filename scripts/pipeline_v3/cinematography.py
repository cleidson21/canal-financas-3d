"""Cinematography V3: 7-shot vertical 9:16 direction with objective camera cuts and Opening A/B support."""

import bpy
from .primitives import create_empty
from .scene_setup import link_to_collection, set_camera_cut_holds


def setup_and_animate_camera(scene, col_lights, opening_variant="A"):
    """Create Camera_Principal and Camera_Target with TRACK_TO constraint and keyframe 7 narrative shots.

    opening_variant:
      - 'A' (default): Cold Open starts with an immediate close-up of the damaged sneaker opening (0.0-1.0s),
        then pulls back to frame the stumble and recovery (1.0-2.2s).
      - 'B': Cold Open starts in a wider medium-low shot of Nico walking and stumbling to reveal the shoe.
    """
    target = create_empty(
        "Camera_Target",
        location=(-2.05, -0.62, 0.25),
        col=col_lights,
        empty_size=0.2,
    )

    cam_data = bpy.data.cameras.new(name="Camera_Principal")
    cam_data.type = "PERSP"
    cam_data.lens = 48.0
    cam_data.clip_start = 0.08
    cam_data.clip_end = 100.0

    cam_obj = bpy.data.objects.new(name="Camera_Principal", object_data=cam_data)
    cam_obj.location = (-1.62, -2.05, 0.42)
    link_to_collection(cam_obj, col_lights)
    scene.camera = cam_obj

    track = cam_obj.constraints.new(type="TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    if opening_variant.upper() == "A":
        shot1_keys = [
            # Shot 1A (Frames 1-30): Tight low-angle Close-Up on Nico's damaged right sneaker peeling open
            (1, (-1.68, -2.02, 0.40), (-2.12, -0.66, 0.22)),
            (15, (-1.62, -1.92, 0.36), (-2.04, -0.66, 0.20)),
            (28, (-1.68, -2.55, 0.64), (-2.00, -0.62, 0.48)),
            # Frames 31-66: Smooth pull-back to capture Nico stumbling forward and looking down at his shoe
            (45, (-1.80, -3.82, 1.05), (-1.94, -0.58, 0.78)),
            (66, (-1.78, -3.82, 1.06), (-1.88, -0.56, 0.80)),
        ]
    else:
        shot1_keys = [
            # Shot 1B (Frames 1-66): Wider medium shot of Nico stumbling first, then pushing in on the shoe
            (1, (-1.95, -3.95, 1.15), (-2.15, -0.60, 0.85)),
            (28, (-1.88, -3.82, 1.08), (-2.00, -0.60, 0.82)),
            (45, (-1.80, -3.65, 1.02), (-1.94, -0.58, 0.76)),
            (66, (-1.65, -2.35, 0.52), (-1.84, -0.56, 0.34)),
        ]

    # Remaining 6 shots across the 15s (450 frames) storyboard
    shots = shot1_keys + [
        # Shot 2 (Frames 67-135 | 2.2-4.5s): CUT to Medium-Full Reveal (Nico + Damaged Shoe + 40kg Potato Cart)
        (67, (-1.68, -4.45, 1.32), (-1.66, -0.22, 0.84)),
        (105, (-1.66, -4.35, 1.28), (-1.64, -0.22, 0.86)),
        (135, (-1.54, -4.25, 1.26), (-1.46, -0.35, 0.84)),

        # Shot 3 (Frames 136-198 | 4.5-6.6s): CUT to Dynamic Tracking Shot of Grounded Heavy Walk
        (136, (-1.15, -3.88, 1.12), (-1.22, -0.48, 0.78)),
        (180, (-0.52, -3.88, 1.14), (-0.56, -0.48, 0.78)),
        (198, (-0.28, -3.92, 1.16), (-0.32, -0.48, 0.80)),

        # Shot 4 (Frames 199-255 | 6.6-8.5s): CUT to Merchandise & Stall Arrival (40kg Sack + Gleaming New Shoes)
        (199, (0.38, -3.85, 1.36), (0.48, -0.28, 1.02)),
        (255, (0.45, -3.95, 1.38), (0.58, -0.25, 1.04)),

        # Shot 5 (Frames 256-345 | 8.5-11.5s): CUT to Barter Proposal Shot (Nico, Potato Sack 'PLOC!', New Shoes, Seller)
        (256, (0.48, -5.05, 1.56), (0.68, -0.18, 1.12)),
        (285, (0.50, -5.02, 1.56), (0.68, -0.18, 1.12)),
        (345, (0.52, -5.02, 1.56), (0.70, -0.18, 1.14)),

        # Shot 6 (Frames 346-405 | 11.5-13.5s): CUT to Refusal & Milk Desire Focus (Nico + Red X + Large Milk Sign all inside 9:16)
        (346, (0.56, -5.58, 1.62), (0.66, -0.20, 1.34)),
        (375, (0.58, -5.65, 1.64), (0.68, -0.20, 1.36)),
        (405, (0.58, -5.65, 1.64), (0.68, -0.20, 1.36)),

        # Shot 7 (Frames 406-450 | 13.5-15.0s): CUT to Medium Close-Up of Nico's Comic Frustration Reaction + Potato Sack
        (406, (0.20, -3.88, 1.34), (0.32, -0.36, 1.22)),
        (435, (0.18, -3.78, 1.30), (0.28, -0.38, 1.18)),
        (450, (0.18, -3.76, 1.30), (0.28, -0.38, 1.18)),
    ]

    for fr, cam_loc, tgt_loc in shots:
        cam_obj.location = cam_loc
        cam_obj.keyframe_insert(data_path="location", frame=fr)
        target.location = tgt_loc
        target.keyframe_insert(data_path="location", frame=fr)

    # Set CONSTANT holds on the last frame of each shot so cuts on frames 67, 136, 199, 256, 346, 406 are instantaneous
    cut_hold_frames = [66, 135, 198, 255, 345, 405]
    set_camera_cut_holds(cam_obj, cut_hold_frames)
    set_camera_cut_holds(target, cut_hold_frames)

    return {"camera": cam_obj, "target": target}
