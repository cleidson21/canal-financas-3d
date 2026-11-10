"""Two-link control animation baked to ordinary keyframes, without runtime handlers."""
import math
import bpy
from mathutils import Matrix, Vector
from pipeline_v3.scene_setup import set_interpolation

def smooth(x):
    x=max(0,min(1,x));return x*x*(3-2*x)

def track(t,keys):
    if t<=keys[0][0]:return Vector(keys[0][1])
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<=b:return Vector(va).lerp(Vector(vb),smooth((t-a)/(b-a)))
    return Vector(keys[-1][1])

def key(ob,frame,path):ob.keyframe_insert(data_path=path,frame=frame)

def _set_chain_rotations(upper, lower, rotations, previous):
    for index, (control, rotation) in enumerate(zip((upper, lower), rotations)):
        if previous is not None:
            rotation.make_compatible(previous[index])
        control.rotation_mode = 'QUATERNION'
        control.rotation_quaternion = rotation


def _endpoint(upper, lower, tip):
    """Predict the point on an unconstrained, unit-scale pivot chain."""
    return upper.parent.matrix_world @ (
        upper.location + upper.rotation_quaternion @ (
            lower.location + lower.rotation_quaternion @ tip.location))


def aim_chain(upper, lower, tip, target, bend=(0,-1,0), *, previous=None, evaluate=True):
    """Preserve the legacy bend and roll on the production pivot hierarchies."""
    parent = upper.parent.matrix_world
    target = Vector(target)
    delta = parent.inverted() @ target - upper.location
    distance = delta.length
    rest1, rest2 = lower.location, tip.location
    a, b = rest1.length, rest2.length
    clamped = max(abs(a-b)+.001, min(distance, a+b-.001))
    axis = delta.normalized()
    bend_local = parent.to_3x3().inverted() @ Vector(bend)
    offset = bend_local - axis * bend_local.dot(axis)
    if offset.length < .001:
        offset = Vector((0,1,0)).cross(axis)
    along = (a*a + clamped*clamped - b*b)/(2*clamped)
    elbow = axis*along + offset.normalized()*math.sqrt(max(0, a*a-along*along))
    shoulder = rest1.rotation_difference(elbow)
    # Inverting the parent first keeps inherited merchant scale out of the solve.
    # Aim the lower segment at the original target, as in the legacy solver.
    lower_goal = shoulder.inverted() @ delta - rest1
    forearm = rest2.rotation_difference(lower_goal)
    _set_chain_rotations(upper, lower, (shoulder, forearm), previous)
    if evaluate:
        bpy.context.view_layer.update()
        return (tip.matrix_world.translation-target).length
    return (_endpoint(upper, lower, tip)-target).length


def nico_elbow_pole(side):
    return (.65 if side == 'R' else -.65, .72, -.18)


def hand(actor, side, target, frame, *, pole=None, previous=None, evaluate=True):
    upper, lower = actor['arms'][side]
    palm = actor['palms'][side]
    prior = previous.get(upper.name) if previous is not None else None
    if pole is None:
        error = aim_chain(upper, lower, palm, target, previous=prior, evaluate=evaluate)
    else:
        pose_arm(upper, lower, palm, target, pole, prior)
        if evaluate:
            bpy.context.view_layer.update()
        position = palm.matrix_world.translation if evaluate else _endpoint(upper, lower, palm)
        error = (position-Vector(target)).length
    if previous is not None:
        previous[upper.name] = (upper.rotation_quaternion.copy(), lower.rotation_quaternion.copy())
    key(upper,frame,'rotation_quaternion')
    key(lower,frame,'rotation_quaternion')
    return error


def _arm_basis(segment, normal):
    """Build a right-handed frame with the limb pointing along local -Z."""
    z = -segment.normalized()
    x = normal.normalized()
    return Matrix((x, z.cross(x), z)).transposed()


def pose_arm(upper, lower, palm, target, pole, previous=None):
    """Pose Nico's empty controls using a torso-local elbow pole and bounded flexion.

    The existing WORLD copy-transform constraints carry this pose to the skin.
    The caller can bake the returned rotations as ordinary quaternion curves.
    """
    start = upper.location
    goal = upper.parent.matrix_world.inverted() @ Vector(target)
    delta = goal - start
    if delta.length < 1e-6:
        raise ValueError("Hand target coincides with shoulder")
    axis = delta.normalized()
    outward = Vector(pole)
    offset = outward - axis * outward.dot(axis)
    if offset.length < 1e-4:
        raise ValueError("Elbow pole is aligned with the shoulder-to-hand axis")
    offset.normalize()

    upper_rest, lower_rest = lower.location, palm.location
    a, b = upper_rest.length, lower_rest.length
    reach = lambda angle: math.sqrt(a*a + b*b + 2*a*b*math.cos(math.radians(angle)))
    distance = min(max(delta.length, reach(120)), reach(12))
    along = (a*a + distance*distance - b*b) / (2*distance)
    elbow = axis * along + offset * math.sqrt(max(0, a*a - along*along))
    forearm = axis * distance - elbow

    # The bend plane supplies roll too, so a rotating wrist target cannot flip the
    # sleeve or the forearm independently of the elbow. Use +X for a forward bend.
    normal = forearm.cross(elbow).normalized()
    rotations = []
    for rest, posed in ((upper_rest, elbow), (lower_rest, forearm)):
        rest_normal = Vector((1, 0, 0))
        rest_normal -= rest.normalized() * rest_normal.dot(rest.normalized())
        rotations.append((_arm_basis(posed, normal) @ _arm_basis(rest, rest_normal).transposed()).to_quaternion())
    shoulder, forearm_absolute = rotations
    local = (shoulder, shoulder.inverted() @ forearm_absolute)
    _set_chain_rotations(upper, lower, local, previous)
    return local

