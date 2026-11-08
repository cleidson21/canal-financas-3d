"""Cinematography setup: Perspective Camera rig with Track-To target and 6-beat vertical 9:16 choreography."""

import bpy
from .primitives import create_empty
from .scene_setup import link_to_collection, set_interpolation


def setup_and_animate_camera(scene, col_lights):
    """Create Camera_Principal and Camera_Target with a TRACK_TO constraint and keyframe the 15s storyboard."""
    target = create_empty(
        "Camera_Target",
        location=(-2.12, -0.68, 0.85),
        col=col_lights,
        empty_size=0.2,
    )

    cam_data = bpy.data.cameras.new(name="Camera_Principal")
    cam_data.type = "PERSP"
    cam_data.lens = 45.0
    cam_data.clip_start = 0.1
    cam_data.clip_end = 100.0

    cam_obj = bpy.data.objects.new(name="Camera_Principal", object_data=cam_data)
    cam_obj.location = (-2.00, -4.15, 1.32)
    link_to_collection(cam_obj, col_lights)
    scene.camera = cam_obj

    # Track-To constraint keeps horizon 100% level and centers Camera_Target accurately
    track = cam_obj.constraints.new(type="TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    # Keyframes: (frame, cam_location, target_location)
    shots = [
        # 0-2s (Frames 1-60): Start with smooth dolly-in onto Nico and his lifted damaged right sneaker
        (1, (-1.95, -4.25, 1.32), (-2.12, -0.65, 0.90)),
        (24, (-1.95, -3.62, 1.02), (-2.10, -0.68, 0.84)),
        (54, (-1.94, -3.65, 1.04), (-2.10, -0.68, 0.85)),
        # 2-4s (Frames 60-120): Pull out to frame the falling Potato Sack beside Nico & his startled jump
        (68, (-1.88, -4.85, 1.46), (-1.86, -0.60, 0.96)),
        (95, (-1.84, -4.75, 1.44), (-1.82, -0.60, 0.94)),
        (120, (-1.76, -4.68, 1.44), (-1.74, -0.60, 0.96)),
        # 4-8s (Frames 120-240): Smooth tracking shot following Nico as he picks up the sack and walks to the stall
        (142, (-1.52, -4.72, 1.48), (-1.50, -0.58, 0.94)),
        (190, (-0.55, -4.85, 1.58), (-0.52, -0.45, 1.05)),
        (238, (0.34, -5.22, 1.70), (0.64, -0.22, 1.18)),
        # 8-11s (Frames 240-330): Clear medium-wide framing of Nico, potato sack on counter, new shoes, and seller
        (265, (0.42, -5.20, 1.72), (0.70, -0.18, 1.22)),
        (325, (0.44, -5.20, 1.72), (0.72, -0.18, 1.24)),
        # 11-13s (Frames 330-390): Tilt slightly up to highlight the Red X and Milk symbol signs above the counter
        (345, (0.48, -5.22, 1.74), (0.72, -0.22, 1.42)),
        (385, (0.50, -5.22, 1.74), (0.74, -0.22, 1.42)),
        # 13-15s (Frames 390-450): Push in onto Nico's comic frustration reaction (camera slightly lower so face is 100% clear under cap)
        (418, (0.22, -4.22, 1.26), (0.46, -0.32, 1.34)),
        (450, (0.20, -4.15, 1.24), (0.44, -0.34, 1.32)),
    ]

    for fr, cam_loc, tgt_loc in shots:
        cam_obj.location = cam_loc
        cam_obj.keyframe_insert(data_path="location", frame=fr)
        target.location = tgt_loc
        target.keyframe_insert(data_path="location", frame=fr)

    set_interpolation(cam_obj, interpolation="BEZIER")
    set_interpolation(target, interpolation="BEZIER")

    return {"camera": cam_obj, "target": target}

