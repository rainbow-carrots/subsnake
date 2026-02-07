import numpy as np
from numba import njit
import math

#constants
twopi = 2*math.pi
oneoverpi = 1.0/math.pi
oneovertwopi = 1.0/twopi

class LFO():
    def __init__(self, fs, freq=10.0, offset=0.0, shape=0):
        self.fs = float(fs)
        self.output = np.zeros((2048), dtype=np.float32)
        self.current_phase = np.zeros((1), dtype=np.float32)
        self.phase_increment = np.float32(twopi*(freq/float(fs)))
        self.frequency = freq
        self.phase_offset = np.float32(offset)
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

    def set_frequency(self, new_freq):
        self.frequency = np.float32(new_freq)
        self.phase_increment = np.float32(twopi*(self.frequency/self.fs))
    
    def set_offset(self, new_offset):
        self.phase_offset = np.float32(twopi*new_offset)

    def set_shape(self, new_shape):
        self.shape = new_shape
    
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

class ModEnv():
    def __init__(self, fs, attack=0.5, release=0.5, mode=0):
        self.output = np.zeros((2048), dtype=np.float32)
        self.value = np.zeros((1), dtype=np.float32)
        self.state = np.zeros((1), dtype=np.int32)
        self.run = np.zeros((1), dtype=np.int32)
        self.gate = False
        self.prev_gate = [False]
        self.attack = attack
        self.release = release
        self.mode = mode
        self.fs = float(fs)
        self.threshold = np.float32(.001)
        self.attack_sample = 0
        self.release_sample = 0

    def process_block(self, frames):
        attack_time = self.attack*self.fs
        release_time = self.release*self.fs
        attack_c = np.float32(1.0 - math.exp(-1/attack_time))
        release_c = np.float32(1.0 - math.exp(-1/release_time))
        if self.mode == 0:
            self.gen_AR_oneshot(self.value, self.state, self.gate, self.run, attack_c, release_c, self.threshold, self.output[:frames], self.attack_sample, self.release_sample)
        elif self.mode == 1:
            self.gen_AHR(self.value, self.state, self.gate, attack_c, release_c, self.threshold, self.output[:frames], self.attack_sample, self.release_sample)
        elif self.mode == 2:
            self.gen_AR_loop(self.value, self.state, self.gate, attack_c, release_c, self.threshold, self.output[:frames], self.attack_sample, self.release_sample)

    def set_attack(self, new_attack):
        self.attack = new_attack
    
    def set_release(self, new_release):
        self.release = new_release

    def set_mode(self, new_mode):
        self.mode = new_mode

    def update_gate(self, new_gate):
        self.gate = new_gate

    def update_attack_start(self, attack_sample):
        self.attack_sample = attack_sample

    def update_release_start(self, release_sample):
        self.release_sample = release_sample

    @staticmethod
    @njit(nogil=True, fastmath=True)
    def gen_AR_oneshot(value, state, gate, run, attack_c, release_c, threshold, output, attack_start, release_start):
        frames = len(output)
        top_threshold =  1.0 - threshold
        for n in range(0, frames):
            if not gate:
                state[0] = 0                        
                if run[0]:                          #clear run flag if set
                    run[0] = 0
                if value[0] > threshold:            #finish release
                    value[0] += release_c*(0.0 - value[0])
                else:                               #stop
                    value[0] = 0.0
            else:
                if not run[0]:
                    if (state[0] == 0) and (n >= attack_start):       #start
                        state[0] = 1
                    elif state[0] == 1:                               #attack
                        if value[0] < top_threshold:
                            value[0] += attack_c*(1.0 - value[0])
                        else:
                            value[0] = 1.0
                            state[0] = 2
                    elif state[0] == 2:                               #release
                        if value[0] > threshold:
                            value[0] += release_c*(0.0 - value[0])
                        else:
                            value[0] = 0.0
                            state[0] = 0                              #stop
                            run[0] = 1
            output[n] = value[0]

    @staticmethod
    @njit(nogil=True, fastmath=True)
    def gen_AR_loop(value, state, gate, attack_c, release_c, threshold, output, attack_start, release_start):
        frames = len(output)
        top_threshold =  1.0 - threshold
        for n in range(0, frames):
            if not gate:
                state[0] = 0                        
                if value[0] > threshold:        #finish release
                    value[0] += release_c*(0.0 - value[0])
                else:                           #stop
                    value[0] = 0.0
            else:
                if state[0] == 0  and (n >= attack_start):               #start
                    state[0] = 1
                elif state[0] == 1:             #attack
                    if value[0] < top_threshold:
                        value[0] += attack_c*(1.0 - value[0])
                    else:
                        value[0] = 1.0
                        state[0] = 2
                elif state[0] == 2:             #release
                    if value[0] > threshold:
                        value[0] += release_c*(0.0 - value[0])
                    else:
                        value[0] = 0.0
                        state[0] = 0            #stop
            output[n] = value[0]

    @staticmethod
    @njit(nogil=True, fastmath=True)
    def gen_AHR(value, state, gate, attack_c, release_c, threshold, output, attack_start, release_start):
        frames = len(output)
        top_threshold =  1.0 - threshold
        for n in range(0, frames):
            if not gate:
                state[0] = 0                        
                if value[0] > threshold:        #finish release
                    value[0] += release_c*(0.0 - value[0])
                else:                           #stop
                    value[0] = 0.0
            else:
                if state[0] == 0  and (n >= attack_start):               #start
                    state[0] = 1
                elif state[0] == 1:             #attack
                    if value[0] < top_threshold:
                        value[0] += attack_c*(1.0 - value[0])
                    else:
                        value[0] = 1.0
                        state[0] = 2
                elif state[0] == 2:             #hold
                    if value[0] < top_threshold:
                        value[0] += attack_c*(1.0 - value[0])
                    else:
                        value[0] = 1.0
            output[n] = value[0]