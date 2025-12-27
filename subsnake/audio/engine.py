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
        self.voices = [Voice(), Voice(), Voice(), Voice()]
        self.voice_output = np.zeros((1024, 2), dtype=np.float32)
        self.voices_playing = []
        self.note_to_voice = {}
        self.octave = 0

    
    #audio callback
    def callback(self, outdata, frames, time, status):
        #outdata[:] = 0.0
        for voice in self.voices:
            voice.callback(self.voice_output)
            outdata += self.voice_output
        outdata *= 0.5

    #voice assignment
    def assign_voice(self, note):
        inc = 0
        for voice in self.voices:
            if (voice.status == 0):    #assign first stopped voice
                self.note_to_voice.update({note: inc})
                return voice
            else:
                inc += 1
        inc = 0
        for voice in self.voices:
            if (voice.status == 1):    #assign first released voice
                note_iter = iter(self.note_to_voice)
                for n in range(len(self.note_to_voice)):
                    note_key = next(note_iter)
                    if (self.note_to_voice[note_key] == inc):
                        self.note_to_voice.pop(note_key)
                        break
                self.note_to_voice.update({note: inc})
                return voice
            else:
                inc += 1
        first_note = next(iter(self.note_to_voice))
        first_voice_index = self.note_to_voice.pop(first_note)
        first_voice = self.voices[first_voice_index]
        self.note_to_voice.update({note: first_voice_index})
        return first_voice 
    
    #key input handlers
    def key_pressed(self, note):
        new_pitch = 440.0 * 2**(float(note)/12.0)
        new_voice = self.assign_voice(note)
        new_voice.osc.update_pitch(new_pitch)
        new_voice.env.update_gate(True)
        new_voice.status = 2

    def key_released(self, note):
        if note in self.note_to_voice:
            voice_index = self.note_to_voice.pop(note)
            self.voices[voice_index].env.update_gate(False)
            self.voices[voice_index].status = 1
        

    #voice helper functions
    def update_pitch(self, newPitch):
        voice = self.voices[0]
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
        self.status = 0

    def callback(self, output):
            self.osc.process_block(self.osc_out)
            self.filt.process_block(self.osc_out, self.filt_out)
            self.env.process_block(self.filt_out, output)
            if (self.env.state[0] == 0.0):
                 self.status = 0
