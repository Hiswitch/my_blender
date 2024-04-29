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
from blender.animation import animate_by_smpl
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


def animate_by_fbx(bones, fbxdata, frame, name):
    # ['liu_Spine', 'liu_Spine1', 'liu_Neck', 'liu_Head', 'liu_LeftShoulder', 'liu_LeftArm', 'liu_LeftForeArm', 'liu_LeftHand', 'liu_RightShoulder', 'liu_RightArm', 'liu_RightForeArm', 'liu_RightHand', 'liu_LeftUpLeg', 'liu_LeftLeg', 'liu_LeftFoot', 'liu_LeftToeBase', 'liu_RightUpLeg', 'liu_RightLeg', 'liu_RightFoot', 'liu_RightToeBase']
    scene = bpy.context.scene
    scene.frame_set(frame)
    for srcname, dstname in [
        ('LeftShoulder', 'LeftShoulder'),
        ('LeftArm', 'LeftArm'),
        ('RightShoulder', 'RightShoulder'),
        ('RightArm', 'RightArm'),
        ('LeftForeArm', 'LeftForeArm'),
        ('RightForeArm', 'RightForeArm'),
        ('LeftHand', 'LeftHand'),
        ('RightHand', 'RightHand'),
        # leg
        ('LeftUpLeg', 'LeftUpLeg'),
        ('RightUpLeg', 'RightUpLeg'),
        ('LeftLeg', 'LeftLeg'),
        ('RightLeg', 'RightLeg'),
        ('LeftFoot', 'LeftFoot'),
        ('RightFoot', 'RightFoot'),
        ('LeftToeBase', 'LeftToeBase'),
        ('RightToeBase', 'RightToeBase'),
    ]:
        srcname = name + '_' + srcname
        dstname = 'mixamorig:' + dstname
        if False:
            bone_rotation = fbxdata[srcname].matrix_channel.to_3x3()
            bones[dstname].rotation_quaternion = Matrix(bone_rotation).to_quaternion()
        else:
            bone_rotation = fbxdata[srcname].rotation_quaternion
            # bone_rotation = Vector((1, 0, 0, 0))
            bones[dstname].rotation_quaternion = bone_rotation
        print(srcname, dstname, bone_rotation)
        bones[dstname].keyframe_insert('rotation_quaternion', frame=frame)

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
    

if __name__ == "__main__":
    parser = get_parser()
    # parser.add_argument("--source", type=str)
    # parser.add_argument("--zoffset", type=float, help="offset for z axis")
    # parser.add_argument('--retarget', action='store_true')
    # args = parse_args(parser)
    parser.add_argument('--id', type=int, default=0)
    parser.add_argument('--end_frame', type=int, default=100000)
    parser.add_argument('--blender_type', type=str, default='adj', choices=['adj', 'img', 'video', 'tpose', 'debug'])
    # parser.add_argument("--path", type=str, default="D:\\blender_project\\begin\\fbx_export_joints_fixrot")
    args = parse_args(parser)

    if args.blender_type == 'debug':
        path = './data/'
        filenames = glob(os.path.join(path, f'{args.id:03d}_*.fbx'))
        assert len(filenames) > 0, f"Cannot find the file with id: {args.id}"
        filename = filenames[0]
        bpy.ops.import_scene.fbx(filepath=filename, automatic_bone_orientation=True, force_connect_children=True)

    frame_num = min(int(bpy.data.actions[0].frame_range[1]), args.end_frame)
    bpy.context.scene.frame_end = frame_num
    # camera = set_camera(location=(3, 0, 2.5), center=(0, 0, 1), focal=30)
    # set_camera_green(camera)

    fbx_data = {
        0: 'liu',
        1: 'ma'
    }
    scene = bpy.context.scene
    results = {}
    if True:
        # 确保骨架在T-Pose
        for pid, name in fbx_data.items():
            armature = bpy.data.objects[name+'_Hips']
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')

            # 打印每个骨骼的位置
            armature.location = Vector((0, 0, 0))
            armature.rotation_euler = Vector((0, 0, 0))
            # 重置每个骨骼到T-Pose
            for bone in armature.pose.bones:
                # bone.location = bone.bone.head_local.copy()
                bone.rotation_quaternion = [1, 0, 0, 0]
            bpy.context.view_layer.update()
            bone_names, positions = [], []
            for bone in armature.pose.bones:
                bone_names.append(bone.name)
                positions.append([bone.head[0], bone.head[1], bone.head[2]])
            positions = np.array(positions)
            bpy.ops.object.mode_set(mode='OBJECT')
            if False:
                for i in range(positions.shape[0]):
                    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.01, 
                                enter_editmode=False, 
                                align='WORLD', 
                                location=0.01*positions[i], scale=(1, 1, 1))
                    print(f'{bone_names[i]:20s}: {positions[i][0]:4.0f} {positions[i][1]:4.0f} {positions[i][2]:4.0f}')
            results[pid] = {'Tpose': positions, 'rotations': []}
    if True:
        for frame in range(frame_num):
            scene.frame_set(frame)
            for pid, name in fbx_data.items():
                rotations = []
                for bone in bpy.data.objects[name+'_Hips'].pose.bones:
                    rot = bone.rotation_quaternion
                    # convert to rotmat
                    rot = rot.to_matrix()
                    # 
                    if bone.parent:
                        rot = bone.parent.matrix_channel.to_3x3().inverted() @ bone.matrix_channel.to_3x3()
                    else:
                        rot = bone.matrix_channel.to_3x3()
                    rotations.append(rot)
                results[pid]['rotations'].append(rotations)
        npy_results = {}
        npy_results['ma_position'] = np.array(results[1]['Tpose'])[None].repeat(frame_num, axis=0)
        npy_results['ma_rotation'] = np.array(results[1]['rotations'])
        np.save('ma.npy', npy_results)