import pygame
import pygame.gfxdraw
from pygame.locals import *

from lib.BaseScene import BaseScene
from lib.colors import *

from lib.Math.Vector import Vector2 as V
import math


class EnhancedDrawScene(BaseScene):
    def load(self):
        self.window_size = V(self.app.options.window.width, self.app.options.window.height)
        self.zoom_level = 1
        self.map_offset = V()


    def update(self, dt, events, no_move=False):
        # Zoom in and out
        if not no_move:
            if events['zoom_in'] or events['zoom_out'] or events.mouse_wheel:
                if events['zoom_in']: 
                    self.zoom_level += self.options.zoom_speed * dt
                if events['zoom_out']:
                    self.zoom_level -= self.options.zoom_speed * dt
                if events.mouse_wheel:
                    self.zoom_level += events.mouse_wheel * self.options.zoom_speed_if_scroll * dt

                # Clamp the zoom level
                if self.zoom_level > self.options.zoom_max:
                    self.zoom_level = self.options.zoom_max
                if self.zoom_level < self.options.zoom_min:
                    self.zoom_level = self.options.zoom_min

            # Pan camera
            if events.mouse.left.down:
                mouse_motion = self.events.mouse.rel_pos # Vector in window frame
                self.map_offset += mouse_motion


    def global_frame_to_draw_frame(self, vector: V):
        """
        Takes a vector in the global frame as input, and returns the vector in the drawing frame
        """
        # res.x = vector.x * scale_factor + window_width / 2
        # res.y = -vector.y * scale_factor + window_height / 2

        u = self.options.unit_vector_size_in_px * self.zoom_level
        return V(vector) * V(u, -u) + self.map_offset + self.window_size / 2


    def draw_frame_to_global_frame(self, vector: V):
        """
        Takes a vector in the drawing frame as input, and returns the vector in the global frame
        """

        u = self.options.unit_vector_size_in_px * self.zoom_level
        return (V(vector) - self.map_offset - self.window_size / 2) * V(1/u, -1/u)

    def dist_global_to_draw(self, dist):
        return dist * self.options.unit_vector_size_in_px * self.zoom_level

    def dist_global_to_draw_int(self, dist):
        return int(dist * self.options.unit_vector_size_in_px * self.zoom_level)

    def draw_point(self, point: V, color: tuple, radius=5, width=0):
        """
        Draws a point on the window

        Arguments:
            point: Vector2 -> The point's position in the global frame
            color: tuple -> color in rgb
            radius: int -> Radius in px
            width: int -> Width in px
        """

        # Uses gfxdraw instead of draw to avoid the bug where a point becomes a line if drawn out of the screen
        # https://github.com/pygame/pygame/issues/3778
        pygame.gfxdraw.filled_circle(self.window, *self.global_frame_to_draw_frame(point).to_pygame(), radius, color)


    def draw_circle(self, point: V, color: tuple, radius=5):
        """
        Draws a point on the window

        Arguments:
            point: Vector2 -> The point's position in the global frame
            color: tuple -> color in rgb
            radius: int -> Radius in px
            width: int -> Width in px
        """

        # Uses gfxdraw instead of draw to avoid the bug where a point becomes a line if drawn out of the screen
        # https://github.com/pygame/pygame/issues/3778
        pygame.gfxdraw.circle(self.window, *self.global_frame_to_draw_frame(point).to_pygame(), radius, color)


    def draw_tangent_arc(self, point: V, normal: V, radius: float, color: tuple, draw_angle_deg: float = 140):
        """
        Draws an arc on the window

        Arguments:
            point: Vector2 -> The point's position in the global frame
            color: tuple -> color in rgb
            radius: int -> Radius in px
            width: int -> Width in px
        """

        # Uses gfxdraw instead of draw to avoid the bug where a point becomes a line if drawn out of the screen
        # https://github.com/pygame/pygame/issues/3778

        draw_radius = abs(self.dist_global_to_draw(radius))
        draw_point = self.global_frame_to_draw_frame(point + normal * radius)
        draw_angle = math.radians(draw_angle_deg)

        center_angle = math.atan2(-normal.y, -normal.x)
        if radius < 0:
            center_angle += math.pi
        start_angle = center_angle - draw_angle / 2
        end_angle = center_angle + draw_angle / 2

        pygame.draw.arc(self.window, color, (
            draw_point.x - draw_radius,
            draw_point.y - draw_radius,
            draw_radius * 2,
            draw_radius * 2
        ), start_angle, end_angle)
        

    def draw_ellipse(self, center: V, minor_axis, major_axis, angle, color: tuple):
        u = self.options.unit_vector_size_in_px * self.zoom_level

        surface = pygame.Surface((u * major_axis, u * minor_axis), pygame.SRCALPHA)
        rect = surface.get_rect()
        pygame.draw.ellipse(surface, color, rect, rect.width)
        rotated_surface = pygame.transform.rotate(surface, math.degrees(angle))
        
        rotated_center = rotated_surface.get_rect().center
        center_draw_frame = self.global_frame_to_draw_frame(center)
        blit_pos = (
            center_draw_frame.x - rotated_center[0],
            center_draw_frame.y - rotated_center[1]
        )

        self.window.blit(rotated_surface, blit_pos)


    def draw_rotated_rectangle(self, reference_point: V, theta_rad: float, size: V, offset: V, color: tuple = WHITE, width: int = 3):
        """
            reference_point: Vector2 -> The position of the reference point in the global frame
            theta_rad: float -> The angle between the rectangles frame and the global frame (x axis is theta = 0, in radians)
            size: Vector2 -> The size of the rectangle, in the global frame (not the window's frame)
            offset: Vector2 -> The position of the reference point in the rectangles frame (based on the "bottom-left" corner)
            color: tuple -> color in rgb
            width: int -> The width of the rectangle in px
        """

        # Initial vector in the rectangle's frame, rotated to the global frame, and moved the origin to match the global frame
        a = V(
            - offset.x,
            (size.y - offset.y)
        )
        b = V(
            (size.x - offset.x),
            (size.y - offset.y) 
        )
        c = V(
            (size.x - offset.x),
            - offset.y
        )
        d = V(
            - offset.x,
            - offset.y
        )

        points_in_global_frame = [point.rotate_by_angle(theta_rad) + reference_point for point in [a, b, c, d]]
        points_in_window_frame = [self.global_frame_to_draw_frame(point).to_pygame() for point in points_in_global_frame]
        pygame.draw.lines(self.window, color, True, points_in_window_frame, int(width * self.zoom_level))

    
    def draw_line(self, pointA: V, pointB: V, color: tuple, width: int):
        """
        Draws a line on the window

        Arguments:
            pointA: Vector2 -> One of the endpoints in the global frame
            pointB: Vector2 -> The second endpoint in the global frame
            color: tuple -> color in rgb
            width: int -> width of the line
        """
        pygame.draw.line(self.window, color, self.global_frame_to_draw_frame(pointA).to_pygame(), self.global_frame_to_draw_frame(pointB).to_pygame(), int(width * self.zoom_level))


    def draw_reference_frame(self, position: V, theta_rad: float, scale_factor: float=1, x_axis_color: tuple = RED, y_axis_color: tuple = GREEN):
        """
        Draws a custom reference frame (x is red, y is green)

        Arguments:
            position: Vector2 -> The reference frame's position in the global frame
            theta_rad: float -> The angle between the global x axis and it's x axis (radians)
            scale_factor: float -> shrink the size of the unit vectors 
        """

        rotated_x_axis = V(math.cos(theta_rad), math.sin(theta_rad)) * scale_factor
        rotated_y_axis = V(-math.sin(theta_rad), math.cos(theta_rad)) * scale_factor

        self.draw_line(position, position + rotated_x_axis, x_axis_color, 2)
        self.draw_line(position, position + rotated_y_axis, y_axis_color, 2)
