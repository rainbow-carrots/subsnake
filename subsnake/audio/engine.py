import numpy as np
import mido
import queue
import sounddevice as sd
from .generators import WrappedOsc
from .filters import HalSVF
from .envelopes import ADSR

fs = 44100
blocksize = 1024
twopi = 2*np.pi
oneoverpi = 1/np.pi
middle_a = 69   #nice

class AudioEngine():
    def __init__(self):
        self.voices = [Voice(), Voice(), Voice(), Voice(),
                       Voice(), Voice(), Voice(), Voice(),
                       Voice(), Voice(), Voice(), Voice()]
        self.stopped_voice_indeces = []
        self.released_voice_indeces = []
        voice_index = 0
        for voice in self.voices:
            voice.index = voice_index
            self.stopped_voice_indeces.append(voice_index)
            voice_index += 1

        self.voice_output = np.zeros((1024, 2), dtype=np.float32)
        self.key_to_note = {}
        self.note_to_voice = {}
        self.octave = 0
        self.pitch_offset_1 = 0
        self.pitch_offset_2 = 0
        self.detune = 0.0
        self.midi_in_queue = queue.SimpleQueue()
        self.stream = None
        self.midi_input = None
        self.midi_channel = None

    #initialize stream
    def start_audio(self):
        self.stream = sd.OutputStream(channels=2, samplerate=fs, blocksize=1024, latency='high', callback=self.callback, dtype=np.float32)
        self.stream.start()

    #initialize midi
    def set_midi_input(self, port_name):
        if self.midi_input:
            self.midi_input.close()
        
        if port_name:
            self.midi_input = mido.open_input(port_name, callback=self.midi_callback)

    def set_midi_channel(self, channel):
        self.midi_channel = channel-1

    def get_midi_inputs(self):
        #get midi inputs
        input_list = mido.get_input_names()
        return input_list

    def close(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
        
        if self.midi_input:
            self.midi_input.close()

    #audio callback
    def callback(self, outdata, frames, time, status):
        #outdata[:] = 0.0
        while not self.midi_in_queue.empty():
            message = self.midi_in_queue.get()
            if (message.type == 'note_on') and (message.channel == self.midi_channel):
                if (message.velocity > 0):
                    self.key_pressed((message.note - middle_a), message.velocity)
                else:
                    self.key_released(message.note - middle_a)
            elif (message.type == 'note_off') and (message.channel == self.midi_channel):
                self.key_released(message.note - middle_a)

        for voice in self.voices:
            voice.callback(self.voice_output, self.note_to_voice, self.stopped_voice_indeces, self.released_voice_indeces)
            outdata += self.voice_output
        outdata *= 0.288675
        outdata = np.tanh(outdata)

    #midi callback
    def midi_callback(self, message):
        self.midi_in_queue.put(message)

    #voice assignment
    def assign_voice(self, note):
        if note in self.note_to_voice:      #assign releasing voice of same note
            if (self.voices[self.note_to_voice[note]].status == 1):
                return self.voices[self.note_to_voice[note]]
        elif self.stopped_voice_indeces:    #assign first stopped voice
            voice_index = self.stopped_voice_indeces.pop(0)
            self.note_to_voice.update({note: voice_index})
            return self.voices[voice_index]
        elif self.released_voice_indeces:   #assign oldest releasing voice
            voice_index = self.released_voice_indeces.pop(0)
            if note in self.note_to_voice:
                self.note_to_voice.pop(note)
            self.note_to_voice.update({note: voice_index})
            return self.voices(voice_index)
        else:                               #steal oldest voice
            first_note = next(iter(self.note_to_voice))
            first_voice_index = self.note_to_voice.pop(first_note)
            first_voice = self.voices[first_voice_index]
            self.note_to_voice.update({note: first_voice_index})
            return first_voice 
    
    #key input handlers
    def key_pressed(self, note, velocity):
        new_pitch = 440.0 * 2**((float(note))/12.0 + self.pitch_offset_1)
        new_pitch2 = 440.0 * 2**((float(note))/12.0 + self.pitch_offset_2) + self.detune
        new_voice = self.assign_voice(note)
        new_voice.osc.update_pitch(new_pitch)
        new_voice.osc2.update_pitch(new_pitch2)
        new_voice.velocity = float(velocity)/127.0
        new_voice.env.update_gate(True)
        new_voice.status = 2
        new_voice.base_note = note

    def key_released(self, note):
        if note in self.note_to_voice:
            voice_index = self.note_to_voice.get(note)
            self.voices[voice_index].env.update_gate(False)
            self.voices[voice_index].status = 1
        

    #voice helper functions
    def update_pitch(self, offset, osc):
        for voice in self.voices:
            if (osc == 1):
                new_pitch = 440.0 * 2**(float(voice.base_note)/12.0 + offset)
                voice.osc.update_pitch(new_pitch)
            elif (osc == 2):
                new_pitch = 440.0 * 2**(float(voice.base_note)/12.0 + offset) + self.detune
                voice.osc2.update_pitch(new_pitch)
        if (osc == 1):
            self.pitch_offset_1 = offset
        elif (osc == 2):
            self.pitch_offset_2 = offset

    def update_detune(self, detune):
        for voice in self.voices:
            new_pitch = 440.0 * 2**(float(voice.base_note)/12.0 + self.pitch_offset_2) + detune
            voice.osc2.update_pitch(new_pitch)
        self.detune = detune

    def update_amplitude(self, newAmp, osc):
        for voice in self.voices:
            if (osc == 1):
                voice.osc.update_amplitude(newAmp)
            elif (osc == 2):
                voice.osc2.update_amplitude(newAmp)

    def update_width(self, newWidth, osc):
        for voice in self.voices:
            if (osc == 1):
                voice.osc.update_width(newWidth)
            elif (osc == 2):
                voice.osc2.update_width(newWidth)
    
    def update_algorithm(self, newAlg, osc):
        for voice in self.voices:
            if (osc == 1):
                voice.osc.update_algorithm(newAlg)
            elif (osc == 2):
                voice.osc2.update_algorithm(newAlg)
    
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
        self.osc2_out = np.zeros((1024, 2), dtype=np.float32)
        self.filt_out = np.zeros((1024, 2), dtype=np.float32)
        #self.env_out = np.zeros((1024, 2), dtype=np.float32)
        self.osc = WrappedOsc(2, 0.5, 55, fs, .5)
        self.osc2 = WrappedOsc(2, 0.5, 55, fs, .5)
        self.filt = HalSVF(0.0, 3520, 10, 1.0)
        self.env = ADSR(.01, 1.0, 0.5, 1.0)
        self.base_note = 0
        self.velocity = 0.0
        self.status = 0
        self.index = 0

    def callback(self, output, note_to_voice, stopped_voices, released_voices):
            self.osc.process_block(self.osc_out)
            self.osc_out *= 0.5
            self.osc2.process_block(self.osc2_out)
            self.osc2_out *= 0.5
            self.osc_out += self.osc2_out
            self.filt.process_block(self.osc_out, self.filt_out)
            self.env.process_block(self.filt_out, output)
            output *= self.velocity
            if (self.env.state[0] == 0.0) and (self.status > 0):
                if self.base_note in note_to_voice:
                    old_voice = note_to_voice.pop(self.base_note)
                    if old_voice in released_voices:
                        old_index = released_voices.index(old_voice)
                        released_voices.pop(old_index)
                stopped_voices.append(self.index)    
                self.status = 0
