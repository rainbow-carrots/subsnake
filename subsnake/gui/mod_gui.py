from PySide6.QtCore import Qt, Signal, QLineF, QRectF
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
    #signals
    lfo1_freq_changed = Signal(float)
    lfo1_offset_changed = Signal(float)
    lfo1_shape_changed = Signal(int)

    lfo2_freq_changed = Signal(float)
    lfo2_offset_changed = Signal(float)
    lfo2_shape_changed = Signal(int)

    menv1_att_changed = Signal(float)
    menv1_rel_changed = Signal(float)
    menv1_mode_changed = Signal(int)

    menv2_att_changed = Signal(float)
    menv2_rel_changed = Signal(float)
    menv2_mode_changed = Signal(int)   

    def __init__(self, display_color=QColor("black")):
        super().__init__()
        self.display_color = display_color

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
        self.lfo_phase_slider_1.setRange(0, 1000)
        self.lfo_freq_slider_1.setSingleStep(1)
        self.lfo_freq_slider_1.setSingleStep(1)

        #   buttons
        self.lfo_shape_buttons_1 = QButtonGroup()
        self.lfo_shape_layout_1 = QHBoxLayout()
        self.lfo_sin_button_1 = QRadioButton("sine")
        self.lfo_sin_button_1.setChecked(True)
        self.lfo_tri_button_1 = QRadioButton("tri")
        self.lfo_rmp_button_1 = QRadioButton("ramp")
        self.lfo_saw_button_1 = QRadioButton("saw")
        self.lfo_sqr_button_1 = QRadioButton("square")
        self.lfo_sah_button_1 = QRadioButton("s+h")
        self.lfo_shape_buttons_1.addButton(self.lfo_sin_button_1)
        self.lfo_shape_buttons_1.addButton(self.lfo_tri_button_1)
        self.lfo_shape_buttons_1.addButton(self.lfo_rmp_button_1)
        self.lfo_shape_buttons_1.addButton(self.lfo_saw_button_1)
        self.lfo_shape_buttons_1.addButton(self.lfo_sqr_button_1)
        self.lfo_shape_buttons_1.addButton(self.lfo_sah_button_1)

        self.lfo_shape_layout_1.addStretch()
        self.lfo_shape_layout_1.addWidget(self.lfo_sin_button_1)
        self.lfo_shape_layout_1.addStretch()
        self.lfo_shape_layout_1.addWidget(self.lfo_tri_button_1)
        self.lfo_shape_layout_1.addStretch()
        self.lfo_shape_layout_1.addWidget(self.lfo_rmp_button_1)
        self.lfo_shape_layout_1.addStretch()
        self.lfo_shape_layout_1.addWidget(self.lfo_saw_button_1)
        self.lfo_shape_layout_1.addStretch()
        self.lfo_shape_layout_1.addWidget(self.lfo_sqr_button_1)
        self.lfo_shape_layout_1.addStretch()
        self.lfo_shape_layout_1.addWidget(self.lfo_sah_button_1)
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
        self.lfo_phase_slider_2.setRange(0, 1000)
        self.lfo_freq_slider_2.setSingleStep(1)
        self.lfo_freq_slider_2.setSingleStep(1)

        #   buttons
        self.lfo_shape_buttons_2 = QButtonGroup()
        self.lfo_shape_layout_2 = QHBoxLayout()
        self.lfo_sin_button_2 = QRadioButton("sine")
        self.lfo_sin_button_2.setChecked(True)
        self.lfo_tri_button_2 = QRadioButton("tri")
        self.lfo_rmp_button_2 = QRadioButton("ramp")
        self.lfo_saw_button_2 = QRadioButton("saw")
        self.lfo_sqr_button_2 = QRadioButton("square")
        self.lfo_sah_button_2 = QRadioButton("s+h")
        self.lfo_shape_buttons_2.addButton(self.lfo_sin_button_2)
        self.lfo_shape_buttons_2.addButton(self.lfo_rmp_button_2)
        self.lfo_shape_buttons_2.addButton(self.lfo_tri_button_2)
        self.lfo_shape_buttons_2.addButton(self.lfo_saw_button_2)
        self.lfo_shape_buttons_2.addButton(self.lfo_sqr_button_2)
        self.lfo_shape_buttons_2.addButton(self.lfo_sah_button_2)

        self.lfo_shape_layout_2.addStretch()
        self.lfo_shape_layout_2.addWidget(self.lfo_sin_button_2)
        self.lfo_shape_layout_2.addStretch()
        self.lfo_shape_layout_2.addWidget(self.lfo_tri_button_2)
        self.lfo_shape_layout_2.addStretch()
        self.lfo_shape_layout_2.addWidget(self.lfo_rmp_button_2)
        self.lfo_shape_layout_2.addStretch()
        self.lfo_shape_layout_2.addWidget(self.lfo_saw_button_2)
        self.lfo_shape_layout_2.addStretch()
        self.lfo_shape_layout_2.addWidget(self.lfo_sqr_button_2)
        self.lfo_shape_layout_2.addStretch()
        self.lfo_shape_layout_2.addWidget(self.lfo_sah_button_2)
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
        self.menv_loop_button_1 = QRadioButton("Loop")
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
        self.menv_loop_button_2 = QRadioButton("Loop")
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

        #connect signals
        self.mod_buttons_group.buttonClicked.connect(self.setModule)
        # lfo 1
        self.lfo_freq_slider_1.valueChanged.connect(self.change_lfo1_freq)
        self.lfo_phase_slider_1.valueChanged.connect(self.change_lfo1_offset)
        self.lfo_shape_buttons_1.buttonClicked.connect(self.change_lfo1_shape)
        self.lfo_freq_display_1.double_clicked.connect(self.reset_lfo1_freq)
        self.lfo_phase_display_1.double_clicked.connect(self.reset_lfo1_offset)
        # lfo 2
        self.lfo_freq_slider_2.valueChanged.connect(self.change_lfo2_freq)
        self.lfo_phase_slider_2.valueChanged.connect(self.change_lfo2_offset)
        self.lfo_shape_buttons_2.buttonClicked.connect(self.change_lfo2_shape)
        self.lfo_freq_display_2.double_clicked.connect(self.reset_lfo2_freq)
        self.lfo_phase_display_2.double_clicked.connect(self.reset_lfo2_offset)
        # menv 1
        self.menv_att_slider_1.valueChanged.connect(self.change_menv1_att)
        self.menv_rel_slider_1.valueChanged.connect(self.change_menv1_rel)
        self.menv_mode_buttons_1.buttonClicked.connect(self.change_menv1_mode)
        self.menv_att_display_1.double_clicked.connect(self.reset_menv1_att)
        self.menv_rel_display_1.double_clicked.connect(self.reset_menv1_rel)
        # menv 2
        self.menv_att_slider_2.valueChanged.connect(self.change_menv2_att)
        self.menv_rel_slider_2.valueChanged.connect(self.change_menv2_rel)
        self.menv_mode_buttons_2.buttonClicked.connect(self.change_menv2_mode)
        self.menv_att_display_2.double_clicked.connect(self.reset_menv2_att)
        self.menv_rel_display_2.double_clicked.connect(self.reset_menv2_rel)
        

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

    #module slots
    # lfo 1
    def change_lfo1_freq(self, value):
        norm_value = float(value)/1000.0
        new_freq = norm_value*10.0
        self.lfo_freq_display_1.display(f"{new_freq:.2f}")
        self.lfo1_freq_changed.emit(new_freq)

    def change_lfo1_offset(self, value):
        norm_value = float(value)/1000.0
        self.lfo_phase_display_1.display(f"{norm_value:.2f}")
        self.lfo1_offset_changed.emit(norm_value)

    def change_lfo1_shape(self, button):
        shape_text = button.text()
        if shape_text == "sine":
            new_shape = 0
        elif shape_text == "tri":
            new_shape = 1
        elif shape_text == "ramp":
            new_shape = 2
        elif shape_text == "saw":
            new_shape = 3
        elif shape_text == "square":
            new_shape = 4
        elif shape_text == "s+h":
            new_shape = 5
        self.lfo1_shape_changed.emit(new_shape)
    
    def reset_lfo1_freq(self):
        self.lfo_freq_slider_1.setValue(500)

    def reset_lfo1_offset(self):
        self.lfo_phase_slider_1.setValue(0)

    # lfo 2
    def change_lfo2_freq(self, value):
        norm_value = float(value)/1000.0
        new_freq = norm_value*10.0
        self.lfo_freq_display_2.display(f"{new_freq:.2f}")
        self.lfo2_freq_changed.emit(new_freq)

    def change_lfo2_offset(self, value):
        norm_value = float(value)/1000.0
        self.lfo_phase_display_2.display(f"{norm_value:.2f}")
        self.lfo2_offset_changed.emit(norm_value)

    def change_lfo2_shape(self, button):
        shape_text = button.text()
        if shape_text == "sine":
            new_shape = 0
        elif shape_text == "tri":
            new_shape = 1
        elif shape_text == "ramp":
            new_shape = 2
        elif shape_text == "saw":
            new_shape = 3
        elif shape_text == "square":
            new_shape = 4
        elif shape_text == "s+h":
            new_shape = 5
        self.lfo2_shape_changed.emit(new_shape)
    
    def reset_lfo2_freq(self):
        self.lfo_freq_slider_2.setValue(500)

    def reset_lfo2_offset(self):
        self.lfo_phase_slider_2.setValue(0)

    # menv 1
    def change_menv1_att(self, value):
        norm_value = float(value)/1000.0
        self.menv_att_display_1.display(f"{norm_value:.2f}")
        self.menv1_att_changed.emit(norm_value)

    def change_menv1_rel(self, value):
        norm_value = float(value)/1000.0
        self.menv_rel_display_1.display(f"{norm_value:.2f}")
        self.menv1_rel_changed.emit(norm_value)

    def change_menv1_mode(self, button):
        mode_text = button.text()
        if mode_text == "AR":
            new_mode = 0
        elif mode_text == "AHR":
            new_mode = 1
        elif mode_text == "Loop":
            new_mode = 2
        self.menv1_mode_changed.emit(new_mode)

    def reset_menv1_att(self):
        self.menv_att_slider_1.setValue(500)

    def reset_menv1_rel(self):
        self.menv_rel_slider_1.setValue(500)
    
    # menv 2
    def change_menv2_att(self, value):
        norm_value = float(value)/1000.0
        self.menv_att_display_2.display(f"{norm_value:.2f}")
        self.menv2_att_changed.emit(norm_value)

    def change_menv2_rel(self, value):
        norm_value = float(value)/1000.0
        self.menv_rel_display_2.display(f"{norm_value:.2f}")
        self.menv2_rel_changed.emit(norm_value)

    def change_menv2_mode(self, button):
        mode_text = button.text()
        if mode_text == "AR":
            new_mode = 0
        elif mode_text == "AHR":
            new_mode = 1
        elif mode_text == "Loop":
            new_mode = 2
        self.menv2_mode_changed.emit(new_mode)

    def reset_menv2_att(self):
        self.menv_att_slider_2.setValue(500)

    def reset_menv2_rel(self):
        self.menv_rel_slider_2.setValue(500)

    #patch helpers
    def set_lfo1_shape(self, shape):
        if shape == "sine":
            new_shape = 0
            self.lfo_sin_button_1.setChecked(True)
        elif shape == "tri":
            new_shape = 1
            self.lfo_tri_button_1.setChecked(True)
        elif shape == "ramp":
            new_shape = 2
            self.lfo_rmp_button_1.setChecked(True)
        elif shape == "saw":
            new_shape = 3
            self.lfo_saw_button_1.setChecked(True)
        elif shape == "square":
            new_shape = 4
            self.lfo_sqr_button_1.setChecked(True)
        elif shape == "s+h":
            new_shape = 5
            self.lfo_sah_button_1.setChecked(True)
        self.lfo1_shape_changed.emit(new_shape)
    
    def set_lfo2_shape(self, shape):
        if shape == "sine":
            new_shape = 0
            self.lfo_sin_button_2.setChecked(True)
        elif shape == "tri":
            new_shape = 1
            self.lfo_tri_button_2.setChecked(True)
        elif shape == "ramp":
            new_shape = 2
            self.lfo_rmp_button_2.setChecked(True)
        elif shape == "saw":
            new_shape = 3
            self.lfo_saw_button_2.setChecked(True)
        elif shape == "square":
            new_shape = 4
            self.lfo_sqr_button_2.setChecked(True)
        elif shape == "s+h":
            new_shape = 5
            self.lfo_sah_button_2.setChecked(True)
        self.lfo2_shape_changed.emit(new_shape)

    def set_menv1_mode(self, mode):
        if mode == "AR":
            new_mode = 0
            self.menv_ar_button_1.setChecked(True)
        elif mode == "AHR":
            new_mode = 1
            self.menv_ahr_button_1.setChecked(True)
        elif mode == "Loop":
            new_mode = 2
            self.menv_loop_button_1.setChecked(True)
        self.menv1_mode_changed.emit(new_mode)

    def set_menv2_mode(self, mode):
        if mode == "AR":
            new_mode = 0
            self.menv_ar_button_2.setChecked(True)
        elif mode == "AHR":
            new_mode = 1
            self.menv_ahr_button_2.setChecked(True)
        elif mode == "Loop":
            new_mode = 2
            self.menv_loop_button_2.setChecked(True)
        self.menv2_mode_changed.emit(new_mode)

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

