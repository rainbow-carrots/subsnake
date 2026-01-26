from PySide6.QtWidgets import (
    QGroupBox, QGridLayout,
    QLabel, QComboBox
)
from PySide6.QtCore import Signal, Qt

class AudioSettings(QGroupBox):
    device_changed = Signal(str)
    rate_changed = Signal(int)

    def __init__(self):
        super().__init__()

        device_label = QLabel("device:")
        device_label.setAlignment(Qt.AlignCenter)
        rate_label = QLabel("rate:")
        rate_label.setAlignment(Qt.AlignCenter)

        self.device_select = QComboBox()
        self.device_select.setEditable(False)
        self.device_select.setInsertPolicy(QComboBox.InsertAtBottom)
        self.device_select.setFocusPolicy(Qt.NoFocus)
        self.rate_select = QComboBox()
        self.rate_select.setEditable(False)
        self.rate_select.setInsertPolicy(QComboBox.InsertAtBottom)
        self.rate_select.setFocusPolicy(Qt.NoFocus)

        layout = QGridLayout()

        layout.addWidget(device_label, 0, 0)
        layout.addWidget(rate_label, 1, 0)

        layout.addWidget(self.device_select, 0, 1)
        layout.addWidget(self.rate_select, 1, 1)
        
        self.setLayout(layout)
        self.setObjectName("audio_group")
        self.setTitle("audio settings")

        self.device_select.currentTextChanged.connect(self.change_device)
        self.rate_select.currentTextChanged.connect(self.change_rate)

    def change_device(self, new_device):
        self.device_changed.emit(new_device)

    def change_rate(self, new_rate):
        rate = int(new_rate)
        self.device_changed.emit(rate)




