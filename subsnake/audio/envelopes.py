import numpy as np
import sounddevice as sd
import math
from numba import njit

fs = 44100
blocksize = 1024
twopi = 2*np.pi
oneoverpi = 1/np.pi

class ADSR():
    def __init__(self, attack=0.01, decay=0.5, sustain=0.5, release=0.5):
        #envelope state array
        #   level, stage, attack c, decay c, sustain, release c
        self.state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.gate = False

        #time constants & sustain
        self.state[2] = 1.0 - math.exp(-1/(fs*attack))
        self.state[3] = 1.0 - math.exp(-1/(fs*decay))
        self.state[4] = sustain
        self.state[5] = 1.0 - math.exp(-1/(fs*release))

    def process_block(self, input, output):
        self.envelope_block(self.state, self.gate, input, output)
    
    def update_gate(self, newGate):
        self.gate = newGate

    def update_attack(self, newAttack):
        N = fs*newAttack
        self.state[2] = 1.0 - math.exp(-1/N)

    def update_decay(self, newDecay):
        N = fs*newDecay
        self.state[3] = 1.0 - math.exp(-1/N)
    
    def update_sustain(self, newSustain):
        self.state[4] = newSustain
    
    def update_release(self, newRelease):
        N = fs*newRelease
        self.state[5] = 1.0 - math.exp(-1/N)
    
    #ADSR envelope (recursive 1-pole LPF)
    @staticmethod
    @njit(nogil=True, fastmath=True)
    def envelope_block(state, gate, input, output):
        for n in range(len(output)):
            if gate:
                if (state[1] == 0.0):  #start envelope
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
