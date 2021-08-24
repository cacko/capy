from PyQt6.QtCore import QSize
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QSizePolicy, QLabel


class Video(QLabel):

    parent = None

    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        QLabel.__init__(self, parent)
        self.resize(parent.width(), parent.height())
        self.setMinimumSize(QSize(200, 112))
        self.setScaledContents(True)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        self.setSizePolicy(sizePolicy)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        size = a0.size()
        self.setFixedHeight(size.width() * (1080 / 1920))
        self.parent.disply_width = size.width()
        self.parent.disply_height = size.height()
        return super().resizeEvent(a0)

    def mouseDoubleClickEvent(self, *args, **kwargs):
        return self.parent.on_fullscreen()
