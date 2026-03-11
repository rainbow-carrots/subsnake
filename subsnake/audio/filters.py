import numpy as np
import math
from numba import njit

fs = 44100
twopi = 2*np.pi
oneoverpi = 1/np.pi

# Hal Chamberlin's digital SV Filter w/ nonlinear feedback | 8x oversampled
class HalSVF():
    def __init__(self, type, cutoff, resonance, drive=1.0, saturate=8.0):
        self.integrators = np.ascontiguousarray(np.zeros((2, 2), dtype=np.float32))
        self.cutoff = cutoff
        self.resonance = resonance
        self.drive = drive
        self.saturate = saturate
        self.env_amount = 0.0
        self.base_freq = 440.0
        self.key_tracking = 0.0
        self.mode = 0
        self.params = np.zeros((8), dtype=np.float32)
        self.mod_values = np.zeros((5), dtype=np.float32)
    
    def process_block(self, input, output, fenv, mod_buffer, mod_values):
        self.params[:] = [self.cutoff, self.resonance, self.drive, self.saturate, self.mode, self.base_freq, self.key_tracking, self.env_amount]
        self.mod_values[:] = [mod_values[0], mod_values[1], mod_values[2], mod_values[3], mod_values[4]]
        self.filter_block(input, output, self.integrators, self.params, fenv, HalSVF.clip_sample,
                          mod_buffer[0], mod_buffer[1], mod_buffer[2], mod_buffer[3], mod_buffer[4], self.mod_values)

    def update_cutoff(self, freq):
        self.cutoff = freq

    def update_resonance(self, res):
        self.resonance = res

    def update_drive(self, drive):
        self.drive = drive
    
    def update_type(self, type):
        self.mode = type

    def update_saturate(self, saturate):
        self.saturate = saturate

    def update_env_amount(self, amount):
        self.env_amount = amount

    def update_key_tracking(self, amount):
        self.key_tracking = amount

    def update_base_freq(self, newFreq):
        self.base_freq = newFreq
        
    @staticmethod
    @njit(nogil=True, fastmath=True, inline="always")
    def filter_block(input, output, states, params, fenv, clip_sample, freq_mod, res_mod, drive_mod, sat_mod, fenv_mod, mod_vals):
        #assign scalars
        cutoff = params[0]
        resonance = params[1]
        drive = params[2]
        saturate = params[3]
        mode = params[4]
        base_freq = params[5]
        kt_amt = params[6]
        fenv_amount = params[7]
        fm_val = mod_vals[0]
        rm_val = mod_vals[1]
        dm_val = mod_vals[2]
        sm_val = mod_vals[3]
        fem_val = mod_vals[4]

        #calculate key tracking
        cutoff_freq_amt = (1.0 - kt_amt)*cutoff
        kt_freq_amt = kt_amt*base_freq*32.0

        #main loop
        for c in range (2):
            for n in range(len(output)):
                freq_mod_amt = freq_mod[n]*fm_val
                res_mod_amt = res_mod[n]*rm_val
                drive_mod_amt = drive_mod[n]*dm_val
                sat_mod_amt = sat_mod[n]*sm_val
                subsample = 0.0
                prev_low = states[0, c]
                prev_band = states[1, c]
                fenv_amount = max(-1.0, min(1.0, fenv_amount + fenv_mod[n]*fem_val))
                new_cutoff = max(0.1, min(cutoff_freq_amt + kt_freq_amt + 14080.0*freq_mod_amt + 14080.0*fenv[n, c]*fenv_amount, 14080.0))
                freq_c = 2*math.sin(np.pi*(new_cutoff/(8*fs)))
                res_c = max(.02, min(20.0, resonance + res_mod_amt))
                substate = mode
                new_drive = max(.025, min(9.0, drive + 4.5*drive_mod_amt))
                new_saturate = max(1.0, min(12.0, saturate + 5.5*sat_mod_amt))
                oneoverdrive = 1.0/new_drive
                for m in range(8):
                    feedback = res_c*(np.tanh(prev_band*new_drive)*oneoverdrive)
                    high = clip_sample(input[n, c] - prev_low - feedback, new_saturate)
                    #clip band
                    newband = freq_c*high + prev_band
                    states[1, c] = clip_sample(newband, new_saturate)
                    #clip low
                    newlow = prev_low + freq_c*states[1, c]
                    states[0, c] = clip_sample(newlow, new_saturate)
                    notch = high + states[0, c]
                    if (substate == 0):   #lowpass
                        subsample += clip_sample(states[0, c], 1.5)
                    elif (substate == 1): #highpass
                        subsample += clip_sample(high, 1.5)
                    elif (substate == 2): #bandpass
                        subsample += clip_sample(states[1, c], 1.5)
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

