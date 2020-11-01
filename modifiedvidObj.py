import cv2

import math
from sklearn import neighbors
import os
import pickle
from PIL import Image, ImageDraw
import numpy as np

# import tensorflow as tf
import mysql
from mysql import *
import PIL
import speech_recognition as sr
from gtts import gTTS as ts
import mysql.connector
import playsound
import os
import threading as mt
import urllib.request
import urllib
import time
import sys
from datetime import datetime
from customStream import Streamer
# from ObjectDetection import 
folder=os.getcwd()
saveTo="H:\\recording"
file='cameraaddress.txt'



def TIME():
    return(str(datetime.now().strftime("%d-%m-%Y-%H-%M-%S")))

class MULTITHREAD(mt.Thread):

    def __init__(self,threadID,cameraID,IPaddress,resX,resY,stopREC,newREC,FPS,port):

        mt.Thread.__init__(self)
        self.threadID=threadID
        self.cameraID=cameraID
        self.resY=resY
        self.resX=resX
        self.IPaddress=IPaddress
        self.stopREC=stopREC
        self.newREC=newREC
        self.FPS=FPS
        self.streamer=Streamer(port)
        self.RECORDSTOP=False

    def run(self):
        print("*****************************************")
        # print(self.options)
        print("*****************************************")

        self.openCamera(self.threadID,self.cameraID,self.IPaddress,self.resX,self.resY,self.stopREC,self.newREC,self.FPS)

    def openCamera(self,threadID,cameraID,IPaddress,resX,resY,stopREC,newREC,FPS):
        try:
            cam=cv2.VideoCapture(IPaddress)
            if not self.streamer.is_streaming:
                self.streamer.start_streaming()

            # retry application    
            if cam is None or not cam.isOpened():
                print("RETRYING")
                for i in range(1,3):
                    time.sleep(i)
                self.openCamera(threadID,cameraID,IPaddress,resX,resY,True,False,FPS)

            else:   

                print("CAMERA RUNNING AT %s , CAMERA ID %s , THREAD %s" %(IPaddress,cameraID,threadID))
                home=False # while true (outside)
                while True:

                    stopREC=self.streamer.playerREC ## pause record
                    terminate=self.streamer.playerStop ## close the cmd
                    print(stopREC) 
                    if terminate==True:
                        print("STOPPED")
                        break

                    # print(stopREC)
                    while stopREC == True:
                        # print("inside")
                        ret,frame=cam.read()

                        stopREC=self.streamer.playerREC ## pause record

                        terminate=self.streamer.playerStop ## close the cmd 

                        if newREC==False:
                            rec=cv2.VideoWriter(os.path.join(saveTo,'output-'+cameraID+'-'+TIME()+".avi"),cv2.VideoWriter_fourcc('M','J','P','G'),FPS,(resX,resY))
                            newREC=not newREC # true
                        

                        rec.write(frame)

                        cv2.putText(frame,"RECORDING",(0,60),1,2,(0,255,255)) 
                        self.streamer.update_frame(frame)
                        # asd
                        if stopREC == False:
                            self.RECORDSTOP=not self.RECORDSTOP # set to true to stop the recording
                        
                        if terminate==True:
                            rec.release()
                            print("STOPPED")
                            cam.release()
                            # exit(1)
                            thread.join()
                            break

                        if self.RECORDSTOP :  # if set true to stop the recording
                            print("RECORDING PAUSED")

                            # cam.release()
                            rec.release()
                            newREC=not newREC # turn to true again
                            self.RECORDSTOP=not self.RECORDSTOP ## setting back to false
                            break
                            
                        
                    # this video is telecasted not the other 
                    while (stopREC==False):

                        ret,frame=cam.read()

                        stopREC=self.streamer.playerREC 

                        self.streamer.update_frame(frame)

                        # cam.release()

                    if terminate==True:
                        cam.release()
                        rec.release()
                        print("STOPPED")
                        break

        except:

            try:
                if not terminate:
                    for i in range(1,3):
                        time.sleep(i)
                    self.openCamera(threadID,cameraID,IPaddress,resX,resY,True,False,FPS)
            except:
                pass


IPADDR=[]

with open(os.path.join(folder,file),'r') as f:
    for line in f.read().split("\n"):
        if line!="":
            IPADDR.append(line.split(" "))
print(IPADDR)
port=3030
for i in range(len(IPADDR)):
    if IPADDR[i][0][0] != "*" :
        
        thread=MULTITHREAD(str(i),str(i),str(IPADDR[i][0]),int(IPADDR[i][2]),int(IPADDR[i][3]),True,False,int(IPADDR[i][1]),port+i)
        thread.start()

