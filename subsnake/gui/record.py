from PySide6.QtWidgets import (
    QWidget, QPushButton, QHBoxLayout,
    QLabel, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, Signal

class RecorderGUI(QWidget):
    pause = Signal()
    play = Signal()
    stop = Signal()
    loop = Signal(bool)
    record = Signal(bool)
    
    def __init__(self):
        super().__init__()

        self.current_time_label = QLabel("00:00")
        slash_label = QLabel("/")
        self.end_time_label = QLabel(("01:23"))

        self.record_button = QPushButton("●︎")
        self.play_button = QPushButton("▶")
        self.stop_button = QPushButton("■")
        self.loop_button = QPushButton("⟳")

        self.record_button.setCheckable(True)
        self.loop_button.setCheckable(True)
        self.play_button.setCheckable(True)

        self.record_button.setObjectName("record_button")
        self.play_button.setObjectName("play_button")
        self.stop_button.setObjectName("stop_button")
        self.loop_button.setObjectName("loop_button")

        self.current_time_label.setAlignment(Qt.AlignCenter)
        self.end_time_label.setAlignment(Qt.AlignCenter)
        slash_label.setAlignment(Qt.AlignCenter)

        self.current_time_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.end_time_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        slash_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        spacer_0 = QFrame()
        spacer_0.setFrameShape(QFrame.NoFrame)
        spacer_0.setObjectName("record_spacer_0")
        spacer_1 = QFrame()
        spacer_1.setFrameShape(QFrame.NoFrame)
        spacer_1.setObjectName("record_spacer_1")
        spacer_2 = QFrame()
        spacer_2.setFrameShape(QFrame.NoFrame)
        spacer_2.setObjectName("record_spacer_2")


        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(self.record_button, 0)
        layout.addWidget(spacer_0)
        layout.addWidget(self.current_time_label, 1)
        layout.addWidget(slash_label, 2)
        layout.addWidget(self.end_time_label, 3)
        layout.addWidget(spacer_1)
        layout.addWidget(self.play_button, 4)
        layout.addWidget(self.stop_button, 5)
        layout.addWidget(spacer_2)
        layout.addWidget(self.loop_button, 6)
        layout.addStretch()

        self.setLayout(layout)
        self.setObjectName("recorder")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.record_button.clicked.connect(self.record_pressed)
        self.play_button.clicked.connect(self.play_pressed)
        self.stop_button.pressed.connect(self.stop_pressed)
        self.loop_button.clicked.connect(self.loop_pressed)

    def record_pressed(self, state):
        self.record.emit(state)

    def play_pressed(self, state):
        if state:
            self.play.emit()
        else:
            self.pause.emit()

    def stop_pressed(self):
        self.play_pressed(False)
        self.play_button.setChecked(False)
        self.record_pressed(False)
        self.record_button.setChecked(False)
        self.stop.emit()

    def loop_pressed(self, state):
        self.loop.emit(state)
