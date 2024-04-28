'''
  @ Date: 2022-09-13 12:32:11
  @ Author: Qing Shuai
  @ Mail: s_q@zju.edu.cn
  @ LastEditors: Qing Shuai
  @ LastEditTime: 2022-09-13 12:36:22
  @ FilePath: /EasyMocapPublic/scripts/blender/render_example.py
'''
# TODO: This scripts show how to use blender to render a cube
import numpy as np
import bpy

import sys
sys.path.append("D:/blender_project/begin/my_blender")

from blender.geometry import (
    load_humanmesh,
    load_scenemesh,
)
from blender.geometry import *
from blender.material import *

from blender.setup import (
    setup_camera_light,
    get_parser,
    parse_args,
    set_cycles_renderer,
    setup_output_option,
    setup,
    render_image,
)
from blender.material import colorObj
from pathlib import Path


def setup_huaijin_obj(args, input_dir, load_color=True, color=None):
    scene_fn = input_dir / args.obj_name
    rotation = (0, 0, 0) if args.zup else (np.pi/2, 0, 0)
    obj = load_scenemesh(str(scene_fn), rotation=rotation)
    if load_color:
        set_scenemesh_ori_color(obj)
    if color != None:
        RGBA = (color[0], color[1], color[2], 1.0)
        meshColor = colorObj(RGBA, 0.5, 1.0, 1.0, 0, 2.0)
        setMat_plastic(obj, meshColor, specular=0.5, roughness=0.5)
    return obj


def setup_motions(input_dir, args, mode="huaijin_setting", k=1, fid=None):
    obj_list = []
    for motion in input_dir.iterdir():
        if motion.is_dir() and motion.name not in ['info', 'rend_imgs']:
            if int(motion.name) not in [3, 5, 6, 10, 13, 14, 16, 17, 19, 23, 24, 26, 27, 28, 30, 32, 35, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 51, 52, 55, 56, 57, 58, 59, 60, 61, 62, 64, 65, 66, 67, 68, 69, 70, 74, 77, 80, 81, 82, 83, 85, 86, 88, 89, 90, 92, 93, 94, 98, 100, 101, 106, 107, 109, 110, 111, 112, 113, 115, 117, 118, 119, 120, 121, 125, 126, 127, 128, 129, 131, 132, 133, 134, 136, 137, 138, 139, 140, 143, 144, 145, 147, 149, 150, 151, 152, 156, 157, 158, 165, 166, 167, 169, 170, 172, 175, 178, 185, 187, 190, 191, 197, 198, 199, 200, 202, 204, 205, 208, 209, 210, 211, 215, 219, 220, 222, 225, 226, 228, 230, 232, 233, 236, 237, 239, 242, 244, 245, 246, 247, 248, 250, 251, 252, 253, 254, 256]:
                continue
            
            mesh, _ = setup_motion(motion, args, mode=mode, k=k, fid=fid)
            obj_list.append(mesh)
    return obj_list

        
def setup_motion(input_dir, args, mode='huaijin_setting', k=1, fid=None):
    motion_dir = input_dir
    key = args.motion
    rotation = (0, 0, 0) if args.zup else (np.pi/2, 0, 0)
    
    start_color = np.array(get_start_color(key))
    end_color = np.array(get_end_color(key))
    
    if mode == 'huaijin_setting':
        all_files = sorted(motion_dir.glob('frame*.obj'))
        num_colors = len(all_files)
        for t, obj_fn in enumerate(all_files):
            color = start_color + (end_color - start_color) * (t / (num_colors - 1))
            RGBA = (color[0], color[1], color[2], 1.0)
            meshColor = colorObj(RGBA, 0.5, 1.0, 1.0, 0, 2.0)
            load_humanmesh(str(obj_fn), pid=None, meshColor=meshColor, rotation=rotation)

    elif mode == 'put_every_k_together':
        all_files = sorted(motion_dir.glob('*.obj'))
        num_colors = len(all_files[::k])
        for t, obj_fn in enumerate(all_files[::k]):
            color = start_color + (end_color - start_color) * (t / (num_colors - 1))
            RGBA = (color[0], color[1], color[2], 1.0)
            meshColor = colorObj(RGBA, 0.5, 1.0, 1.0, 0, 2.0)
            load_humanmesh(str(obj_fn), pid=None, meshColor=meshColor, rotation=rotation)
        obj_fn = all_files[-1]
        load_humanmesh(str(obj_fn), pid=None, meshColor=meshColor, rotation=rotation)
        
    elif mode == 'vis_fid':
        RGBA = (end_color[0], end_color[1], end_color[2], 1.0)
        meshColor = colorObj(RGBA, 0.5, 1.0, 1.0, 0, 2.0)
        all_files = sorted(motion_dir.glob('frame*.obj'))
        if fid >= len(all_files):
            obj_fn = all_files[-1]
        else:
            obj_fn = all_files[fid]
        obj = load_humanmesh(str(obj_fn), pid=None, meshColor=meshColor, rotation=rotation)
        return obj, obj_fn


