import numpy as np
import mido
import queue
import sounddevice as sd
import random
import time as pytime
from PySide6.QtCore import QMutex, QThreadPool
from .generators import WrappedOsc
from .filters import HalSVF
from .envelopes import ADSR
from .workers import KeyEventWorker
from .effects import StereoDelay, AudioRecorder

fs = 44100
blocksize = 1024
twopi = 2*np.pi
oneoverpi = 1/np.pi
middle_a = 69
midi_latency = 0.0029025   #seconds

class AudioEngine():
    def __init__(self):
        self.voices = [Voice(), Voice(), Voice(), Voice(),
                       Voice(), Voice(), Voice(), Voice(),
                       Voice(), Voice(), Voice(), Voice()]
        self.delay = StereoDelay(fs)
        self.recorder = AudioRecorder(fs)
        self.stopped_voice_indeces = []
        self.released_voice_indeces = []
        voice_index = 0
        for voice in self.voices:
            voice.index = voice_index
            self.stopped_voice_indeces.append(voice_index)
            voice.detune_offset = .975 + .050*random.random()
            voice_index += 1

        self.voice_output = np.zeros((1024, 2), dtype=np.float32)
        self.recorder_output = np.zeros((1024, 2), dtype=np.float32)
        self.key_to_note = {}
        self.note_to_voice = {}
        self.octave = 0
        self.pitch_offset_1 = 0
        self.pitch_offset_2 = 0
        self.detune = 0.0
        self.midi_in_queue = queue.SimpleQueue()
        self.frame_times = queue.SimpleQueue()
        self.pending_event = None
        self.midi_cc_functions = {}
        self.midi_cc_values = {}
        self.stream = None
        self.midi_input = None
        self.midi_channel = None
        self.previous_buffer_dac_time = pytime.perf_counter()
        self.mutex = QMutex()
        self.threadpool = QThreadPool()
        self.key_event_worker = KeyEventWorker(self)
        self.threadpool.start(self.key_event_worker)
        self.run_threads = True

    #initialize stream
    def start_audio(self):
        self.stream = sd.OutputStream(channels=2, samplerate=fs, blocksize=0, latency="low", callback=self.callback, dtype=np.float32)
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

        self.run_threads = False

    #audio callback
    def callback(self, outdata, frames, time, status):
        frame_width = frames/fs
        frame_start = time.outputBufferDacTime
        frame_end = frame_start + frame_width
        self.frame_times.put((frame_width, frame_start, frame_end, frames))
        for voice in self.voices:
            voice.callback(self.voice_output[:frames], self.note_to_voice, self.stopped_voice_indeces, self.released_voice_indeces, frames)
            outdata += self.voice_output[:frames]
        self.delay.process_block(outdata, outdata)
        self.recorder.process_block(outdata, outdata)
        outdata *= 0.288675
        outdata = np.tanh(outdata)

    #midi callback
    def midi_callback(self, message):
        stamped_message = (message, pytime.perf_counter())
        self.midi_in_queue.put(stamped_message) 
    
    #key input handlers
    def key_pressed(self, note_val, velocity_val, sample_offset=0):
        note_on_msg = mido.Message("note_on", note=note_val, velocity=velocity_val, channel=self.midi_channel)
        stamped_message = (note_on_msg, pytime.perf_counter())
        self.midi_in_queue.put(stamped_message) 

    def key_released(self, note_val, sample_offset=0):
        note_off_msg = mido.Message("note_off", note=note_val, velocity=0, channel=self.midi_channel)
        stamped_message = (note_off_msg, pytime.perf_counter())
        self.midi_in_queue.put(stamped_message)

    #recorder slots
    def update_record(self, state):
        self.recorder.set_record(state)

    def update_play(self):
        self.recorder.play()

    def update_pause(self):
        self.recorder.pause()

    def update_stop(self):
        self.recorder.stop()

    def update_loop(self, state):
        self.recorder.set_loop(state)

    #voice helper functions
    def update_pitch_1(self, offset):
        for voice in self.voices:
            new_pitch = 440.0 * 2**(float(voice.base_note)/12.0 + offset)
            voice.osc.update_pitch(new_pitch)
            self.pitch_offset_1 = offset

    def update_pitch_2(self, offset):
        for voice in self.voices:
            new_pitch = 440.0 * 2**(float(voice.base_note)/12.0 + offset) + self.detune*voice.detune_offset
            voice.osc2.update_pitch(new_pitch)
            self.pitch_offset_2 = offset

    def update_detune(self, detune):
        for voice in self.voices:
            new_pitch = 440.0 * 2**(float(voice.base_note)/12.0 + self.pitch_offset_2) + detune*voice.detune_offset
            voice.osc2.update_pitch(new_pitch)
        self.detune = detune

    def update_amplitude_1(self, newAmp):
        for voice in self.voices:
            voice.osc.update_amplitude(newAmp)

    def update_amplitude_2(self, newAmp):
        for voice in self.voices:
            voice.osc2.update_amplitude(newAmp)

    def update_width_1(self, newWidth):
        for voice in self.voices:
            voice.osc.update_width(newWidth)

    def update_width_2(self, newWidth):
        for voice in self.voices:
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

    def update_fenv_attack(self, newAttack):
        for voice in self.voices:
             voice.fenv.update_attack(newAttack)

    def update_fenv_decay(self, newDecay):
        for voice in self.voices:
             voice.fenv.update_decay(newDecay)
    
    def update_fenv_sustain(self, newSustain):
        for voice in self.voices:
             voice.fenv.update_sustain(newSustain)
    
    def update_fenv_release(self, newRelease):
        for voice in self.voices:
            voice.fenv.update_release(newRelease)

    def update_fenv_amount(self, newAmount):
        for voice in self.voices:
            voice.filt.update_env_amount(newAmount)

    def update_del_time(self, newTime):
        self.delay.update_time(newTime)

    def update_del_feedback(self, newFeedback):
        self.delay.update_feedback(newFeedback)

    def updat_del_mix(self, newMix):
        self.delay.update_mix(newMix)


    #cc helpers
    #osc 1
    def cc_change_pitch_1(self, value):
        new_pitch = (float(value)/127.0)*10 - 5
        self.update_pitch_1(new_pitch)

    def cc_change_level_1(self, value):
        new_level = float(value)/127.0
        self.update_amplitude_1(new_level)

    def cc_change_width_1(self, value):
        new_width = float(value)/127.0
        self.update_width_1(new_width)

    #osc 2
    def cc_change_pitch_2(self, value):
        new_pitch = (float(value)/127.0)*10.0 - 5
        self.update_pitch_2(new_pitch)

    def cc_change_level_2(self, value):
        new_level = float(value)/127.0
        self.update_amplitude_2(new_level)

    def cc_change_width_2(self, value):
        new_width = float(value)/127.0
        self.update_width_2(new_width)

    def cc_change_detune_2(self, value):
        new_detune = (float(value)/127.0)*20.0 - 10
        self.update_detune(new_detune)

    #filt
    def cc_change_cutoff(self, value):
        new_freq = 27.5 * 2**((float(value)/127.0)*8.0)
        self.update_cutoff(new_freq)

    def cc_change_resonance(self, value):
        new_res = 10.0 / (10.0**((float(value)/127.0)*2.0))
        self.update_resonance(new_res)

    def cc_change_drive(self, value):
        new_drive = (float(value)/127.0)*9 + .001
        self.update_drive(new_drive)

    def cc_change_saturate(self, value):
        new_sat = (float(value)/127.0)*11.0 + 1.0
        self.update_saturate(new_sat)
        
    #filter env
    def cc_change_fenv_attack(self, value):
        new_attack = (float(value)/127.0) + .001
        self.update_fenv_attack(new_attack)

    def cc_change_fenv_decay(self, value):
        new_decay = (float(value)/127.0) + .001
        self.update_fenv_decay(new_decay)

    def cc_change_fenv_sustain(self, value):
        new_sustain = (float(value)/127.0) + .001
        self.update_fenv_sustain(new_sustain)

    def cc_change_fenv_release(self, value):
        new_release = (float(value)/127.0) + .001
        self.update_fenv_release(new_release)

    def cc_change_fenv_amount(self, value):
        new_depth = (float(value)/127.0)*10.0 - 5.0
        self.update_fenv_amount(new_depth)

    #envelope
    def cc_change_env_attack(self, value):
        new_attack = (float(value)/127.0) + .001
        self.update_attack(new_attack)

    def cc_change_env_decay(self, value):
        new_decay = (float(value)/127.0) + .001
        self.update_decay(new_decay)

    def cc_change_env_sustain(self, value):
        new_sustain = (float(value)/127.0) + .001
        self.update_sustain(new_sustain)

    def cc_change_env_release(self, value):
        new_release = (float(value)/127.0) + .001
        self.update_release(new_release)


