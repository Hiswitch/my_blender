'''
  @ Date: 2022-04-24 15:21:36
  @ Author: Qing Shuai
  @ Mail: s_q@zju.edu.cn
  @ LastEditors: Qing Shuai
  @ LastEditTime: 2022-09-05 19:51:27
  @ FilePath: /EasyMocapPublic/easymocap/blender/setup.py
'''
import bpy
import numpy as np
import sys
import json
from .geometry import set_camera

def get_parser():
    # Args
    import argparse
    parser = argparse.ArgumentParser(
        usage='''
    render: `blender --background -noaudio --python ./scripts/blender/render_camera.py -- ${data} --nf 90`
''',
        description='render example')
    parser.add_argument('path', type=str,
        help='Input file or directory')
    parser.add_argument('--out', type=str, default=None,
        help='Output file or directory')
    parser.add_argument('--out-img', action='store_true')
    parser.add_argument('--res_x', type=int, default=1024)
    parser.add_argument('--res_y', type=int, default=1024)
    parser.add_argument('--format', type=str, default='PNG', choices=['JPEG', 'PNG'])
    parser.add_argument('--num_samples', type=int, default=128,
        help='Output file or directory')
    parser.add_argument('--denoising', action='store_true')
    parser.add_argument('--use-transparent-bg', action='store_true')
    parser.add_argument('--nocycle', action='store_true')

    return parser


def get_parser_scene():
    parser = get_parser()
    # Args
    
    parser.add_argument('--scene-id', type=str, default=None,)
    parser.add_argument('--draw-env-sensor', action='store_true')
    parser.add_argument('--draw-tgt-sensor', action='store_true')
    parser.add_argument('--draw-traj-sensor', action='store_true')
    parser.add_argument('--draw-tgt-bbx', action='store_true')
    parser.add_argument('--draw-tgt-rel', action='store_true')
    parser.add_argument('--draw-all-bbx', action='store_true')
    parser.add_argument('--draw-all-rel', action='store_true')
    parser.add_argument('--draw-wrong-bbx', action='store_true')
    parser.add_argument('--nk', type=int)
    return parser


def parse_args(parser):
    if '--' in sys.argv:
        args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    else:
        args = parser.parse_args(['debug'])
    return args

def clean_objects(name='Cube', version = '2.83') -> None:
    if name not in bpy.data.objects.keys():
        return 0
    bpy.ops.object.select_all(action='DESELECT')
    if version == '2.83':
        bpy.data.objects[name].select_set(True)
    else:
        bpy.data.objects[name].select = True
    bpy.ops.object.delete(use_global=False)

def add_sunlight(name='Light', location=(10., 0., 5.), rotation=(0., -np.pi/4, 3.14), strength=4., rgb=(1,1,1,1)):
    bpy.ops.object.light_add(type='SUN', location=location, rotation=rotation)

    if name is not None:
        bpy.context.object.name = name

    sun_object = bpy.context.object
    sun_object.data.use_nodes = True
    sun_object.data.node_tree.nodes["Emission"].inputs["Strength"].default_value = strength
    sun_object.data.node_tree.nodes["Emission"].inputs["Color"].default_value = rgb

def setLight_sun(rotation_euler, strength, shadow_soft_size = 0.05, location=(0,0,0)):
	x = rotation_euler[0] * 1.0 / 180.0 * np.pi 
	y = rotation_euler[1] * 1.0 / 180.0 * np.pi 
	z = rotation_euler[2] * 1.0 / 180.0 * np.pi 
	angle = (x,y,z)
	bpy.ops.object.light_add(type = 'SUN', location=location, rotation = angle)
	lamp = bpy.data.lights['Sun']
	lamp.use_nodes = True
	# lamp.shadow_soft_size = shadow_soft_size # this is for older blender 2.8
	lamp.angle = shadow_soft_size

	lamp.node_tree.nodes["Emission"].inputs['Strength'].default_value = strength
	return lamp

def setLight_ambient(color = (0,0,0,1)):
	bpy.data.scenes[0].world.use_nodes = True
	bpy.data.scenes[0].world.node_tree.nodes["Background"].inputs['Color'].default_value = color
 

def setup(rgb=(1,1,1,1)):
    np.random.seed(666)
    scene = bpy.context.scene
    build_rgb_background(scene.world, rgb=rgb, strength=1.)
    clean_objects('Cube')
    clean_objects('Light')


