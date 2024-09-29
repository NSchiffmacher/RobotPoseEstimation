from lib.Math.Vector import Vector2 as V

from collections import deque

class PathDrawer:
    def __init__(self, max_num_points, color, radius):
        self.points = deque([], max_num_points) # points in global frame
        self.num_points = max_num_points
        self.color = color
        self.radius = radius

    def addPoint(self, point):
        self.points.append(V(point))
        # self.points.append(V(point))
        # if len(self.points) > self.num_points:
        #     self.points.pop(0)

    def draw(self, scene):
        for point in self.points: # (self, point: V, color: tuple, radius=5, width=0):
            scene.draw_point(point, self.color, self.radius)
