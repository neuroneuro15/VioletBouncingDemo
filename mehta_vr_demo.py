
__author__ = 'ratcave'

from psychopy import event
import ratcave
from ratcave.graphics import *
from ratcave.utils import rotate_to_var
import numpy as np
import argparse
from ball_simulation import Bouncer

np.set_printoptions(precision=2, suppress=True)

import motive
motive.load_project("vr_demo.ttp")
motive.update()

# Create Arena and cube
reader = WavefrontReader(ratcave.graphics.resources.obj_arena)
arena = reader.get_mesh('Arena', lighting=True, centered=False)
arena_rb = motive.get_rigid_bodies()['Arena']
player = motive.get_rigid_bodies()['CalibWand']
wand = motive.get_rigid_bodies()['CalibWand']

# Calculate Arena's orientation
for attempt in range(3):
        arena_rb.reset_orientation()
        motive.update()
arena_markers = np.array(arena_rb.point_cloud_markers)
additional_rotation = rotate_to_var(arena_markers)

# Create Virtual Objects
reader = WavefrontReader('vr_demo.obj')
meshes = {name:reader.get_mesh(name, lighting=True, centered=False) for name in reader.mesh_names}
meshes['Arena'].visible = False
meshes['StarGrid'].drawstyle = 'point'

meshes['Monkey'].load_texture(resources.img_colorgrid)
meshes['Monkey'].material.spec_weight = 10.
meshes['Monkey'].material.diffuse.rgb = (1.,)*3

meshes['SkyBox'].material.diffuse.rgb = 1., 0., 0.
#meshes['SkyBox'].data.normals *= -1.
meshes['SkyBox'].local.scale = 1.
meshes['SkyBox'].lighting = False
meshes['SkyBox'].load_texture('DEEP_SPACE.png')

#del meshes['StarGrid']

# Try reversing the plank normals  TODO: Find out why the cube normals are reversed!  Doesn't appear to be a Blender thing, and is only happening with the cubes as far as I can see.
for name in meshes:
    if 'Plank' in name:
        meshes[name].load_texture('wood5.png')
        meshes[name].material.diffuse.rgb = (.3,) * 3
        meshes[name].material.spec_weight = 0.
        meshes[name].material.spec_color.rgb = .4, .4, .4,

        meshes[name].data.normals *= -1.


# Make a scene and put projector properties into it.
active_scene = Scene([arena])
active_scene.bgColor.rgb = 0., .3, 0.
active_scene.camera = projector
active_scene.camera.fov_y = 27.8
active_scene.light.position = active_scene.camera.position

# Make a virtual scene -- this is what the player will see!
virtual_scene = Scene(meshes.values())
arena.cubemap = True
virtual_scene.light.position = active_scene.camera.position
virtual_scene.light.rotation = active_scene.camera.rotation  # For correct shadows.  The light is being treated as directional-ish so the shadow camera knows where to point.  Bug, or quirk? Not sure.
virtual_scene.bgColor.rgb = .1, 0., .1
virtual_scene.camera.zFar = 100.

# Make a Window
window = Window(active_scene, screen=1, fullscr=True, virtual_scene=virtual_scene, shadow_rendering=True, shadow_fov_y = 80, autoCam=False)

# Ball Physics
balls = {name: meshes[name] for name in meshes if 'Ball' in name}
for name, ball in balls.items():
    position = ball.local.position.copy()
    prefix = name.split('B')[0]
    floor_height = meshes[prefix+'Plank'].local.position[1]
    ball.local = Bouncer(velocity=(-.1, 0., 1.), acceleration_amt=-4., position=position, floor_height=floor_height)  #(-.1, 0., 1.)
    ball.material.diffuse.rgb = np.random.random(3)
    ball.material.spec_color.rgb = (.7,) * 3
    ball.material.spec_weight = 15.

for prefix in ['High', 'Mid', 'Low']:
    meshes[prefix+'Ball'].local.floor_height = meshes[prefix+'Plank'].local.position[1]

direction = np.array([-.1, 0., 1.])
pos_border = meshes['HighPlank'].local.position + (1. * direction)
neg_border = meshes['HighPlank'].local.position + (1. * -direction)

print("Borders: \n{}\n{}\n{}\n".format(pos_border, neg_border, ball.local.position))

# Main loop
clock = ratcave.utils.timers.countdown_timer(3000)
old_time = 3000.
while not 'escape' in event.getKeys() and clock.next() > 0.:


    # Transform to Optitrack Coordinates
    motive.update()
    for mesh in meshes.values() + [arena]:
        mesh.world.position = arena_rb.location
        mesh.world.rotation = arena_rb.rotation_global
        mesh.world.rotation[1] += additional_rotation

    new_time = clock.next()
    dt = old_time - new_time  # Because it's a countdown timer.
    old_time = new_time
    for ball in balls.values():
        ball.local.update_physics(dt)
        # Keep the balls inside the arena!
        if ball.local.position[2] < neg_border[2] or ball.local.position[2] > pos_border[2]:
            ball.local.velocity[0] *= -1.
            ball.local.velocity[2] *= -1.




    #virtual_scene.light.position[0] = np.sin(2* clock.next()) + active_scene.camera.position[0]
    virtual_scene.camera.position = player.location

    window.draw()
    window.flip()
