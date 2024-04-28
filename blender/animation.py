import bpy
import numpy as np
import json
from mathutils import Vector, Quaternion, Matrix

XBOT_BONES = [
    'mixamorig:Hips', 
    'mixamorig:Spine', 
    'mixamorig:Spine1', 
    'mixamorig:Spine2', 
    'mixamorig:Neck', 
    'mixamorig:Head', 
    'mixamorig:HeadTop_End', 
    'mixamorig:LeftEye', 
    'mixamorig:RightEye', 
    'mixamorig:LeftShoulder', 
    'mixamorig:LeftArm', 
    'mixamorig:LeftForeArm', 
    'mixamorig:LeftHand', 
    'mixamorig:LeftHandThumb1', 
    'mixamorig:LeftHandThumb2', 
    'mixamorig:LeftHandThumb3', 
    'mixamorig:LeftHandThumb4', 
    'mixamorig:LeftHandIndex1', 
    'mixamorig:LeftHandIndex2', 
    'mixamorig:LeftHandIndex3', 
    'mixamorig:LeftHandIndex4', 
    'mixamorig:LeftHandMiddle1', 
    'mixamorig:LeftHandMiddle2', 
    'mixamorig:LeftHandMiddle3', 
    'mixamorig:LeftHandMiddle4', 
    'mixamorig:LeftHandRing1', 
    'mixamorig:LeftHandRing2', 
    'mixamorig:LeftHandRing3', 
    'mixamorig:LeftHandRing4', 
    'mixamorig:LeftHandPinky1', 
    'mixamorig:LeftHandPinky2', 
    'mixamorig:LeftHandPinky3', 
    'mixamorig:LeftHandPinky4', 
    'mixamorig:RightShoulder', 
    'mixamorig:RightArm', 
    'mixamorig:RightForeArm', 
    'mixamorig:RightHand', 
    'mixamorig:RightHandPinky1', 
    'mixamorig:RightHandPinky2', 
    'mixamorig:RightHandPinky3', 
    'mixamorig:RightHandPinky4', 
    'mixamorig:RightHandRing1', 
    'mixamorig:RightHandRing2', 
    'mixamorig:RightHandRing3', 
    'mixamorig:RightHandRing4', 
    'mixamorig:RightHandMiddle1', 'mixamorig:RightHandMiddle2', 'mixamorig:RightHandMiddle3', 'mixamorig:RightHandMiddle4', 'mixamorig:RightHandIndex1', 'mixamorig:RightHandIndex2', 'mixamorig:RightHandIndex3', 'mixamorig:RightHandIndex4', 'mixamorig:RightHandThumb1', 'mixamorig:RightHandThumb2', 'mixamorig:RightHandThumb3', 'mixamorig:RightHandThumb4', 
    'mixamorig:LeftUpLeg', 
    'mixamorig:LeftLeg', 
    'mixamorig:LeftFoot', 
    'mixamorig:LeftToeBase', 
    'mixamorig:LeftToe_End', 
    'mixamorig:RightUpLeg', 
    'mixamorig:RightLeg', 
    'mixamorig:RightFoot', 
    'mixamorig:RightToeBase', 
    'mixamorig:RightToe_End']

MAP_SMPL_XBOT = [
    "mixamorig:Hips",
    # left leg
    "mixamorig:LeftUpLeg",
    "mixamorig:RightUpLeg",
    "mixamorig:Spine",
    # 
    "mixamorig:LeftLeg",
    "mixamorig:RightLeg",
    "mixamorig:Spine1",
    # 
    "mixamorig:LeftFoot",
    "mixamorig:RightFoot",
    "mixamorig:Spine2",
    # 
    "mixamorig:LeftToeBase",
    "mixamorig:RightToeBase",
    "mixamorig:Neck",
    # 13
    "mixamorig:LeftShoulder",
    "mixamorig:RightShoulder",
    "mixamorig:Head",
    # 16
    "mixamorig:LeftArm",
    "mixamorig:RightArm",
    # # right leg
    # # spine
    # # neck
    # 18
    "mixamorig:LeftForeArm",
    "mixamorig:RightForeArm",
    # 20, 21
    "mixamorig:LeftHand",
    "mixamorig:RightHand",
    # "",
    # "",
]

MOTIVE_JOINTS_NAMES = [
    'Hips', # 0
    'Spine', # 1
    'Spine1', # 2
    'Neck', # 3
    'Head', # 4
    'LeftShoulder', # 5
    'LeftArm', # 6
    'LeftForeArm', # 7 
    'LeftHand', # 8
    'RightShoulder', # 9
    'RightArm', # 10
    'RightForeArm', # 11
    'RightHand', # 12
    'LeftUpLeg', # 13
    'LeftLeg', # 14
    'LeftFoot', # 15
    'LeftToeBase', # 16
    'RightUpLeg', # 17
    'RightLeg', # 18
    'RightFoot', # 19
    'RightToeBase', # 20
]

