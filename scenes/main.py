import pygame
from pygame.locals import *

# Models
from models.BicycleModel import BicycleModel
from scenes.TrailerTestingScene import TrailerTestingScene

from lib.Math.Vector import Vector2 as V
import math
import copy

class Scene(TrailerTestingScene):
    def load(self):
        super().load()

        # Definition of the vehicule
        start_pos = V(2,1)
        start_angle_deg = 0

        tracteasy_width = 1.8288 # m 
        tracteasy_length = 3.2004 # m
        tracteasy_wheelbase = 2.5 # m 
        tracteasy_hook_offset_abs = 0.4 # m
        self.vehicule = BicycleModel(V(tracteasy_length, tracteasy_width), V(tracteasy_hook_offset_abs, tracteasy_width/2), tracteasy_wheelbase, start_pos, math.radians(start_angle_deg))

    def update(self, dt, events):
        dt = super().update(dt, events)

        # Update the model
        self.vehicule.receiveInputs(math.radians(self.steering_deg), self.velocity)

        # Compute the model's derivatives
        self.vehicule.computeStateDerivatives(dt)

        # Compute the model's next state
        self.vehicule.computeNextState(dt)
        
    def draw(self, fenetre):
        super().draw(fenetre)
        self.vehicule.draw(self, fenetre)
