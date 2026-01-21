from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLCDNumber

class ClickLCD(QLCDNumber):
    double_clicked = Signal()

    def __init__(self):
        super().__init__()

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()
        return super().mouseDoubleClickEvent(event)