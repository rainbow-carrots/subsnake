from PySide6.QtWidgets import (
    QGroupBox, QGridLayout, QPushButton,
    QLabel, QSlider, QLCDNumber,
    QDialog, QDialogButtonBox, QLineEdit
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QPalette
from subsnake.gui.lcd import ClickLCD
from platformdirs import user_data_dir
from pathlib import Path

class SynthSettings(QGroupBox):
    drift_changed = Signal(float)

    def __init__(self, display_color=QColor("black")):
        super().__init__()

        drift_label = QLabel("osc drift:")

        self.drift_slider = QSlider(Qt.Horizontal)
        self.drift_slider.setRange(0, 1000)
        self.drift_slider.setSingleStep(1)
        self.drift_slider.setValue(0)

        self.display_color = display_color        
        self.drift_display = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.set_palette(self.drift_display)

        layout = QGridLayout()

        layout.addWidget(drift_label, 0, 0)
        layout.addWidget(self.drift_slider, 0, 1)
        layout.addWidget(self.drift_display, 0, 2)
        
        self.setLayout(layout)
        self.setObjectName("synth_group")
        self.setTitle("synth settings")

        self.drift_slider.valueChanged.connect(self.change_drift)
        self.drift_display.double_clicked.connect(self.reset_drift)

    def change_drift(self, value):
        norm_value = float(value)/100.0
        self.drift_display.display(f"{norm_value:.2f}")
        self.drift_changed.emit(norm_value)

    def reset_drift(self):
        self.drift_slider.setValue(0)

    #helpers
    def configure_display(self, display, num_digits, num_mode, dig_style, small_dec):
        display.setMode(num_mode)
        display.setDigitCount(num_digits)
        display.setSegmentStyle(dig_style)
        display.setSmallDecimalPoint(small_dec)
        return display
    
    def set_palette(self, display):
        text_color = self.display_color
        display_palette = display.palette()
        display_palette.setColor(QPalette.ColorRole.WindowText, text_color)
        display.setAutoFillBackground(True)
        display.setPalette(display_palette)

class RecorderSettings(QGroupBox):
    save_rec_buffer = Signal(str)

    def __init__(self, display_color=QColor("black")):
        super().__init__()
        self.save_button = QPushButton("save")
        self.save_rec_dialog = SaveRecDialog()

        layout = QGridLayout()
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.setObjectName("record_group")
        self.setTitle("record settings")

        self.user_sound_path = Path(user_data_dir("subsnake", "rainbow-carrots")) / "sound"
        self.check_user_dir()

        self.save_button.clicked.connect(self.save_file)

    def save_file(self):
        if self.save_rec_dialog.exec():
            new_name = self.save_rec_dialog.get_name()
            if (new_name != ""):
                new_filename = new_name + ".wav"
                new_path = self.user_sound_path / new_filename
                new_str_path = str(new_path)
                self.save_rec_buffer.emit(new_str_path)
        self.save_rec_dialog.clear_name()
    
    def check_user_dir(self):
        self.user_sound_path.mkdir(parents=True, exist_ok=True)

class SaveRecDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.name_input = QLineEdit()
        self.buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttons.setFocusPolicy(Qt.NoFocus)

        layout = QGridLayout()
        layout.addWidget(self.name_input, 0, 0)
        layout.addWidget(self.buttons, 1, 0)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setLayout(layout)
        self.setObjectName("save_rec_dialog")
        self.setWindowTitle("enter filename:")

    def get_name(self):
        return self.name_input.text()
    
    def clear_name(self):
        self.name_input.setText("")