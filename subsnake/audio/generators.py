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
# alg = 0.0: sine, 1.0: BLIT sawtooth, 2.0: BLIT pulse | width = 0.0 to 1.0
class WrappedOsc():
    def __init__(self, alg, amplitude, frequency, sample_rate, width=0.5):
        phase_increment = twopi * (frequency/sample_rate)
        self.state = np.array([0.0, amplitude, phase_increment], dtype=np.float32)
        self.state2 = np.array([0.0, amplitude, phase_increment], dtype=np.float32)
        self.hardSyncBuffer = np.zeros((2048, 2), dtype=np.float32)
        self.random_walk = np.zeros((2048), dtype=np.float32)
        self.walk_state = np.zeros((1), dtype=np.float32)
        self.walk_amt = 0.0
        self.blit_integrators = np.zeros((3, 2), dtype=np.float32)
        self.blep_integrator = np.zeros((1), dtype=np.float32)
        self.blit_states = np.array([[0.0, amplitude, phase_increment], [0.0, amplitude, phase_increment]], dtype=np.float32)
        self.blit_buffer = np.zeros((8192, 2))
        self.blit_buffer_read = np.zeros((1, 2), dtype=np.float32)
        self.blit_buffer_write = np.zeros((1, 2), dtype=np.int32)
        self.blit_blocker_ins = np.zeros((1, 2), dtype=np.float32)
        self.blit_blocker_outs = np.zeros((1, 2), dtype=np.float32)
        self.alg = alg
        self.pulsewidth = width
        self.smoothed_widths = np.zeros((1, 2), dtype=np.float32)
        self.smoothed_blep_width = np.zeros((1), dtype=np.float32)
        self.output_hpf = np.zeros((2), dtype=np.float32)
        self.freq = frequency
        self.amp = amplitude
        self.alg_type = 0
    
    def process_block(self, buffer, mod_buffers, mod_values):
        frames = len(buffer)
        self.generate_walk(self.random_walk[:frames], self.walk_state)
        if (self.alg == 0):
            self.generate_sine(self.state, buffer, self.random_walk[:frames], self.walk_amt, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_values[0], mod_values[1], mod_values[2], self.amp, self.freq)
        elif (self.alg == 1.0):
            if (self.alg_type == 0):
                self.blit_saw(buffer, self.blit_states, self.blit_integrators,
                          self.random_walk[:frames], self.walk_amt, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_values[0], mod_values[1], mod_values[2], self.amp, self.freq)
            else:
                self.polyblep_saw(self.state, buffer, self.random_walk, self.walk_amt, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_values[1], mod_values[2], mod_values[3], self.amp, self.freq)
        elif (self.alg == 2.0):
            if (self.alg_type == 0):
                self.blit_pulse(buffer, self.blit_states, self.blit_integrators, self.smoothed_widths,
                          self.random_walk[:frames], self.walk_amt, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_buffers[3], mod_values[0], mod_values[1], mod_values[2], mod_values[3], self.amp, self.freq, self.pulsewidth)
            else:
                self.polyblep_pulse(self.state, buffer, self.state2, self.pulsewidth, self.random_walk, self.walk_amt,
                                    mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_buffers[3], mod_values[0], mod_values[1], mod_values[2], mod_values[3], self.amp, self.freq)
        elif (self.alg == 3.0):
            if (self.alg_type == 0):
                self.blit_triangle(buffer, self.blit_states, self.blit_integrators, self.smoothed_widths,
                          self.random_walk[:frames], self.walk_amt, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_buffers[3], mod_values[0], mod_values[1], mod_values[2], mod_values[3], self.amp, self.freq, self.pulsewidth)
            else:
                self.polyblep_triangle(self.state, self.blep_integrator, self.smoothed_blep_width, self.output_hpf, buffer, self.state2, self.pulsewidth, self.random_walk, self.walk_amt,
                                    mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_buffers[3], mod_values[0], mod_values[1], mod_values[2], mod_values[3], self.amp, self.freq)

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

    def update_type(self, newType):
        self.alg_type = newType


    #phase-wrapped sine wave
    @staticmethod
    @njit(nogil=True, fastmath=True, cache=True)
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

    #anti-aliased sawtooth (polyBLEP)
    @staticmethod
    @njit(nogil=True, fastmath=True, cache=True)
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

    #anti-aliased pulse (polyBLEP)
    @staticmethod
    @njit(nogil=True, fastmath=True, cache=True)
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

    #anti-aliased trisaw (polyBLEP)
    # (width=0.5: triangle, width≈0.0: sawtooth, width≈1.0: ramp)
    @staticmethod
    @njit(nogil=True, fastmath=True, cache=True)
    def polyblep_triangle(state, integrator, smoothed_width, hpf, outdata, state2, width, walk_mod, walk_amt, pitch_mod, det_mod, amp_mod, width_mod, pm_amt, dm_amt, am_amt, wm_amt, amp=1.0, freq=440.0):
        frames = len(outdata)
        base_inc = twopi*freq*oneoverfs
        alpha = 1.0 - math.exp(-twopi*50.0*oneoverfs)
        for n in range(frames):
            #modulate phase increment
            state[2] = base_inc + base_inc*pitch_mod[n]*pm_amt + max_det_inc*det_mod[n]*dm_amt + max_det_inc*walk_mod[n]*walk_amt

            #smooth width
            new_width = max(.01, min(.99, width + width_mod[n]*wm_amt))
            smoothed_width[0] += alpha*(new_width - smoothed_width[0])

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

            state2[0] = state[0] + twopi*smoothed_width[0]
            norm_phase = state2[0]*oneovertwopi
            wrapped_phase = norm_phase - np.floor(norm_phase)
            state2[0] = twopi*wrapped_phase
            if (state[0] > twopi):
                state[0] -= twopi

            #generate pulse
            slope = sample - sample2

            #integrate pulse -> triangle
            leak_c = 1.0 - state[2]*.1
            integrator[0] = integrator[0]*leak_c + slope
            hpf_out = integrator[0] - hpf[0] + .995*hpf[1]
            hpf[0] = integrator[0]
            hpf[1] = hpf_out

            #output
            scale = (state[2]*oneovertwopi)/(smoothed_width[0]*(1.0 - smoothed_width[0]))
            output_sample = hpf_out*scale*(amp - amp_mod[n]*am_amt)

            outdata[n, 0] = output_sample
            outdata[n, 1] = output_sample

    #random walk generator
    @staticmethod
    @njit(nogil=True, fastmath=True, cache=True)
    def generate_walk(output, walk_state):
        frames = len(output)
        walk_offset = 2*random.random() - 1.0
        for n in range(0, frames):
            walk_state[0] = walk_state[0]*.99999 + .00001*walk_offset
            output[n] = walk_state[0]

    #anti-aliased sawtooth (BLIT)
    @staticmethod
    @njit(nogil=True, fastmath=True, cache=True)
    def blit_saw(outdata, states, integrators,
                 walk_mod, walk_amt, pitch_mod, det_mod, amp_mod, pm_amt, dm_amt, am_amt, amp=1.0, freq=440.0):
        frames = len(outdata)
        base_inc = freq*oneoverfs
        for n in range(0, frames):
            for c in range(0, 2):
                mod_inc = base_inc + base_inc*pitch_mod[n]*pm_amt + max_det_inc*walk_mod[n]*walk_amt + max_det_inc*det_mod[n]*dm_amt
                new_freq = max(1e-9, mod_inc)*fs
                harmonics = 2*int(nyquist/new_freq) + 1
                phase = states[c, 0]
                leak_c = 1.0 - twopi*mod_inc*.1
                kernel_den = math.sin(np.pi*phase)
                if phase < .0000001:
                    slope = 1.0-harmonics
                else:
                    slope = 1.0-math.sin(np.pi*harmonics*phase)/kernel_den
                slope *= mod_inc*2
                integrators[0, c] = integrators[0, c]*leak_c + slope
                states[c, 0] += mod_inc
                states[c, 0] -= np.floor(states[c, 0])

                output_sample = integrators[0, c]
                mod_amp = max(-1.0, min(1.0, amp + amp_mod[n]*am_amt))
                outdata[n, c] = output_sample*mod_amp

    #anti-aliased pulse (BLIT)
    @staticmethod
    @njit(nogil=True, fastmath=True, cache=True)
    def blit_pulse(outdata, states, integrators, smoothed_widths,
                    walk_mod, walk_amt, pitch_mod, det_mod, amp_mod, width_mod, pm_amt, dm_amt, am_amt, wm_amt, amp=1.0, freq=440.0, width=0.5):
        frames = len(outdata)
        base_inc = freq*oneoverfs
        alpha = 1.0 - math.exp(-twopi*50.0*oneoverfs)
        leak_c = .9995
        for n in range(0, frames):
            for c in range(0, 2):
                mod_inc = base_inc + base_inc*pitch_mod[n]*pm_amt + max_det_inc*walk_mod[n]*walk_amt + max_det_inc*det_mod[n]*dm_amt
                new_freq = max(1e-9, mod_inc)*fs
                harmonics = 2*int(nyquist/new_freq) + 1
                new_width = max(0.0, min(1.0, width + width_mod[n]*wm_amt))
                smoothed_widths[0, c] += alpha*(new_width - smoothed_widths[0, c])
                smoothed_width = smoothed_widths[0, c]
                phase1 = states[c, 0]
                phase2 = phase1 + smoothed_width
                phase2 -= np.floor(phase2)
                kernel_den_1 = math.sin(np.pi*phase1)
                kernel_den_2 = math.sin(np.pi*phase2)
                if phase1 < 1e-9:
                    slope1 = 1.0-harmonics
                else:
                    slope1 = 1.0-math.sin(np.pi*harmonics*phase1)/kernel_den_1
                if phase2 < 1e-9:
                    slope2 = 1.0-harmonics
                else:
                    slope2 = 1.0-math.sin(np.pi*harmonics*phase2)/kernel_den_2
                slope1 *= mod_inc*2
                slope2 *= mod_inc*2
                integrators[0, c] = integrators[0, c]*leak_c + slope1
                integrators[1, c] = integrators[1, c]*leak_c + slope2
                states[c, 0] += mod_inc
                states[c, 0] -= np.floor(states[c, 0])

                output_sample = integrators[0, c] - integrators[1, c]
                mod_amp = max(-1.0, min(1.0, amp + amp_mod[n]*am_amt))
                outdata[n, c] = output_sample*mod_amp

    #anti-aliased trisaw (BLIT)
    # (width=0.5: triangle, width≈0.0: sawtooth, width≈1.0: ramp)
    @staticmethod
    @njit(nogil=True, fastmath=True, cache=True)
    def blit_triangle(outdata, states, integrators, smoothed_widths,
                    walk_mod, walk_amt, pitch_mod, det_mod, amp_mod, width_mod, pm_amt, dm_amt, am_amt, wm_amt, amp=1.0, freq=440.0, width=0.5):
        frames = len(outdata)
        base_inc = freq*oneoverfs
        alpha = 1.0 - math.exp(-twopi*50.0*oneoverfs)
        for n in range(0, frames):
            for c in range(0, 2):
                mod_inc = base_inc + base_inc*pitch_mod[n]*pm_amt + max_det_inc*walk_mod[n]*walk_amt + max_det_inc*det_mod[n]*dm_amt
                new_freq = max(1e-9, mod_inc)*fs
                harmonics = 2*int(nyquist/new_freq) + 1
                new_width = max(.01, min(.99, width + width_mod[n]*wm_amt))
                smoothed_widths[0, c] += alpha*(new_width - smoothed_widths[0, c])
                smoothed_width = smoothed_widths[0, c]
                phase1 = states[c, 0]
                phase2 = phase1 + smoothed_width
                phase2 -= np.floor(phase2)
                leak_c = 1.0 - twopi*mod_inc*.1
                kernel_den_1 = math.sin(np.pi*phase1)
                kernel_den_2 = math.sin(np.pi*phase2)
                if phase1 < 1e-9:
                    slope1 = 1.0-harmonics
                else:
                    slope1 = 1.0-math.sin(np.pi*harmonics*phase1)/kernel_den_1
                if phase2 < 1e-9:
                    slope2 = 1.0-harmonics
                else:
                    slope2 = 1.0-math.sin(np.pi*harmonics*phase2)/kernel_den_2
                slope1 *= mod_inc*2
                slope2 *= mod_inc*2
                integrators[0, c] = integrators[0, c]*leak_c + slope1
                integrators[1, c] = integrators[1, c]*leak_c + slope2
                states[c, 0] += mod_inc
                states[c, 0] -= np.floor(states[c, 0])

                blit_pulse = (integrators[0, c] - integrators[1, c])
                integrators[2, c] = integrators[2, c]*leak_c + blit_pulse
                scale = (mod_inc)/(smoothed_width*(1.0 - smoothed_width))
                output_sample = integrators[2, c]*scale
                mod_amp = max(-1.0, min(1.0, amp + amp_mod[n]*am_amt))
                outdata[n, c] = output_sample*mod_amp