import pygame
from pygame.locals import *

from lib.Math.Vector import Vector2 as V

from scenes.EnhancedDrawScene import EnhancedDrawScene
import math

class TrailerTestingScene(EnhancedDrawScene):
    def load(self):
        super().load()
        self.pause_simulation = False

        self.steering_deg = 0
        self.velocity = 0

        self.draw_virtual_wheels = getattr(self.options, "draw_virtual_wheels", True)
        self.debug_draw_reference_frame = getattr(self.options, "debug_draw_reference_frame", True)
        self.steering_zeroing_speed = getattr(self.options, "steering_zeroing_speed", 0)

    def update(self, dt, events, no_move=False):
        super().update(dt, events, no_move)
        if self.pause_simulation:
            dt = 0
            
        self.handleInputs(dt, events)
        return dt


    def draw(self, fenetre):
        self.draw_reference_frame(V(0,0), 0)


    def handleInputs(self, dt, events):
        # Pause user inputs
        if events.on_first_pause:
            self.pause_simulation = not self.pause_simulation

        if self.pause_simulation: 
            return # Don't handle inputs of the simulation is paused
        
        # Steering user inputs
        if events.steer_left:
            self.steering_deg += self.options.steering_speed * dt
            if self.steering_deg > self.options.max_steering_deg:
                self.steering_deg = self.options.max_steering_deg
        if events.steer_right:
            self.steering_deg -= self.options.steering_speed * dt
            if self.steering_deg < -self.options.max_steering_deg:
                self.steering_deg = -self.options.max_steering_deg

        if not (events.steer_left or events.steer_right):
            self.steering_deg -= math.copysign(self.steering_zeroing_speed * dt, self.steering_deg)

        if events.breaking:
            if abs(self.velocity) > 0.05:
                deceleration = math.copysign(self.options.deceleration * dt, self.velocity)
                self.velocity -= deceleration
            else:
                self.velocity = 0
        
        # Velocity user inputs
        if events.increase_velocity:
            self.velocity += self.options.acceleration * dt
            if self.velocity > self.options.max_velocity:
                self.velocity = self.options.max_velocity
        if events.decrease_velocity:
            self.velocity -= self.options.deceleration * dt
            if self.velocity < self.options.min_velocity:
                self.velocity = self.options.min_velocity
        if events.estop:
            self.velocity = 0


    def physics_update(self, dt):
        pass
