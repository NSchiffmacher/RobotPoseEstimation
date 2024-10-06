import pygame
from pygame.locals import *

# Models
from models.BicycleModel import BicycleModel
from scenes.TrailerTestingScene import TrailerTestingScene

from lib.Math.Vector import Vector2 as V
import math
import numpy as np

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

        self.x = np.array([start_pos.x, start_pos.y, np.radians(start_angle_deg)])
        self.Q = np.diag([0.10 / 3, np.pi / 60]) ** 2
        self.Q_corr = np.diag([0.40 / 3, 0.40 / 3]) ** 2
        self.P = np.zeros((len(self.x), len(self.x)))

        # DEBUG
        self.noisy_P = start_pos

    def update(self, dt, events):
        dt = super().update(dt, events)

        # Update the model
        self.vehicule.receiveInputs(math.radians(self.steering_deg), self.velocity)

        # Compute the model's derivatives
        self.vehicule.computeStateDerivatives(dt)

        # Compute the model's next state
        self.vehicule.computeNextState(dt)

        # Update the KF 
        # Model
        # input: velocity_x and steering_angle
        # state: x, y, theta
        # x_dot = velocity * cos(theta)
        # y_dot = velocity * sin(theta)
        # theta_dot = velocity * tan(steering_angle) / wheelbase

        # donc
        # x_k°1 = x_k + dt * (velocity + n_v) * cos(theta)
        # y_k°1 = y_k + dt * (velocity + n_v) * sin(theta)
        # theta_k°1 = theta_k + dt * velocity * tan(steering_angle + n_a) / wheelbase
        # donc X_k+1 = f(X_k, U_k, 0)
        # avec f((x, y, theta), (velocity, steering), (n_v, n_a)) = [
        #   x + dt * (velocity + n_v) * cos(theta), 
        #   y + dt * (velocity + n_v) * sin(theta), 
        #   theta + dt * velocity * tan(steering_angle + n_a) / wheelbase]
        # )

        # F = derivate of f wrt to X 
        # F = [
        #   [1, 0, -dt * (velocity) * sin(theta)],
        #   [0, 1, dt * (velocity) * cos(theta)],
        #   [0, 0, 1]
        # ]

        # G = derivate of f wrt to N 
        # G = [
        #   [dt * cos(theta), 0],
        #   [dt * sin(theta), 0],
        #   [0, dt * velocity / (wheelbase * cos(steering_angle + n_a) ** 2)]
        # ]

        # Prédiction
        velocity = self.vehicule.getNoisyVelocity()
        steering_angle = self.vehicule.getNoisySteering()
        F = np.array([
            [1, 0, -dt * velocity * math.sin(self.x[2])],
            [0, 1, dt * velocity * math.cos(self.x[2])],
            [0, 0, 1]
        ])

        G = np.array([
            [dt * math.cos(self.x[2]), 0],
            [dt * math.sin(self.x[2]), 0],
            [0, dt * velocity / (self.vehicule.wheelbase * math.cos(steering_angle) ** 2)]
        ])

        self.x = self.x + np.array([
            dt * velocity * math.cos(self.x[2]),
            dt * velocity * math.sin(self.x[2]),
            dt * velocity * math.tan(steering_angle) / self.vehicule.wheelbase
        ])

        self.P = F @ self.P @ F.T + G @ self.Q @ G.T

        # Mesures et corrections
        pos_mesuree = self.vehicule.getNoisyPosition()
        # h(x) = [x, y]
        # H = derivate of h wrt to X 
        H = np.array([
            [1, 0, 0],
            [0, 1, 0]
        ])

        innovation = (pos_mesuree - V(self.x[0], self.x[1])).to_np()
        S = H @ self.P @ H.T + self.Q_corr
        K = self.P @ H.T @ np.linalg.inv(S)

        self.x = self.x + K @ innovation
        self.P = (np.eye(len(self.x)) - K @ H) @ self.P

        # DEBUG
        self.noisy_P = pos_mesuree

        
    def draw(self, fenetre):
        super().draw(fenetre)
        self.vehicule.draw(self, fenetre)

        #self.draw_circle(self.vehicule.position, (255, 0, 0), 20)
        self.draw_reference_frame(V(self.x[0:2]), self.x[2], 1, (255, 0, 0), (255, 0, 0))
        #self.draw_reference_frame(self.noisy_P, self.vehicule.theta_rad, 1, (0, 255, 0), (0, 255, 0))

        # Covariance 
        P = self.P[0:2, 0:2]
        [a, b] = np.sort(np.linalg.eigvals(P)).tolist()
        semi_minor = 2 * a * np.sqrt(5.991)
        semi_major = 2 * b * np.sqrt(5.991)
        self.draw_ellipse(V(self.x[0], self.x[1]), semi_minor, semi_major, self.x[2], (0, 0, 255))
