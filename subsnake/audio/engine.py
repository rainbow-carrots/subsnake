import numpy as np
from .generators import WrappedOsc
from .filters import HalSVF
from .envelopes import ADSR

fs = 44100
blocksize = 1024
twopi = 2*np.pi
oneoverpi = 1/np.pi

class AudioEngine():
    def __init__(self):
        self.voices = [Voice()]
        self.octave = 0
        
    
    #audio callback
    def callback(self, outdata, frames, time, status):
        for voice in self.voices:
            voice.callback(outdata)


    #voice helper functions
    def update_pitch(self, newPitch):
        for voice in self.voices:
             voice.osc.update_pitch(newPitch)

    def update_amplitude(self, newAmp):
        for voice in self.voices:
             voice.osc.update_amplitude(newAmp)

    def update_width(self, newWidth):
        for voice in self.voices:
             voice.osc.update_width(newWidth)
    
    def update_algorithm(self, newAlg):
        for voice in self.voices:
             voice.osc.update_algorithm(newAlg)
    
    def update_cutoff(self, newFreq):
        for voice in self.voices:
             voice.filt.update_cutoff(newFreq)

    def update_resonance(self, newRes):
        for voice in self.voices:
             voice.filt.update_resonance(newRes)

    def update_drive(self, newDrive):
        for voice in self.voices:
             voice.filt.update_drive(newDrive)
    
    def update_type(self, newType):
        for voice in self.voices:
             voice.filt.update_type(newType)

    def update_saturate(self, newSat):
        for voice in self.voices:
              voice.filt.update_saturate(newSat)
         
    def update_gate(self, newGate):
        for voice in self.voices:
              voice.env.update_gate(newGate)

    def update_attack(self, newAttack):
        for voice in self.voices:
             voice.env.update_attack(newAttack)

    def update_decay(self, newDecay):
        for voice in self.voices:
             voice.env.update_decay(newDecay)
    
    def update_sustain(self, newSustain):
        for voice in self.voices:
             voice.env.update_sustain(newSustain)
    
    def update_release(self, newRelease):
         for voice in self.voices:
              voice.env.update_release(newRelease)


class Voice():
    def __init__(self):
        self.osc_out = np.zeros((1024, 2), dtype=np.float32)
        self.filt_out = np.zeros((1024, 2), dtype=np.float32)
        #self.env_out = np.zeros((1024, 2), dtype=np.float32)
        self.osc = WrappedOsc(2, 0.5, 55, fs, .5)
        self.filt = HalSVF(0.0, 3520, 10, 1.0)
        self.env = ADSR(.01, 1.0, 0.5, 1.0)

    def callback(self, output):
            self.osc.process_block(self.osc_out)
            self.filt.process_block(self.osc_out, self.filt_out)
            self.env.process_block(self.filt_out, output)
