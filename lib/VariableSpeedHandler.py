class VariableSpeedHandler():
    def __init__(self, initial_speed, debug=False, print_current_speed=False):
        self.patterns = []
        self.current_pattern_index = 0
        self.current_pattern_time = 0
        self.pattern_start_speed = initial_speed
        self.done = True
        self.debug = debug
        self.print_current_speed = print_current_speed


    def addStep(self, speed, duration):
        if self.debug:
            print(f"Added a step holding a speed of {speed} m/s for {duration} s")
        self.patterns.append({
            "type": "step",
            "speed": speed,
            "duration": duration
        })
        self.done = False

    def addCallback(self, callback):
        self.patterns.append({
            "type": "callback",
            "callback": callback,
            "duration": 0
        })

    def holdSpeed(self, duration):
        if len(self.patterns) == 0:
            speed = self.pattern_start_speed
        else:
            speed = self.patterns[-1]["speed"]
        
        self.addStep(speed, duration)

    def addSlope(self, target_speed, duration):
        if self.debug:
            print(f"Added a slope reaching a speed of {target_speed} m/s in {duration} s")
        self.patterns.append({
            "type": "slope",
            "speed": target_speed, # the speed of a "slope" pattern corresponds to the end speed
            "duration": duration,
        })
        self.done = False


    def update(self, dt):
        if self.done: 
            return self.current_speed
        
        self.current_pattern_time += dt
        if self.patterns[self.current_pattern_index]["type"] == "callback":
            self.current_pattern_index += 1
            self.done = self.current_pattern_index >= len(self.patterns)

        elif self.current_pattern_time > self.patterns[self.current_pattern_index]["duration"]:
            self.current_pattern_time -= self.patterns[self.current_pattern_index]["duration"]
            self.pattern_start_speed = self.patterns[self.current_pattern_index]["speed"]
            self.current_pattern_index += 1
            self.done = self.current_pattern_index >= len(self.patterns)

        return self._computeCurrentSpeed()


    def _computeCurrentSpeed(self):
        if self.done:
            self.current_speed = self.pattern_start_speed
            return self.current_speed
        
        current_pattern = self.patterns[self.current_pattern_index]
        if current_pattern["type"] == "step":
            self.current_speed = current_pattern["speed"]
        elif current_pattern["type"] == "callback":
            # self.current_speed = 
            current_pattern["callback"]()
        elif current_pattern["type"] == "slope":
            alpha = self.current_pattern_time / current_pattern["duration"]
            self.current_speed = self.pattern_start_speed + alpha * (current_pattern["speed"] - self.pattern_start_speed)
        else:
            raise NotImplementedError(f"Pattern type \"{current_pattern['type']}\" hasn't been implemented yet.")
        
        if self.print_current_speed:
            print(f"Current speed is {self.current_speed} m/s")
        return self.current_speed
        

    def getSpeed(self):
        return self.current_speed
