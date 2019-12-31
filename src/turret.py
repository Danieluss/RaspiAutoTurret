from imutils.video.pivideostream import PiVideoStream
from imutils.video import FPS
from time import sleep
from datetime import *
import cv2
from turret_servo import *
from turret_repository import *
from turret_renderer import *
import turret_webstreaming
import argparse
import logging


parser = argparse.ArgumentParser()
parser.add_argument('-r', '--resolution', type=tuple, default=(640, 480), help='camera resolution, usage: -R width,height')
parser.add_argument('-F', '--framerate', type=int, default=32, help='camera framerate')
parser.add_argument('-T', '--rotation', type=int, default=180, help='camera rotation')
parser.add_argument('-R', '--render', type=bool, default=False, help='draw a window with turret vision')
parser.add_argument('-S', '--stream', type=bool, default=True, help='host turret vision webapp')
parser.add_argument('--sr_port', type=int, default=8080, help='webapp port')
parser.add_argument('-C', '--classifiers', type=list, default=['haarcascade_frontalface_default.xml'], help='list of opencv .xml cascade classifiers, usage: -C /example/path,/example/path2')
parser.add_argument('-D', '--database', type=bool, default=True, help='save detection history to database')
parser.add_argument('--db_on', type=bool, default=True, help='use mysql db')
parser.add_argument('--db_host', type=str, default='localhost', help='mysql db host')
parser.add_argument('--db_user', type=str, default='turretuser', help='mysql db user')
parser.add_argument('--db_password', type=str, default='pi', help='mysql db password')
parser.add_argument('--db_cooldown', type=float, default=1, help='detection db write cooldown')
args = parser.parse_args()
    
logging.basicConfig(format='[%(asctime)-15s]:[%(levelname)s]:[%(process)d]: %(message)s',
                    level='INFO',
                    handlers=[
                        logging.FileHandler("{0}/{1}.log".format('/tmp/', 'turret')),
                        logging.StreamHandler()
                    ])

RESOLUTION = args.resolution
FRAMERATE = args.framerate
ROTATION = args.rotation
DRAW = args.render
CLASSIFIERS = args.classifiers
    
def get_stream():
    pi_stream = PiVideoStream(resolution=RESOLUTION, framerate=FRAMERATE)
    pi_stream.camera.rotation = ROTATION
    return pi_stream

def sgn(x):
    if x < 0:
        return -1
    elif x > 0:
        return 1
    return 0

def cam_x_to_deg(x):
    val = (RESOLUTION[0]/2 - x)/(RESOLUTION[0]/2)
    aval = abs(val)
    if aval < 0.1:
        return 0
    return sgn(val) * np.degrees(np.arctan((aval*8)/15.15))
    
def cam_y_to_deg(y):
    val = (RESOLUTION[1]/2 - y)/(RESOLUTION[1]/2)
    aval = abs(val)
    if aval < 0.1:
        return 0
    return sgn(val) * np.degrees(np.arctan((aval*6.5)/15.15))
    
if __name__ == "__main__":
    repos = []
    if args.database:
        repos = [Repository(args.db_host, args.db_user, args.db_password, args.db_cooldown)]
    renderer = Renderer()
    turret = Turret()
    stream = get_stream().start()
    turret_webstreaming.run('0.0.0.0', args.sr_port)
    sleep(1.0)
    turret.run()
    classifiers = [cv2.CascadeClassifier(x) for x in CLASSIFIERS]
    try:
        f = True
        last_target = None
        counter = FPS().start()
        while f:
            frame = stream.read()
            faces = []
            pos = turret.pos()
            for classifier in classifiers:
                faces.extend(classifier.detectMultiScale(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.2, minNeighbors=5))
            
            for face in faces:
                if renderer:
                    renderer.draw_face(frame, face)


            if len(faces) > 0:
                x, y, w, h = faces[0]
            
            def to_turret_space(face):
                x, y, w, h = face
                return (pos[0] - cam_x_to_deg(x + w/2),
                          pos[1] + cam_y_to_deg(y + h/2))
    
            faces = [np.array(x) for x in map(to_turret_space, faces)]
            
            if len(faces) > 0:
                if last_target is None:
                    last_target = faces[0]
                else:
                    last_target = min(faces, key=lambda face:np.linalg.norm(face - last_target))
                turret.set_target(last_target)
                for repo in repos:
                    repo.insert_detection(pos[0], pos[1], last_target[0], last_target[1])
            
            if args.render:
                renderer.render(frame)

            turret_webstreaming.set_frame(frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                f = False
                turret.stop()
                break
            counter.update()
    finally:
        counter.stop()
        logging.info("time: {:.2f}".format(counter.elapsed()));
        logging.info("FPS: {:.2f}".format(counter.fps()))
         
        cv2.destroyAllWindows()
        stream.stop()
