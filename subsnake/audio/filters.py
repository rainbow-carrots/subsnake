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
        self.filter_block(state, input, output)

    def update_cutoff(self, freq):
        f = 2*math.sin(np.pi*(freq/(4*fs)))
        self.state[0, 2] = f
        self.state[1, 2] = f

    def update_resonance(self, res):
        self.state[0, 3] = res
        self.state[1, 3] = res

    def update_drive(self, drive):
        self.state[0, 5] = drive
    
    def update_type(self, type):
        self.state[0, 4] = type
        self.state[1, 4] = type
        
    @staticmethod
    @njit(nogil=True, fastmath=True)
    def filter_block(state, input, output):
        for c in range (2):
            for n in range(len(output)):
                subsample = 0.0
                substate = state[c, 4]
                for m in range(4):
                    state[c, 0] = state[c, 0] + state[c, 2]*state[c, 1]
                    feedback = state[c, 3]*(np.tanh(state[c, 1]*state[c, 5])/state[c, 5])
                    high = input[n, 0] - state[c, 0] - feedback
                    state[c, 1] = state[c, 2]*high + state[c, 1]
                    notch = high + state[c, 0]
                    if (substate == 0.0):   #lowpass
                        subsample += state[c, 0]
                    elif (substate == 1.0): #highpass
                        subsample += high
                    elif (substate == 2.0): #bandpass
                        subsample += state[c, 1]
                    elif (substate == 3.0): #notch
                        subsample += notch
                sample = subsample*0.25
                output[n, c] = sample
