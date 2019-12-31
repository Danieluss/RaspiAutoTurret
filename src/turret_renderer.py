import cv2

class Renderer:
    def __init__(self):
        pass
        
    def draw_face(self, frame, face):
        x, y, w, h = face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255,255,255), 2)

    def render(self, frame):
        cv2.imshow("Turret", frame)
        
