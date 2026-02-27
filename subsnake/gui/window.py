from subsnake.gui.keys import Keys
from subsnake.gui.osc_gui import OscillatorGUI
from subsnake.gui.osc2_gui import Oscillator2GUI
from subsnake.gui.osc3_gui import Oscillator3GUI
from subsnake.gui.filt_gui import FilterGUI
from subsnake.gui.env_gui import EnvelopeGUI
from subsnake.gui.fenv_gui import FilterEnvGUI
from subsnake.gui.midi import MIDISettings
from subsnake.gui.settings import SynthSettings, RecorderSettings
from subsnake.gui.gui_timer import UpdateGUI
from subsnake.gui.delay_gui import DelayGUI
from subsnake.gui.patch import PatchManager
from subsnake.gui.record import RecorderGUI
from subsnake.gui.mod_gui import ModulatorGUI
from subsnake.gui.scope_gui import ScopeGUI
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QMainWindow, QGridLayout,
    QFrame, QWidget, QGraphicsDropShadowEffect,
    QPushButton, QHBoxLayout, 
    QStackedLayout, QButtonGroup, QGroupBox)
from importlib import resources

key_conv = Keys()

class MainWindow(QMainWindow):

    def __init__(self, engine):
        super().__init__()
        #set window title
        self.setWindowTitle("subsnake")

        #attributes
        self.param_sliders = {}
        self.mod_dials = {}
        self.param_button_groups = []
        self.midi_controls = []
        self.midi_cc_sliders = {}
        self.midi_cc_displays = {}
        self.cc_rows = 0
        self.engine = engine
        self.display_color = QColor("black")
        self.key_to_note = {}
        self.osc_drop_shadow = self.configure_drop_shadow(QGraphicsDropShadowEffect(), QColor("#1c0627"))
        self.osc2_drop_shadow = self.configure_drop_shadow(QGraphicsDropShadowEffect(), QColor("#1c0627"))
        self.osc3_drop_shadow = self.configure_drop_shadow(QGraphicsDropShadowEffect(), QColor("#1c0627"))
        self.filt_drop_shadow = self.configure_drop_shadow(QGraphicsDropShadowEffect(), QColor("#1c0627"))
        self.fenv_drop_shadow = self.configure_drop_shadow(QGraphicsDropShadowEffect(), QColor("#1c0627"))
        self.env_drop_shadow = self.configure_drop_shadow(QGraphicsDropShadowEffect(), QColor("#1c0627"))
        self.del_drop_shadow = self.configure_drop_shadow(QGraphicsDropShadowEffect(), QColor("#1c0627"))
        self.mod_drop_shadow = self.configure_drop_shadow(QGraphicsDropShadowEffect(), QColor("#1c0627"))
        self.settings_drop_shadow = self.configure_drop_shadow(QGraphicsDropShadowEffect(), QColor("#1c0627"))
        self.options_drop_shadow = self.configure_drop_shadow(QGraphicsDropShadowEffect(), QColor("#1c0627"))
        self.patch_drop_shadow = self.configure_drop_shadow(QGraphicsDropShadowEffect(), QColor("#1c0627"))
        self.record_drop_shadow = self.configure_drop_shadow(QGraphicsDropShadowEffect(), QColor("#1c0627"))

        #toolbar
        self.patch_manager = PatchManager(self.param_sliders, self.param_button_groups, self.mod_dials)
        self.recorder = RecorderGUI()
        settings_layout = QHBoxLayout()
        self.settings_group = QGroupBox("settings")
        self.settings_group.setAttribute(Qt.WA_StyledBackground, True)

        self.toggle_dark = QPushButton("dark")
        self.toggle_dark.setCheckable(True)
        self.toggle_dark.setChecked(False)
        self.toggle_midi = QPushButton("midi")
        self.toggle_midi.setCheckable(True)
        self.toggle_midi.setChecked(True)
        self.toggle_synth = QPushButton("synth")
        self.toggle_synth.setCheckable(True)
        self.toggle_synth.setChecked(False)
        self.toggle_record = QPushButton("record")
        self.toggle_record.setCheckable(True)
        self.toggle_record.setChecked(False)
        self.toggle_scope = QPushButton("scope")
        self.toggle_scope.setCheckable(True)
        self.toggle_scope.setChecked(False)

        settings_layout.addWidget(self.toggle_dark)
        settings_layout.addWidget(self.toggle_midi)
        settings_layout.addWidget(self.toggle_synth)
        settings_layout.addWidget(self.toggle_record)
        settings_layout.addWidget(self.toggle_scope)
        self.settings_group.setLayout(settings_layout)

        self.toggle_dark.setObjectName("toggle_dark")
        self.toggle_midi.setObjectName("toggle_midi")
        self.toggle_synth.setObjectName("toggle_synth")
        self.toggle_record.setObjectName("toggle_record")
        self.toggle_scope.setObjectName("toggle_scope")

        self.toggle_button_group = QButtonGroup()
        self.toggle_button_group.addButton(self.toggle_midi)
        self.toggle_button_group.addButton(self.toggle_synth)
        self.toggle_button_group.addButton(self.toggle_record)
        self.toggle_button_group.addButton(self.toggle_scope)

        #layouts
        self.window_grid = QGridLayout()

        #settings widgets
        self.midi_group = MIDISettings()
        self.midi_group.setFocusPolicy(Qt.NoFocus)

        self.synth_group = SynthSettings()
        self.synth_group.setFocusPolicy(Qt.NoFocus)

        self.record_group = RecorderSettings()
        self.record_group.setFocusPolicy(Qt.NoFocus)

        self.scope_group = ScopeGUI(self.engine.scope_mutex, self.engine.scope_buffer, self.engine.scope_frames)
        self.scope_group.setFocusPolicy(Qt.NoFocus)

        self.settings_view = QWidget()
        self.settings_stack = QStackedLayout()
        self.settings_stack.addWidget(self.midi_group)
        self.settings_stack.addWidget(self.synth_group)
        self.settings_stack.addWidget(self.record_group)
        self.settings_stack.addWidget(self.scope_group)
        self.settings_stack.setCurrentIndex(0)
        self.settings_view.setLayout(self.settings_stack)

        #module GUIs
        self.filt_group = FilterGUI(self.display_color)
        self.osc_group = OscillatorGUI(self.display_color)
        self.osc2_group = Oscillator2GUI(self.display_color)
        self.osc3_group = Oscillator3GUI(self.display_color)
        self.env_group = EnvelopeGUI(self.display_color)
        self.fenv_group = FilterEnvGUI(self.display_color)
        self.del_group = DelayGUI(self.display_color)
        self.mod_group = ModulatorGUI(self.display_color)

        #module drop shadows
        self.osc_group.setGraphicsEffect(self.osc_drop_shadow)
        self.osc2_group.setGraphicsEffect(self.osc2_drop_shadow)
        self.osc3_group.setGraphicsEffect(self.osc3_drop_shadow)
        self.filt_group.setGraphicsEffect(self.filt_drop_shadow)
        self.env_group.setGraphicsEffect(self.env_drop_shadow)
        self.fenv_group.setGraphicsEffect(self.fenv_drop_shadow)
        self.del_group.setGraphicsEffect(self.del_drop_shadow)
        self.mod_group.setGraphicsEffect(self.mod_drop_shadow)
        self.settings_view.setGraphicsEffect(self.settings_drop_shadow)
        self.settings_group.setGraphicsEffect(self.options_drop_shadow)
        self.patch_manager.setGraphicsEffect(self.patch_drop_shadow)
        self.recorder.setGraphicsEffect(self.record_drop_shadow)

        #init slider, button group & mod dial dictionaries
        self.init_sliders_dict()
        self.init_buttons_dict()
        self.init_mod_dials_dict()

        #grid spacers
        # row 0
        self.grid_space_0 = QFrame()
        self.grid_space_0.setFrameShape(QFrame.NoFrame)
        self.grid_space_1 = QFrame()
        self.grid_space_1.setFrameShape(QFrame.NoFrame)
        self.grid_space_2 = QFrame()
        self.grid_space_2.setFrameShape(QFrame.NoFrame)
        self.grid_space_3 = QFrame()
        self.grid_space_3.setFrameShape(QFrame.NoFrame)

        #object names
        self.grid_space_0.setObjectName("grid_space")
        self.grid_space_1.setObjectName("grid_space")
        self.grid_space_2.setObjectName("grid_space")
        self.grid_space_3.setObjectName("grid_space")

        #add modules/settings groups to window
        self.window_grid.addWidget(self.grid_space_2, 0, 0)
        self.window_grid.addWidget(self.grid_space_0, 0, 2)
        self.window_grid.addWidget(self.grid_space_1, 0, 4)
        self.window_grid.addWidget(self.grid_space_3, 0, 6)

        self.window_grid.addWidget(self.settings_group, 0, 1)
        self.window_grid.addWidget(self.patch_manager, 0, 3)
        self.window_grid.addWidget(self.recorder, 0, 5)

        self.window_grid.addWidget(self.osc_group, 1, 1)
        self.window_grid.addWidget(self.filt_group, 1, 3)
        self.window_grid.addWidget(self.env_group, 1, 5)

        self.window_grid.addWidget(self.osc2_group, 2, 1)
        self.window_grid.addWidget(self.fenv_group, 2, 3)
        self.window_grid.addWidget(self.del_group, 2, 5)

        self.window_grid.addWidget(self.osc3_group, 3, 1)
        self.window_grid.addWidget(self.mod_group, 3, 3)
        self.window_grid.addWidget(self.settings_view, 3, 5)

        #set layout of window
        window_widget = QWidget()
        window_widget.setLayout(self.window_grid)

        #connect signals
        # recorder
        self.recorder.delete.connect(self.update_rec_delete)
        self.recorder.record.connect(self.update_rec_record)
        self.recorder.play.connect(self.update_rec_play)
        self.recorder.pause.connect(self.update_rec_pause)
        self.recorder.stop.connect(self.update_rec_stop)
        self.recorder.loop.connect(self.update_rec_loop)
        self.record_group.save_rec_buffer.connect(self.save_rec_buffer)

        # midi
        self.midi_group.input_changed.connect(self.update_midi_in)
        self.midi_group.channel_changed.connect(self.update_midi_ch)
        self.midi_group.inputs_refreshed.connect(self.refresh_midi_ins)
        self.midi_group.cc_added.connect(self.add_cc)
        self.midi_group.cc_changed.connect(self.update_cc)
        self.midi_group.cc_param_changed.connect(self.update_param)
        self.midi_group.cc_deleted.connect(self.delete_cc)

        # settings
        self.toggle_button_group.buttonClicked.connect(self.update_active_settings)
        self.toggle_dark.toggled.connect(self.update_dark_mode)

        # filter
        self.filt_group.freq_changed.connect(self.update_filt_freq)
        self.filt_group.res_changed.connect(self.update_filt_res)
        self.filt_group.drive_changed.connect(self.update_filt_drive)
        self.filt_group.sat_changed.connect(self.update_filt_sat)
        self.filt_group.alg_changed.connect(self.update_filt_alg)

        # oscillators
        #  1
        self.osc_group.pitch_changed.connect(self.update_osc_freq)
        self.osc_group.level_changed.connect(self.update_osc_amp)
        self.osc_group.width_changed.connect(self.update_osc_width)
        self.osc_group.alg_changed.connect(self.update_osc_alg)
        self.osc_group.type_changed.connect(self.update_osc_type)
        #  2
        self.osc2_group.pitch_changed.connect(self.update_osc2_freq)
        self.osc2_group.detune_changed.connect(self.update_osc2_det)
        self.osc2_group.level_changed.connect(self.update_osc2_amp)
        self.osc2_group.width_changed.connect(self.update_osc2_width)
        self.osc2_group.alg_changed.connect(self.update_osc2_alg)
        self.osc2_group.type_changed.connect(self.update_osc_type)
        #  3
        self.osc3_group.pitch_changed.connect(self.update_osc3_freq)
        self.osc3_group.detune_changed.connect(self.update_osc3_det)
        self.osc3_group.level_changed.connect(self.update_osc3_amp)
        self.osc3_group.width_changed.connect(self.update_osc3_width)
        self.osc3_group.alg_changed.connect(self.update_osc3_alg)
        self.osc3_group.type_changed.connect(self.update_osc_type)
        # envelope
        self.env_group.attack_changed.connect(self.update_env_attack)
        self.env_group.decay_changed.connect(self.update_env_decay)
        self.env_group.sustain_changed.connect(self.update_env_sustain)
        self.env_group.release_changed.connect(self.update_env_release)
        self.env_group.gate_changed.connect(self.update_env_gate)

        # filter envelope
        self.fenv_group.attack_changed.connect(self.update_fenv_attack)
        self.fenv_group.decay_changed.connect(self.update_fenv_decay)
        self.fenv_group.sustain_changed.connect(self.update_fenv_sustain)
        self.fenv_group.release_changed.connect(self.update_fenv_release)
        self.fenv_group.amount_changed.connect(self.update_fenv_amount)

        # delay
        self.del_group.time_changed.connect(self.update_del_time)
        self.del_group.feedback_changed.connect(self.update_del_feedback)
        self.del_group.mix_changed.connect(self.update_del_mix)

        # modulators
        #  values
        #   oscillator 1
        self.osc_group.osc_freq_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.osc_group.osc_amp_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.osc_group.osc_width_mod_dial.value_changed.connect(self.update_mod_dial_value)
        #   oscillator 2
        self.osc2_group.osc2_freq_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.osc2_group.osc2_det_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.osc2_group.osc2_amp_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.osc2_group.osc2_width_mod_dial.value_changed.connect(self.update_mod_dial_value)
        #   oscillator 3
        self.osc3_group.osc3_freq_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.osc3_group.osc3_det_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.osc3_group.osc3_amp_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.osc3_group.osc3_width_mod_dial.value_changed.connect(self.update_mod_dial_value)
        #   filter
        self.filt_group.filt_freq_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.filt_group.filt_res_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.filt_group.filt_drive_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.filt_group.filt_sat_mod_dial.value_changed.connect(self.update_mod_dial_value)
        #   filter envelope
        self.fenv_group.fenv_att_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.fenv_group.fenv_dec_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.fenv_group.fenv_sus_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.fenv_group.fenv_rel_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.fenv_group.fenv_amt_mod_dial.value_changed.connect(self.update_mod_dial_value)
        #   envelope
        self.env_group.env_att_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.env_group.env_dec_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.env_group.env_sus_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.env_group.env_rel_mod_dial.value_changed.connect(self.update_mod_dial_value)
        #   delay
        self.del_group.del_time_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.del_group.del_feedback_mod_dial.value_changed.connect(self.update_mod_dial_value)
        self.del_group.del_mix_mod_dial.value_changed.connect(self.update_mod_dial_value)
        #   lfo1
        self.mod_group.lfo_freq_mod_dial_1.value_changed.connect(self.update_mod_dial_value)
        self.mod_group.lfo_phase_mod_dial_1.value_changed.connect(self.update_mod_dial_value)
        #   lfo2
        self.mod_group.lfo_freq_mod_dial_2.value_changed.connect(self.update_mod_dial_value)
        self.mod_group.lfo_phase_mod_dial_2.value_changed.connect(self.update_mod_dial_value)
        #   menv1
        self.mod_group.menv_att_mod_dial_1.value_changed.connect(self.update_mod_dial_value)
        self.mod_group.menv_rel_mod_dial_1.value_changed.connect(self.update_mod_dial_value)
        #   menv2
        self.mod_group.menv_att_mod_dial_2.value_changed.connect(self.update_mod_dial_value)
        self.mod_group.menv_rel_mod_dial_2.value_changed.connect(self.update_mod_dial_value)

        #  modes
        #   oscillator 1
        self.osc_group.osc_freq_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.osc_group.osc_amp_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.osc_group.osc_width_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        #   oscillator 2
        self.osc2_group.osc2_freq_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.osc2_group.osc2_det_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.osc2_group.osc2_amp_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.osc2_group.osc2_width_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        #   oscillator 3
        self.osc3_group.osc3_freq_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.osc3_group.osc3_det_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.osc3_group.osc3_amp_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.osc3_group.osc3_width_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        #   filter
        self.filt_group.filt_freq_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.filt_group.filt_res_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.filt_group.filt_drive_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.filt_group.filt_sat_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        #   filter envelope
        self.fenv_group.fenv_att_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.fenv_group.fenv_dec_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.fenv_group.fenv_sus_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.fenv_group.fenv_rel_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.fenv_group.fenv_amt_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        #   envelope
        self.env_group.env_att_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.env_group.env_dec_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.env_group.env_sus_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.env_group.env_rel_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        #   delay
        self.del_group.del_time_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.del_group.del_feedback_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        self.del_group.del_mix_mod_dial.mode_changed.connect(self.update_mod_dial_mode)
        #   lfo1
        self.mod_group.lfo_freq_mod_dial_1.mode_changed.connect(self.update_mod_dial_mode)
        self.mod_group.lfo_phase_mod_dial_1.mode_changed.connect(self.update_mod_dial_mode)
        #   lfo2
        self.mod_group.lfo_freq_mod_dial_2.mode_changed.connect(self.update_mod_dial_mode)
        self.mod_group.lfo_phase_mod_dial_2.mode_changed.connect(self.update_mod_dial_mode)
        #   menv1
        self.mod_group.menv_att_mod_dial_1.mode_changed.connect(self.update_mod_dial_mode)
        self.mod_group.menv_rel_mod_dial_1.mode_changed.connect(self.update_mod_dial_mode)
        #   menv2
        self.mod_group.menv_att_mod_dial_2.mode_changed.connect(self.update_mod_dial_mode)
        self.mod_group.menv_rel_mod_dial_2.mode_changed.connect(self.update_mod_dial_mode)

        #   modulation
        #    lfo 1
        self.mod_group.lfo1_freq_changed.connect(self.update_lfo1_freq)
        self.mod_group.lfo1_offset_changed.connect(self.update_lfo1_offset)
        self.mod_group.lfo1_shape_changed.connect(self.update_lfo1_shape)
        #    lfo 2
        self.mod_group.lfo2_freq_changed.connect(self.update_lfo2_freq)
        self.mod_group.lfo2_offset_changed.connect(self.update_lfo2_offset)
        self.mod_group.lfo2_shape_changed.connect(self.update_lfo2_shape)
        #    menv 1
        self.mod_group.menv1_att_changed.connect(self.update_menv1_att)
        self.mod_group.menv1_rel_changed.connect(self.update_menv1_rel)
        self.mod_group.menv1_mode_changed.connect(self.update_menv1_mode)
        #    menv 2
        self.mod_group.menv2_att_changed.connect(self.update_menv2_att)
        self.mod_group.menv2_rel_changed.connect(self.update_menv2_rel)
        self.mod_group.menv2_mode_changed.connect(self.update_menv2_mode)

        # patch select
        self.patch_manager.patch_loaded.connect(self.load_patch)

        # synth settings
        self.synth_group.drift_changed.connect(self.update_osc_drift)
        self.synth_group.key_tracking_changed.connect(self.update_key_tracking)

        self.setCentralWidget(window_widget)

        #load stylesheets
        light_style_file = resources.files() / 'window.qss'
        self.light_style = light_style_file.read_text(encoding='utf-8')
        dark_style_file = resources.files() / 'window_dark.qss'
        self.dark_style = dark_style_file.read_text(encoding='utf-8')
        self.setStyleSheet(self.light_style)

        #start slider cc update timer
        self.slider_timer = UpdateGUI(self.engine, self)
        self.slider_timer.start()

        self.patch_manager.load_patch(self.patch_manager.patch_select.currentText())

    #helper functions
    # args: QLCDDisplay widget, # of digits, mode (hex, dec, oct, bin),
    # dig_style (outline, filled, flat), small decimal flag (for floats)
    def configure_display(self, display, num_digits, num_mode, dig_style, small_dec):
        display.setMode(num_mode)
        display.setDigitCount(num_digits)
        display.setSegmentStyle(dig_style)
        display.setSmallDecimalPoint(small_dec)
        return display
    
    def configure_drop_shadow(self, drop_shadow, color):
        drop_shadow.setColor(color)
        drop_shadow.setBlurRadius(12)
        drop_shadow.setXOffset(3)
        drop_shadow.setYOffset(3)
        return drop_shadow
    
    def update_drop_shadow_colors(self, color):
        self.osc_drop_shadow.setColor(color)
        self.osc2_drop_shadow.setColor(color)
        self.osc3_drop_shadow.setColor(color)
        self.filt_drop_shadow.setColor(color)
        self.fenv_drop_shadow.setColor(color)
        self.env_drop_shadow.setColor(color)
        self.del_drop_shadow.setColor(color)
        self.mod_drop_shadow.setColor(color)
        self.settings_drop_shadow.setColor(color)
        self.options_drop_shadow.setColor(color)
        self.patch_drop_shadow.setColor(color)
        self.record_drop_shadow.setColor(color)
    
    def init_sliders_dict(self):
        self.param_sliders.update({"osc_drift": self.synth_group.drift_slider})
        self.param_sliders.update({"osc_freq": self.osc_group.osc_freq_slider})
        self.param_sliders.update({"osc_amp": self.osc_group.osc_amp_slider})
        self.param_sliders.update({"osc_width": self.osc_group.osc_width_slider})

        self.param_sliders.update({"osc2_freq": self.osc2_group.osc2_freq_slider})
        self.param_sliders.update({"osc2_det": self.osc2_group.osc2_det_slider})
        self.param_sliders.update({"osc2_amp": self.osc2_group.osc2_amp_slider})
        self.param_sliders.update({"osc2_width": self.osc2_group.osc2_width_slider})

        self.param_sliders.update({"osc3_freq": self.osc3_group.osc3_freq_slider})
        self.param_sliders.update({"osc3_det": self.osc3_group.osc3_det_slider})
        self.param_sliders.update({"osc3_amp": self.osc3_group.osc3_amp_slider})
        self.param_sliders.update({"osc3_width": self.osc3_group.osc3_width_slider})

        self.param_sliders.update({"filt_freq": self.filt_group.filt_freq_slider})
        self.param_sliders.update({"filt_res": self.filt_group.filt_res_slider})
        self.param_sliders.update({"filt_drive": self.filt_group.filt_drive_slider})
        self.param_sliders.update({"filt_sat": self.filt_group.filt_sat_slider})
        self.param_sliders.update({"filt_track": self.synth_group.key_tracking_slider})

        self.param_sliders.update({"fenv_att": self.fenv_group.fenv_att_slider})
        self.param_sliders.update({"fenv_dec": self.fenv_group.fenv_dec_slider})
        self.param_sliders.update({"fenv_sus": self.fenv_group.fenv_sus_slider})
        self.param_sliders.update({"fenv_rel": self.fenv_group.fenv_rel_slider})
        self.param_sliders.update({"fenv_amt": self.fenv_group.fenv_amt_slider})

        self.param_sliders.update({"env_att": self.env_group.adsr_att_slider})
        self.param_sliders.update({"env_dec": self.env_group.adsr_dec_slider})
        self.param_sliders.update({"env_sus": self.env_group.adsr_sus_slider})
        self.param_sliders.update({"env_rel": self.env_group.adsr_rel_slider})

        self.param_sliders.update({"del_time": self.del_group.del_time_slider})
        self.param_sliders.update({"del_fback": self.del_group.del_feedback_slider})
        self.param_sliders.update({"del_mix": self.del_group.del_mix_slider})

        self.param_sliders.update({"lfo1_freq": self.mod_group.lfo_freq_slider_1})
        self.param_sliders.update({"lfo1_phase": self.mod_group.lfo_phase_slider_1})

        self.param_sliders.update({"lfo2_freq": self.mod_group.lfo_freq_slider_2})
        self.param_sliders.update({"lfo2_phase": self.mod_group.lfo_phase_slider_2})

        self.param_sliders.update({"menv1_att": self.mod_group.menv_att_slider_1})
        self.param_sliders.update({"menv1_rel": self.mod_group.menv_rel_slider_1})

        self.param_sliders.update({"menv2_att": self.mod_group.menv_att_slider_2})
        self.param_sliders.update({"menv2_rel": self.mod_group.menv_rel_slider_2})
    
    def init_buttons_dict(self):
        self.param_button_groups.append(self.osc_group.osc_alg_group)
        self.param_button_groups.append(self.osc2_group.osc2_alg_group)
        self.param_button_groups.append(self.osc3_group.osc3_alg_group)
        self.param_button_groups.append(self.filt_group.filt_alg_group)
        self.param_button_groups.append(self.mod_group.lfo_shape_buttons_1)
        self.param_button_groups.append(self.mod_group.lfo_shape_buttons_2)
        self.param_button_groups.append(self.mod_group.menv_mode_buttons_1)
        self.param_button_groups.append(self.mod_group.menv_mode_buttons_2)

    def init_mod_dials_dict(self):
        self.mod_dials.update({"osc_freq": self.osc_group.osc_freq_mod_dial})
        self.mod_dials.update({"osc_amp": self.osc_group.osc_amp_mod_dial})
        self.mod_dials.update({"osc_width": self.osc_group.osc_width_mod_dial})

        self.mod_dials.update({"osc2_freq": self.osc2_group.osc2_freq_mod_dial})
        self.mod_dials.update({"osc2_det": self.osc2_group.osc2_det_mod_dial})
        self.mod_dials.update({"osc2_amp": self.osc2_group.osc2_amp_mod_dial})
        self.mod_dials.update({"osc2_width": self.osc2_group.osc2_width_mod_dial})

        self.mod_dials.update({"osc3_freq": self.osc3_group.osc3_freq_mod_dial})
        self.mod_dials.update({"osc3_det": self.osc3_group.osc3_det_mod_dial})
        self.mod_dials.update({"osc3_amp": self.osc3_group.osc3_amp_mod_dial})
        self.mod_dials.update({"osc3_width": self.osc3_group.osc3_width_mod_dial})

        self.mod_dials.update({"filt_freq": self.filt_group.filt_freq_mod_dial})
        self.mod_dials.update({"filt_res": self.filt_group.filt_res_mod_dial})
        self.mod_dials.update({"filt_drive": self.filt_group.filt_drive_mod_dial})
        self.mod_dials.update({"filt_sat": self.filt_group.filt_sat_mod_dial})

        self.mod_dials.update({"fenv_att": self.fenv_group.fenv_att_mod_dial})
        self.mod_dials.update({"fenv_dec": self.fenv_group.fenv_dec_mod_dial})
        self.mod_dials.update({"fenv_sus": self.fenv_group.fenv_sus_mod_dial})
        self.mod_dials.update({"fenv_rel": self.fenv_group.fenv_rel_mod_dial})
        self.mod_dials.update({"fenv_amt": self.fenv_group.fenv_amt_mod_dial})

        self.mod_dials.update({"env_att": self.env_group.env_att_mod_dial})
        self.mod_dials.update({"env_dec": self.env_group.env_dec_mod_dial})
        self.mod_dials.update({"env_sus": self.env_group.env_sus_mod_dial})
        self.mod_dials.update({"env_rel": self.env_group.env_rel_mod_dial})

        self.mod_dials.update({"del_time": self.del_group.del_time_mod_dial})
        self.mod_dials.update({"del_fback": self.del_group.del_feedback_mod_dial})
        self.mod_dials.update({"del_mix": self.del_group.del_mix_mod_dial})

        self.mod_dials.update({"lfo1_freq": self.mod_group.lfo_freq_mod_dial_1})
        self.mod_dials.update({"lfo1_phase": self.mod_group.lfo_phase_mod_dial_1})

        self.mod_dials.update({"lfo2_freq": self.mod_group.lfo_freq_mod_dial_2})
        self.mod_dials.update({"lfo2_phase": self.mod_group.lfo_phase_mod_dial_2})

        self.mod_dials.update({"menv1_att": self.mod_group.menv_att_mod_dial_1})
        self.mod_dials.update({"menv1_rel": self.mod_group.menv_rel_mod_dial_1})

        self.mod_dials.update({"menv2_att": self.mod_group.menv_att_mod_dial_2})
        self.mod_dials.update({"menv2_rel": self.mod_group.menv_rel_mod_dial_2})
        

    def load_patch(self, patch):
        for param in patch:
            if param in self.param_sliders:
                self.param_sliders[param].setValue(patch[param])
                self.param_sliders[param].valueChanged.emit(patch[param])
            elif param == "osc_wave":
                self.osc_group.update_wave(patch[param])
            elif param == "osc2_wave":
                self.osc2_group.update_wave(patch[param])
            elif param == "osc3_wave":
                self.osc3_group.update_wave(patch[param])
            elif param == "filt_type":
                self.filt_group.update_type(patch[param])
            elif param == "lfo1_shape":
                self.mod_group.set_lfo1_shape(patch[param])
            elif param == "lfo2_shape":
                self.mod_group.set_lfo2_shape(patch[param])
            elif param == "menv1_mode":
                self.mod_group.set_menv1_mode(patch[param])
            elif param == "menv2_mode":
                self.mod_group.set_menv2_mode(patch[param])
            elif param.endswith("_mod"):
                norm_param = param.removesuffix("_mod")
                self.mod_dials[norm_param].setValue(patch[param])
            elif param.endswith("_ass"):
                norm_param = param.removesuffix("_ass")
                self.mod_dials[norm_param].set_mode(patch[param])


    def assign_cc_function(self, module, param):
        cc_function = None
        if (module == "oscillator 1"):
            if (param == "pitch"):
                cc_function = self.engine.cc_change_pitch_1
            elif (param == "level"):
                cc_function = self.engine.cc_change_level_1
            elif (param == "width"):
                cc_function = self.engine.cc_change_width_1
        elif (module == "oscillator 2"):
            if (param == "pitch"):
                cc_function = self.engine.cc_change_pitch_2
            elif (param == "detune"):
                cc_function = self.engine.cc_change_detune_2
            elif (param == "level"):
                cc_function = self.engine.cc_change_level_2
            elif (param == "width"):
                cc_function = self.engine.cc_change_width_2
        elif (module == "oscillator 3"):
            if (param == "pitch"):
                cc_function = self.engine.cc_change_pitch_3
            elif (param == "detune"):
                cc_function = self.engine.cc_change_detune_3
            elif (param == "level"):
                cc_function = self.engine.cc_change_level_3
            elif (param == "width"):
                cc_function = self.engine.cc_change_width_3
        elif (module == "filter"):
            if (param == "cutoff"):
                cc_function = self.engine.cc_change_cutoff
            elif (param == "feedback"):
                cc_function = self.engine.cc_change_resonance
            elif (param == "drive"):
                cc_function = self.engine.cc_change_drive
            elif (param == "saturate"):
                cc_function = self.engine.cc_change_saturate
        elif (module == "filter env"):
            if (param == "attack"):
                cc_function = self.engine.cc_change_fenv_attack
            elif (param == "decay"):
                cc_function = self.engine.cc_change_fenv_decay
            elif (param == "sustain"):
                cc_function = self.engine.cc_change_fenv_sustain
            elif (param == "release"):
                cc_function = self.engine.cc_change_fenv_release
            elif (param == "depth"):
                cc_function = self.engine.cc_change_fenv_amount
        elif (module == "envelope"):
            if (param == "attack"):
                cc_function = self.engine.cc_change_env_attack
            elif (param == "decay"):
                cc_function = self.engine.cc_change_env_decay
            elif (param == "sustain"):
                cc_function = self.engine.cc_change_env_sustain
            elif (param == "release"):
                cc_function = self.engine.cc_change_env_release
        elif (module == "delay"):
            if (param == "time"):
                cc_function = self.engine.cc_change_del_time
            elif (param == "feedback"):
                cc_function = self.engine.cc_change_del_feedback
            elif (param == "mix"):
                cc_function = self.engine.cc_change_del_mix
        elif (module == "lfo 1"):
            if (param == "speed"):
                cc_function = self.engine.cc_change_lfo1_speed
            elif (param == "phase"):
                cc_function = self.engine.cc_change_lfo1_phase
        elif (module == "lfo 2"):
            if (param == "speed"):
                cc_function = self.engine.cc_change_lfo2_speed
            elif (param == "phase"):
                cc_function = self.engine.cc_change_lfo2_phase
        elif (module == "menv 1"):
            if (param == "attack"):
                cc_function = self.engine.cc_change_menv1_attack
            elif (param == "release"):
                cc_function = self.engine.cc_change_menv1_release
        elif (module == "menv 2"):
            if (param == "attack"):
                cc_function = self.engine.cc_change_menv2_attack
            elif (param == "release"):
                cc_function = self.engine.cc_change_menv2_release
        return cc_function
    
    def set_palette(self, display):
        text_color = self.display_color
        display_palette = display.palette()
        display_palette.setColor(QPalette.ColorRole.WindowText, text_color)
        display.setAutoFillBackground(False)
        display.setPalette(display_palette)
    
    def set_display_colors(self):
        #osc 1
        self.set_palette(self.osc_group.osc_freq_display)
        self.set_palette(self.osc_group.osc_amp_display)
        self.set_palette(self.osc_group.osc_width_display)
        #osc 2
        self.set_palette(self.osc2_group.osc2_freq_display)
        self.set_palette(self.osc2_group.osc2_det_display)
        self.set_palette(self.osc2_group.osc2_amp_display)
        self.set_palette(self.osc2_group.osc2_width_display)
        #osc 3
        self.set_palette(self.osc3_group.osc3_freq_display)
        self.set_palette(self.osc3_group.osc3_det_display)
        self.set_palette(self.osc3_group.osc3_amp_display)
        self.set_palette(self.osc3_group.osc3_width_display)
        #filter
        self.set_palette(self.filt_group.filt_freq_display)
        self.set_palette(self.filt_group.filt_fback_display)
        self.set_palette(self.filt_group.filt_drive_display)
        self.set_palette(self.filt_group.filt_sat_display)
        #filter envelope
        self.set_palette(self.fenv_group.fenv_att_display)
        self.set_palette(self.fenv_group.fenv_dec_display)
        self.set_palette(self.fenv_group.fenv_sus_display)
        self.set_palette(self.fenv_group.fenv_rel_display)
        self.set_palette(self.fenv_group.fenv_amt_display)
        #amp envelope
        self.set_palette(self.env_group.adsr_att_display)
        self.set_palette(self.env_group.adsr_dec_display)
        self.set_palette(self.env_group.adsr_sus_display)
        self.set_palette(self.env_group.adsr_rel_display)
        #delay
        self.set_palette(self.del_group.del_time_display)
        self.set_palette(self.del_group.del_feedback_display)
        self.set_palette(self.del_group.del_mix_display)
        #lfos
        self.set_palette(self.mod_group.lfo_freq_display_1)
        self.set_palette(self.mod_group.lfo_freq_display_2)
        self.set_palette(self.mod_group.lfo_phase_display_1)
        self.set_palette(self.mod_group.lfo_phase_display_2)
        #menvs
        self.set_palette(self.mod_group.menv_att_display_1)
        self.set_palette(self.mod_group.menv_att_display_2)
        self.set_palette(self.mod_group.menv_rel_display_1)
        self.set_palette(self.mod_group.menv_rel_display_2)
        #synth settings
        self.set_palette(self.synth_group.drift_display)
        self.set_palette(self.synth_group.key_tracking_display)

    #slots
    # toggle dark mode
    def update_dark_mode(self, checked):
        if checked:
            self.setStyleSheet(self.dark_style)
            self.display_color = QColor("#dfdfef")
            self.update_drop_shadow_colors(QColor("#b4b4d2"))
            self.scope_group.scope_pen.setColor(QColor("#b4b4d2"))
            self.toggle_dark.setText("lite")
        else:
            self.setStyleSheet(self.light_style)
            self.display_color = QColor("black")
            self.update_drop_shadow_colors(QColor("#1c0627"))
            self.scope_group.scope_pen.setColor(QColor("#1c0627"))
            self.toggle_dark.setText("dark")
        self.set_display_colors()
        
    # settings toggles
    def update_active_settings(self, button):
        text = button.text()
        if text == "midi":
            self.settings_stack.setCurrentIndex(0)
        elif text == "synth":
            self.settings_stack.setCurrentIndex(1)
        elif text == "record":
            self.settings_stack.setCurrentIndex(2)
        elif text == "scope":
            self.settings_stack.setCurrentIndex(3)

    # modulator dials
    def update_mod_dial_value(self, name, value):
        self.engine.update_mod_value(name, value)
    
    def update_mod_dial_mode(self, name, mode):
        self.engine.update_mod_mode(name, mode)

    # midi settings
    def update_midi_in(self, input_name):
        self.engine.set_midi_input(input_name)

    def update_midi_ch(self, channel):
        self.engine.set_midi_channel(channel)

    def refresh_midi_ins(self):
        self.midi_group.midi_select.clear()
        input_list = self.engine.get_midi_inputs()
        if input_list:
            self.midi_group.midi_select.addItems(input_list)
            self.midi_group.midi_select.setCurrentIndex(0)

    def add_cc(self, cc_val, cc_param, module):
        cc_function = self.assign_cc_function(module, cc_param)
        cc_slider = self.slider_timer.assign_cc_slider(module, cc_param)
        cc_display = self.slider_timer.assign_cc_display(module, cc_param)
        if cc_val not in self.engine.midi_cc_functions:
            self.engine.midi_cc_functions.update({cc_val: cc_function})
        if cc_val not in self.midi_cc_sliders:
            self.midi_cc_sliders.update({cc_val: cc_slider})
        if cc_val not in self.midi_cc_displays:
            self.midi_cc_displays.update({cc_val: (cc_display, module, cc_param)})

    def update_cc(self, new_cc, old_cc, param, module):
        if old_cc in self.engine.midi_cc_functions:
            self.engine.midi_cc_functions.pop(old_cc)
        if old_cc in self.midi_cc_sliders:
            self.midi_cc_sliders.pop(old_cc)
        if old_cc in self.midi_cc_displays:
            self.midi_cc_displays.pop(old_cc)
        if new_cc not in self.engine.midi_cc_functions:
            self.engine.midi_cc_functions.update({new_cc: self.assign_cc_function(module, param)})
        if new_cc not in self.midi_cc_sliders:
            self.midi_cc_sliders.update({new_cc: self.slider_timer.assign_cc_slider(module, param)})
        if new_cc not in self.midi_cc_displays:
            self.midi_cc_displays.update({new_cc: (self.slider_timer.assign_cc_display(module, param), module, param)})
            

    def update_param(self, cc, new_param, module):
        if cc in self.engine.midi_cc_functions:
            self.engine.midi_cc_functions.pop(cc)
        if cc in self.midi_cc_sliders:
            self.midi_cc_sliders.pop(cc)
        if cc in self.midi_cc_displays:
            self.midi_cc_displays.pop(cc)
        self.engine.midi_cc_functions.update({cc: self.assign_cc_function(module, new_param)})
        self.midi_cc_sliders.update({cc: self.slider_timer.assign_cc_slider(module, new_param)})
        self.midi_cc_displays.update({cc: (self.slider_timer.assign_cc_display(module, new_param), module, new_param)})


    def delete_cc(self, cc):
        if cc in self.engine.midi_cc_functions:
            self.engine.midi_cc_functions.pop(cc)
        if cc in self.midi_cc_sliders:
            self.midi_cc_sliders.pop(cc)
        if cc in self.midi_cc_displays:
            self.midi_cc_displays.pop(cc)

    # recorder
    def update_rec_delete(self):
        self.engine.update_delete()

    def update_rec_record(self, state):
        self.engine.update_record(state)

    def update_rec_play(self):
        self.engine.update_play()
    
    def update_rec_pause(self):
        self.engine.update_pause()
    
    def update_rec_stop(self):
        self.engine.update_stop()

    def update_rec_loop(self, state):
        self.engine.update_loop(state)

    def save_rec_buffer(self, filename):
        self.engine.save_rec_buffer(filename)

    # filter
    def update_filt_freq(self, newFreq):
        self.engine.update_cutoff(newFreq)

    def update_filt_res(self, newRes):
        self.engine.update_resonance(newRes)

    def update_filt_drive(self, newDrive):
        self.engine.update_drive(newDrive)

    def update_filt_sat(self, newSat):
        self.engine.update_saturate(newSat)

    def update_filt_alg(self, text):
        if (text == "low"):
            newAlg = 0.0
        elif (text == "high"):
            newAlg = 1.0
        elif (text == "band"):
            newAlg = 2.0
        elif (text == "notch"):
            newAlg = 3.0
        self.engine.update_type(newAlg)

    def update_key_tracking(self, value):
        self.engine.update_key_tracking(value)

    # oscillator drift
    def update_osc_drift(self, value):
        self.engine.update_osc_drift(value)

    # oscillator type (algorithm)
    def update_osc_type(self, osc, new_type):
        self.engine.update_osc_type(osc, new_type)
        print(f"DEBUG: osc {osc}, algorithm: {new_type}")
        if new_type == 0:
            print("BLIT")
        elif new_type == 1:
            print("polyBLEP")
        
    # oscillator 1
    def update_osc_freq(self, value):
        self.engine.update_pitch_1(value)

    def update_osc_amp(self, value):
        self.engine.update_amplitude_1(value)

    def update_osc_width(self, value):
        self.engine.update_width_1(value)

    def update_osc_alg(self, text):
        if (text == "sine"):
            newAlg = 0.0
        elif (text == "triangle"):
            newAlg = 3.0
        elif (text == "saw"):
            newAlg = 1.0
        elif (text == "pulse"):
            newAlg = 2.0
        self.engine.update_algorithm(newAlg, 1)

    # oscillator 2
    def update_osc2_freq(self, value):
        self.engine.update_pitch_2(value)

    def update_osc2_det(self, value):
        self.engine.update_detune_2(value)

    def update_osc2_amp(self, value):
        self.engine.update_amplitude_2(value)

    def update_osc2_width(self, value):
        self.engine.update_width_2(value)

    def update_osc2_alg(self, text):
        if (text == "sine"):
            newAlg = 0.0
        elif (text == "triangle"):
            newAlg = 3.0
        elif (text == "saw"):
            newAlg = 1.0
        elif (text == "pulse"):
            newAlg = 2.0
        self.engine.update_algorithm(newAlg, 2)

    # oscillator 3
    def update_osc3_freq(self, value):
        self.engine.update_pitch_3(value)

    def update_osc3_det(self, value):
        self.engine.update_detune_3(value)

    def update_osc3_amp(self, value):
        self.engine.update_amplitude_3(value)

    def update_osc3_width(self, value):
        self.engine.update_width_3(value)

    def update_osc3_alg(self, text):
        if (text == "sine"):
            newAlg = 0.0
        elif (text == "triangle"):
            newAlg = 3.0
        elif (text == "saw"):
            newAlg = 1.0
        elif (text == "pulse"):
            newAlg = 2.0
        self.engine.update_algorithm(newAlg, 3)

    # envelope
    def update_env_attack(self, value):
        self.engine.update_attack(value)

    def update_env_decay(self, value):
        self.engine.update_decay(value)

    def update_env_sustain(self, value):
        self.engine.update_sustain(value)

    def update_env_release(self, value):
        self.engine.update_release(value)
    
    def update_env_gate(self, checked):
        self.engine.update_gate(checked)

    # filter envelope
    def update_fenv_attack(self, value):
        self.engine.update_fenv_attack(value)

    def update_fenv_decay(self, value):
        self.engine.update_fenv_decay(value)

    def update_fenv_sustain(self, value):
        self.engine.update_fenv_sustain(value)

    def update_fenv_release(self, value):
        self.engine.update_fenv_release(value)
    
    def update_fenv_amount(self, value):
        self.engine.update_fenv_amount(value)

    # delay
    def update_del_time(self, value):
        self.engine.update_del_time(value)
    
    def update_del_feedback(self, value):
        self.engine.update_del_feedback(value)

    def update_del_mix(self, value):
        self.engine.update_del_mix(value)

    # lfo 1
    def update_lfo1_freq(self, value):
        self.engine.update_lfo1_freq(value)
    
    def update_lfo1_offset(self, value):
        self.engine.update_lfo1_offset(value)
    
    def update_lfo1_shape(self, value):
        self.engine.update_lfo1_shape(value)

    # lfo 2
    def update_lfo2_freq(self, value):
        self.engine.update_lfo2_freq(value)
    
    def update_lfo2_offset(self, value):
        self.engine.update_lfo2_offset(value)
    
    def update_lfo2_shape(self, value):
        self.engine.update_lfo2_shape(value)

    # menv 1
    def update_menv1_att(self, value):
        self.engine.update_menv1_att(value)
    
    def update_menv1_rel(self, value):
        self.engine.update_menv1_rel(value)
    
    def update_menv1_mode(self, value):
        self.engine.update_menv1_mode(value)

    # menv 2
    def update_menv2_att(self, value):
        self.engine.update_menv2_att(value)
    
    def update_menv2_rel(self, value):
        self.engine.update_menv2_rel(value)
    
    def update_menv2_mode(self, value):
        self.engine.update_menv2_mode(value)

    # process pc keyboard press events (chromatic)
    def keyPressEvent(self, event):
        if (event.isAutoRepeat()):
            return
        else:
            offset = key_conv.key_offset(event.key())
            if (offset is not None):
                if (offset < 18):
                    note = min(127, 12*self.engine.octave + offset + 60)
                    self.key_to_note.update({offset: note})
                    self.engine.key_pressed(self.key_to_note[offset], 127)
                else:
                    if (offset == 18):
                        if (self.engine.octave < 5):
                            self.engine.octave += 1
                    elif (offset == 19):
                        if (self.engine.octave > -5):
                            self.engine.octave -= 1
            else:
                print(f"DEBUG: key: {event.text()}, value: {event.key()}")
            return super().keyPressEvent(event)

    
    def keyReleaseEvent(self, event):
        if (event.isAutoRepeat()):
            return
        else:
            offset = key_conv.key_offset(event.key())
            if (offset is not None):
                if (offset < 18):
                    if offset in self.key_to_note:
                        self.engine.key_released(self.key_to_note[offset])
                        self.key_to_note.pop(offset)
            return super().keyReleaseEvent(event)

    def closeEvent(self, event):
        self.engine.close()
        return super().closeEvent(event)