xbot2motive = [0, 13, 17, 1, 14, 18, None, 15, 19, 2, 16, 20, 3, 5, 9, 4, 6, 10, 7, 11, 8, 12]

# def change_left_right_arm(xbot2motive):
#     for i in range(len(xbot2motive)):
#         if xbot2motive[i] in [5, 6, 7,8]:
#             xbot2motive[i] += 4
#         elif xbot2motive[i] in [9, 10, 11, 12]:
#             xbot2motive[i] -= 4

# change_left_right_arm(xbot2motive)

# def read_smpl(filename='/tmp/smpl.json'):
#     with open(filename, 'r') as f:
#         data = json.load(f)
#     return data

def Rodrigues(rotvec):
    theta = np.linalg.norm(rotvec)
    r = (rotvec/theta).reshape(3, 1) if theta > 0. else rotvec
    cost = np.cos(theta)
    mat = np.asarray([[0, -r[2], r[1]],
                      [r[2], 0, -r[0]],
                      [-r[1], r[0], 0]])
    return(cost*np.eye(3) + (1-cost)*r.dot(r.T) + np.sin(theta)*mat)

def change_by_euler(rot, x, y, z):
    Rx = np.array([[1, 0, 0],
                    [0, np.cos(x), -np.sin(x)],
                    [0, np.sin(x), np.cos(x)]])
    Ry = np.array([[np.cos(y), 0, np.sin(y)],
                    [0, 1, 0],
                    [-np.sin(y), 0, np.cos(y)]])
    Rz = np.array([[np.cos(z), -np.sin(z), 0],
                    [np.sin(z), np.cos(z), 0],
                    [0, 0, 1]])
    R = rot
    return np.dot(Rz, np.dot(Ry, np.dot(Rx, R)))

def change_by_mat(rot, mat):
    return np.dot(mat, rot)



def animate_by_smpl(param, bones, frame, retarget=True, offset=[0,0,0], tpose=False):
    if retarget:
        root_name = 'mixamorig:Hips'
        scale = 100.
    #     zoffset = 0
    # else:
    #     root_name = 'm_avg_root'
    #     scale = 1.
    scene = bpy.context.scene
    scene.frame_set(frame)
    # trans = param['Th'][0]
    position = param['position'][0]
    bones[root_name].location = Vector((scale*(position[0]+offset[0]), 
                                        scale*(position[1]+offset[1]), 
                                        scale*(position[2]+offset[2])))
    bones[root_name].keyframe_insert('location', frame=frame)
    bone_rotation = Matrix(param['rotation'][0]).to_quaternion()   
    bones[root_name].rotation_quaternion = bone_rotation
    bones[root_name].keyframe_insert('rotation_quaternion', frame=frame)
    for i in range(1, len(MAP_SMPL_XBOT)):
        bone_name = MAP_SMPL_XBOT[i]
        if xbot2motive[i] != None and not tpose:
            rvec = np.array(Matrix(param['rotation'][xbot2motive[i]]).to_euler())
            if bone_name in ['mixamorig:LeftUpLeg', 'mixamorig:RightUpLeg', 'mixamorig:LeftLeg', 'mixamorig:RightLeg', 'mixamorig:LeftFoot', 'mixamorig:RightFoot', 'mixamorig:LeftToeBase', 'mixamorig:RightToeBase']:
                rvec[1] *= -1
                rvec[2] *= -1
            if bone_name in ['mixamorig:RightShoulder', 'mixamorig:RightArm', 'mixamorig:RightForeArm', 'mixamorig:RightHand']:
                rvec[[0,1]] = rvec[[1,0]]
            if bone_name in ['mixamorig:LeftShoulder', 'mixamorig:LeftArm', 'mixamorig:LeftForeArm', 'mixamorig:LeftHand']:
                rvec[[0,1]] = rvec[[1,0]]
                rvec[2] *= -1

            # position = param['position'][xbot2motive[i]]
            # # bones[bone_name].location = Vector((position[0], position[1], position[2]))
            # bones[root_name].location = Vector((scale*(position[0]+offset[0]), 
            #                         scale*(position[1]+offset[1]), 
            #                         scale*(position[2]+offset[2])))
            # bones[bone_name].keyframe_insert('location', frame=frame)
        else:
            rvec = np.array([0, 0, 0])
            # if bone_name in ['mixamorig:LeftShoulder']:
            #     rvec = np.array([0, 0, np.pi/2])

        bone_rotation = Rodrigues(rvec)
        if bone_name in ['mixamorig:LeftShoulder']:
            mat = np.array([[1, 0, 0],
                            [0, 1, 0],
                            [0, 0, 1]])
            bone_rotation = change_by_mat(bone_rotation, mat)
       
        bone_rotation = Matrix(bone_rotation).to_quaternion()
        bones[bone_name].rotation_quaternion = bone_rotation
        bones[bone_name].keyframe_insert('rotation_quaternion', frame=frame)