class Voice():
    def __init__(self):
        self.osc_out = np.zeros((1024, 2), dtype=np.float32)
        self.osc2_out = np.zeros((1024, 2), dtype=np.float32)
        self.filt_out = np.zeros((1024, 2), dtype=np.float32)
        self.fenv_in = np.ones((1024, 2), dtype=np.float32)
        self.fenv_out = np.zeros((1024, 2), dtype=np.float32)
        self.osc = WrappedOsc(2, 0.5, 55, fs, .5)
        self.osc2 = WrappedOsc(2, 0.5, 55, fs, .5)
        self.filt = HalSVF(0.0, 3520, 10, 1.0)
        self.env = ADSR(.01, 1.0, 0.5, 1.0)
        self.fenv = ADSR(.01, .5, .5, .5)
        self.base_note = 0
        self.velocity = 0.0
        self.status = 0
        self.index = 0
        self.detune_offset = 0.0

    def callback(self, output, note_to_voice, stopped_voices, released_voices, frames):
            self.osc.process_block(self.osc_out[:frames])
            self.osc_out *= 0.5
            self.osc2.process_block(self.osc2_out[:frames])
            self.osc2_out *= 0.5
            self.osc_out += self.osc2_out
            self.fenv.process_block(self.fenv_in[:frames], self.fenv_out[:frames])
            self.filt.process_block(self.osc_out[:frames], self.filt_out[:frames], self.fenv_out[:frames])
            self.env.process_block(self.filt_out[:frames], output)
            output *= self.velocity
            if (self.env.state[0] == 0.0) and (self.status > 0):
                if self.base_note in note_to_voice:
                    old_voice = note_to_voice.pop(self.base_note)
                    if old_voice in released_voices:
                        old_index = released_voices.index(old_voice)
                        released_voices.pop(old_index)
                stopped_voices.append(self.index)    
                self.status = 0
