import pygame
from pygame.locals import *

import time

from lib.Options import Options
from lib.Events import Events

RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
WHITE = (255,255,255)
BLACK = (0,0,0)

class BaseScene:
    def __init__(self, app, options):
        self.app            = app
        self.window         = app.window
        self.options        = options
        self.loaded         = False
        self.continuer      = True

        self.last_frame_dt = 0
        self.instant_fps = float('inf')

        self.events         = Events(self,  options.keys)
        self.return_value   = None

    def _load(self):
        self.load()

    def run(self):
        if not self.loaded:
            self.load()

        self.continuer      = True
        frame_length        = 1/self.options.fps_target
        physicsframe_length = frame_length / self.options.physics_frame

        last_physics_dt     = 0
        last_frame_dt       = 0

        while self.continuer:
            try:
                frame_dt = 0
                for i in range(self.options.physics_frame):
                    start_physics_frame = time.time()
                    self._physics_update(last_physics_dt)
                    # Update last variables
                    
                    if i == self.options.physics_frame - 1:
                        self._update(last_frame_dt)
                        self._draw()

                        if pygame.event.peek(QUIT, False):
                            self.continuer = False
                        # pygame.event.pump()

                    
                    now = time.time()
                    if now - start_physics_frame <= physicsframe_length:
                        time.sleep(physicsframe_length + start_physics_frame - now)
                    
                    re_now = time.time()
                    last_physics_dt = re_now - start_physics_frame
                    frame_dt += last_physics_dt
                
                last_frame_dt = frame_dt
                self.last_frame_dt = last_frame_dt
                if self.last_frame_dt > 0:
                    self.instant_fps = 1/self.last_frame_dt
                else:
                    self.instant_fps = float('inf')
            except Exception as e:
                self.continuer = False
                raise e

        return self.return_value

    def swap_scene(self, scene):
        """
        Used to quit the current scene and go to "scene"
        """
        self.continuer = False
        self.return_value = scene
            
            

    def _update(self, dt):
        # Handle events
        self.events.check()
        if self.events.quitter or self.events.close_button_pressed:
            self.continuer = False

        self.update(dt, self.events)

    def _physics_update(self, dt):
        self.physics_update(dt)

    def _draw(self):
        # self.window
        self.window.fill(self.options.background_color)
        self.draw(self.window)
        
        pygame.display.update()

