import numpy as np
import math
from numba import njit

fs = 44100
twopi = 2*np.pi
oneoverpi = 1/np.pi

class ADSR():
    def __init__(self, attack=0.01, decay=0.5, sustain=0.5, release=0.5):
        #envelope state array
        #   level, stage, attack c, decay c, sustain, release c
        self.state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.gate = False
        self.attack_sample = 0
        self.release_sample = 0
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release

        #time constants & sustain
        self.state[2] = 1.0 - math.exp(-1/(fs*attack))
        self.state[3] = 1.0 - math.exp(-1/(fs*decay))
        self.state[4] = sustain
        self.state[5] = 1.0 - math.exp(-1/(fs*release))

    def process_block(self, input, output, mod_buffers, mod_values):
        self.envelope_block(self.state, self.gate, input, output, self.attack_sample, self.release_sample,
                            mod_buffers[0], mod_buffers[1], mod_buffers[2], mod_buffers[3], mod_values[0], mod_values[1], mod_values[2], mod_values[3],
                            self.attack, self.decay, self.sustain, self.release)
    
    def update_gate(self, newGate):
        self.gate = newGate
    
    def update_attack_start(self, attack_sample):
        self.attack_sample = attack_sample

    def update_release_start(self, release_sample):
        self.release_sample = release_sample

    def update_attack(self, newAttack):
        self.attack = newAttack

    def update_decay(self, newDecay):
        self.decay = newDecay
    
    def update_sustain(self, newSustain):
        self.sustain = newSustain
    
    def update_release(self, newRelease):
        self.release = newRelease
    
    #ADSR envelope (recursive 1-pole LPF)
    @staticmethod
    @njit(nogil=True, fastmath=True)
    def envelope_block(state, gate, input, output, attack_start, release_start, att_mod, dec_mod, sus_mod, rel_mod, am_val, dm_val, sm_val, rm_val, att, dec, sus, rel):
        for n in range(len(output)):
            mod_att = max(1.0, fs*att + fs*att_mod[n]*am_val)
            mod_dec = max(1.0, fs*dec + fs*dec_mod[n]*dm_val)
            mod_sus = max(0.0, min(1.0, sus + sus_mod[n]*sm_val))
            mod_rel = max(1.0, fs*rel + fs*rel_mod[n]*rm_val)
            state[2] = 1.0 - math.exp(-1/(mod_att))
            state[3] = 1.0 - math.exp(-1/(mod_dec))
            state[4] = mod_sus
            state[5] = 1.0 - math.exp(-1/(mod_rel))
            if gate:
                if (state[1] == 0.0) and (n >= attack_start):  #start envelope
                    state[1] = 1.0
                elif (state[1] == 1.0): #attack
                    state[0] = state[0] + state[2]*(1.0 - state[0])
                    if (state[0] + .01 >= 1.0):
                        state[0] = 1.0
                        state[1] = 2.0
                elif (state[1] == 2.0): #decay
                    state[0] = state[0] + state[3]*(state[4] - state[0])
                    if (state[0] - .01 <= state[4]):
                        state[0] = state[4]
                        state[1] = 3.0
                elif (state[1] == 3.0): #sustain
                    state[0] = state[4]
                else:
                    state[1] = 1.0
            else:
                if (state[1] == 0.0):   #envelope off
                    state[0] = 0.0
                elif (state[1] < 4.0):  #attack/decay/sustain -> release
                    if (n >= release_start):
                        state[1] = 4.0
                else:                   #release
                    state[0] = state[0] + state[5]*(0.0 - state[0])
                    if (state[0] - .01 <= 0.0):
                        state[0] = 0.0
                        state[1] = 0.0  #stop envelope

            #apply envelope (stereo)
            sample_L = input[n, 0] * state[0]
            sample_R = input[n, 1] * state[0]
            output[n, 0] = sample_L
            output[n, 1] = sample_R
