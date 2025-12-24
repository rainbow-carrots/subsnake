import sys
import numpy as np
import sounddevice as sd
import math
from numba import njit

fs = 44100
blocksize = 1024
twopi = 2*np.pi
oneoverpi = 1/np.pi

# Hal Chamberlin's digital SV Filter w/ nonlinear feedback | 4x oversampled
# type = 1.0: lowpass, 2.0: highpass, 3.0: bandpass, 4.0: notch
class HalSVF():
    def __init__(self, type, cutoff, resonance, drive=1.0):
        self.cutoff = cutoff
        self.resonance = resonance

        q = resonance
        f = 2*math.sin(np.pi*(cutoff/(4*fs)))

        #init parameter buffer | lowpass, bandpass, tuning, dampening, type, drive
        self.state = np.array([[0.0, 0.0, f, q, type, drive], [0.0, 0.0, f, q, type, drive]], dtype=np.float32)
    
    def process_block(self, state, input, output):
        self.filter_block(state, input, output, HalSVF.clip_sample)

    def update_cutoff(self, freq):
        f = 2*math.sin(np.pi*(freq/(4*fs)))
        self.state[0, 2] = f
        self.state[1, 2] = f

    def update_resonance(self, res):
        self.state[0, 3] = res
        self.state[1, 3] = res

    def update_drive(self, drive):
        self.state[0, 5] = drive
        self.state[1, 5] = drive
    
    def update_type(self, type):
        self.state[0, 4] = type
        self.state[1, 4] = type
        
    @staticmethod
    @njit(nogil=True, fastmath=True)
    def filter_block(state, input, output, clip_sample):
        for c in range (2):
            for n in range(len(output)):
                subsample = 0.0
                prev_low = state[c, 0]
                prev_band = state[c, 1]
                freq_c = state[c, 2]
                res_c = state[c, 3]
                substate = int(state[c, 4])
                drive = state[c, 5]
                oneoverdrive = 1.0/drive
                for m in range(4):
                    feedback = res_c*(np.tanh(prev_band*drive)*oneoverdrive)
                    high = input[n, c] - prev_low - feedback
                    #clip band
                    newband = freq_c*high + prev_band
                    state[c, 1] = clip_sample(newband, 8.0)
                    #clip low
                    newlow = prev_low + freq_c*state[c, 1]
                    state[c, 0] = clip_sample(newlow, 8.0)
                    notch = high + state[c, 0]
                    if (substate == 0):   #lowpass
                        subsample += state[c, 0]
                    elif (substate == 1): #highpass
                        subsample += high
                    elif (substate == 2): #bandpass
                        subsample += state[c, 1]
                    elif (substate == 3): #notch
                        subsample += notch
                sample = subsample*0.25
                output[n, c] = sample

    @staticmethod
    @njit(nogil=True, fastmath=True)
    def clip_sample(sample, threshold):
        if (sample > threshold):
            output = threshold * 0.66667
        elif (sample < -threshold):
            output = -threshold * 0.66667
        else:
            norm_sample = sample/threshold
            clip_sample = norm_sample - (norm_sample**3) * 0.33333
            output = clip_sample * threshold
        return output