import numpy as np
from numba import njit
import math

#constants
twopi = 2*math.pi
oneoverpi = 1.0/math.pi
oneovertwopi = 1.0/twopi

class LFO():
    def __init__(self, fs, freq=10.0, offset=0.0, shape=0):
        self.fs = fs
        self.output = np.zeros((2048), dtype=np.float32)
        self.current_phase = np.zeros((1), dtype=np.float32)
        self.phase_increment = twopi*(freq/float(fs))
        self.frequency = freq
        self.phase_offset = offset
        self.shape = shape
        self.held_value = np.zeros((1), dtype=np.float32)
        self.held_value[0] = 2*np.random.random() - 1.0

    def process_block(self, frames):
        if self.shape == 0:
            self.generate_sine(self.current_phase, self.phase_offset, self.phase_increment, self.output[:frames])
        elif self.shape == 1:
            self.generate_triangle(self.current_phase, self.phase_offset, self.phase_increment, self.output[:frames])
        elif self.shape == 2:
            self.generate_ramp(self.current_phase, self.phase_offset, self.phase_increment, self.output[:frames])
        elif self.shape == 3:
            self.generate_sawtooth(self.current_phase, self.phase_offset, self.phase_increment, self.output[:frames])
        elif self.shape == 4:
            self.generate_square(self.current_phase, self.phase_offset, self.phase_increment, self.output[:frames], 0.5)
        elif self.shape == 5:
            self.sample_and_hold(self.current_phase, self.phase_increment, self.output, self.held_value)
    
    @staticmethod
    @njit(nogil=True, fastmath=True)
    def generate_sine(phase, offset, increment, output):
        frames = len(output)
        for n in range(0, frames):
            output[n] = math.sin(phase[0] + offset)
            phase[0] += increment
            if phase[0] >= twopi:
                phase[0] -= twopi
            
    @staticmethod
    @njit(nogil=True, fastmath=True)
    def generate_triangle(phase, offset, increment, output):
        frames = len(output)
        for n in range(0, frames):
            new_phase = phase[0] + offset
            norm_phase = new_phase*oneovertwopi
            norm_phase = norm_phase - np.floor(norm_phase)
            output[n] = 4*abs(norm_phase - 0.5) - 1
            phase[0] += increment
            if phase[0] >= twopi:
                phase[0] -= twopi

    @staticmethod
    @njit(nogil=True, fastmath=True)
    def generate_ramp(phase, offset, increment, output):
        frames = len(output)
        for n in range(0, frames):
            new_phase = phase[0] + offset
            norm_phase = new_phase*oneovertwopi
            norm_phase = norm_phase - np.floor(norm_phase)
            output[n] = 2*norm_phase - 1.0
            phase[0] += increment
            if phase[0] >= twopi:
                phase[0] -= twopi

    @staticmethod
    @njit(nogil=True, fastmath=True)
    def generate_sawtooth(phase, offset, increment, output):
        frames = len(output)
        for n in range(0, frames):
            new_phase = phase[0] + offset
            norm_phase = new_phase*oneovertwopi
            norm_phase = norm_phase - np.floor(norm_phase)
            output[n] = 2*(1.0-norm_phase) - 1.0
            phase[0] += increment
            if phase[0] >= twopi:
                phase[0] -= twopi

    @staticmethod
    @njit(nogil=True, fastmath=True)
    def generate_square(phase, offset, increment, output, width):
        frames = len(output)
        for n in range(0, frames):
            new_phase = phase[0] + offset
            norm_phase = new_phase*oneovertwopi
            norm_phase = norm_phase - np.floor(norm_phase)
            output[n] = 2*(norm_phase < width) - 1.0
            phase[0] += increment
            if phase[0] >= twopi:
                phase[0] -= twopi

    @staticmethod
    @njit(nogil=True, fastmath=True)
    def sample_and_hold(phase, increment, output, held_value):
        frames = len(output)
        for n in range(0, frames):
            output[n] = held_value[0]
            phase[0] += increment
            if phase[0] >= twopi:
                phase[0] -= twopi
                held_value[0] = 2*np.random.random() - 1.0
