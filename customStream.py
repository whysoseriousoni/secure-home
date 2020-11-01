"""Stores a Streamer class"""
import time
from datetime import datetime
from functools import wraps
from threading import Thread

import cv2
from cryptography.fernet import Fernet
from flask import Flask, Response, render_template, request



class Streamer:
    """A clean wrapper class for a Flask OpenCV Video Streamer"""

    def __init__(
        self,
        port,
        stream_res=(1280, 720),
        frame_rate=10,
    ):
        self.flask_name = "{}_{}".format(__name__, port)
        self.flask = Flask(self.flask_name)
        self.frame_to_stream = None
        self.thread = None
        self.is_streaming = False
        self.port = port
        self.stream_res = stream_res
        self.frame_rate = frame_rate
        self.playerREC=True
        self.playerStop=False
    def __getstate__(self):
        """An override for loading this object's state from pickle"""
        ret = {
            "flask_name": self.flask_name,
            "port": self.port,
            "stream_res": self.stream_res,
        }
        return ret

    def __setstate__(self, dict_in):
        """An override for pickling this object's state"""
        self.flask_name = dict_in["flask_name"]
        self.flask = Flask(self.flask_name)
        self.frame_to_stream = None
        self.thread = None
        self.is_streaming = False
        self.port = dict_in["port"]
        self.stream_res = dict_in["stream_res"]
        

    def start_streaming(self):
        """Starts the video stream hosting process"""
        gen_function = self.gen

        @self.flask.route("/video_feed")
        # @self.requires_auth
        def video_feed():
           
            return Response(
                gen_function(), mimetype="multipart/x-mixed-replace; boundary=jpgboundary"
            )

        @self.flask.route("/",methods = ['POST', 'GET'])
        # @self.requires_auth
        def index():
            if request.method=='POST':
                    
                if request.form['control']=='PAUSE':
                    self.playerREC=not self.playerREC
                    # print(request.form['control'])

                elif request.form['control']=='STOP':

                    self.playerStop=not self.playerStop
                    # print(pause)
                
                else:
                    return render_template("index.html")

            """Route which renders the video within an HTML template"""
            return render_template("index.html")


        self.thread = Thread(
            daemon=True,
            target=self.flask.run,
            kwargs={
                "host": "192.168.1.6", #local host
                "port": self.port,
                "debug": False,
                "threaded": True,
            },
        )
        self.thread.start()
        self.is_streaming = True

    def update_frame(self, frame):
        """Updates the frame for streaming"""
        self.frame_to_stream = self.get_frame(frame)

    def get_frame(self, frame):
        """Encodes the OpenCV image to a 1280x720 image"""
        _, jpeg = cv2.imencode(
            ".jpg",
            cv2.resize(frame, self.stream_res),
            params=(cv2.IMWRITE_JPEG_QUALITY, 70),
        )
        return jpeg.tobytes()

    def gen(self):
        """A generator for the image."""
        header = "--jpgboundary\r\nContent-Type: image/jpeg\r\n"
        prefix = ""
        while True:
            # frame = self.frame_to_stream
            msg = (
                prefix
                + header
                + "Content-Length: {}\r\n\r\n".format(len(self.frame_to_stream))
            )

            yield (msg.encode("utf-8") + self.frame_to_stream)
            prefix = "\r\n"
            time.sleep(1 / self.frame_rate)

