from flask import Response
from flask import Flask
from flask import render_template
import threading
import logging
import imutils
import cv2

output_frame = None
lock = threading.Lock()
app = Flask(__name__)

@app.route("/")
def index():
    logging.info("responding to request for index.html")
    return render_template("index.html")
        
def generate():
    global output_frame, lock

    while True:
        with lock:
            if output_frame is None:
                continue

            (flag, encodedImage) = cv2.imencode(".jpg", output_frame)

            if not flag:
                continue

        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
    return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

def _run(ip, port):
    app.run(host=ip, port=port, debug=True,
        threaded=True, use_reloader=False)

def set_frame(frame):
    global output_frame
    with lock:
        output_frame = frame.copy()

def run(ip, port):
    thread = threading.Thread(target=_run, args=(ip, port), daemon=True)
    thread.start()
    