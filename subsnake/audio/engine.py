import numpy as np
from .generators import WrappedOsc
from .filters import HalSVF
from .envelopes import ADSR

fs = 44100
blocksize = 1024
twopi = 2*np.pi
oneoverpi = 1/np.pi

class AudioEngine():
    def __init__(self):
        self.osc_out = np.zeros((1024, 2), dtype=np.float32)
        self.filt_out = np.zeros((1024, 2), dtype=np.float32)
        self.osc = WrappedOsc(2, 0.5, 55, fs, .5)
        self.filt = HalSVF(0.0, 3520, 10, 1.0)
        self.env = ADSR(.01, 1.0, 0.5, 1.0)
        self.octave = 0
    
    def callback(self, outdata, frames, time, status):
        self.osc.process_block(self.osc_out)
        self.filt.process_block(self.osc_out, self.filt_out)
        self.env.process_block(self.filt_out, outdata)
