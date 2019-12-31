import pigpio 
import time
import numpy as np
from threading import Thread, Lock


class Servo:
    def __init__(self, pin, mx, mn, direction, deg, speed=510, precision=2):
        self.pin = pin
        self.max = mx
        self.min = mn
        self.dir = direction
        self.deg = deg
        self.speed = speed
        self.tmp_speed = speed
        self.precision = precision
        
        self.pi = pigpio.pi()
        self.pos = deg / 2
        self.go_deg(deg / 2)
        
    def get_pos(self):
        w = 0
        if self.last_pos_travel_time > 0:
            w = (time.time() - self.last_pos_timestamp) / self.last_pos_travel_time
        w = 0 if w < 0 else w if w < 1 else 1
        return self.pos * w + self.last_pos * (1 - w)
        
    def step_time(self, x):
        return abs(x - self.pos) / self.speed

    def go_center(self):
        return self.go_deg(self.deg / 2)
                
    def go_deg(self, x):
        if (x < 0):
            return self.go_deg(0)
        elif (x > self.deg):
            return self.go_deg(self.deg)
        else:
            per_deg = (self.max - self.min) / self.deg
            distance = abs(x - self.pos)
            self.last_pos = self.pos
            self.pos = x
            self.last_pos_travel_time = distance / self.tmp_speed
            self.last_pos_timestamp = time.time()
            duty_cycle = (x * per_deg + self.min) if self.dir else (self.max - x * per_deg)
            self.pi.set_servo_pulsewidth(self.pin, duty_cycle)
            return self.last_pos_travel_time
        
    def move_deg(self, x):
        return self.go_deg(x + self.pos)
        
    def go_min(self):
        return self.go_deg(0)
    
    def go_max(self):
        return self.go_deg(self.deg)
    
    def set_speed(self, speed):
        self.tmp_speed = speed
        
    def restore_speed(self):
        self.tmp_speed = self.speed
            
    def steps(self, steps):
        for x in np.linspace(0, self.deg, steps):
            yield x
            
    def stop(self):
        self.pi.stop()
        

class Turret:
    def __init__(self,
                 pin_x = 12, pin_y = 18,
                 max_x = 2500, min_x = 500,
                 max_y = 1000, min_y = 500,
                 dir_x = False, dir_y = False,
                 deg_y = 0, deg_x = 180):
        deg_y = (max_y - min_y) / (2000) * 180
        self.scan_speed = 50
        self.target = None
        self.servo_x = Servo(pin_x, max_x, min_x, dir_x, deg_x)
        self.servo_y = Servo(pin_y, max_y, min_y, dir_y, deg_y)
        self.pos_lock = Lock()
        self.target_lock = Lock()
    
    def go_center(self):
        with self.pos_lock:
            return max(self.servo_x.go_center(), self.servo_y.go_center())
        
    def move_deg(self, x, y):
        with self.pos_lock:
            return max(self.servo_x.move_deg(x), self.servo_y.move_deg(y))
        
    def go_deg(self, x, y):
        with self.pos_lock:
            return max(self.servo_x.go_deg(x), self.servo_y.go_deg(y))

    def pos(self):
        with self.pos_lock:
            return self.servo_x.get_pos(), self.servo_y.get_pos()

    def set_speed(self, x):
        self.servo_x.set_speed(x)
        self.servo_y.set_speed(x)
        
    def restore_speed(self):
        self.servo_x.restore_speed()
        self.servo_y.restore_speed()

    def scan_steps(self, steps_x, steps_y):
        self.set_speed(self.scan_speed)
        for y in list(self.servo_y.steps(steps_y)):
            for x in self.servo_x.steps(steps_x):
                yield x, y
            for x in reversed(list(self.servo_x.steps(steps_x))):
                yield x, y
        for y in reversed(list(self.servo_y.steps(steps_y))):
            for x in self.servo_x.steps(steps_x):
                yield x, y
            for x in reversed(list(self.servo_x.steps(steps_x))):
                yield x, y
        self.restore_speed()

    def follow_target(self):
        with self.target_lock:
            x, y = self.target
            self.target = None
        time.sleep(self.go_deg(x, y))
        
    def _run(self):
        try:
            while self.running:
                for x, y in self.scan_steps(20, 3):
                    time.sleep(self.go_deg(x, y))
                    while self.target is not None:
                        self.set_speed(50)
                        self.follow_target()
                        i = 0
                        while self.target is None and i < 60:
                            time.sleep(0.05)
                            i += 1
                        self.set_speed(self.scan_speed)
                    if not self.running:
                        break
        finally:
            self.servo_x.stop()
            self.servo_y.stop()
            
    def run(self):
        self.running = True
        thread = Thread(target=self._run, daemon=True)
        thread.start()
        
    def stop(self):
        self.running = False
        
    def set_target(self, target):
        with self.target_lock:
            self.target = target
        
if __name__ == "__main__":
    turret = Turret()
    turret.servo_y.go_min()
    turret.servo_x.go_center()
