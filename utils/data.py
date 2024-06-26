import numpy as np
# from scipy.spatial.transform import Rotation
from glob import glob
import os

# def quaternion2matrix(quaternions):
#     matrices = []
#     for quaternion in quaternions:
#         rotation = Rotation.from_quat(quaternion)
#         matrices.append(rotation.as_matrix())
#     return np.stack(matrices)

# def euler2quaternion(euler_angles):
#     # 将欧拉角分量拆分
#     yaw = euler_angles[:, 0]
#     pitch = euler_angles[:, 1]
#     roll = euler_angles[:, 2]

#     # 计算欧拉角的一半的余弦和正弦值
#     c1 = np.cos(yaw / 2.0)
#     s1 = np.sin(yaw / 2.0)
#     c2 = np.cos(pitch / 2.0)
#     s2 = np.sin(pitch / 2.0)
#     c3 = np.cos(roll / 2.0)
#     s3 = np.sin(roll / 2.0)

#     # 计算四元数的四个分量
#     w = c1 * c2 * c3 + s1 * s2 * s3  
#     x = s1 * c2 * c3 - c1 * s2 * s3  
#     y = c1 * s2 * c3 + s1 * c2 * s3  
#     z = c1 * c2 * s3 - s1 * s2 * c3  

#     # 将四元数的分量堆叠成一个数组并返回
#     return np.column_stack((w, x, y, z))

def read_data(path, id):
    filenames = sorted(glob(os.path.join(path, f'{id:03d}_*.npy')))
    assert len(filenames) > 0, f"Cannot find the file with id: {id}"
    filename = filenames[0]

    data = np.load(filename, allow_pickle=True).item()
    data_dict = {key: value for key, value in data.items()}

    frame_num = len(data_dict['liu_position'])

    params = []
    params.append({'id': 0, 'params': [{'position': data_dict['liu_position'][frame], 'rotation': data_dict['liu_rotation'][frame]} for frame in range(0, frame_num, 4)]})
    params.append({'id': 1, 'params': [{'position': data_dict['ma_position'][frame], 'rotation': data_dict['ma_rotation'][frame]} for frame in range(0, frame_num, 4)]})
    # params_1 = {'id': 0, 'rotation': data_dict['liu_rotation'], 'position': data_dict['liu_position']}
    # params_2 = {'id': 1, 'rotation': data_dict['ma_rotation'], 'position': data_dict['ma_position']}
    frame_num = len(params[0]['params'])

    return params, frame_num

