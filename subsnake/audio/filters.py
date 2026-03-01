import numpy as np
import math
from numba import njit

fs = 44100
twopi = 2*np.pi
oneoverpi = 1/np.pi

# Hal Chamberlin's digital SV Filter w/ nonlinear feedback | 8x oversampled
# type = 1.0: lowpass, 2.0: highpass, 3.0: bandpass, 4.0: notch
class HalSVF():
    def __init__(self, type, cutoff, resonance, drive=1.0, saturate=8.0):
        self.cutoff = cutoff
        self.resonance = resonance
        self.drive = drive
        self.saturate = saturate
        self.env_amount = 0.0
        self.base_freq = 440.0
        self.key_tracking = 0.0

        q = resonance
        f = 2*math.sin(np.pi*(cutoff/(8*fs)))

        #init parameter buffer | lowpass, bandpass, tuning, dampening, type, drive, saturation
        self.state = np.array([[0.0, 0.0, f, q, type, drive, saturate], [0.0, 0.0, f, q, type, drive, saturate]], dtype=np.float32)
    
    def process_block(self, input, output, fenv, mod_buffer, mod_values):
        self.filter_block(self.state, input, output, fenv, self.env_amount, HalSVF.clip_sample, self.cutoff, self.base_freq, self.key_tracking,
                          mod_buffer[0], mod_buffer[1], mod_buffer[2], mod_buffer[3], mod_buffer[4], mod_values[0], mod_values[1], mod_values[2], mod_values[3], mod_values[4])

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

    def update_key_tracking(self, amount):
        self.key_tracking = amount

    def update_base_freq(self, newFreq):
        self.base_freq = newFreq
        
    @staticmethod
    @njit(nogil=True, fastmath=True, cache=True, inline="always")
    def filter_block(state, input, output, fenv, fenv_amount, clip_sample, cutoff, base_freq, kt_amt, freq_mod, res_mod, drive_mod, sat_mod, fenv_mod, fm_val, rm_val, dm_val, sm_val, fem_val):
        cutoff_freq_amt = (1.0 - kt_amt)*cutoff
        kt_freq_amt = kt_amt*base_freq*32.0
        for c in range (2):
            for n in range(len(output)):
                freq_mod_amt = freq_mod[n]*fm_val
                res_mod_amt = res_mod[n]*rm_val
                drive_mod_amt = drive_mod[n]*dm_val
                sat_mod_amt = sat_mod[n]*sm_val
                subsample = 0.0
                prev_low = state[c, 0]
                prev_band = state[c, 1]
                fenv_amount = max(-1.0, min(1.0, fenv_amount + fenv_mod[n]*fem_val))
                new_cutoff = max(0.1, min(cutoff_freq_amt + kt_freq_amt + 14080.0*freq_mod_amt + 14080.0*fenv[n, c]*fenv_amount, 14080.0))
                freq_c = 2*math.sin(np.pi*(new_cutoff/(8*fs)))
                res_c = max(.02, min(20.0, state[c, 3] + res_mod_amt))
                substate = int(state[c, 4])
                drive = max(.025, min(9.0, state[c, 5] + 4.5*drive_mod_amt))
                saturate = max(1.0, min(12.0, state[c, 6] + 5.5*sat_mod_amt))
                oneoverdrive = 1.0/drive
                for m in range(8):
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
                sample = subsample*0.125
                output[n, c] = sample

    @staticmethod
    @njit(nogil=True, fastmath=True, cache=True)
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
