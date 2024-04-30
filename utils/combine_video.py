import argparse
import os
import torch
from pathlib import Path
import numpy as np
import imageio.v2 as imageio

def combine_video(args):
    print('combining images as a video')
    image_folder = Path(args.work_dir)
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
    parser.add_argument("--work-dir", type=str)
    parser.add_argument("--save-path", type=str)
    # render video
    parser.add_argument('--start-frame', type=int, default=0)
    parser.add_argument('--end-frame', type=int, default=0)
    args = parser.parse_args()

    combine_video(args)