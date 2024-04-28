import argparse
import os
import torch
from pathlib import Path
import numpy as np
import imageio.v2 as imageio
# from lib.utils.geo_transform import apply_T_on_points


# datapath_dict = {
#     'rich': {
#         'gt': "export/supermotion/vid2gt.pt",
#         'ours': "export/supermotion/vid2gt.pt",
#         'baseline': "export/supermotion/vid2gt.pt",
#     }
# }

def combine_video(args):
    print('combining images as a video')
    input_dir = Path(args.work_dir)
    image_folder = input_dir / 'rend_imgs'
    images = []
    for frame_id in range(args.start_frame, args.end_frame+1):
        images.append(os.path.join(image_folder, f'{frame_id:04d}.png'))

    output_path = Path(args.save_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with imageio.get_writer(output_path, mode="I", fps=30) as writer:
        for image in images:
            img = imageio.imread(image)
            writer.append_data(img)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument('--task', type=str, choices=['load_data', 'combine_video'])
    # parser.add_argument('--dataset', type=str, default='rich', choices=['rich'])
    # parser.add_argument("--vid", type=str)
    # parser.add_argument("--method", type=str, choices=['gt', 'baseline', 'ours'])
    parser.add_argument("--work-dir", type=str)
    parser.add_argument("--save-path", type=str)
    # render video
    parser.add_argument('--start-frame', type=int, default=0)
    parser.add_argument('--end-frame', type=int, default=0)
    args = parser.parse_args()

    # if args.task == 'load_data':
    #     save_path = f"{args.work_dir}/motion.npy"
    #     if os.path.exists(save_path):
    #         print(f'{save_path} already exists, skip')
    #         exit(0)
    #     vid2gt_data = torch.load(datapath_dict[args.dataset][args.method])
    #     sample_joints3d = vid2gt_data[args.vid] # (L, 22, 3)
    #     T_y2z = torch.tensor([
    #         [1, 0, 0, 0],
    #         [0, 0, -1, 0],
    #         [0, 1, 0, 0],
    #         [0, 0, 0, 1],
    #     ]).float()
    #     sample_joints3d = apply_T_on_points(sample_joints3d, T_y2z)
    #     print(f'saving motions to {save_path}, shape: {sample_joints3d.shape}')
    #     os.makedirs(args.work_dir, exist_ok=True)
    #     np.save(save_path, sample_joints3d.numpy())
    # elif args.task == 'combine_video':
    #     combine_video(args)

    combine_video(args)