def draw_image_video_common(args, input_dir):
    setup()
    if args.blender_type == 'tpose':
        build_plane(translation=(0, 0, 0), plane_size=50)
    else:
        if args.zup:
            build_plane(translation=(0, 0, 0), plane_size=30)
        else: # yup
            build_plane(translation=(0, 0, -0.5355), plane_size=30)
    if args.blender_type != 'tpose':
        my_obj = setup_huaijin_obj(args, input_dir, load_color=True, color=None)
    else: my_obj = None
    
    (input_dir / 'info').mkdir(exist_ok=True)
    cam_fn = input_dir / 'info' / 'cam.json'
    setup_camera_light(input_dir, scene_obj=my_obj, cam_fn=cam_fn)

    # ------
    setup_output_option(args)
    
    set_cycles_renderer(
        bpy.context.scene,
        bpy.data.objects["Camera"],
        num_samples=args.num_samples,
        use_transparent_bg=args.use_transparent_bg,
        use_denoising=args.denoising,
    )


def render_tpose(args):
    input_dir = Path(args.path) / args.motion
    draw_image_video_common(args, input_dir)
    setup_motion(input_dir, args, mode="vis_fid", fid=0)
    
    output_fn = f'{input_dir}/tpose.png'
    render_image(output_fn)


def render_video(args):
    if args.diverse:
        input_dir = Path(args.path) / args.motion
        all_sample_ids =  [x.name for x in input_dir.iterdir() if x.is_dir()]
        length = len(list((input_dir / all_sample_ids[0]).glob('frame*.obj')))
        print(f'length: {length}')
    else:
        input_dir = Path(args.path) / args.motion / args.sample_id
        length = len(list(input_dir.glob('frame*.obj')))

    draw_image_video_common(args, input_dir)
    
    obj_list = []
    obj = None
    for t in range(0, length, 1):
        if args.diverse:
            for obj in obj_list:
                bpy.data.objects.remove(obj, do_unlink=True)
            obj_list = setup_motions(input_dir, args, mode="vis_fid", fid=t)
            obj_fn = None
        else:
            if obj is not None:
                bpy.data.objects.remove(obj, do_unlink=True)
            obj, obj_fn = setup_motion(input_dir, args, mode="vis_fid", fid=t)
        
        if obj_fn is not None:
            frame_name = obj_fn.name[5:-4]
            frame_name = int(frame_name)
            output_fn = f'{input_dir}/rend_imgs/{frame_name:04d}.png'
        else:
            output_fn = f'{input_dir}/rend_imgs/{t:04d}.png'
        render_image(output_fn)
    

def adjust_camera(args):
    if args.diverse:
        input_dir = Path(args.path) / args.motion
        setup_motions(input_dir, args, mode="vis_fid", fid=297)
    else:
        input_dir = Path(args.path) / args.motion / args.sample_id
        if args.blender_type == 'adj':
            setup_motion(input_dir, args, mode="put_every_k_together", k=1)
        elif args.blender_type == 'img':
            setup_motion(input_dir, args, mode="huaijin_setting", k=1)
    
    draw_image_video_common(args, input_dir)

    if args.blender_type == 'img':
        out_dir = Path(args.path) / args.motion
        out_fn = str(out_dir / f'm-{args.motion}-{args.sample_id}.png')
        render_image(out_fn)


if __name__ == '__main__':
    parser = get_parser()
    parser.add_argument('--blender-type', type=str, default='adj', choices=['adj', 'img', 'video', 'tpose'])
    parser.add_argument('--diverse', action='store_true', default=False)
    parser.add_argument('--zup', action='store_true', default=False)
    parser.add_argument('--obj-name', type=str, default='object.obj')
    parser.add_argument('--motion', type=str, default='hghoi')
    parser.add_argument('--sample-id', type=str, default='0')
    args = parse_args(parser)

    if args.blender_type == 'video':
        render_video(args)
    elif args.blender_type in ['img', 'adj']:
        adjust_camera(args)
    elif args.blender_type == 'tpose':
        render_tpose(args)
        