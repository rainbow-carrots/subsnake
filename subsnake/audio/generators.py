import numpy as np
import sounddevice as sd
import math
from numba import njit

fs = 44100
blocksize = 1024
twopi = 2*np.pi
oneoverpi = 1/np.pi

# phase-wrapped oscillator
# alg = 0.0: sine, 1.0: polyblep ramp, 2.0: polyblep pulse | width = 0.0 to 1.0
class WrappedOsc():
    def __init__(self, alg, amplitude, frequency, sample_rate, width=0.5):
        phase_increment = twopi * (frequency/sample_rate)
        self.state = np.array([0.0, amplitude, phase_increment], dtype=np.float32)
        self.state2 = np.array([0.0, amplitude, phase_increment], dtype=np.float32)
        self.hardSyncBuffer = np.zeros((1024, 2), dtype=np.float32)
        self.alg = alg
        self.pulsewidth = width
    
    def process_block(self, buffer, frames):
        #print(f"DEBUG: buffer shape is {buffer.shape}")
        if (self.alg == 0):
            self.generate_sine(self.state, buffer)
        elif (self.alg == 1.0):
            self.polyblep_saw(self.state, buffer)
        elif (self.alg == 2.0):
            #anti-aliased square wave
            self.state2[0] = self.state[0] + self.pulsewidth*twopi
            if (self.state2[0] > twopi):
                self.state2[0] -= twopi
            self.polyblep_saw(self.state, buffer)
            self.polyblep_saw(self.state2, self.hardSyncBuffer)
            buffer[:] -= self.hardSyncBuffer[:frames]

    def update_pitch(self, newPitch):
        new_increment = twopi * (newPitch/fs)
        self.state[2] = new_increment
        self.state2[2] = new_increment

    def update_amplitude(self, newAmp):
        self.state[1] = newAmp
        self.state2[1] = newAmp

    def update_width(self, newWidth):
        self.pulsewidth = newWidth
    
    def update_algorithm(self, newAlg):
        self.alg = newAlg


    #phase-wrapped sine wave
    @staticmethod
    @njit(nogil=True, fastmath=True)
    def generate_sine(state, outdata):
        for n in range(len(outdata)):
            sample = state[1] * math.sin(state[0])
            outdata[n][0] = sample
            outdata[n][1] = sample
            state[0] += state[2]
            if (state[0] > twopi):
                state[0] -= twopi

    #anti-aliased sawtooth
    @staticmethod
    @njit(nogil=True, fastmath=True)
    def polyblep_saw(state, outdata):
        frames = len(outdata)
        for n in range(frames):
            #generate naive saw
            sample = (state[0] * oneoverpi) - 1.0
            
            #apply polyblep corrections
            if (state[0] < state[2]):           #phase just wrapped
                t = state[0]/state[2]
                sample += (t - 1.0)**2
            elif (state[0] + state[2] > twopi):   #phase about to wrap
                t = (twopi - state[0])/state[2]
                sample -= (t - 1.0)**2

            #increment phase & wrap
            state[0] += state[2]
            if (state[0] > twopi):
                state[0] -= twopi

            #output
            sample *= state[1]
            outdata[n, 0] = sample
            outdata[n, 1] = sample