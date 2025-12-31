import sys
import sounddevice as sd
import numpy as np
import mido
from PySide6.QtWidgets import QApplication
from subsnake.gui import MainWindow
import subsnake.gui as gui
from subsnake.audio import WrappedOsc, HalSVF, ADSR
from importlib import resources

fs = 44100
blocksize = 1024
twopi = 2*np.pi
oneoverpi = 1/np.pi

#init compile
osc_test = np.array([0.0, 0.0, 0.0], dtype=np.float32)
filt_test = np.array([[0.0, 0.0, 1.0, 2.0, 0.0, 1.0, 8.0], [0.0, 0.0, 1.0, 2.0, 0.0, 1.0, 8.0]], dtype=np.float32)
env_test = np.array([0.0, 0.0, 1.0, 1.0, 0.5, 1.0], dtype=np.float32)
WrappedOsc.generate_sine(osc_test, np.zeros((16, 2), dtype=np.float32))
WrappedOsc.polyblep_saw(osc_test, np.zeros((16, 2), dtype=np.float32))
HalSVF.filter_block(filt_test, np.zeros((16, 2), dtype=np.float32), np.zeros((16, 2), dtype=np.float32), HalSVF.clip_sample)
ADSR.envelope_block(env_test, False, np.zeros((16, 2), dtype=np.float32), np.zeros((16, 2), dtype=np.float32))

#instance app
app = QApplication(sys.argv)
window = MainWindow()

#load stylesheet
style_file = resources.files(gui) / 'window.qss'
style = style_file.read_text(encoding='utf-8')
app.setStyleSheet(style)

#show window
window.show()

#get first midi input (test)
input = mido.get_input_names()[0]
#start midi callback
with mido.open_input(input, callback=window.engine.midi_callback) as inport:

     #start stream & main loop
     with sd.OutputStream(channels=2, samplerate=fs, blocksize=1024, latency='high', callback=window.engine.callback, dtype=np.float32):
          app.exec()