class CoolDial(QDial):
    mode_changed = Signal(str, int)
    value_changed = Signal(str, float)

    def __init__(self, step, min, max, name):
        super().__init__()
        self.mode = 0
        self.mode_colors = ["#BBBBBB", "#9ba4fa", "#a19bfa", "#ae9bfa", "#b69bfa"]
        self.max = max
        self.min = min
        self.name = name
        self.cursor_y_pos = 0
        self.cursor_y_pos_click = 0
        self.last_pressed = None
        self.setSingleStep(step)
        self.setRange(min, max)
        self.setValue((min+max)/2)
        self.valueChanged.connect(self.change_value)

    #normalize value to range (-1.0, 1.0) & emit
    def change_value(self, value):
        norm_value = float(value)/float(self.max)
        self.value_changed.emit(self.name, norm_value)

    #mode helpers (for patch save/load)
    def get_mode(self):
        return self.mode
    
    def set_mode(self, mode):
        self.mode = mode
        self.setStyleSheet("background-color:" + self.mode_colors[self.mode])
        self.mode_changed.emit(self.name, self.mode)

    #redraw QDial - circle w/ border & notch
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        bg_color = self.palette().color(QPalette.ColorRole.Window)
        painter.setBrush(bg_color)
        painter.setPen(QColor("white"))

        f_rect = QRectF(self.rect())
        e_rect = f_rect.adjusted(1, 1, -1, -1)
        painter.drawEllipse(e_rect)

        center = e_rect.center()
        painter.translate(center)
        rotation_deg = 120.0*(self.value()/self.max)
        painter.rotate(rotation_deg)
        radius = min(e_rect.width(), e_rect.height())/2.0 - 1
        notch_pen = QPen(QColor("black"))
        notch_pen.setWidth(1.2)
        #notch_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(notch_pen)

        notch = QLineF(0, 0, 0, -radius)
        painter.drawLine(notch)

        painter.end()

    #get cursor y pos
    def mousePressEvent(self, event):
        if (event.button() == Qt.MouseButton.LeftButton):
            self.cursor_y_pos = event.position().y()
            self.cursor_y_pos_click = self.cursor_y_pos
        self.last_pressed = event.button()
        event.accept()

    #cycle modes (wrap)
    def mouseReleaseEvent(self, event):
        if (event.button() == Qt.MouseButton.RightButton):
            if self.mode < 4:
                self.mode += 1
            else:
                self.mode = 0
            self.setStyleSheet("background-color:" + self.mode_colors[self.mode])
            self.mode_changed.emit(self.name, self.mode)
        event.accept()
    
    #single-axis knob movement (y, 1:1)
    def mouseMoveEvent(self, event):
        if (self.last_pressed == Qt.MouseButton.LeftButton):
            delta_y = self.cursor_y_pos - event.position().y()
            self.cursor_y_pos = event.position().y()
            new_value = self.value() + int(delta_y)
            self.setValue(new_value)
        event.accept()

    def mouseDoubleClickEvent(self, event):
        if (event.button() == Qt.MouseButton.LeftButton):
            self.setValue(0)
        event.accept()

        

