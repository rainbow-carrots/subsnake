import numpy as np
from numba import njit
import math

#constants
twopi = 2*math.pi
oneoverpi = 1/math.pi

class LFO():
    def __init__(self, fs, freq=10.0, offset=0.0, shape=0):
        self.fs = fs
        self.output = np.zeros((2048), dtype=np.float32)
        self.current_phase = np.zeros((1), dtype=np.float32)
        self.phase_increment = twopi*(freq/float(fs))
        self.frequency = freq
        self.phase_offset = offset
        self.shape = shape

    def process_block(self, frames):
        if self.shape == 0:
            self.generate_sine(self.current_phase, self.phase_offset, self.phase_increment, self.output[:frames])
    
    @staticmethod
    @njit(nogil=True, fastmath=True)
    def generate_sine(phase, offset, increment, output):
        frames = len(output)
        for n in range(0, frames):
            output[n] = math.sin(phase[0] + offset)
            phase[0] += increment
            if phase[0] >= twopi:
                phase[0] -= twopi
            
        

