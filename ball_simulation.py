__author__ = 'ratcave'

import numpy as np
from ratcave.graphics.core.mixins import Physical

class Bouncer(Physical):

    def __init__(self, velocity=(0., 0., 0.), floor_height=0., acceleration_amt=-2.2, *args, **kwargs):
        super(Bouncer, self).__init__(*args, **kwargs)
        assert self.position[1] >= floor_height, "object must start at floor level or above!"
        self.floor_height = float(floor_height)
        self.velocity = np.array(velocity, dtype=float)
        self.acceleration = np.array([0., acceleration_amt, 0.], dtype=float)

    def update_physics(self, dt):

        # Move by acceleration
        self.velocity += (self.acceleration * dt)
        self.position += (self.velocity * dt)

        # If you hit the floor, Bounce!
        if self.position[1] < self.floor_height and self.velocity[1] < 0.:
            self.velocity[1] = 1.5
            # self.velocity[1] *= -1




