from PySide6.QtCore import Qt, Signal, QLineF
from PySide6.QtGui import QColor, QPalette, QPainter, QPen
from PySide6.QtWidgets import (
    QGroupBox, QGridLayout, QSlider,
    QStackedLayout, QPushButton,
    QRadioButton, QButtonGroup,
    QWidget, QLabel, QHBoxLayout,
    QLCDNumber, QDial
)
from subsnake.gui.lcd import ClickLCD

class ModulatorGUI(QGroupBox):
    def __init__(self):
        super().__init__()

        #main layout & groups
        layout = QGridLayout()
        self.lfo_group_1 = QGroupBox("lfo 1")
        self.lfo_group_2 = QGroupBox("lfo 2")
        self.menv_group_1 = QGroupBox("env 1")
        self.menv_group_2 = QGroupBox("env 2")

        #sub-page layouts
        lfo_layout_1 = QGridLayout()
        lfo_layout_2 = QGridLayout()
        menv_layout_1 = QGridLayout()
        menv_layout_2 = QGridLayout()

        #module layout & widget 
        self.mod_stack = QStackedLayout()
        self.mod_widget = QWidget()

        #lfo 1 module
        freq_label_1 = QLabel("speed:")
        phase_label_1 = QLabel("phase:")
        shape_label_1 = QLabel("shape:")

        #   sliders
        self.lfo_freq_slider_1 = QSlider(Qt.Horizontal)
        self.lfo_phase_slider_1 = QSlider(Qt.Horizontal)
        self.lfo_freq_slider_1.setRange(1, 1000)
        self.lfo_phase_slider_1.setRange(1, 800)
        self.lfo_freq_slider_1.setSingleStep(1)
        self.lfo_freq_slider_1.setSingleStep(1)

        #   buttons
        self.lfo_shape_buttons_1 = QButtonGroup()
        self.lfo_shape_layout_1 = QHBoxLayout()
        self.lfo_sin_button_1 = QRadioButton("sine")
        self.lfo_sin_button_1.setChecked(True)
        self.lfo_tri_button_1 = QRadioButton("triangle")
        self.lfo_saw_button_1 = QRadioButton("sawtooth")
        self.lfo_sqr_button_1 = QRadioButton("square")
        self.lfo_shape_buttons_1.addButton(self.lfo_sin_button_1)
        self.lfo_shape_buttons_1.addButton(self.lfo_tri_button_1)
        self.lfo_shape_buttons_1.addButton(self.lfo_saw_button_1)
        self.lfo_shape_buttons_1.addButton(self.lfo_sqr_button_1)

        self.lfo_shape_layout_1.addStretch()
        self.lfo_shape_layout_1.addWidget(self.lfo_sin_button_1)
        self.lfo_shape_layout_1.addStretch()
        self.lfo_shape_layout_1.addWidget(self.lfo_tri_button_1)
        self.lfo_shape_layout_1.addStretch()
        self.lfo_shape_layout_1.addWidget(self.lfo_saw_button_1)
        self.lfo_shape_layout_1.addStretch()
        self.lfo_shape_layout_1.addWidget(self.lfo_sqr_button_1)
        self.lfo_shape_layout_1.addStretch()

        #   displays
        self.lfo_freq_display_1 = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.lfo_phase_display_1 = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        self.set_palette(self.lfo_freq_display_1)
        self.set_palette(self.lfo_phase_display_1)

        #   layout config
        lfo_layout_1.addWidget(freq_label_1, 0, 0)
        lfo_layout_1.addWidget(phase_label_1, 1, 0)
        lfo_layout_1.addWidget(shape_label_1, 2, 0)

        lfo_layout_1.addWidget(self.lfo_freq_slider_1, 0, 1)
        lfo_layout_1.addWidget(self.lfo_phase_slider_1, 1, 1)
        lfo_layout_1.addLayout(self.lfo_shape_layout_1, 2, 1)

        lfo_layout_1.addWidget(self.lfo_freq_display_1, 0, 2)
        lfo_layout_1.addWidget(self.lfo_phase_display_1, 1, 2)

        self.lfo_group_1.setObjectName("lfo1_group")

        #lfo 2 module
        freq_label_2 = QLabel("speed:")
        phase_label_2 = QLabel("phase:")
        shape_label_2 = QLabel("shape:")

        #   sliders
        self.lfo_freq_slider_2 = QSlider(Qt.Horizontal)
        self.lfo_phase_slider_2 = QSlider(Qt.Horizontal)
        self.lfo_freq_slider_2.setRange(1, 1000)
        self.lfo_phase_slider_2.setRange(1, 800)
        self.lfo_freq_slider_2.setSingleStep(1)
        self.lfo_freq_slider_2.setSingleStep(1)

        #   buttons
        self.lfo_shape_buttons_2 = QButtonGroup()
        self.lfo_shape_layout_2 = QHBoxLayout()
        self.lfo_sin_button_2 = QRadioButton("sine")
        self.lfo_sin_button_2.setChecked(True)
        self.lfo_tri_button_2 = QRadioButton("triangle")
        self.lfo_saw_button_2 = QRadioButton("sawtooth")
        self.lfo_sqr_button_2 = QRadioButton("square")
        self.lfo_shape_buttons_2.addButton(self.lfo_sin_button_2)
        self.lfo_shape_buttons_2.addButton(self.lfo_tri_button_2)
        self.lfo_shape_buttons_2.addButton(self.lfo_saw_button_2)
        self.lfo_shape_buttons_2.addButton(self.lfo_sqr_button_2)

        self.lfo_shape_layout_2.addStretch()
        self.lfo_shape_layout_2.addWidget(self.lfo_sin_button_2)
        self.lfo_shape_layout_2.addStretch()
        self.lfo_shape_layout_2.addWidget(self.lfo_tri_button_2)
        self.lfo_shape_layout_2.addStretch()
        self.lfo_shape_layout_2.addWidget(self.lfo_saw_button_2)
        self.lfo_shape_layout_2.addStretch()
        self.lfo_shape_layout_2.addWidget(self.lfo_sqr_button_2)
        self.lfo_shape_layout_2.addStretch()

        #   displays
        self.lfo_freq_display_2 = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.lfo_phase_display_2 = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        self.set_palette(self.lfo_freq_display_2)
        self.set_palette(self.lfo_phase_display_2)

        #   layout config
        lfo_layout_2.addWidget(freq_label_2, 0, 0)
        lfo_layout_2.addWidget(phase_label_2, 1, 0)
        lfo_layout_2.addWidget(shape_label_2, 2, 0)

        lfo_layout_2.addWidget(self.lfo_freq_slider_2, 0, 1)
        lfo_layout_2.addWidget(self.lfo_phase_slider_2, 1, 1)
        lfo_layout_2.addLayout(self.lfo_shape_layout_2, 2, 1)

        lfo_layout_2.addWidget(self.lfo_freq_display_2, 0, 2)
        lfo_layout_2.addWidget(self.lfo_phase_display_2, 1, 2)

        self.lfo_group_2.setObjectName("lfo2_group")

        #envelope 1 module
        #   labels
        attack_label_1 = QLabel("attack:")
        release_label_1 = QLabel("release:")
        mode_label_1 = QLabel("mode:")

        #   sliders
        self.menv_att_slider_1 = QSlider(Qt.Horizontal)
        self.menv_rel_slider_1 = QSlider(Qt.Horizontal)
        self.menv_att_slider_1.setRange(1, 1000)
        self.menv_rel_slider_1.setRange(1, 1000)
        self.menv_att_slider_1.setSingleStep(1)
        self.menv_rel_slider_1.setSingleStep(1)

        #   buttons
        self.menv_mode_buttons_1 = QButtonGroup()
        self.menv_mode_layout_1 = QHBoxLayout()
        self.menv_ar_button_1 = QRadioButton("AR")
        self.menv_ar_button_1.setChecked(True)
        self.menv_ahr_button_1 = QRadioButton("AHR")
        self.menv_loop_button_1 = QRadioButton("loop")
        self.menv_mode_buttons_1.addButton(self.menv_ar_button_1)
        self.menv_mode_buttons_1.addButton(self.menv_ahr_button_1)
        self.menv_mode_buttons_1.addButton(self.menv_loop_button_1)

        self.menv_mode_layout_1.addStretch()
        self.menv_mode_layout_1.addWidget(self.menv_ar_button_1)
        self.menv_mode_layout_1.addStretch()
        self.menv_mode_layout_1.addWidget(self.menv_ahr_button_1)
        self.menv_mode_layout_1.addStretch()
        self.menv_mode_layout_1.addWidget(self.menv_loop_button_1)
        self.menv_mode_layout_1.addStretch()

        #   displays
        self.menv_att_display_1 = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.menv_rel_display_1 = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        self.set_palette(self.menv_att_display_1)
        self.set_palette(self.menv_rel_display_1)

        #   layout config
        menv_layout_1.addWidget(attack_label_1, 0, 0)
        menv_layout_1.addWidget(release_label_1, 1, 0)
        menv_layout_1.addWidget(mode_label_1, 2, 0)

        menv_layout_1.addWidget(self.menv_att_slider_1, 0, 1)
        menv_layout_1.addWidget(self.menv_rel_slider_1, 1, 1)
        menv_layout_1.addLayout(self.menv_mode_layout_1, 2, 1)

        menv_layout_1.addWidget(self.menv_att_display_1, 0, 2)
        menv_layout_1.addWidget(self.menv_rel_display_1, 1, 2)

        self.menv_group_1.setObjectName("menv1_group")

        #envelope 2 module
        #   labels
        attack_label_2 = QLabel("attack:")
        release_label_2 = QLabel("release:")
        mode_label_2 = QLabel("mode:")

        #   sliders
        self.menv_att_slider_2 = QSlider(Qt.Horizontal)
        self.menv_rel_slider_2 = QSlider(Qt.Horizontal)
        self.menv_att_slider_2.setRange(1, 1000)
        self.menv_rel_slider_2.setRange(1, 1000)
        self.menv_att_slider_2.setSingleStep(1)
        self.menv_rel_slider_2.setSingleStep(1)

        #   buttons
        self.menv_mode_buttons_2 = QButtonGroup()
        self.menv_mode_layout_2 = QHBoxLayout()
        self.menv_ar_button_2 = QRadioButton("AR")
        self.menv_ar_button_2.setChecked(True)
        self.menv_ahr_button_2 = QRadioButton("AHR")
        self.menv_loop_button_2 = QRadioButton("loop")
        self.menv_mode_buttons_2.addButton(self.menv_ar_button_2)
        self.menv_mode_buttons_2.addButton(self.menv_ahr_button_2)
        self.menv_mode_buttons_2.addButton(self.menv_loop_button_2)

        self.menv_mode_layout_2.addStretch()
        self.menv_mode_layout_2.addWidget(self.menv_ar_button_2)
        self.menv_mode_layout_2.addStretch()
        self.menv_mode_layout_2.addWidget(self.menv_ahr_button_2)
        self.menv_mode_layout_2.addStretch()
        self.menv_mode_layout_2.addWidget(self.menv_loop_button_2)
        self.menv_mode_layout_2.addStretch()

        #   displays
        self.menv_att_display_2 = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)
        self.menv_rel_display_2 = self.configure_display(ClickLCD(), 3, QLCDNumber.Dec, QLCDNumber.Flat, True)

        self.set_palette(self.menv_att_display_2)
        self.set_palette(self.menv_rel_display_2)

        #   layout config
        menv_layout_2.addWidget(attack_label_2, 0, 0)
        menv_layout_2.addWidget(release_label_2, 1, 0)
        menv_layout_2.addWidget(mode_label_2, 2, 0)

        menv_layout_2.addWidget(self.menv_att_slider_2, 0, 1)
        menv_layout_2.addWidget(self.menv_rel_slider_2, 1, 1)
        menv_layout_2.addLayout(self.menv_mode_layout_2, 2, 1)

        menv_layout_2.addWidget(self.menv_att_display_2, 0, 2)
        menv_layout_2.addWidget(self.menv_rel_display_2, 1, 2)

        self.menv_group_2.setObjectName("menv2_group")

        #module select buttons
        self.lfo_button_1 = QPushButton("lfo 1")
        self.lfo_button_2 = QPushButton("lfo 2")
        self.menv_button_1 = QPushButton("env 1")
        self.menv_button_2 = QPushButton("env 2")
        self.lfo_button_1.setCheckable(True)
        self.lfo_button_2.setCheckable(True)
        self.menv_button_1.setCheckable(True)
        self.menv_button_2.setCheckable(True)
        self.lfo_button_1.setChecked(True)
        self.mod_buttons_group = QButtonGroup()
        self.mod_buttons_group.addButton(self.lfo_button_1)
        self.mod_buttons_group.addButton(self.lfo_button_2)
        self.mod_buttons_group.addButton(self.menv_button_1)
        self.mod_buttons_group.addButton(self.menv_button_2)
        self.mod_buttons = QWidget()
        self.mod_buttons_layout = QGridLayout()

        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mod_stack.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lfo_layout_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lfo_layout_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        menv_layout_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        menv_layout_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mod_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mod_widget.setAttribute(Qt.WA_StyledBackground, True)

        self.lfo_group_1.setLayout(lfo_layout_1)
        self.lfo_group_2.setLayout(lfo_layout_2)
        self.menv_group_1.setLayout(menv_layout_1)
        self.menv_group_2.setLayout(menv_layout_2)

        self.mod_stack.addWidget(self.lfo_group_1)
        self.mod_stack.addWidget(self.lfo_group_2)
        self.mod_stack.addWidget(self.menv_group_1)
        self.mod_stack.addWidget(self.menv_group_2)

        self.mod_buttons_layout.addWidget(self.lfo_button_1, 0, 0)
        self.mod_buttons_layout.addWidget(self.lfo_button_2, 0, 1)
        self.mod_buttons_layout.addWidget(self.menv_button_1, 0, 2)
        self.mod_buttons_layout.addWidget(self.menv_button_2, 0, 3)
        self.mod_buttons.setLayout(self.mod_buttons_layout)

        self.mod_widget.setLayout(self.mod_stack)
        layout.addWidget(self.mod_widget, 0, 0)
        layout.addWidget(self.mod_buttons, 1, 0)
        
        self.setLayout(layout)
        self.setObjectName("mod_group")
        self.mod_widget.setObjectName("mod_subgroup")
        self.lfo_button_1.setObjectName("lfo1_button")
        self.lfo_button_2.setObjectName("lfo2_button")
        self.menv_button_1.setObjectName("menv1_button")
        self.menv_button_2.setObjectName("menv2_button")
        self.setTitle("modulators")

        self.mod_buttons_group.buttonClicked.connect(self.setModule)

    #module select slot
    def setModule(self, button):
        button_text = button.text()
        if button_text == "lfo 1":
            self.mod_stack.setCurrentIndex(0)
        elif button_text == "lfo 2":
            self.mod_stack.setCurrentIndex(1)
        elif button_text == "env 1":
            self.mod_stack.setCurrentIndex(2)
        elif button_text == "env 2":
            self.mod_stack.setCurrentIndex(3)

    #helpers
    def configure_display(self, display, num_digits, num_mode, dig_style, small_dec):
        display.setMode(num_mode)
        display.setDigitCount(num_digits)
        display.setSegmentStyle(dig_style)
        display.setSmallDecimalPoint(small_dec)
        return display
    
    def set_palette(self, display):
        text_color = QColor("black")
        display_palette = display.palette()
        display_palette.setColor(QPalette.ColorRole.WindowText, text_color)
        display.setAutoFillBackground(True)
        display.setPalette(display_palette)

