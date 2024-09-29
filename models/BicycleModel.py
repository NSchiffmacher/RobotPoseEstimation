from lib.Math.Vector import Vector2 as V

from lib.colors import *

from models.BaseModel import BaseModel

import math
import numpy as np

class BicycleModel(BaseModel):
    def __init__(self, bounding_box_size: V, kinematic_center_offset: V, wheelbase: float, base_position: V, base_theta_rad: float) -> None:
        """Basic bicycle model

        Args:
            bounding_box_size (V): The size of the bounding box of the vehicle
            kinematic_center_offset (V): The offset of the kinematic center from the bottom left corner of the vehicle
            wheelbase (float): The distance between the front and back wheels
            base_position (V): The initial position of the vehicle
            base_theta_rad (float): The initial angle of the vehicle
        """
        super().__init__()
        
        # The models parameters
        self.bounding_box_size = bounding_box_size
        self.kinematic_center_offset = kinematic_center_offset
        self.wheelbase = wheelbase

        # The models state initial conditions
        self.theta_rad = base_theta_rad
        self.position = base_position

        # The models state derivates
        self.theta_dot = 0
        self.x_dot = 0
        self.y_dot = 0

        # The inputs the model receives (set at arbitrary values for now)
        self.steering_rad = 0
        self.velocity = 0

        # Kinematic center velocity 
        self.kinematic_center_velocity = 0
        self.hook_velocity_global = V()
        self.computeNextState(0)


    def receiveInputs(self, steering_angle_rad, velocity):
        self.steering_rad = steering_angle_rad
        self.velocity = velocity


    def computeStateDerivatives(self, dt):
        # Compute derivates 
        self.x_dot = self.velocity * math.cos(self.theta_rad)
        self.y_dot = self.velocity * math.sin(self.theta_rad)
        self.theta_dot = self.velocity * math.tan(self.steering_rad) / self.wheelbase


    def computeNextState(self, dt):        
        # Apply euler forward discretization with step size dt
        self.position.x += dt * self.x_dot
        self.position.y += dt * self.y_dot
        self.theta_rad  = (self.theta_rad + dt *  self.theta_dot) % (2 * math.pi)


    def vehicleFrameToGlobalFrame(self, point: V) -> V:
        """Moves a point from the vehicle frame to the global frame

        Args:
            point (V): The point in the vehicle frame

        Returns:
            V: The point in the global frame
        """
        return self.position + point.rotate_by_angle(self.theta_rad)


    def draw(self, scene, fenetre):
        # Draw the bounding box
        scene.draw_rotated_rectangle(
            self.position, 
            self.theta_rad, 
            self.bounding_box_size, 
            self.kinematic_center_offset,
            self.draw_bounding_box_color,
            self.draw_bounding_box_width
        )

        # Draw back "center wheel"
        scene.draw_rotated_rectangle(
            self.position,
            self.theta_rad,
            self.draw_back_wheel_size,
            self.draw_back_wheel_size/2,
            self.draw_back_wheel_color,
            self.draw_back_wheel_width
        )

        # Draw front "center wheel"
        scene.draw_rotated_rectangle(
            self.vehicleFrameToGlobalFrame(V(self.wheelbase, 0)),
            self.theta_rad + self.steering_rad,
            self.draw_front_wheel_size,
            self.draw_front_wheel_size/2,
            self.draw_front_wheel_color,
            self.draw_front_wheel_width
        )

        #Draw the vehicle's reference frame
        scene.draw_reference_frame(
            self.position,
            self.theta_rad,
            self.draw_reference_frame_size
        )