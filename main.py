import sys
import numpy as np
import mido
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from subsnake.gui import MainWindow
import subsnake.gui as gui
from subsnake.audio import WrappedOsc, HalSVF, ADSR, AudioEngine
from subsnake.audio.effects import AudioRecorder, StereoDelay
from subsnake.audio.modulators import LFO, ModEnv
from importlib import resources

fs = 44100
twopi = 2*np.pi
oneoverpi = 1/np.pi

#init compile (numba functions)
osc_test = np.array([0.1, 0.1, 0.1], dtype=np.float32)
filt_test = np.array([[0.0, 0.0, 1.0, 2.0, 0.0, 1.0, 8.0], [0.0, 0.0, 1.0, 2.0, 0.0, 1.0, 8.0]], dtype=np.float32)
env_test = np.array([0.0, 0.0, 1.0, 1.0, 0.5, 1.0], dtype=np.float32)
phase_test = np.zeros((1), dtype=np.float32)
test_out = np.zeros((128), dtype=np.float32)
f32_increment = np.float32(0.1)
f32_offset = np.float32(0.0)
f32_attack_c = np.float32(0.1)
f32_release_c = np.float32(0.1)
f32_threshold = np.float32(.001)
WrappedOsc.generate_sine(osc_test, np.zeros((16, 2), dtype=np.float32), osc_test, osc_test, osc_test, 0, 0, 0)
WrappedOsc.polyblep_saw(osc_test, np.zeros((16, 2), dtype=np.float32), osc_test, osc_test, osc_test, 0, 0, 0)
WrappedOsc.polyblep_pulse(osc_test, np.zeros((16, 2), dtype=np.float32), osc_test, 0.5, osc_test, osc_test, osc_test, osc_test, 0, 0, 0, 0)
HalSVF.filter_block(filt_test, np.zeros((16, 2), dtype=np.float32), np.zeros((16, 2), dtype=np.float32), np.ones((16, 2), dtype=np.float32), 0.0, HalSVF.clip_sample, 100,
                    osc_test, osc_test, osc_test, osc_test, osc_test, 0, 0, 0, 0, 0)
ADSR.envelope_block(env_test, False, np.zeros((16, 2), dtype=np.float32), np.zeros((16, 2), dtype=np.float32), 0, 0, env_test, env_test, env_test, env_test, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1)
AudioRecorder.process_samples(np.zeros((32, 2), dtype=np.float32), np.zeros((16, 2), dtype=np.float32), np.zeros((16, 2), dtype=np.float32), 0,
                              [False], [True], [False], False, np.zeros((2), dtype=np.int32), np.zeros((2), dtype=np.int32), [False])
StereoDelay.delay_block(np.zeros((32, 2), dtype=np.float32), np.zeros((32, 2), dtype=np.float32), np.zeros((32, 2), dtype=np.float32), 0,
                        np.zeros((2), dtype=np.int32), np.zeros((2), dtype=np.int32), 0.5, 0.5)
LFO.generate_sine(phase_test, f32_increment, f32_offset, test_out)
LFO.generate_triangle(phase_test, f32_increment, f32_offset, test_out)
LFO.generate_ramp(phase_test, f32_increment, f32_offset, test_out)
LFO.generate_sawtooth(phase_test, f32_increment, f32_offset, test_out)
LFO.generate_square(phase_test, f32_increment, f32_offset, test_out, 0.5)
LFO.sample_and_hold(phase_test, f32_increment, test_out, np.zeros((1), dtype=np.float32))
ModEnv.gen_AR_oneshot(np.zeros((1), dtype=np.float32), np.zeros((1), dtype=np.int32), True, np.zeros((1), dtype=np.int32),
                      f32_attack_c, f32_release_c, f32_threshold, np.zeros((16), dtype=np.float32), 0, 0)
ModEnv.gen_AR_loop(np.zeros((1), dtype=np.float32), np.zeros((1), dtype=np.int32), True,
                   f32_attack_c, f32_release_c, f32_threshold, np.zeros((16), dtype=np.float32), 0, 0)
ModEnv.gen_AHR(np.zeros((1), dtype=np.float32), np.zeros((1), dtype=np.float32), True,
               f32_attack_c, f32_release_c, f32_threshold, np.zeros((16), dtype=np.float32), 0, 0)


#get midi inputs & channels
input_list = mido.get_input_names()
midi_channels = np.arange(1, 17)

#init audio engine
engine = AudioEngine()

#instance app
app = QApplication(sys.argv)
window = MainWindow(engine)
window.setObjectName("main_window")

#add midi inputs
if input_list is not None:
    window.midi_group.midi_select.addItems(input_list)

#assign midi channels
for channel in midi_channels:
    window.midi_group.channel_select.addItem(str(channel))

#start audio & assign midi input
window.engine.start_audio()

#load stylesheet
style_file = resources.files(gui) / 'window.qss'
style = style_file.read_text(encoding='utf-8')
app.setStyleSheet(style)
app.setApplicationName("subsnake")
app.setApplicationDisplayName("subsnake")
app.setDesktopFileName("subsnake")
with resources.as_file(resources.files("subsnake").joinpath("images/icon.png")) as icon_path:
    path_str = str(icon_path)
    app_pixmap = QPixmap(path_str)
    app_icon = QIcon()
    app_icon.addPixmap(app_pixmap)
    for size in [16, 24, 32, 48, 64, 256]:
        smooth_pixmap = app_pixmap.scaled(
            size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        app_icon.addPixmap(smooth_pixmap)
    app.setWindowIcon(app_icon)
    window.setWindowIcon(app_icon)

#show window
window.show()

#start app
app.exec()
