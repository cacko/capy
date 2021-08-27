from PyQt6 import QtCore
from PyQt6.QtWidgets import QDialog, QVBoxLayout
from PyQt6.QtGui import QKeySequence, QMouseEvent, QPixmap, QImage, QShortcut
import cv2
from PyQt6.QtCore import QPoint, QSize, pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
from av import Player
from .video import Video


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(0)
        player = Player()
        while self._run_flag:
            frame, _ = next(player)
            self.change_pixmap_signal.emit(frame)

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class App(QDialog):

    __on_top = 0
    __on_fullscreen = 0
    disply_width = 960
    display_height = 540
    __last_size = QSize()

    def __init__(self):
        super().__init__()

        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.resize(self.disply_width, self.display_height)
        self.setWindowTitle("CAPY")

        self.shortcut_top = QShortcut(QKeySequence(Qt.Key.Key_A), self)
        self.shortcut_top.activated.connect(self.on_top)
        self.shortcut_fs = QShortcut(QKeySequence(Qt.Key.Key_F), self)
        self.shortcut_fs.activated.connect(self.on_fullscreen)
        self.shortcut_escape = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self.shortcut_escape.activated.connect(self.on_escape)

        self.setSizeGripEnabled(True)

        self.image_label = Video(self)
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.image_label)
        self.setLayout(vbox)
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()
        self.on_top()
        self.oldPos = self.pos()

    def mousePressEvent(self, event: QMouseEvent):
        self.oldPos = event.globalPosition()

    def mouseMoveEvent(self, event: QMouseEvent):
        delta: QPoint = (event.globalPosition() - self.oldPos).toPoint()
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition()

    def on_top(self):
        self.__on_top = 1 ^ self.__on_top
        if self.__on_top:
            self.setWindowFlags(
                self.windowFlags() | QtCore.Qt.WindowType.WindowStaysOnTopHint
            )
        else:
            self.setWindowFlags(
                self.windowFlags() & ~QtCore.Qt.WindowType.WindowStaysOnTopHint
            )
        self.show()

    def on_fullscreen(self):
        self.__on_fullscreen = 1 ^ self.__on_fullscreen
        if self.__on_fullscreen:
            self.__last_size = self.size()
            self.showFullScreen()
        else:
            self.showNormal()
            self.resize(self.__last_size)

    def on_escape(self):
        if self.__on_fullscreen:
            return self.on_fullscreen()
        return self.close()

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(
            rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
        )
        p = convert_to_Qt_format.scaled(
            self.disply_width,
            self.display_height,
            aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
            transformMode=Qt.TransformationMode.SmoothTransformation,
        )
        return QPixmap.fromImage(p)
