import numpy as np
import cv2
import torch
import torch.nn.functional as F

# ['root', 'liu_Spine', 'liu_Spine1', 'liu_Neck', 'liu_Head', 'liu_LeftShoulder', 'liu_LeftArm', 'liu_LeftForeArm', 'liu_LeftHand', 'liu_RightShoulder', 'liu_RightArm', 'liu_RightForeArm', 'liu_RightHand', 'liu_LeftUpLeg', 'liu_LeftLeg', 'liu_LeftFoot', 'liu_LeftToeBase', 'liu_RightUpLeg', 'liu_RightLeg', 'liu_RightFoot', 'liu_RightToeBase']

vis_cfg = [
    {
        'color': (0, 0, 0),
        'pairs': [(0, 1), (1, 2), (2, 3), (3, 4)]
    },
    {
        'color': (0, 0, 255),
        'pairs': [(1, 5), (5, 6), (6, 7), (7, 8)]
    },
    {
        'color': (0, 255, 0),
        'pairs': [(1, 9), (9, 10), (10, 11), (11, 12)]
    },
    {
        'color': (255, 0, 0),
        'pairs': [(0, 13), (13, 14), (14, 15), (15, 16)]
    },
    {
        'color': (255, 0, 255),
        'pairs': [(0, 17), (17, 18), (18, 19), (19, 20)]
    }
]

MOTIVE_JOINTS_PARENTS = np.array([
    -1, 0, 1, 2, 3,
    2, 5, 6, 7,
    2, 9, 10, 11,
    0, 13, 14, 15,
    0, 17, 18, 19,
])

def transform_mat(R, t):
    ''' Creates a batch of transformation matrices
        Args:
            - R: Bx3x3 array of a batch of rotation matrices
            - t: Bx3x1 array of a batch of translation vectors
        Returns:
            - T: Bx4x4 Transformation matrix
    '''
    # No padding left or right, only add an extra row
    return torch.cat([F.pad(R, [0, 0, 0, 1]),
                      F.pad(t, [0, 0, 0, 1], value=1)], dim=2)

def batch_rigid_transform(rot_mats, joints, parents, dtype=torch.float32):
    """
    Applies a batch of rigid transformations to the joints

    Parameters
    ----------
    rot_mats : torch.tensor BxNx3x3
        Tensor of rotation matrices
    joints : torch.tensor BxNx3
        Locations of joints
    parents : torch.tensor BxN
        The kinematic tree of each object
    dtype : torch.dtype, optional:
        The data type of the created tensors, the default is torch.float32

    Returns
    -------
    posed_joints : torch.tensor BxNx3
        The locations of the joints after applying the pose rotations
    rel_transforms : torch.tensor BxNx4x4
        The relative (with respect to the root joint) rigid transformations
        for all the joints
    """

    joints = torch.unsqueeze(joints, dim=-1)

    rel_joints = joints.clone()
    rel_joints[:, 1:] -= joints[:, parents[1:]]

    transforms_mat = transform_mat(
        rot_mats.view(-1, 3, 3),
        rel_joints.contiguous().view(-1, 3, 1)).view(-1, joints.shape[1], 4, 4)

    transform_chain = [transforms_mat[:, 0]]
    for i in range(1, parents.shape[0]):
        # Subtract the joint location at the rest pose
        # No need for rotation, since it's identity when at rest
        curr_res = torch.matmul(transform_chain[parents[i]],
                                transforms_mat[:, i])
        transform_chain.append(curr_res)

    transforms = torch.stack(transform_chain, dim=1)

    # The last column of the transformations contains the posed joints
    posed_joints = transforms[:, :, :3, 3]

    # The last column of the transformations contains the posed joints
    posed_joints = transforms[:, :, :3, 3]

    joints_homogen = F.pad(joints, [0, 0, 0, 1])

    rel_transforms = transforms - F.pad(
        torch.matmul(transforms, joints_homogen), [3, 0, 0, 0, 0, 0, 0, 0])

    return posed_joints, rel_transforms

def forward_kinematics(template, rotation):
    rotation = np.vstack([np.eye(3)[None], rotation])
    J = torch.FloatTensor(template)[None]
    rot_mats = torch.FloatTensor(rotation)[None]
    J_transformed, A = batch_rigid_transform(rot_mats, J, MOTIVE_JOINTS_PARENTS, dtype=torch.float32)
    return J_transformed[0]

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str)
    parser.add_argument('--num', type=int, default=1)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    npy_data = quat2rot_data = np.load(args.path, allow_pickle=True).item()

    template = npy_data['ma_position'][0]
    template = np.vstack([np.zeros((1, 3)), template])
    rotation = npy_data['ma_rotation']
    vis_size = 512
    for frame in range(rotation.shape[0]):
        skeleton = forward_kinematics(template, rotation[frame])
        vis = np.zeros((vis_size, vis_size, 3), dtype=np.uint8) + 255
        skeleton2d = skeleton[:, [0,1]]/100 * vis_size/2 + vis_size/2
        skeleton2d = skeleton2d.cpu().numpy()
        for cfg in vis_cfg:
            for pair in cfg['pairs']:
                cv2.line(vis, tuple(skeleton2d[pair[0]].astype(int)), tuple(skeleton2d[pair[1]].astype(int)), cfg['color'], 2)
        cv2.imshow('skeleton', vis)
        cv2.waitKey(10)