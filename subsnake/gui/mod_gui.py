from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGroupBox, QGridLayout, QSlider,
    QStackedLayout, QPushButton,
    QRadioButton, QButtonGroup,
    QWidget
)

class ModulatorGUI(QGroupBox):
    def __init__(self):
        super().__init__()

        layout = QGridLayout()
        self.lfo_group_1 = QGroupBox("lfo 1")
        self.lfo_group_2 = QGroupBox("lfo 2")
        self.menv_group_1 = QGroupBox("env 1")
        self.menv_group_2 = QGroupBox("env 2")

        lfo_layout_1 = QGridLayout()
        lfo_layout_2 = QGridLayout()
        menv_layout_1 = QGridLayout()
        menv_layout_2 = QGridLayout()
        mod_stack = QStackedLayout()
        mod_widget = QWidget()

        self.lfo_group_1.setLayout(lfo_layout_1)
        self.lfo_group_2.setLayout(lfo_layout_2)
        self.menv_group_1.setLayout(menv_layout_1)
        self.menv_group_2.setLayout(menv_layout_2)

        mod_stack.addWidget(self.lfo_group_1)
        mod_stack.addWidget(self.lfo_group_2)
        mod_stack.addWidget(self.menv_group_1)
        mod_stack.addWidget(self.menv_group_2)

        mod_widget.setLayout(mod_stack)
        layout.addWidget(mod_widget, 0, 0)
        
        self.setLayout(layout)
        self.setObjectName("mod_group")
        self.setTitle("modulators")
