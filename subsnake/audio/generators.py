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
integrator_gain = math.tan(np.pi * 10.0/fs)
g_norm = 1.0/(1.0 + integrator_gain)

# phase-wrapped oscillator
# alg = 0.0: sine, 1.0: BLIT sawtooth, 2.0: BLIT pulse | width = 0.0 to 1.0
class WrappedOsc():
    def __init__(self, alg, amplitude, frequency, sample_rate, width=0.5):
        phase_increment = twopi * (frequency/sample_rate)
        self.state = np.ascontiguousarray(np.array([0.0, amplitude, phase_increment], dtype=np.float32))
        self.state2 = np.ascontiguousarray(np.array([0.0, amplitude, phase_increment], dtype=np.float32))
        self.random_walk = np.ascontiguousarray(np.zeros((2048), dtype=np.float32))
        self.walk_state = np.zeros((1), dtype=np.float32)
        self.walk_amt = 0.0
        self.blit_integrators = np.ascontiguousarray(np.zeros((3, 2), dtype=np.float32))
        self.blep_integrator = np.zeros((1), dtype=np.float32)
        self.blit_states = np.ascontiguousarray(np.array([[0.0, amplitude, phase_increment, 0.0], [0.0, amplitude, phase_increment, 0.0]], dtype=np.float32))
        self.blit_blocker_ins = np.zeros((1, 2), dtype=np.float32)
        self.blit_blocker_outs = np.zeros((1, 2), dtype=np.float32)
        self.blit_env_follower = np.zeros((2, 2), dtype=np.float32)
        self.blit_env_follower[0][:] = -10000.0
        self.blit_env_follower[1][:] = 10000.0
        self.alg = alg
        self.pulsewidth = width
        self.smoothed_widths = np.zeros((1, 2), dtype=np.float32)
        self.smoothed_blep_width = np.zeros((1), dtype=np.float32)
        self.output_hpf = np.zeros((2), dtype=np.float32)
        self.freq = frequency
        self.amp = amplitude
        self.alg_type = 0

        #init compile calls
        mod_test = np.zeros((16), dtype=np.float32)
        test_out = np.zeros((16, 2), dtype=np.float32)
        generate_walk(self.random_walk[:16], self.walk_state)
        generate_sine(self.state, test_out, self.random_walk[:16], 1.0, self.pulsewidth, mod_test, mod_test, mod_test, mod_test, 0.0, 0.0, 0.0, 0.0, 1.0, 440.0)
        polyblep_saw(self.state, test_out, self.pulsewidth, self.random_walk[:16], 1.0, mod_test, mod_test, mod_test, mod_test, 0.0, 0.0, 0.0, 0.0, 1.0, 440.0)
        polyblep_pulse(self.state, test_out, self.state2, 0.5, self.random_walk[:16], 1.0, mod_test, mod_test, mod_test, mod_test, 0.0, 0.0, 0.0, 0.0, 1.0, 440.0)
        polyblep_triangle(self.state, self.blep_integrator, self.smoothed_blep_width, self.output_hpf, test_out, self.state2, 0.5, self.random_walk[:16], 1.0, mod_test, mod_test, mod_test, mod_test, 0.0, 0.0, 0.0, 0.0, 1.0, 440.0)
        blit_saw(test_out, self.blit_states, self.blit_integrators, self.pulsewidth, self.random_walk[:16], 1.0, mod_test, mod_test, mod_test, mod_test, 0.0, 0.0, 0.0, 0.0, 0.5, 440.0)
        blit_pulse(test_out, self.blit_states, self.blit_integrators, self.smoothed_widths, self.random_walk[:16], 1.0, mod_test, mod_test, mod_test, mod_test, 0.0, 0.0, 0.0, 0.0, 0.5, 440.0, 0.5)
        blit_triangle(test_out, self.blit_states, self.blit_integrators, self.smoothed_widths, self.blit_env_follower, self.random_walk[:16], 1.0, mod_test, mod_test, mod_test, mod_test, 0.0, 0.0, 0.0, 0.0, 0.5, 440.0, 0.5)
    
    def process_block(self, buffer, mod_buffers, mod_values):
        frames = len(buffer)
        generate_walk(self.random_walk[:frames], self.walk_state)
        if (self.alg == 0):
            generate_sine(self.state, buffer, self.random_walk[:frames], self.walk_amt, self.pulsewidth, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_buffers[3], mod_values[0], mod_values[1], mod_values[2], mod_values[3], self.amp, self.freq)
        elif (self.alg == 1.0):
            if (self.alg_type == 0):
                blit_saw(buffer, self.blit_states, self.blit_integrators, self.pulsewidth,
                          self.random_walk[:frames], self.walk_amt, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_buffers[3], mod_values[0], mod_values[1], mod_values[2], mod_values[3], self.amp, self.freq)
            else:
                polyblep_saw(self.state, buffer, self.pulsewidth, self.random_walk, self.walk_amt, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_buffers[3], mod_values[0], mod_values[1], mod_values[2], mod_values[3], self.amp, self.freq)
        elif (self.alg == 2.0):
            if (self.alg_type == 0):
                blit_pulse(buffer, self.blit_states, self.blit_integrators, self.smoothed_widths,
                          self.random_walk[:frames], self.walk_amt, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_buffers[3], mod_values[0], mod_values[1], mod_values[2], mod_values[3], self.amp, self.freq, self.pulsewidth)
            else:
                polyblep_pulse(self.state, buffer, self.state2, self.pulsewidth, self.random_walk, self.walk_amt,
                                    mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_buffers[3], mod_values[0], mod_values[1], mod_values[2], mod_values[3], self.amp, self.freq)
        elif (self.alg == 3.0):
            if (self.alg_type == 0):
                blit_triangle(buffer, self.blit_states, self.blit_integrators, self.smoothed_widths, self.blit_env_follower,
                          self.random_walk[:frames], self.walk_amt, mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_buffers[3], mod_values[0], mod_values[1], mod_values[2], mod_values[3], self.amp, self.freq, self.pulsewidth)
            else:
                polyblep_triangle(self.state, self.blep_integrator, self.smoothed_blep_width, self.output_hpf, buffer, self.state2, self.pulsewidth, self.random_walk, self.walk_amt,
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

    def reset_buffers(self):
        self.blit_integrators[:, :] = 0.0
        self.blep_integrator[0] = 0.0
        self.blit_blocker_ins[0, :] = 0.0
        self.blit_blocker_outs[0, :] = 0.0
        self.blit_env_follower[0][:] = -10000.0
        self.blit_env_follower[1][:] = 10000.0

#numba DSP - oscillators
#-naive
#--sinusoid (w/ bipolar "width" mod (amplitude))
@njit(nogil=True, fastmath=True, cache=True)
def generate_sine(state, outdata, walk_mod, walk_amt, width, pitch_mod, det_mod, amp_mod, width_mod, pm_amt, dm_amt, am_amt, wm_amt, amp=1.0, freq=440.0):
    base_inc = twopi*freq*oneoverfs
    for n in range(len(outdata)):
        state[2] = base_inc + base_inc*pitch_mod[n]*pm_amt + max_det_inc*det_mod[n]*dm_amt + max_det_inc*walk_mod[n]*walk_amt
        mod_width = 2*np.abs(0.5 - (width + width_mod[n]*wm_amt))
        mod_amp = max(-1.0, min(1.0, (amp + amp_mod[n]*am_amt)*(1.0 - mod_width)))
        sample = math.sin(state[0])*mod_amp
        outdata[n, :] = sample
        state[0] += state[2]
        if (state[0] > twopi):
            state[0] -= twopi

#-polyBLEP
#--anti-aliased sawtooth
@njit(nogil=True, fastmath=True, cache=True)
def polyblep_saw(state, outdata, width, walk_mod, walk_amt, pitch_mod, det_mod, amp_mod, width_mod, pm_amt, dm_amt, am_amt, wm_amt, amp=1.0, freq=440.0):
    frames = len(outdata)
    base_inc = twopi*freq*oneoverfs
    for n in range(frames):
        #modulate phase increment
        state[2] = base_inc + base_inc*pitch_mod[n]*pm_amt + max_det_inc*det_mod[n]*dm_amt + max_det_inc*walk_mod[n]*walk_amt
        mod_inc_d = state[2]*2

        #generate naive saw
        sample = (state[0] * oneoverpi) - 1.0
        sample_d = (state[3] * oneoverpi) - 1.0
        
        #apply polyblep corrections
        if (state[0] < state[2]):           #phase just wrapped
            t = state[0]/state[2]
            sample += (t - 1.0)**2
        elif (state[0] + state[2] > twopi):   #phase about to wrap
            t = (twopi - state[0])/state[2]
            sample -= (t - 1.0)**2

        #apply polyblep corrections (double freq.)
        if (state[3] < mod_inc_d):           #phase just wrapped
            t_d = state[3]/mod_inc_d
            sample_d += (t_d - 1.0)**2
        elif (state[3] + mod_inc_d > twopi):   #phase about to wrap
            t_d = (twopi - state[3])/mod_inc_d
            sample_d -= (t_d - 1.0)**2

        #increment phases & wrap
        state[0] += state[2]
        if (state[0] > twopi):
            state[0] -= twopi

        state[3] += mod_inc_d
        if (state[3] > twopi):
            state[3] -= twopi

        #output
        mod_width = 2*np.abs(0.5 - (width + width_mod[n]*wm_amt))
        mod_amp = max(-1.0, min(1.0, amp + amp_mod[n]*am_amt))
        out_sample = (1.0 - mod_width)*sample + mod_width*sample_d
        out_sample *= mod_amp
        outdata[n, 0] = out_sample
        outdata[n, 1] = out_sample

#--anti-aliased pulse
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

#--anti-aliased trisaw
#---(width=0.5: triangle, width≈0.0: sawtooth, width≈1.0: ramp)
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

#-BLIT
#--anti-aliased sawtooth
@njit(nogil=True, fastmath=True, cache=True, inline="always")
def blit_saw(outdata, states, integrators, width,
                walk_mod, walk_amt, pitch_mod, det_mod, amp_mod, width_mod, pm_amt, dm_amt, am_amt, wm_amt, amp=1.0, freq=440.0):
    frames = len(outdata)
    base_inc = freq*oneoverfs
    for n in range(0, frames):
        for c in range(0, 2):
            mod_inc = base_inc + base_inc*pitch_mod[n]*pm_amt + max_det_inc*walk_mod[n]*walk_amt + max_det_inc*det_mod[n]*dm_amt
            mod_inc_d = mod_inc*2
            new_freq = max(1e-9, mod_inc)*fs
            new_freq_d = max(1e-9, mod_inc_d)*fs
            harmonics = 2*int(nyquist/new_freq) + 1
            harmonics_d = 2*int(nyquist/new_freq_d) + 1
            phase = states[c, 0]
            phase_d = states[c, 3]
            #leak_c = 1.0 - twopi*mod_inc*.1
            kernel_den = math.sin(np.pi*phase)
            kernel_den_d = math.sin(np.pi*phase_d)

            if phase < .0000001:
                slope = 1.0-harmonics
            else:
                slope = 1.0-math.sin(np.pi*harmonics*phase)/kernel_den
            if phase_d < .0000001:
                slope_d = 1.0-harmonics_d
            else:
                slope_d = 1.0-math.sin(np.pi*harmonics_d*phase_d)/kernel_den_d

            slope *= mod_inc*2
            slope_d *= mod_inc_d*2
            v1, integrators[0, c] = leaky_trapezoidal_integrate(slope, integrators[0, c])
            v1_d, integrators[1, c] = leaky_trapezoidal_integrate(slope_d, integrators[1, c])
            states[c, 0] += mod_inc
            states[c, 3] += mod_inc_d
            states[c, 0] -= np.floor(states[c, 0])
            states[c, 3] -= np.floor(states[c, 3])

            mod_width = 2*np.abs(0.5 - (width + width_mod[n]*wm_amt))
            output_sample = v1*(1.0 - mod_width) + v1_d*mod_width
            mod_amp = max(-1.0, min(1.0, amp + amp_mod[n]*am_amt))
            outdata[n, c] = output_sample*mod_amp

#--anti-aliased pulse
@njit(nogil=True, fastmath=True, cache=True, inline="always")
def blit_pulse(outdata, states, integrators, smoothed_widths,
                walk_mod, walk_amt, pitch_mod, det_mod, amp_mod, width_mod, pm_amt, dm_amt, am_amt, wm_amt, amp=1.0, freq=440.0, width=0.5):
    frames = len(outdata)
    base_inc = freq*oneoverfs
    alpha = 1.0 - math.exp(-twopi*50.0*oneoverfs)
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
            v1, integrators[0, c] = leaky_trapezoidal_integrate(slope1, integrators[0, c])
            v2, integrators[1, c] = leaky_trapezoidal_integrate(slope2, integrators[1, c])
            states[c, 0] += mod_inc
            states[c, 0] -= np.floor(states[c, 0])

            output_sample = v1 - v2
            mod_amp = max(-1.0, min(1.0, amp + amp_mod[n]*am_amt))
            outdata[n, c] = output_sample*mod_amp

#--anti-aliased trisaw (BLIT)
#---(width=0.5: triangle, width≈0.0: sawtooth, width≈1.0: ramp)
@njit(nogil=True, fastmath=True, cache=True, inline="always")
def blit_triangle(outdata, states, integrators, smoothed_widths, followers,
                walk_mod, walk_amt, pitch_mod, det_mod, amp_mod, width_mod, pm_amt, dm_amt, am_amt, wm_amt, amp=1.0, freq=440.0, width=0.5):
    frames = len(outdata)
    base_inc = freq*oneoverfs
    alpha = 1.0 - math.exp(-twopi*50.0*oneoverfs)
    for n in range(0, frames):
        for c in range(0, 2):
            mod_inc = base_inc + base_inc*pitch_mod[n]*pm_amt + max_det_inc*walk_mod[n]*walk_amt + max_det_inc*det_mod[n]*dm_amt
            new_freq = max(1e-9, mod_inc)*fs
            nyquist_by_nf = nyquist/new_freq
            harmonics = 2*int(nyquist_by_nf) + 1
            harmonic_f = nyquist_by_nf - int(nyquist_by_nf)
            new_width = max(.01, min(.99, width + width_mod[n]*wm_amt))
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
            slope1 -= mod_inc*4*harmonic_f*math.cos(twopi*phase1*int(nyquist_by_nf + 1))
            slope2 -= mod_inc*4*harmonic_f*math.cos(twopi*phase2*int(nyquist_by_nf + 1))             
            v1, integrators[0, c] = leaky_trapezoidal_integrate(slope1, integrators[0, c])
            v2, integrators[1, c] = leaky_trapezoidal_integrate(slope2, integrators[1, c])
            states[c, 0] += mod_inc
            states[c, 0] -= np.floor(states[c, 0])

            blit_pulse = (v1 - v2)
            v3, integrators[2, c] = leaky_trapezoidal_integrate(blit_pulse, integrators[2, c])
            
            if v3 > followers[0, c]:
                followers[0, c] = v3
            if v3 < followers[1, c]:
                followers[1, c] = v3

            dc_correct = (followers[0, c] + followers[1, c]) / 2.0
            v3 = v3 - dc_correct

            scale = (mod_inc)/(smoothed_width*(1.0 - smoothed_width))
            output_sample = v3*scale
            mod_amp = max(-1.0, min(1.0, amp + amp_mod[n]*am_amt))
            outdata[n, c] = output_sample*mod_amp

            follower_leak = 1.0 - (mod_inc*10.0)
            followers[0, c] *= follower_leak
            followers[1, c] *= follower_leak

#-utilities
#--random walk generator
@njit(nogil=True, fastmath=True, cache=True)
def generate_walk(output, walk_state):
    frames = len(output)
    walk_offset = 2*random.random() - 1.0
    for n in range(0, frames):
        walk_state[0] = walk_state[0]*.99999 + .00001*walk_offset
        output[n] = walk_state[0]

#--leaky integrator (BLT)
@njit(nogil=True, fastmath=True, cache=True)
def leaky_trapezoidal_integrate(x, state, gn=g_norm):
    x = x*0.5
    v = (x + state)*gn
    next_state = 2*v - state
    return v, next_state