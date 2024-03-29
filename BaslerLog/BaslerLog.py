import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtGui import QImage, QPixmap
import tkinter as tk
from tkinter import filedialog
from threading import Thread
import time
from datetime import datetime

# pylon
from pypylon import pylon
#import cv2
import numpy as np

WIN_WIDTH = 1300
WIN_HEIGHT = 1020

IMG_WIDTH = 1288
IMG_HEIGHT = 920

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        #uic.loadUi('./gui/Logger.ui', self)
        ui_path = os.path.dirname(os.path.realpath(__file__)) + '/gui/Logger.ui'
        uic.loadUi(ui_path, self)
        self.setFixedSize(WIN_WIDTH, WIN_HEIGHT)
        self.show()

        root = tk.Tk()
        root.withdraw()
        self.save_dir = os.getcwd()
        
        # Signals
        self.dirButton.clicked.connect(self.saveDir)
        self.saveButton.clicked.connect(self.saveImage)
        self.camButton.clicked.connect(self.camSet)
        

        # Camera
        self.camera = None
        self.isCon = False
        self.isSaving = False
        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        # Thread
        self.closing = False
        self.thread = Thread(target=self.displayThread)
        self.thread.start()
        

    def displayThread(self):
        while self.closing is False:

            try:
            #if self.isCon and self.camera.IsGrabbing():
                """
                if self.isSaving:
                    font = self.capLabel.font()
                    font.setPointSize(36)
                    font.setBold(True)
                    self.capLabel.setFont(font)
                    self.capLabel.setText("Capturing...")
                    time.sleep(3.0)
                    self.isSaving = False
                else:
                    self.capLabel.setText("")
                self.capLabel.setText("")
                """
                if self.isSaving:
                    time.sleep(3.0)
                    self.isSaving = False
                    self.saveButton.setText("Save Image")


                self.grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

                if self.grabResult.GrabSucceeded():
                    image = self.converter.Convert(self.grabResult)
                    img = image.GetArray()

                    guiImg = QImage(img, self.grabResult.Width, self.grabResult.Height, self.grabResult.Width*3, QImage.Format_RGB888)
                    pix = QPixmap(guiImg)
                    outpix = pix.scaledToWidth(IMG_WIDTH)
                    self.imgLabel.setPixmap(outpix)
            
            except:
                blank = np.ones([1080, 1080, 3], dtype=np.uint8)*255
                blankImg = QImage(blank, 1080, 1080, 1080*3, QImage.Format_RGB888)
                blankpix = QPixmap(blankImg)
                blankout = blankpix.scaledToWidth(IMG_WIDTH)
                self.imgLabel.setPixmap(blankout)

            time.sleep(0.1)
                

    
    def saveDir(self):
        direct = filedialog.askdirectory(initialdir="./", title="Select Folder")

        if isinstance(direct, str) and len(direct) > 0:
            self.save_dir = direct
            self.dirShow.setText(self.save_dir)
        else:
            self.save_dir = os.getcwd()
            self.dirShow.setText(self.save_dir)



    def saveImage(self):
        if self.save_dir is "./":
            self.saveDir()
        self.isSaving = True
        self.saveButton.setText("Saving...")

        now = "{}".format(datetime.now()).replace(":", "-")
        filename = now + ".png"
        path = self.save_dir + "/" + filename
        #print(path)

        try:
            
            img = pylon.PylonImage()
            img.AttachGrabResultBuffer(self.grabResult)
            img.Save(pylon.ImageFileFormat_Png, path)

        except:
            QtWidgets.QMessageBox.about(None, "Saving Error", "Camera is not connected")
        #print("Save Function")
        

    
    def camSet(self):
        if self.isCon is False:
            try:
                self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
                self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
                self.camButton.setText("Disconnect")
                self.isCon = True

            
            except:
                QtWidgets.QMessageBox.about(None, "Connection Error", "Camera is not connected")
                self.isCon = False
                self.camButton.setText("Connect")

        else:
            self.isCon = False
            self.camButton.setText("Connect")
            self.camera.Close()
            self.camera = None


    def closeEvent(self, QCloseEvent):
        self.closing = True
        self.isCon = False
        self.camera = None

            


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
