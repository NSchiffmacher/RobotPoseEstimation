from lib.Math.Vector import Vector2 as V
from lib.colors import *

from utils.PathDrawer import PathDrawer

import numpy as np
import math

class BaseModel:
    draw_frame_color = BLACK
    draw_frame_width = 3

    draw_bounding_box_color = WHITE
    draw_bounding_box_width = 5

    draw_wheel_size = V(0.3, 0.15)

    draw_back_wheel_color = DARK_BLUE
    draw_back_wheel_width = 3
    draw_back_wheel_size = V(draw_wheel_size)

    draw_front_wheel_color = DARK_BLUE
    draw_front_wheel_width = 3
    draw_front_wheel_size = V(draw_wheel_size)

    draw_virtual_wheel_color = PURPLE
    draw_virtual_wheel_width = 3
    draw_virtual_wheel_size = V(draw_wheel_size)

    draw_reference_frame_size = 0.5

    draw_hitch_joint_color = RED
    draw_hitch_joint_radius = 5
    draw_hitch_joint_width = 0

    draw_hook_color = BLACK
    draw_hook_radius = 3
    draw_hook_width = 0

    path_drawer = None

    def __init__(self) -> None:
        pass

    def usePathDrawer(self, max_num_points=500, color=(*DARK_BLUE, 40), radius=2):
        self.path_drawer = PathDrawer(max_num_points, color, radius)

    def computeNextState(self, dt):
        if self.path_drawer and self.kinematic_center_velocity != 0:
            self.path_drawer.addPoint(self.position)

    def draw(self, scene, fenetre):
        if self.path_drawer:
            self.path_drawer.draw(scene)

    def create_covariance_ellipse(self, covariance_matrix, confidence_prc=0.99):
        eigen_val, eigen_vec = np.linalg.eig(covariance_matrix)

        confidence_map = {
            0.9  : 4.61,
            0.95 : 5.99,
            0.99 : 9.21,
            0.999: 13.82
        }
        if confidence_prc not in confidence_map:
            raise Exception(f"confidence_prc should be one of {list(confidence_map.keys())}")

        # Sort the eigen values (ascending)
        idx = eigen_val.argsort()
        eigen_val = eigen_val[idx]
        eigen_vec = eigen_vec[:,idx]

        confidence_coeff = confidence_map[confidence_prc]
        minor_axis = 2 * np.sqrt(confidence_coeff * eigen_val[0]) # 95% confidence
        major_axis = 2 * np.sqrt(confidence_coeff * eigen_val[1])
        alpha = math.atan2(eigen_vec[1, 1], eigen_vec[0, 1])

        return minor_axis, major_axis, alpha

    