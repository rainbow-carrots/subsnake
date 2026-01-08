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
    def __init__(self, type, cutoff, resonance, drive=1.0, saturate=8.0):
        self.cutoff = cutoff
        self.resonance = resonance
        self.env_amount = 0.0

        q = resonance
        f = 2*math.sin(np.pi*(cutoff/(4*fs)))

        #init parameter buffer | lowpass, bandpass, tuning, dampening, type, drive, saturation
        self.state = np.array([[0.0, 0.0, f, q, type, drive, saturate], [0.0, 0.0, f, q, type, drive, saturate]], dtype=np.float32)
    
    def process_block(self, input, output, fenv):
        self.filter_block(self.state, input, output, fenv, self.env_amount, HalSVF.clip_sample, self.cutoff)

    def update_cutoff(self, freq):
        self.cutoff = freq

    def update_resonance(self, res):
        self.state[0, 3] = res
        self.state[1, 3] = res

    def update_drive(self, drive):
        self.state[0, 5] = drive
        self.state[1, 5] = drive
    
    def update_type(self, type):
        self.state[0, 4] = type
        self.state[1, 4] = type

    def update_saturate(self, saturate):
        self.state[0, 6] = saturate
        self.state[1, 6] = saturate

    def update_env_amount(self, amount):
        self.env_amount = amount
        
    @staticmethod
    @njit(nogil=True, fastmath=True)
    def filter_block(state, input, output, fenv, fenv_amount, clip_sample, cutoff):
        for c in range (2):
            for n in range(len(output)):
                subsample = 0.0
                prev_low = state[c, 0]
                prev_band = state[c, 1]
                if (fenv_amount >= 0.0):
                    new_cutoff = min(cutoff + cutoff*fenv_amount*fenv[n, c], 7040.0)
                else:
                    new_cutoff = max(cutoff + cutoff*fenv_amount*fenv[n, c], 0.1)
                freq_c = 2*math.sin(np.pi*(new_cutoff/(4*fs)))
                res_c = state[c, 3]
                substate = int(state[c, 4])
                drive = state[c, 5]
                saturate = state[c, 6]
                oneoverdrive = 1.0/drive
                for m in range(4):
                    feedback = res_c*(np.tanh(prev_band*drive)*oneoverdrive)
                    high = clip_sample(input[n, c] - prev_low - feedback, saturate)
                    #clip band
                    newband = freq_c*high + prev_band
                    state[c, 1] = clip_sample(newband, saturate)
                    #clip low
                    newlow = prev_low + freq_c*state[c, 1]
                    state[c, 0] = clip_sample(newlow, saturate)
                    notch = high + state[c, 0]
                    if (substate == 0):   #lowpass
                        subsample += clip_sample(state[c, 0], 1.5)
                    elif (substate == 1): #highpass
                        subsample += clip_sample(high, 1.5)
                    elif (substate == 2): #bandpass
                        subsample += clip_sample(state[c, 1], 1.5)
                    elif (substate == 3): #notch
                        subsample += clip_sample(notch, 1.5)
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
