import numpy as np
import math
from numba import njit
import random

fs = 44100
nyquist = 22050
oneoverfs = 1.0/float(fs)
twopi = 2*np.pi
oneoverpi = 1/np.pi
oneovertwopi = 1/twopi
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
        self.random_walk = np.zeros((2048), dtype=np.float32)
        self.walk_state = np.zeros((1), dtype=np.float32)
        self.walk_amt = 0.0
        self.blit_integrators = np.zeros((1, 2), dtype=np.float32)
        self.blit_states = np.array([[0.0, amplitude, phase_increment], [0.0, amplitude, phase_increment]], dtype=np.float32)
        self.blit_buffer = np.zeros((8192, 2))
        self.blit_buffer_read = np.zeros((1, 2), dtype=np.float32)
        self.blit_buffer_write = np.zeros((1, 2), dtype=np.int32)
        self.alg = alg
        self.pulsewidth = width
        self.freq = frequency
        self.amp = amplitude
    
    def process_block(self, buffer, mod_buffers, mod_values):
        frames = len(buffer)
        self.generate_walk(self.random_walk[:frames], self.walk_state)
        if (self.alg == 0):
            self.generate_sine(self.state, buffer, self.random_walk[:frames], self.walk_amt, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_values[0], mod_values[1], mod_values[2], self.amp, self.freq)
        elif (self.alg == 1.0):
            self.blit_saw(buffer, self.blit_buffer, self.blit_buffer_write, self.blit_states, self.blit_integrators, self.hermite_interpolate,  
                          self.random_walk[:frames], self.walk_amt, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_values[0], mod_values[1], mod_values[2], self.amp, self.freq)
        elif (self.alg == 2.0):
            self.blit_pulse(buffer, self.blit_buffer, self.blit_buffer_write, self.blit_states, self.blit_integrators, self.hermite_interpolate,  
                          self.random_walk[:frames], self.walk_amt, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_buffers[3], mod_values[0], mod_values[1], mod_values[2], mod_values[3], self.amp, self.freq, self.pulsewidth)

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

    def update_drift(self, newDrift):
        self.walk_amt = newDrift


    #phase-wrapped sine wave
    @staticmethod
    @njit(nogil=True, fastmath=True)
    def generate_sine(state, outdata, walk_mod, walk_amt, pitch_mod, det_mod, amp_mod, pm_amt, dm_amt, am_amt, amp=1.0, freq=440.0):
        base_inc = twopi*freq*oneoverfs
        for n in range(len(outdata)):
            state[2] = base_inc + base_inc*pitch_mod[n]*pm_amt + max_det_inc*det_mod[n]*dm_amt + max_det_inc*walk_mod[n]*walk_amt
            sample = state[1] * math.sin(state[0])
            outdata[n][0] = sample*(amp - amp_mod[n]*am_amt)
            outdata[n][1] = sample*(amp - amp_mod[n]*am_amt)
            state[0] += state[2]
            if (state[0] > twopi):
                state[0] -= twopi

    #anti-aliased sawtooth
    @staticmethod
    @njit(nogil=True, fastmath=True)
    def polyblep_saw(state, outdata, walk_mod, walk_amt, pitch_mod, det_mod, amp_mod, pm_amt, dm_amt, am_amt, amp=1.0, freq=440.0):
        frames = len(outdata)
        base_inc = twopi*freq*oneoverfs
        for n in range(frames):
            #modulate phase increment
            state[2] = base_inc + base_inc*pitch_mod[n]*pm_amt + max_det_inc*det_mod[n]*dm_amt + max_det_inc*walk_mod[n]*walk_amt

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
    def polyblep_pulse(state, outdata, state2, width, walk_mod, walk_amt, pitch_mod, det_mod, amp_mod, width_mod, pm_amt, dm_amt, am_amt, wm_amt, amp=1.0, freq=440.0):
        frames = len(outdata)
        base_inc = twopi*freq*oneoverfs
        for n in range(frames):
            #modulate phase increment
            state[2] = base_inc + base_inc*pitch_mod[n]*pm_amt + max_det_inc*det_mod[n]*dm_amt + max_det_inc*walk_mod[n]*walk_amt

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
            state2[0] = state[0] + twopi*width + twopi*width_mod[n]*wm_amt
            norm_phase = state2[0]*oneovertwopi
            wrapped_phase = norm_phase - np.floor(norm_phase)
            state2[0] = twopi*wrapped_phase
            if (state[0] > twopi):
                state[0] -= twopi

            #output
            sample -= sample2
            sample *= state[1]
            outdata[n, 0] = sample*(amp - amp_mod[n]*am_amt)
            outdata[n, 1] = sample*(amp - amp_mod[n]*am_amt)

    @staticmethod
    @njit(nogil=True, fastmath=True)
    def generate_walk(output, walk_state):
        frames = len(output)
        walk_offset = 2*random.random() - 1.0
        for n in range(0, frames):
            walk_state[0] = walk_state[0]*.99999 + .00001*walk_offset
            output[n] = walk_state[0]

    @staticmethod
    @njit(nogil=True, fastmath=True)
    def blit_saw(outdata, buffer, write_heads, states, integrators, hermite_interpolate,
                 walk_mod, walk_amt, pitch_mod, det_mod, amp_mod, pm_amt, dm_amt, am_amt, amp=1.0, freq=440.0):
        frames = len(outdata)
        buffer_len = len(buffer)
        for n in range(0, frames):
            for c in range(0, 2):
                increment = freq*oneoverfs + max_det_inc*walk_mod[n]*walk_amt + max_det_inc*det_mod[n]*dm_amt
                increment = max(1e-9, increment)
                period = 1/increment
                new_freq = increment*fs
                harmonics = 2*int(nyquist/new_freq) + 1
                phase = states[c, 0]
                leak_c = 1.0 - twopi*increment*.1
                kernel_den = math.sin(np.pi*phase)
                if phase < .0000001:
                    slope = 1.0-harmonics
                else:
                    slope = 1.0-math.sin(np.pi*harmonics*phase)/kernel_den
                slope *= increment*2
                integrators[0, c] = integrators[0, c]*leak_c + slope
                states[c, 0] += increment
                states[c, 0] -= np.floor(states[c, 0])

                buffer[write_heads[0, c], c] = integrators[0, c]
                base_delay = period + 2.0
                total_delay = base_delay + pm_amt*pitch_mod[n]*period
                int_offset = np.floor(total_delay)
                frac_offset = total_delay - int_offset
                read_head = write_heads[0, c] - int(int_offset)
                read_head = read_head % buffer_len
                y0_index = read_head-1
                if y0_index < 0:
                    y0_index += buffer_len
                y2_index = read_head+1
                if y2_index >= buffer_len:
                    y2_index -= buffer_len
                y3_index = read_head+2
                if y3_index >= buffer_len:
                    y3_index -= buffer_len
                mod_amp = max(-1.0, min(1.0, amp + amp_mod[n]*am_amt))
                outdata[n, c] = hermite_interpolate(buffer[y0_index, c], buffer[read_head, c], buffer[y2_index, c], buffer[y3_index, c], frac_offset)*mod_amp
                write_heads[0, c] += 1
                if write_heads[0, c] >= buffer_len:
                    write_heads[0, c] -= buffer_len

    @staticmethod
    @njit(nogil=True, fastmath=True)
    def blit_pulse(outdata, buffer, write_heads, states, integrators, hermite_interpolate,
                    walk_mod, walk_amt, pitch_mod, det_mod, amp_mod, width_mod, pm_amt, dm_amt, am_amt, wm_amt, amp=1.0, freq=440.0, width=0.5):
        frames = len(outdata)
        buffer_len = len(buffer)
        for n in range(0, frames):
            for c in range(0, 2):
                increment = freq*oneoverfs + max_det_inc*walk_mod[n]*walk_amt + max_det_inc*det_mod[n]*dm_amt
                increment = max(1e-9, increment)
                period = 1/increment
                new_freq = increment*fs
                harmonics = 2*int(nyquist/new_freq) + 1
                phase1 = states[c, 0]
                new_width = max(0.0, min(1.0, width + width_mod[n]*wm_amt))
                phase2 = phase1 + new_width
                phase2 -= np.floor(phase2)
                leak_c = 1.0 - twopi*increment*.1
                kernel_den_rise = math.sin(np.pi*phase1)
                kernel_den_fall = math.sin(np.pi*phase2)
                if phase1 < .0000001:
                    slope_rise = harmonics
                else:
                    slope_rise = math.sin(np.pi*harmonics*phase1)/kernel_den_rise
                if phase2 < .0000001:
                    slope_fall = harmonics
                else:
                    slope_fall = math.sin(np.pi*harmonics*phase2)/kernel_den_fall
                slope = (slope_rise - slope_fall)*increment*2
                integrators[0, c] = integrators[0, c]*leak_c + slope
                states[c, 0] += increment
                states[c, 0] -= np.floor(states[c, 0])

                buffer[write_heads[0, c], c] = integrators[0, c]
                base_delay = period + 2.0
                total_delay = base_delay + pm_amt*pitch_mod[n]*period
                int_offset = np.floor(total_delay)
                frac_offset = total_delay - int_offset
                read_head = write_heads[0, c] - int(int_offset)
                read_head = read_head % buffer_len
                y0_index = read_head-1
                if y0_index < 0:
                    y0_index += buffer_len
                y2_index = read_head+1
                if y2_index >= buffer_len:
                    y2_index -= buffer_len
                y3_index = read_head+2
                if y3_index >= buffer_len:
                    y3_index -= buffer_len
                mod_amp = max(-1.0, min(1.0, amp + amp_mod[n]*am_amt))
                outdata[n, c] = hermite_interpolate(buffer[y0_index, c], buffer[read_head, c], buffer[y2_index, c], buffer[y3_index, c], frac_offset)*mod_amp
                write_heads[0, c] += 1
                if write_heads[0, c] >= buffer_len:
                    write_heads[0, c] -= buffer_len

    @staticmethod
    @njit(nogil=True, fastmath=True)
    def hermite_interpolate(y0, y1, y2, y3, frac):
        c0 = y1
        c1 = 0.5*(y2-y0)
        c2 = y0 - 2.5*y1 + 2.0*y2 - 0.5*y3
        c3 = 0.5*(y3-y0) + 1.5*(y1-y2)

        return ((c3*frac + c2)*frac + c1)*frac + c0