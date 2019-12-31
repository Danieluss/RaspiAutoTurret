import pigpio 
import time
from threading import Lock, Thread, Condition


r_pin = 17
g_pin = 27
b_pin = 22

class RGB_LED:
    def __init__(self, r_pin = 27, g_pin = 17, b_pin = 22):
        self.r_pin = r_pin
        self.g_pin = g_pin
        self.b_pin = b_pin
        self.pi = pigpio.pi()
        self.cond = Condition()
        self.pi_lock = Lock()
        self.requests = []
        
    def _run(self):
        try:
            while True:
                self.cond.acquire()
                while len(self.requests) == 0:
                    self.cond.wait()
                    
                r, g, b, t = self.requests.pop(0)
                self.cond.release()
                if t != -1:
                    self.set_rgb(r, g, b)
                    time.sleep(t)
                else:
                    self.set_rgb(r, g, b)
        finally:
            self.cond.release()
            self.set_rgb(0, 0, 0)
            with self.pi_lock:
                self.pi.stop()
            
    def run(self):
        thread = Thread(target=self._run, daemon=True)
        thread.start()
            
    def set_rgb(self, r, g, b):
        with self.pi_lock:
            self.pi.set_PWM_dutycycle(self.r_pin, 255 * r)
            self.pi.set_PWM_dutycycle(self.g_pin, 255 * g)
            self.pi.set_PWM_dutycycle(self.b_pin, 255 * b)
    
    def set_r(self, r):
        with self.pi_lock:
            self.pi.set_PWM_dutycycle(self.r_pin, 255 * r)
        
    def set_g(self, g):
        with self.pi_lock:
            self.pi.set_PWM_dutycycle(self.g_pin, 255 * g)
        
    def set_b(self, b):
        with self.pi_lock:
            self.pi.set_PWM_dutycycle(self.b_pin, 255 * b)
        
    def set_rgb_t(self, r, g, b, t):
        self.cond.acquire()
        self.requests.append((r, g, b, t))
        self.cond.notifyAll()
        self.cond.release()
        
rgb = RGB_LED()
        
if __name__ == "__main__":
    rgb_led = RGB_LED()
    rgb_led.run()
    rgb_led.set_rgb_t(0, 0, 1, 1)
    rgb_led.set_rgb_t(0, 0, 0, 1)
    rgb_led.set_rgb_t(0, 0, 1, 1)
    rgb_led.set_rgb_t(0, 0, 0, 1)  
