#!/usr/bin/python3
#-*- coding:utf-8 -*-


import os
import sys
import cv2
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class FaceSightEngine(object):
    """"""

    def __init__(self, video_type = 0, video_path = ""):
        """Constructor"""
        
        if video_type == 1:
            self._capture = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        elif video_type == 2:
            self._capture = cv2.VideoCapture(video_path)
        else:
            self._capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
        self._face_detector = None
        self._is_face_detector = False
            
    def __def__(self):
        
        self.release()
        
    def release(self):
        self._capture.release()
            
        
    def faceDetector(self):
        # 加载人脸检测器模型
        self._face_detector = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
        self._is_face_detector = True
        
        
    def cancelFaceDetector(self):
        
        self._is_face_detector = False
        
    def readFrame(self):
        
        if not self._capture.isOpened():
            return None
        
        ret, self._frame = self._capture.read()
        if not ret:
            return None
        
        cv2.cvtColor(self._frame, cv2.COLOR_BGR2RGB, self._frame)

        return self._frame
    
    def frameFaceDetector(self):
        
        if self._face_detector and self._is_face_detector:
            gray = cv2.cvtColor(self._frame, code = cv2.COLOR_BGR2GRAY)  # 转化为灰度图进行检测，减少计算量
            faces = self._face_detector.detectMultiScale(gray)  # 获得人脸检测结果
            for x, y, w, h in faces:  # 进行for循环，将检测到的所有人脸区域绘制标注
                cv2.circle(self._frame, (x + w // 2, y + h // 2), w // 2, [255, 0, 0], 2) # 用圆圈圈出识别人脸        
    
    def frame2Image(self):
    
        img_rows, img_cols, channels = self._frame.shape
        bytesPerLine = channels * img_cols    
    
        img = QImage(self._frame.data, img_cols, img_rows, bytesPerLine, QImage.Format_RGB888)  
        
        return img
    

class SightFrame(QWidget):
    
    def __init__(self):
        
        super().__init__()
        
        self.initUI()
        
        self.is_open = False
        self._engine = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.runvideoFrame)
        self._timer.setInterval(25)
        
        
    def initUI(self):
        
        self.setWindowTitle("人脸识别")
        self.resize(860, 520)
        
        group1 = QGroupBox("摄像头/视频", self)
        group2 = QGroupBox("截获图", self)
        
        self.lab_video = QLabel(group1)
        self.lab_capture_img = QLabel(group2)
        
        self.btn_open = QPushButton("打开内置摄像头", self)
        self.btn_stream_type1 = QRadioButton("内置摄像头", self)
        self.btn_stream_type2 = QRadioButton("外接摄像头", self)
        self.btn_stream_type3 = QRadioButton("视频文件", self)
        self.btn_stream_type1.setChecked(True)
        self.btn_open.setFixedSize(110, 40)
        
        self.btn_check_face = QCheckBox("人脸识别", self)
        
        self.btn_capture = QPushButton("截获图", self)
        self.btn_save = QPushButton("保存图", self)
        self.btn_capture.setFixedSize(110, 40)
        self.btn_save.setFixedSize(110, 40)
        
        layout_g1 = QHBoxLayout()
        layout_g1.addWidget(self.lab_video)
        group1.setLayout(layout_g1)
        
        layout_g2 = QHBoxLayout()
        layout_g2.addWidget(self.lab_capture_img)
        group2.setLayout(layout_g2)
        
        
        layout_g3 = QHBoxLayout()
        layout_g31 = QHBoxLayout()
        layout_g31.addWidget(self.btn_open)
        layout_g31.addSpacing(10)
        layout_g31.addWidget(self.btn_stream_type1)
        layout_g31.addWidget(self.btn_stream_type2)
        layout_g31.addWidget(self.btn_stream_type3)
        layout_g31.addWidget(self.btn_check_face)
        
        layout_g32 = QHBoxLayout()
        layout_g32.addWidget(self.btn_capture)
        layout_g32.addWidget(self.btn_save)
        
        layout_g3.addLayout(layout_g31)
        layout_g3.addLayout(layout_g32)
    
        layout = QVBoxLayout()
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        
        layout1.addWidget(group1)
        layout1.addWidget(group2)

        
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        layout.addSpacing(10)
        layout.addLayout(layout_g3)
        
        self.setLayout(layout)
        
        self.btn_open.clicked.connect(self.slotClickedOpen)
        self.btn_stream_type1.clicked.connect(self.slotClickedStreamType)
        self.btn_stream_type2.clicked.connect(self.slotClickedStreamType)
        self.btn_stream_type3.clicked.connect(self.slotClickedStreamType)
        self.btn_check_face.clicked.connect(self.slotClickedCheckFace)
        self.btn_capture.clicked.connect(self.slotClickedCapture)
        self.btn_save.clicked.connect(self.slotClickedSave)
        
    def updateStreamTypeStatus(self, status):
        
        self.btn_stream_type1.setEnabled(status)
        self.btn_stream_type2.setEnabled(status)
        self.btn_stream_type3.setEnabled(status)
        
    def updateStreamTypeText(self):
        
        if self.btn_stream_type1.isChecked():
            if self.is_open:
                self.btn_open.setText("关闭内置摄像头")
            else:
                self.btn_open.setText("打开内置摄像头")
        elif self.btn_stream_type2.isChecked():
            if self.is_open:
                self.btn_open.setText("关闭外接摄像头")
            else:
                self.btn_open.setText("打开外接摄像头")                    
        elif self.btn_stream_type3.isChecked():
            if self.is_open:
                self.btn_open.setText("关闭视频文件流")
            else:
                self.btn_open.setText("打开视频文件流") 

    def startEngine(self, stream_type, path = ""):
        
        self._engine = FaceSightEngine(stream_type, path)
        if self._engine:
            ischecked = self.btn_check_face.isChecked()        
            if ischecked:
                self._engine.faceDetector()

                
        self._timer.start()
        
    def stopEngine(self):
        
        self._engine.release()
        self._timer.stop()
        
    def slotClickedOpen(self, evt):
        
        self.is_open = not self.is_open
        if self.btn_stream_type1.isChecked():
            if self.is_open:
                self.startEngine(0)
            else:
                self.stopEngine()
                
        elif self.btn_stream_type2.isChecked():
            if self.is_open:
                self.startEngine(1)
            else:
                self.stopEngine()
                
        elif self.btn_stream_type3.isChecked():
            if self.is_open:
                dlg = QFileDialog(self)
                dlg.setWindowTitle("选择视频文件")
                dlg.setNameFilter("mp4 file (*.mp4)\navi file (*.avi)\nall file (*.*)")
                ret = dlg.exec_()
                if ret == QDialog.Accepted:
                    path = dlg.selectedFiles()[0] 
                    self.startEngine(2, path)
            else:
                self.stopEngine()                
                
           
        self.updateStreamTypeText()
        self.updateStreamTypeStatus(not self.is_open)
        
                
    def slotClickedStreamType(self, evt):
        
        self.updateStreamTypeText()

    def slotClickedCheckFace(self, evt):
        
        ischecked = self.btn_check_face.isChecked()
        if self._engine:
            if ischecked:
                self._engine.faceDetector()
            else:
                self._engine.cancelFaceDetector()
                
                
    def slotClickedCapture(self, evt):
        
        frame = self._engine.readFrame()
        if frame is not None:    
            self.capture_img = self._engine.frame2Image()
            if self.capture_img:
                newimg = QPixmap.fromImage(self.capture_img).scaled(self.lab_capture_img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lab_capture_img.setPixmap(newimg)
                
    def slotClickedSave(self, evt):
        
        if hasattr(self, 'capture_img') and self.capture_img:
            #获取当前时间,转化成字符串
            timenow = datetime.datetime.now()
            timestr = timenow.strftime("%Y-%m-%d-%H-%M-%S")
            
            #保存二维码图片
            if not os.path.exists("imgs"):
                os.makedirs("imgs")
                
            filename = "imgs/imges-" + timestr + '.png'        
            self.capture_img.save(filename)
        else:         
            QMessageBox.warning(self, "警告提示", "请先截取图在保存该图片！")
            
    def resizeEvent(self, evt):
        
        super().resizeEvent(evt)
        
        if hasattr(self, 'capture_img') and self.capture_img:
            newimg = QPixmap.fromImage(self.capture_img).scaled(self.lab_capture_img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lab_capture_img.setPixmap(newimg)  
            
        
    def runvideoFrame(self):
        
        frame = self._engine.readFrame()
        if frame is not None:
            self._engine.frameFaceDetector()
            img = self._engine.frame2Image()
            if img:
                newimg = QPixmap.fromImage(img).scaled(self.lab_video.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lab_video.setPixmap(newimg)


if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    
    frame = SightFrame()
    frame.show()
    
    code = app.exec_()
    sys.exit(code)