def build_rgb_background(world,
                         rgb = (0.9, 0.9, 0.9, 1.0),
                         strength = 1.0) -> None:
    world.use_nodes = True
    node_tree = world.node_tree

    rgb_node = node_tree.nodes.new(type="ShaderNodeRGB")
    rgb_node.outputs["Color"].default_value = rgb
    node_tree.nodes["Background"].inputs["Strength"].default_value = strength
    node_tree.links.new(rgb_node.outputs["Color"], node_tree.nodes["Background"].inputs["Color"])

def set_cycles_renderer(scene: bpy.types.Scene,
                        camera_object: bpy.types.Object,
                        num_samples: int,
                        use_denoising: bool = True,
                        use_motion_blur: bool = False,
                        use_transparent_bg: bool = True,
                        prefer_cuda_use: bool = True,
                        use_adaptive_sampling: bool = False) -> None:
    scene.camera = camera_object

    scene.render.engine = 'CYCLES'
    scene.render.use_motion_blur = use_motion_blur

    scene.render.film_transparent = use_transparent_bg
    scene.view_layers[0].cycles.use_denoising = use_denoising

    scene.cycles.use_adaptive_sampling = use_adaptive_sampling
    scene.cycles.samples = num_samples

    # Enable GPU acceleration
    # Source - https://blender.stackexchange.com/a/196702
    if prefer_cuda_use:
        bpy.context.scene.cycles.device = "GPU"

        # Change the preference setting
        try:
            bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"
        except:
            print("No CUDA device found, using CPU instead.")

    # Call get_devices() to let Blender detects GPU device (if any)
    bpy.context.preferences.addons["cycles"].preferences.get_devices()

    # Let Blender use all available devices, include GPU and CPU
    for d in bpy.context.preferences.addons["cycles"].preferences.devices:
        d["use"] = 1

    # Display the devices to be used for rendering
    print("----")
    print("The following devices will be used for path tracing:")
    for d in bpy.context.preferences.addons["cycles"].preferences.devices:
        print("- {}".format(d["name"]))
    print("----")

def set_output_properties(scene,
                          resolution_percentage: int = 100,
                          output_file_path: str = "",
                          res_x: int = 1920,
                          res_y: int = 1080,
                          tile_x: int = 1920,
                          tile_y: int = 1080,
                          format='PNG') -> None:
    scene.render.resolution_percentage = resolution_percentage
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    if hasattr(scene.render, 'tile_x'):
        scene.render.tile_x = tile_x
        scene.render.tile_y = tile_y
    # scene.render.use_antialiasing = True
    # scene.render.antialiasing_samples = '5'
    if output_file_path is not None:
        scene.render.filepath = output_file_path
    if format == 'PNG':
        scene.render.image_settings.file_format = "PNG"
        # scene.render.alpha_mode = "TRANSPARENT"
        scene.render.image_settings.color_mode = "RGBA"
    elif format == 'JPEG':
        scene.render.image_settings.file_format = "JPEG"
        scene.render.image_settings.color_mode = "RGB"


def setup_output_option(args):
    n_parallel = 1
    set_output_properties(bpy.context.scene, output_file_path=args.out, 
        res_x=args.res_x, res_y=args.res_y, 
        tile_x=args.res_x//n_parallel, tile_y=args.res_y, resolution_percentage=100,
        format=args.format)
    bpy.context.scene.frame_end = 1


def setup_camera_light(input_dir, scene_obj=None, cam_fn=None):
    if scene_obj is not None:
        verts = [v.co for v in scene_obj.data.vertices]
        location = np.mean(verts, axis=0)
    else:
        location = [0,0,0]
    
    # camera
    if cam_fn == None:
        cam_fn = input_dir / 'info' / 'cam.json'
    if cam_fn.exists():
        f = json.load(cam_fn.open('r'))
        cam_xyz = f['cam_xyz']
        cam_euler = f['cam_euler']
        cam_f = f['cam_f']
        set_camera(location=cam_xyz, rotation=cam_euler, focal=cam_f) 
    else: # default camera
        location[2] = 2.
        set_camera(location=location, center=(0, 0, 1), focal=40)
        # create cam.json
        cam_info = {
            "cam_xyz": [0,0,0],
            "cam_euler": [0,0,0],
            "cam_f": 40,
        }
        json.dump(cam_info, cam_fn.open('w'))

    # light
    location[2] = 5.
    lightAngle = [0, 0, 0]
    setLight_sun(lightAngle, strength=2, shadow_soft_size=0.5, location=location)
    setLight_ambient(color=(0.1,0.1,0.1,1))


def render_image(output_path):
    scene = bpy.context.scene
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True, animation=False)