def action_curve(start,duration,intensity=1):
    """Normalized anticipation, presentation, settling and recovery envelope."""
    return [(start,0),(start+duration*.16,-.12*intensity),(start+duration*.55,intensity),(start+duration*.74,.92*intensity),(start+duration,0)]

def gesture(actor,name,start,duration=1,intensity=1,side='R',direction=None):
    """Keyed offer/receive/point/accept/refuse and expressive body actions.

    Hand actions are authored in world space, so the prop can share a contact point.
    Returns cue metadata; caller may coordinate multiple characters on the same cue.
    """
    scene=bpy.context.scene;frames=range(round(start*30)+1,round((start+duration)*30)+2)
    base=None;base_rotation=None
    for frame in frames:
        t=(frame-1)/30;phase=max(0,min(1,(t-start)/duration))
        scene.frame_set(frame)
        if name in ('offer','deliver','receive','point','transport'):
            if base is None:base=actor['palms'][side].matrix_world.translation.copy()
            dest=Vector(direction) if direction else base+Vector((.15,-.1,.10))*intensity
            target=base.lerp(dest,smooth(phase))
            hand(actor,side,target,frame)
        else:
            head=actor['head']
            if base_rotation is None:base_rotation=head.rotation_euler.copy()
            head.rotation_euler.x=math.sin(phase*math.tau)*.12*intensity if name in ('accept','satisfaction') else 0
            head.rotation_euler.z=math.sin(phase*math.tau)*.15*intensity if name in ('refuse','distrust','surprise') else 0
            if name=='recovery':head.rotation_euler=tuple(v*(1-smooth(phase)) for v in base_rotation)
            key(head,frame,'rotation_euler')
    return dict(action=name,start=start,duration=duration,intensity=intensity)

def look_at(actor,target,frame,intensity=1):
    p=actor['root'].matrix_world.inverted()@Vector(target)
    yaw=math.atan2(p.x,-p.y)
    actor['head'].rotation_euler.z=max(-.55,min(.55,yaw))*intensity
    key(actor['head'],frame,'rotation_euler')

def settle(actor,start,duration=.5,intensity=1):return gesture(actor,'recovery',start,duration,intensity)
def offer(actor,start,direction,duration=1,intensity=1):return gesture(actor,'offer',start,duration,intensity,direction=direction)
def accept(actor,start,duration=.6,intensity=1):return gesture(actor,'accept',start,duration,intensity)
def refuse(actor,start,duration=.7,intensity=1):return gesture(actor,'refuse',start,duration,intensity)
def deliver(actor,start,direction,duration=.7,intensity=1):return gesture(actor,'deliver',start,duration,intensity,direction=direction)
def receive(actor,start,direction,duration=.7,intensity=1):return gesture(actor,'receive',start,duration,intensity,direction=direction)
def point(actor,start,direction,duration=.7,intensity=1):return gesture(actor,'point',start,duration,intensity,direction=direction)
def surprise(actor,start,duration=.7,intensity=1):return gesture(actor,'surprise',start,duration,intensity)
def satisfaction(actor,start,duration=.7,intensity=1):return gesture(actor,'satisfaction',start,duration,intensity)
def distrust(actor,start,duration=.7,intensity=1):return gesture(actor,'distrust',start,duration,intensity)
def transport(actor,start,direction,duration=.7,intensity=1):return gesture(actor,'transport',start,duration,intensity,direction=direction)

def bind_transfer(prop,frame,giver,receiver,handoff_frame,offset=(0,0,.07),giver_offset=None,receiver_offset=None):
    """Bake one visible object to the current palm; contact poses must coincide at handoff."""
    owner=giver if frame<handoff_frame else receiver
    support_offset=(giver_offset or offset) if frame<handoff_frame else (receiver_offset or offset)
    prop.location=owner.matrix_world.translation+Vector(support_offset)
    key(prop,frame,'location')


def set_nico_grip(side, grip_value, frame):
    """Keyframe Nico's thumb opposition (0.0 open -> 1.0 grip) without breaking _endpoint."""
    thumb = bpy.data.objects.get(f'Nico_Mao_Polegar_{side}')
    if thumb is None:
        return
    g = max(0.0, min(1.0, float(grip_value)))
    sign = 1.0 if side == 'R' else -1.0
    thumb.location = (
        -sign * (0.042 + 0.008 * (1.0 - g)),
        -0.044 - 0.008 * (1.0 - g),
        -0.235 - 0.008 * g,
    )
    key(thumb, frame, 'location')


def clamp_nico_reach(nico, side, target, min_angle=16.0, max_angle=115.0):
    """Clamp a world-space hand target into Nico's anatomical reach shell."""
    upper, lower = nico['arms'][side]
    palm = nico['palms'][side]
    parent_mat = upper.parent.matrix_world
    goal_local = parent_mat.inverted() @ Vector(target)
    delta = goal_local - upper.location
    dist = delta.length
    if dist < 1e-5:
        delta = Vector((0.15 if side == 'R' else -0.15, -0.25, -0.15))
        dist = delta.length
    a, b = lower.location.length, palm.location.length
    min_d = math.sqrt(a*a + b*b + 2*a*b*math.cos(math.radians(max_angle)))
    max_d = math.sqrt(a*a + b*b + 2*a*b*math.cos(math.radians(min_angle)))
    clamped_d = min(max(dist, min_d), max_d)
    return tuple(parent_mat @ (upper.location + delta.normalized() * clamped_d))


def finalize_curves(objects):
    for ob in objects:set_interpolation(ob,interpolation='LINEAR')
