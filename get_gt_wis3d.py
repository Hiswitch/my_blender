from utils.wis3d_utils import make_vis3d, vis3d_add_skeleton
from utils.data import read_data
parents = [
    0, 0, 1, 2, 3,
             2, 5, 6, 7,
             2, 9, 10, 11,
       0, 13, 14, 15,
       0, 17, 18, 19,
]

path = "D:/blender_project/begin/fbx_export_joints_fixrot"
id = 1
params = read_data(path, id)

frame_num = 250
vis3d = make_vis3d(None, 'debug-rotation', 'data/vis3d')
for param in params:
    pid = param['id']
    pose_pos = param['position']
    for t in range(frame_num):
        vis3d_add_skeleton(vis3d, t, pose_pos[t], parents, str(pid))