# ZDF-solved Chamberlin SVF w/ nonlinear resonance & output soft clipping
class ZDFSVF():
    def __init__(self):
        self.integrator_states = np.ascontiguousarray(np.zeros((2, 2), dtype=np.float32))
        self.cutoff = 20000.0
        self.feedback = 1.0
        self.drive = 1.0
        self.saturate = 8.0
        self.env_amount = 0.0
        self.base_freq = 440.0
        self.key_tracking = 0.0
        self.mode = 0
        self.params = np.zeros((8), dtype=np.float32)
        self.mod_values = np.zeros((5), dtype=np.float32)
    
    def process_block(self, filt_input, filt_output, fenv, mod_buffers, mod_values):
        self.params[:] = [self.cutoff, self.feedback, self.drive, self.saturate, self.mode, self.base_freq, self.key_tracking, self.env_amount]
        self.mod_values[:] = [mod_values[0], mod_values[1], mod_values[2], mod_values[3], mod_values[4]]
        self.filter_block(filt_input, filt_output, self.integrator_states, self.params, fenv,
                          mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_buffers[3], mod_buffers[4], self.mod_values,
                          self.trapezoidal_integrate, self.clip_sample)

    def update_cutoff(self, freq):
        self.cutoff = freq

    def update_resonance(self, res):
        self.feedback = res

    def update_drive(self, drive):
        self.drive = drive

    def update_saturate(self, saturate):
        self.saturate = saturate
    
    def update_type(self, type):
        self.mode = type

    def update_env_amount(self, amount):
        self.env_amount = amount

    def update_key_tracking(self, amount):
        self.key_tracking = amount

    def update_base_freq(self, newFreq):
        self.base_freq = newFreq

    @staticmethod
    @njit(nogil=True, fastmath=True, inline="always")
    def filter_block(filt_in, filt_out, states, params, fenv, freq_mod, res_mod, drive_mod, sat_mod, fenv_mod, mod_vals, trap_int, clip):
        #assign scalars
        cutoff = params[0]
        feedback = params[1]
        drive = params[2]
        saturate = params[3]
        mode = params[4]
        base_freq = params[5]
        kt_amt = params[6]
        fenv_amt = params[7]
        fm_val = mod_vals[0]
        rm_val = mod_vals[1]
        dm_val = mod_vals[2]
        sm_val = mod_vals[3]
        fem_val = mod_vals[4]

        #calculate key tracking
        cutoff_freq_amt = (1.0 - kt_amt)*cutoff
        kt_freq_amt = kt_amt*base_freq*32.0

        #main loop
        for c in range(2):
            for n in range(len(filt_out)):
                freq_mod_amt = freq_mod[n]*fm_val
                res_mod_amt = res_mod[n]*rm_val
                drive_mod_amt = drive_mod[n]*dm_val
                sat_mod_amt = sat_mod[n]*sm_val
                fenv_amount = max(-1.0, min(1.0, fenv_amt + fenv_mod[n]*fem_val))
                new_cutoff = max(0.1, min(cutoff_freq_amt + kt_freq_amt + 20000.0*freq_mod_amt + 20000.0*fenv[n, c]*fenv_amount, 20000.0))
                freq_c = math.tan(np.pi*(new_cutoff/fs))
                res_c = max(.02, min(20.0, feedback + res_mod_amt))

                new_drive = max(.025, min(9.0, drive + 4.5*drive_mod_amt))
                new_saturate = max(1.0, min(12.0, saturate + 5.5*sat_mod_amt))
                oneoverdrive = 1.0/new_drive
                
                prev_band = states[0, c]
                if prev_band != 0.0:
                    nl_res_c = res_c*math.tanh((prev_band*new_drive)*oneoverdrive) / prev_band
                else:
                    nl_res_c = res_c

                HP_out = (filt_in[n, c] - states[0, c]*(nl_res_c + freq_c) - states[1, c])/(1 + nl_res_c*freq_c + freq_c**2)
                HP_clipped = clip(HP_out, new_saturate)

                BP_out, next_band_state = trap_int(HP_clipped, freq_c, states[0, c])
                BP_clipped = clip(BP_out, new_saturate)
                states[0, c] = clip(next_band_state, new_saturate)

                LP_out, next_low_state = trap_int(BP_clipped, freq_c, states[1, c])
                LP_clipped = clip(LP_out, new_saturate)
                states[1, c] = clip(next_low_state, new_saturate)

                N_out = HP_clipped + LP_clipped

                if mode == 0:
                    filt_out[n, c] = LP_clipped
                elif mode == 1:
                    filt_out[n, c] = BP_clipped
                elif mode == 2:
                    filt_out[n, c] = HP_clipped
                elif mode == 3:
                    filt_out[n, c] = N_out

    @staticmethod
    @njit(nogil=True, fastmath=True)
    def trapezoidal_integrate(x, g, state):
        v = g*x + state
        next_state = v + g*x
        return v, next_state
    
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