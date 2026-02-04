import numpy as np
import math
from numba import njit

fs = 44100
twopi = 2*np.pi
oneoverpi = 1/np.pi

# phase-wrapped oscillator
# alg = 0.0: sine, 1.0: polyblep ramp, 2.0: polyblep pulse | width = 0.0 to 1.0
class WrappedOsc():
    def __init__(self, alg, amplitude, frequency, sample_rate, width=0.5):
        phase_increment = twopi * (frequency/sample_rate)
        self.state = np.array([0.0, amplitude, phase_increment], dtype=np.float32)
        self.state2 = np.array([0.0, amplitude, phase_increment], dtype=np.float32)
        self.hardSyncBuffer = np.zeros((2048, 2), dtype=np.float32)
        self.alg = alg
        self.pulsewidth = width
        self.freq = frequency
        self.amp = amplitude
    
    def process_block(self, buffer, mod_buffers, mod_values):
        #print(f"DEBUG: buffer shape is {buffer.shape}")
        if (self.alg == 0):
            self.generate_sine(self.state, buffer, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_values[0], mod_values[1], mod_values[2], self.amp)
        elif (self.alg == 1.0):
            self.polyblep_saw(self.state, buffer, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_values[0], mod_values[1], mod_values[2], self.amp)
        elif (self.alg == 2.0):
            #anti-aliased square wave
            frames = len(buffer)
            self.state2[0] = self.state[0] + self.pulsewidth*twopi
            if (self.state2[0] > twopi):
                self.state2[0] -= twopi
            self.polyblep_saw(self.state, buffer, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_values[0], mod_values[1], mod_values[2], self.amp)
            self.polyblep_saw(self.state2, self.hardSyncBuffer, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_values[0], mod_values[1], mod_values[2], self.amp)
            buffer[:] -= self.hardSyncBuffer[:frames]

    def update_pitch(self, newPitch):
        self.freq = newPitch
        new_increment = twopi * (newPitch/fs)
        self.state[2] = new_increment
        self.state2[2] = new_increment

    def update_amplitude(self, newAmp):
        self.amp = newAmp
        self.state[1] = newAmp
        self.state2[1] = newAmp

    def update_width(self, newWidth):
        self.pulsewidth = newWidth
    
    def update_algorithm(self, newAlg):
        self.alg = newAlg


    #phase-wrapped sine wave
    @staticmethod
    @njit(nogil=True, fastmath=True)
    def generate_sine(state, outdata, pitch_mod, det_mod, amp_mod, pm_amt, dm_amt, am_amt, amp=1.0):
        for n in range(len(outdata)):
            sample = state[1] * math.sin(state[0])
            outdata[n][0] = sample*(amp - amp_mod[n]*am_amt)
            outdata[n][1] = sample*(amp - amp_mod[n]*am_amt)
            state[0] += state[2]
            if (state[0] > twopi):
                state[0] -= twopi

    #anti-aliased sawtooth
    @staticmethod
    @njit(nogil=True, fastmath=True)
    def polyblep_saw(state, outdata, pitch_mod, det_mod, amp_mod, pm_amt, dm_amt, am_amt, amp=1.0):
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
            outdata[n, 0] = sample*(amp - amp_mod[n]*am_amt)
            outdata[n, 1] = sample*(amp - amp_mod[n]*am_amt)
