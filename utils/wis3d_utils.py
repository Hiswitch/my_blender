from wis3d import Wis3D
from pathlib import Path
from datetime import datetime
import torch
import time
import os
import numpy as np

def to_numpy(batch, non_blocking=False, ignore_list: bool = False):
    if isinstance(batch, (tuple, list)) and not ignore_list:
        batch = [to_numpy(b, non_blocking, ignore_list) for b in batch]
    elif isinstance(batch, dict):
        batch = dotdict({k: to_numpy(v, non_blocking, ignore_list) for k, v in batch.items()})
    elif isinstance(batch, torch.Tensor):
        batch = batch.detach().to('cpu', non_blocking=non_blocking).numpy()
    else:  # numpy and others
        batch = np.asarray(batch)
    return batch

log = print

def make_vis3d(cfg, exp_name=None, record_dir='out/vis3d/', time_postfix=False):
    if cfg is not None and exp_name is not None:
        exp_name = f"{cfg.task}@{exp_name}"
    elif exp_name is None:
        exp_name = f"{cfg.task}"
    if time_postfix:
        exp_name = f'{exp_name}_{int(time.time()) % 10000:04d}'
    log_dir = Path(record_dir) / exp_name
    if log_dir.exists():
        log(f'remove contents of directory {log_dir}')
        os.system(f"rm -rf {log_dir}")
    log_dir.mkdir(parents=True)
    log(f"Making directory: {log_dir}")
    vis3d = Wis3D(record_dir, exp_name)
    return vis3d

def vis3d_add_skeleton(vis3d: Wis3D, t: int, joints, parents: list, name: str):
    # joints: (J, 3)
    vis3d.set_scene_id(t)
    joints = to_numpy(joints)
    start_points = joints[1:]
    end_points = [joints[parents[i]] for i in range(1, len(joints))]
    end_points = np.stack(end_points, axis=0)
    vis3d.add_lines(start_points=start_points, end_points=end_points, name=name)

def vis3d_add_coords(vis3d: Wis3D, t: int, axises, origins, name: str):
    vis3d.set_scene_id(t)
    axises = to_numpy(axises)
    origins = to_numpy(origins)
    start_points_list, end_opints_list = [], []
    for axis, origin in zip(axises, origins):
        start_points = np.repeat(origin, 3, axis=0).reshape(3, 3).T
        end_points = start_points + axis.T * 0.1
        start_points_list.append(start_points)
        end_opints_list.append(end_points)
    start_points_list = np.stack(start_points_list)
    end_opints_list = np.stack(end_opints_list)
    vis3d.add_lines(start_points=start_points_list[:, 0], end_points=end_opints_list[:, 0], name=f"{name}_x"),
    vis3d.add_lines(start_points=start_points_list[:, 1], end_points=end_opints_list[:, 1], name=f"{name}_y"),
    vis3d.add_lines(start_points=start_points_list[:, 2], end_points=end_opints_list[:, 2], name=f"{name}_z"),