class CoolDial(QDial):
    def __init__(self, step, min, max):
        super().__init__()
        self.mode = 0
        self.max = max
        self.min = min
        self.cursor_y_pos = 0
        self.setSingleStep(step)
        self.setRange(min, max)
        self.setValue((min+max)/2)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        bg_color = self.palette().color(QPalette.ColorRole.Window)
        painter.setBrush(bg_color)
        painter.setPen(QColor("white"))

        painter.drawEllipse(self.rect())

        center = self.rect().center()
        painter.translate(center)
        rotation_deg = 120.0*(self.value()/self.max)
        painter.rotate(rotation_deg)
        radius = min(self.rect().width(), self.rect().height())/2.0

        notch_pen = QPen(QColor("black"))
        notch_pen.setWidth(1.2)
        #notch_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(notch_pen)

        notch = QLineF(0, 0, 0, -radius)
        painter.drawLine(notch)

        painter.end()

    #get cursor y pos
    def mousePressEvent(self, event):
        self.cursor_y_pos = event.position().y()
        event.accept()

    #disable set value on release
    def mouseReleaseEvent(self, event):
        event.accept()
    
    #single-axis knob movement (y, 1:1)
    def mouseMoveEvent(self, event):
        delta_y = self.cursor_y_pos - event.position().y()
        self.cursor_y_pos = event.position().y()
        new_value = self.value() + int(delta_y)
        self.setValue(new_value)
        event.accept()

        

