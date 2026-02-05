import numpy as np
import math
from numba import njit

fs = 44100
oneoverfs = 1.0/float(fs)
twopi = 2*np.pi
oneoverpi = 1/np.pi
piovertwo = np.pi/2.0
max_det_inc = twopi*(10.0/float(fs))

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
            self.generate_sine(self.state, buffer, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_values[0], mod_values[1], mod_values[2], self.amp, self.freq)
        elif (self.alg == 1.0):
            self.polyblep_saw(self.state, buffer, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_values[0], mod_values[1], mod_values[2], self.amp, self.freq)
        elif (self.alg == 2.0):
            self.polyblep_pulse(self.state, buffer, self.state2, self.pulsewidth, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_buffers[3], mod_values[0], mod_values[1], mod_values[2], mod_values[3], self.amp, self.freq)

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
    def generate_sine(state, outdata, pitch_mod, det_mod, amp_mod, pm_amt, dm_amt, am_amt, amp=1.0, freq=440.0):
        base_inc = twopi*freq*oneoverfs
        for n in range(len(outdata)):
            state[2] = base_inc + base_inc*pitch_mod[n]*pm_amt + max_det_inc*det_mod[n]*dm_amt
            sample = state[1] * math.sin(state[0])
            outdata[n][0] = sample*(amp - amp_mod[n]*am_amt)
            outdata[n][1] = sample*(amp - amp_mod[n]*am_amt)
            state[0] += state[2]
            if (state[0] > twopi):
                state[0] -= twopi

    #anti-aliased sawtooth
    @staticmethod
    @njit(nogil=True, fastmath=True)
    def polyblep_saw(state, outdata, pitch_mod, det_mod, amp_mod, pm_amt, dm_amt, am_amt, amp=1.0, freq=440.0):
        frames = len(outdata)
        base_inc = twopi*freq*oneoverfs
        for n in range(frames):
            #modulate phase increment
            state[2] = base_inc + base_inc*pitch_mod[n]*pm_amt + max_det_inc*det_mod[n]*dm_amt

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

    #anti-aliased pulse
    @staticmethod
    @njit(nogil=True, fastmath=True)
    def polyblep_pulse(state, outdata, state2, width, pitch_mod, det_mod, amp_mod, width_mod, pm_amt, dm_amt, am_amt, wm_amt, amp=1.0, freq=440.0):
        frames = len(outdata)
        base_inc = twopi*freq*oneoverfs
        for n in range(frames):
            #modulate phase increment
            state[2] = base_inc + base_inc*pitch_mod[n]*pm_amt + max_det_inc*det_mod[n]*dm_amt

            #generate naive saws
            sample = (state[0] * oneoverpi) - 1.0
            sample2 = (state2[0]* oneoverpi) - 1.0
            
            #apply polyblep corrections
            # main osc
            if (state[0] < state[2]):           #phase just wrapped
                t = state[0]/state[2]
                sample += (t - 1.0)**2
            elif (state[0] + state[2] > twopi):   #phase about to wrap
                t = (twopi - state[0])/state[2]
                sample -= (t - 1.0)**2
            
            # sync osc
            if (state2[0] < state2[2]):           #phase just wrapped
                t2 = state2[0]/state2[2]
                sample2 += (t2 - 1.0)**2
            elif (state2[0] + state2[2] > twopi):   #phase about to wrap
                t2 = (twopi - state2[0])/state2[2]
                sample2 -= (t2 - 1.0)**2

            #increment phases & wrap
            state[0] += state[2]
            state2[0] = state[0] + twopi*width + piovertwo*width_mod[n]*wm_amt
            if (state[0] > twopi):
                state[0] -= twopi
            if (state2[0] > twopi):
                state2[0] -= twopi

            #output
            sample -= sample2
            sample *= state[1]
            outdata[n, 0] = sample*(amp - amp_mod[n]*am_amt)
            outdata[n, 1] = sample*(amp - amp_mod[n]*am_amt)
