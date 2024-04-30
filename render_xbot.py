import bpy
import os
from glob import glob
from os.path import join
from pathlib import Path
import numpy as np
from mathutils import Vector, Quaternion, Matrix
import json
import sys
dirname = os.path.abspath(os.path.dirname(__file__))
sys.path.append(dirname)

from utils.data import read_data

from blender.geometry import (
    set_camera,
    build_plane,
    create_plane_blender,
    look_at
)
from blender.camera import set_extrinsic, set_intrinsic
from blender.animation import animate_by_motive
from blender.setup import (
    add_sunlight,
    get_parser,
    parse_args,
    set_cycles_renderer,
    set_output_properties,
    setup,
)

def set_camera_green(camera):
    K =[13365.842100, 0.000000, 1266.274010, 0.000000, 13353.006300, 1029.775970, 0.000000, 0.000000, 1.000000]
    K = np.array(K).reshape(3, 3)
    set_intrinsic(K, camera, 2448, 2048)
    R = [0.021391, 0.999674, -0.013928, 0.160876, -0.017191, -0.986825, -0.986743, 0.018868, -0.161191]
    T = [1.414816, -0.064123, 30.749459]
    R = np.array(R).reshape(3, 3)
    T = np.array(T).reshape(3, 1)
    set_extrinsic(R, T, camera)

color_table = [
    (94/255, 124/255, 226/255), # 青色
    (255/255, 200/255, 87/255), # yellow
    (74/255.,  189/255.,  172/255.), # green
    (8/255, 76/255, 97/255), # blue
    (219/255, 58/255, 52/255), # red
    (77/255, 40/255, 49/255), # brown
    '114B5F',
    'D89D6A',
    'A0A4B8',
    '2EC0F9',
    '30332E', # 淡黑色
    'F2D1C9', # 淡粉色
]

for i, color in enumerate(color_table):
    if isinstance(color, str):
        color_table[i] = tuple(map(lambda x: int(x, 16)/255., [color[:2], color[2:4], color[4:]]))
    color_table[i] = (*color_table[i], 1.0)

def load_xbot(mapname, pids):
    # 预先load所有的模型进来
    models = {}
    for pid in pids:
        target = mapname.get(pid, 'assets/xbot.fbx')
        scale = 1.
        bpy.ops.import_scene.fbx(
            filepath=target,
            use_manual_orientation=True,
            use_anim=False,
            axis_forward="Y",
            axis_up="Z",
            automatic_bone_orientation=True,
            global_scale=scale
        )
        obj_names = [o.name for o in bpy.context.selected_objects]
        ## e.g., ['Armature', 'Beta_Joints', 'Beta_Surface'] for `xbot.fbx`
        # 设置joints和surface的scale
        target_model = obj_names[0]
        for obj_name in obj_names[1:]:
            matname = list(bpy.data.objects[obj_name].material_slots.keys())[0]
            bpy.data.materials[matname].node_tree.nodes["Principled BSDF"].inputs[0].default_value = color_table[pid]
        character = bpy.data.objects[target_model]
        character.location = Vector((0, 0, 0))
        armature = bpy.data.armatures[target_model]
        armature.animation_data_clear()
        models[pid] = target_model
    return models

if __name__ == "__main__":
    parser = get_parser()
    parser.add_argument('--id', type=int, default=0)
    parser.add_argument('--start_frame', type=int, default=0)
    parser.add_argument('--end_frame', type=int, default=0)
    parser.add_argument('--blender_type', type=str, default='adj', choices=['adj', 'img', 'video', 'tpose', 'debug'])
    args = parse_args(parser)

    assert args.start_frame <= args.end_frame, f"Error: start frame: {args.start_frame} > end frame: {args.end_frame}"

    if args.blender_type == 'debug':
        path = 'D:/blender_project/begin/fbx_binary'
        filenames = glob(os.path.join(path, f'{args.id:03d}_*.fbx'))
        assert len(filenames) > 0, f"Cannot find the file with id: {args.id}"
        filename = filenames[0]
        bpy.ops.import_scene.fbx(filepath=filename, automatic_bone_orientation=True, force_connect_children=True)

    setup()
    add_sunlight(name='Light0', location=(2., 5., 5.), rotation=(-np.pi/4, 0, 0), strength=1.)
    add_sunlight(name='Light1', location=(2., -5., 5.), rotation=(np.pi/4, 0, 0), strength=1.)


    cam_fn = Path(args.path) / 'info' / 'cam.json'
    f = json.load(cam_fn.open('r'))
    cam_xyz = f['cam_xyz']
    cam_euler = f['cam_euler']
    cam_f = f['cam_f']
    camera = set_camera(location=cam_xyz, rotation=cam_euler, focal=cam_f) 
    # set_camera_green(camera)
    
    pids = [0, 1]
    mapname = {
        0: 'assets/xbot.fbx',
        1: 'assets/xbot.fbx'
    }
    models = load_xbot(mapname, pids)

    params, frame_num = read_data(args.path, args.id)
    print(frame_num)
    if args.end_frame - args.start_frame + 1 > frame_num:
        start = 0
        end   = frame_num
    else:
        start = args.start_frame
        end = args.end_frame + 1

    assert end <= frame_num, f'end: {end} > frame num: {frame_num}'
    frame_num = end - start
    bpy.context.scene.frame_end = frame_num

    args.res_x = 2448
    args.res_y = 2048

    set_cycles_renderer(
        bpy.context.scene,
        bpy.data.objects["Camera"],
        num_samples=args.num_samples,
        use_transparent_bg=True,
        use_denoising=args.denoising,
    )

    scene = bpy.context.scene
    offset = [0, -1, 0]

    for frame in range(start, end):
        scene.frame_set(frame - start)
        print('Loading frames: ', frame)
        for param in params:
            pid = param['id']
            character = bpy.data.objects[models[pid]]
            bones = character.pose.bones
            animate_by_motive(param['params'][frame], bones, frame, offset, args.blender_type=='tpose')
        if args.blender_type == 'video':
            output_fn = f'{args.path}/rend_imgs/{args.id}/{frame:04d}.png'
            bpy.context.scene.render.filepath = output_fn
            bpy.ops.render.render(write_still=True, animation=False)
        elif args.blender_type == 'img':
            output_fn = f'{args.path}/rend_img/{args.id}/{frame:04d}.png'
            bpy.context.scene.render.filepath = output_fn
            bpy.ops.render.render(write_still=True, animation=False)


    # 创建一个地面用来制造阴影
    plane = create_plane_blender((7, 0, 0.0), size=15)
    plane.hide_viewport = True
    plane.is_shadow_catcher = True

