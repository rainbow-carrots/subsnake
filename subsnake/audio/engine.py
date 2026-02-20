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
from .modulators import LFO, ModEnv

fs = 44100
twopi = 2*np.pi
oneoverpi = 1/np.pi
middle_a = 69
midi_latency = 0.0029025   #seconds

class AudioEngine():
    def __init__(self):
        #mod dial value states (float)
        self.mod_dial_values = {"osc_freq": 0.0, "osc_amp": 0.0, "osc_width": 0.0,
                                "osc2_freq": 0.0, "osc2_det": 0.0, "osc2_amp": 0.0, "osc2_width": 0.0,
                                "osc3_freq": 0.0, "osc3_det": 0.0, "osc3_amp": 0.0, "osc3_width": 0.0,
                                "filt_freq": 0.0, "filt_res": 0.0, "filt_drive": 0.0, "filt_sat": 0.0,
                                "fenv_att": 0.0, "fenv_dec": 0.0, "fenv_sus": 0.0, "fenv_rel": 0.0, "fenv_amt": 0.0,
                                "env_att": 0.0, "env_dec": 0.0, "env_sus": 0.0, "env_rel": 0.0,
                                "del_time": 0.0, "del_feedback": 0.0, "del_mix": 0.0,
                                "lfo1_freq": 0.0, "lfo1_phase": 0.0, "lfo2_freq": 0.0, "lfo2_phase": 0.0,
                                "menv1_att": 0.0, "menv1_rel": 0.0, "menv2_att": 0.0, "menv2_rel": 0.0}
        #mod dial mode states (int)
        self.mod_dial_modes =  {"osc_freq": 0, "osc_amp": 0, "osc_width": 0,
                                "osc2_freq": 0, "osc2_det": 0, "osc2_amp": 0, "osc2_width": 0,
                                "osc3_freq": 0, "osc3_det": 0, "osc3_amp": 0, "osc3_width": 0,
                                "filt_freq": 0, "filt_res": 0, "filt_drive": 0, "filt_sat": 0,
                                "fenv_att": 0, "fenv_dec": 0, "fenv_sus": 0, "fenv_rel": 0, "fenv_amt": 0,
                                "env_att": 0, "env_dec": 0, "env_sus": 0, "env_rel": 0,
                                "del_time": 0, "del_feedback": 0, "del_mix": 0,
                                "lfo1_freq": 0, "lfo1_phase": 0, "lfo2_freq": 0, "lfo2_phase": 0,
                                "menv1_att": 0, "menv1_rel": 0, "menv2_att": 0, "menv2_rel": 0}
        self.voices = []
        for n in range(0, 16):
            self.voices.append(Voice(self.mod_dial_values, self.mod_dial_modes))
        self.delay = StereoDelay(fs)
        self.delay_modulators = [LFO(fs, 5, 0, 0), LFO(fs, 5, 0, 0), ModEnv(fs, 0.5, 0.5, 0), ModEnv(fs, 0.5, 0.5, 0)]
        self.no_mod = np.zeros((2048), dtype=np.float32)
        self.recorder = AudioRecorder(fs)
        self.stopped_voice_indeces = []
        self.released_voice_indeces = []
        voice_index = 0
        for voice in self.voices:
            voice.index = voice_index
            self.stopped_voice_indeces.append(voice_index)
            voice.detune_offset_2 = .975 + .050*random.random()
            voice.detune_offset_3 = .975 + .050*random.random()
            voice_index += 1

        self.voice_output = np.zeros((2048, 2), dtype=np.float32)
        self.recorder_output = np.zeros((2048, 2), dtype=np.float32)
        self.delay_output = np.zeros((2048, 2), dtype=np.float32)
        self.key_to_note = {}
        self.note_to_voice = {}
        self.octave = 0
        self.osc_drift_amt = 0.0
        self.pitch_offset_1 = 0
        self.pitch_offset_2 = 0
        self.pitch_offset_3 = 0
        self.detune_2 = 0.0
        self.detune_3 = 0.0
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
        self.stream = sd.OutputStream(channels=2, samplerate=fs, blocksize=0, latency="high", callback=self.callback, dtype=np.float32)
        self.stream.start()

    def get_devices(self):
        audio_devices = sd.query_devices()
        return audio_devices

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
        outdata[:frames] = 0.0
        frame_width = frames/fs
        frame_start = time.outputBufferDacTime
        frame_end = frame_start + frame_width
        self.frame_times.put((frame_width, frame_start, frame_end, frames))
        for voice in self.voices:
            voice.callback(self.voice_output[:frames], self.note_to_voice, self.stopped_voice_indeces, self.released_voice_indeces, frames)
            outdata += self.voice_output[:frames]
        self.recorder.process_block(outdata, self.recorder_output)
        outdata += self.recorder_output[:frames]
        del_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["del_time"])]
        del_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["del_feedback"]))
        del_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["del_mix"]))
        del_mod_values = [self.mod_dial_values["del_time"], self.mod_dial_values["del_feedback"],
                           self.mod_dial_values["del_mix"]]
        self.delay.process_block(outdata, outdata, del_mod_buffers, del_mod_values)
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
    def update_delete(self):
        self.recorder.delete()

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
    # oscillator drift
    def update_osc_drift(self, drift):
        for voice in self.voices:
            voice.osc.update_drift(drift)
            voice.osc2.update_drift(drift)
            voice.osc3.update_drift(drift)
    
    # oscillator type (algorithm)
    def update_osc_type(self, osc, new_type):
        if osc == 0:
            for voice in self.voices:
                voice.osc.update_type(new_type)
        elif osc == 1:
            for voice in self.voices:
                voice.osc2.update_type(new_type)
        elif osc == 2:
            for voice in self.voices:
                voice.osc3.update_type(new_type)


    # oscillators
    def update_pitch_1(self, offset):
        for voice in self.voices:
            new_pitch = 440.0 * 2**(float(voice.base_note)/12.0 + offset)
            voice.osc.update_pitch(new_pitch)
            self.pitch_offset_1 = offset

    def update_pitch_2(self, offset):
        for voice in self.voices:
            new_pitch = 440.0 * 2**(float(voice.base_note)/12.0 + offset) + self.detune_2*voice.detune_offset_2
            voice.osc2.update_pitch(new_pitch)
            self.pitch_offset_2 = offset

    def update_pitch_3(self, offset):
        for voice in self.voices:
            new_pitch = 440.0 * 2**(float(voice.base_note)/12.0 + offset) + self.detune_3*voice.detune_offset_3
            voice.osc3.update_pitch(new_pitch)
            self.pitch_offset_3 = offset

    def update_detune_2(self, detune):
        for voice in self.voices:
            new_pitch = 440.0 * 2**(float(voice.base_note)/12.0 + self.pitch_offset_2) + detune*voice.detune_offset_2
            voice.osc2.update_pitch(new_pitch)
        self.detune_2 = detune

    def update_detune_3(self, detune):
        for voice in self.voices:
            new_pitch = 440.0 * 2**(float(voice.base_note)/12.0 + self.pitch_offset_3) + detune*voice.detune_offset_3
            voice.osc3.update_pitch(new_pitch)
        self.detune_3 = detune

    def update_amplitude_1(self, newAmp):
        for voice in self.voices:
            voice.osc.update_amplitude(newAmp)

    def update_amplitude_2(self, newAmp):
        for voice in self.voices:
            voice.osc2.update_amplitude(newAmp)

    def update_amplitude_3(self, newAmp):
        for voice in self.voices:
            voice.osc3.update_amplitude(newAmp)

    def update_width_1(self, newWidth):
        for voice in self.voices:
            voice.osc.update_width(newWidth)

    def update_width_2(self, newWidth):
        for voice in self.voices:
            voice.osc2.update_width(newWidth)

    def update_width_3(self, newWidth):
        for voice in self.voices:
            voice.osc3.update_width(newWidth)
    
    def update_algorithm(self, newAlg, osc):
        for voice in self.voices:
            if (osc == 1):
                voice.osc.update_algorithm(newAlg)
            elif (osc == 2):
                voice.osc2.update_algorithm(newAlg)
            elif (osc == 3):
                voice.osc3.update_algorithm(newAlg)
    
    # filter
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

    # envelope
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

    # filter envelope
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

    # delay
    def update_del_time(self, newTime):
        self.delay.update_time(newTime)

    def update_del_feedback(self, newFeedback):
        self.delay.update_feedback(newFeedback)

    def update_del_mix(self, newMix):
        self.delay.update_mix(newMix)

    # modulators
    #  lfo 1
    def update_lfo1_freq(self, newFreq):
        for voice in self.voices:
            voice.lfo1.set_frequency(newFreq)
        self.delay_modulators[0].set_frequency(newFreq)

    def update_lfo1_offset(self, newPhase):
        for voice in self.voices:
            voice.lfo1.set_offset(newPhase)
        self.delay_modulators[0].set_offset(newPhase)

    def update_lfo1_shape(self, newShape):
        for voice in self.voices:
            voice.lfo1.set_shape(newShape)
        self.delay_modulators[0].set_shape(newShape)

    #  lfo 2
    def update_lfo2_freq(self, newFreq):
        for voice in self.voices:
            voice.lfo2.set_frequency(newFreq)
        self.delay_modulators[1].set_frequency(newFreq)

    def update_lfo2_offset(self, newPhase):
        for voice in self.voices:
            voice.lfo2.set_offset(newPhase)
        self.delay_modulators[1].set_offset(newPhase)

    def update_lfo2_shape(self, newShape):
        for voice in self.voices:
            voice.lfo2.set_shape(newShape)
        self.delay_modulators[1].set_shape(newShape)

    #  menv 1
    def update_menv1_att(self, newAtt):
        for voice in self.voices:
            voice.menv1.set_attack(newAtt)
        self.delay_modulators[2].set_attack(newAtt)

    def update_menv1_rel(self, newRel):
        for voice in self.voices:
            voice.menv1.set_release(newRel)
        self.delay_modulators[2].set_release(newRel)

    def update_menv1_mode(self, newMode):
        for voice in self.voices:
            voice.menv1.set_mode(newMode)
        self.delay_modulators[2].set_mode(newMode)

    #  menv 2
    def update_menv2_att(self, newAtt):
        for voice in self.voices:
            voice.menv2.set_attack(newAtt)
        self.delay_modulators[3].set_attack(newAtt)

    def update_menv2_rel(self, newRel):
        for voice in self.voices:
            voice.menv2.set_release(newRel)
        self.delay_modulators[3].set_release(newRel)

    def update_menv2_mode(self, newMode):
        for voice in self.voices:
            voice.menv2.set_mode(newMode)
        self.delay_modulators[3].set_mode(newMode)

    #cc helpers
    #osc 1
    def cc_change_pitch_1(self, value):
        new_pitch = (float(value)/127.0)*4.0 - 2
        self.update_pitch_1(new_pitch)

    def cc_change_level_1(self, value):
        new_level = float(value)/127.0
        self.update_amplitude_1(new_level)

    def cc_change_width_1(self, value):
        new_width = float(value)/127.0
        self.update_width_1(new_width)

    #osc 2
    def cc_change_pitch_2(self, value):
        new_pitch = (float(value)/127.0)*4.0 - 2
        self.update_pitch_2(new_pitch)

    def cc_change_level_2(self, value):
        new_level = float(value)/127.0
        self.update_amplitude_2(new_level)

    def cc_change_width_2(self, value):
        new_width = float(value)/127.0
        self.update_width_2(new_width)

    def cc_change_detune_2(self, value):
        new_detune = (float(value)/127.0)*20.0 - 10
        self.update_detune_2(new_detune)

    #osc 3
    def cc_change_pitch_3(self, value):
        new_pitch = (float(value)/127.0)*4.0 - 2
        self.update_pitch_3(new_pitch)

    def cc_change_level_3(self, value):
        new_level = float(value)/127.0
        self.update_amplitude_3(new_level)

    def cc_change_width_3(self, value):
        new_width = float(value)/127.0
        self.update_width_3(new_width)

    def cc_change_detune_3(self, value):
        new_detune = (float(value)/127.0)*20.0 - 10
        self.update_detune_3(new_detune)

    #filt
    def cc_change_cutoff(self, value):
        new_freq = 27.5 * 2**((float(value)/127.0)*8.0)
        self.update_cutoff(new_freq)

    def cc_change_resonance(self, value):
        new_res = 5.0 / (10.0**((float(value)/127.0)*2.0))
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
        new_sustain = (float(value)/127.0)
        self.update_fenv_sustain(new_sustain)

    def cc_change_fenv_release(self, value):
        new_release = (float(value)/127.0) + .001
        self.update_fenv_release(new_release)

    def cc_change_fenv_amount(self, value):
        new_depth = (float(value)/127.0)*2.0 - 1
        self.update_fenv_amount(new_depth)

    #envelope
    def cc_change_env_attack(self, value):
        new_attack = (float(value)/127.0) + .001
        self.update_attack(new_attack)

    def cc_change_env_decay(self, value):
        new_decay = (float(value)/127.0) + .001
        self.update_decay(new_decay)

    def cc_change_env_sustain(self, value):
        new_sustain = (float(value)/127.0)
        self.update_sustain(new_sustain)

    def cc_change_env_release(self, value):
        new_release = (float(value)/127.0) + .001
        self.update_release(new_release)

    #delay
    def cc_change_del_time(self, value):
        new_time = (float(value)/127.0)
        self.update_del_time(new_time)

    def cc_change_del_feedback(self, value):
        new_feedback = (float(value)/127.0)
        self.update_del_feedback(new_feedback)

    def cc_change_del_mix(self, value):
        new_mix = (float(value)/127.0)
        self.update_del_mix(new_mix)

    #modulators
    # lfo 1
    def cc_change_lfo1_speed(self, value):
        new_speed = (float(value)/127.0)*10.0 + .001
        self.update_lfo1_freq(new_speed)
    
    def cc_change_lfo1_phase(self, value):
        new_phase = (float(value)/127.0)
        self.update_lfo1_offset(new_phase)
    
    # lfo 2
    def cc_change_lfo2_speed(self, value):
        new_speed = (float(value)/127.0)*10.0 + .001
        self.update_lfo2_freq(new_speed)
    
    def cc_change_lfo2_phase(self, value):
        new_phase = (float(value)/127.0)
        self.update_lfo2_offset(new_phase)

    # menv 1
    def cc_change_menv1_attack(self, value):
        new_attack = (float(value)/127.0) + .001
        self.update_menv1_att(new_attack)

    def cc_change_menv1_release(self, value):
        new_release = (float(value)/127.0) + .001
        self.update_menv1_rel(new_release)

    # menv 2
    def cc_change_menv2_attack(self, value):
        new_attack = (float(value)/127.0) + .001
        self.update_menv2_att(new_attack)

    def cc_change_menv2_release(self, value):
        new_release = (float(value)/127.0) + .001
        self.update_menv2_rel(new_release)
    

    #mod dial helpers
    def update_mod_value(self, name, value):
        self.mod_dial_values.update({name: value})

    def update_mod_mode(self, name, mode):
        self.mod_dial_modes.update({name: mode})

    def assign_mod_buffer(self, mode):
        if mode == 0:
            return self.no_mod
        elif mode == 1:
            return self.delay_modulators[0].output
        elif mode == 2:
            return self.delay_modulators[1].output
        elif mode == 3:
            return self.delay_modulators[2].output
        elif mode == 4:
            return self.delay_modulators[3].output


class Voice():
    def __init__(self, mod_dial_values, mod_dial_modes):
        self.mod_dial_values = mod_dial_values
        self.mod_dial_modes = mod_dial_modes
        self.osc_out = np.zeros((2048, 2), dtype=np.float32)
        self.osc2_out = np.zeros((2048, 2), dtype=np.float32)
        self.osc3_out = np.zeros((2048, 2), dtype=np.float32)
        self.filt_out = np.zeros((2048, 2), dtype=np.float32)
        self.fenv_in = np.ones((2048, 2), dtype=np.float32)
        self.fenv_out = np.zeros((2048, 2), dtype=np.float32)
        self.no_mod = np.zeros((2048), dtype=np.float32)
        self.osc = WrappedOsc(2, 0.5, 55, fs, .5)
        self.osc2 = WrappedOsc(2, 0.5, 55, fs, .5)
        self.osc3 = WrappedOsc(2, 0.5, 55, fs, .5)
        self.filt = HalSVF(0.0, 3520, 10, 1.0)
        self.env = ADSR(.01, 1.0, 0.5, 1.0)
        self.fenv = ADSR(.01, .5, .5, .5)
        self.lfo1 = LFO(fs, 5, 0, 0)
        self.lfo2 = LFO(fs, 5, 0, 1)
        self.menv1 = ModEnv(fs, 0.5, 0.5, 0)
        self.menv2 = ModEnv(fs, 0.5, 0.5, 1)
        self.base_note = 0
        self.velocity = 0.0
        self.status = 0
        self.index = 0
        self.detune_offset_2 = 0.0
        self.detune_offset_3 = 0.0

    def callback(self, output, note_to_voice, stopped_voices, released_voices, frames):
        if self.status != 0:
            #modulators
            # lfo 1
            lfo1_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["lfo1_freq"])]
            lfo1_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["lfo1_phase"]))
            lfo1_mod_values = [self.mod_dial_values["lfo1_freq"], self.mod_dial_values["lfo1_phase"]]
            self.lfo1.process_block(frames, lfo1_mod_buffers, lfo1_mod_values)
            # lfo 2
            lfo2_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["lfo2_freq"])]
            lfo2_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["lfo2_phase"]))
            lfo2_mod_values = [self.mod_dial_values["lfo2_freq"], self.mod_dial_values["lfo2_phase"]]
            self.lfo2.process_block(frames, lfo2_mod_buffers, lfo2_mod_values)
            # menv 1
            menv1_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["menv1_att"])]
            menv1_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["menv1_rel"]))
            menv1_mod_values = [self.mod_dial_values["menv1_att"], self.mod_dial_values["menv1_rel"]]
            self.menv1.process_block(frames, menv1_mod_buffers, menv1_mod_values)
            # menv 2
            menv2_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["menv2_att"])]
            menv2_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["menv2_rel"]))
            menv2_mod_values = [self.mod_dial_values["menv2_att"], self.mod_dial_values["menv2_rel"]]
            self.menv2.process_block(frames, menv2_mod_buffers, menv2_mod_values)

            #oscillators
            # 1
            osc1_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["osc_freq"])]
            osc1_mod_buffers.append(self.no_mod)
            osc1_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc_amp"]))
            osc1_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc_width"]))
            osc1_mod_values = [self.mod_dial_values["osc_freq"], 0.0,
                            self.mod_dial_values["osc_amp"], self.mod_dial_values["osc_width"]]
            self.osc.process_block(self.osc_out[:frames], osc1_mod_buffers, osc1_mod_values)
            self.osc_out *= 0.33
            # 2
            osc2_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["osc2_freq"])]
            osc2_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc2_det"]))
            osc2_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc2_amp"]))
            osc2_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc2_width"]))
            osc2_mod_values = [self.mod_dial_values["osc2_freq"], self.mod_dial_values["osc2_det"],
                            self.mod_dial_values["osc2_amp"], self.mod_dial_values["osc2_width"]]
            self.osc2.process_block(self.osc2_out[:frames], osc2_mod_buffers, osc2_mod_values)
            self.osc2_out *= 0.33
            # 3
            osc3_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["osc3_freq"])]
            osc3_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc3_det"]))
            osc3_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc3_amp"]))
            osc3_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc3_width"]))
            osc3_mod_values = [self.mod_dial_values["osc3_freq"], self.mod_dial_values["osc3_det"],
                            self.mod_dial_values["osc3_amp"], self.mod_dial_values["osc3_width"]]
            self.osc3.process_block(self.osc3_out[:frames], osc3_mod_buffers, osc3_mod_values)
            self.osc3_out *= 0.33
            # sum
            self.osc_out += self.osc2_out
            self.osc_out += self.osc3_out

            # filter envelope
            fenv_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["fenv_att"])]
            fenv_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["fenv_dec"]))
            fenv_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["fenv_sus"]))
            fenv_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["fenv_rel"]))
            fenv_mod_values = [self.mod_dial_values["fenv_att"], self.mod_dial_values["fenv_dec"],
                            self.mod_dial_values["fenv_sus"], self.mod_dial_values["fenv_rel"]]
            self.fenv.process_block(self.fenv_in[:frames], self.fenv_out[:frames], fenv_mod_buffers, fenv_mod_values)

            # filter
            filt_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["filt_freq"])]
            filt_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["filt_res"]))
            filt_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["filt_drive"]))
            filt_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["filt_sat"]))
            filt_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["fenv_amt"]))
            filt_mod_values = [self.mod_dial_values["filt_freq"], self.mod_dial_values["filt_res"],
                            self.mod_dial_values["filt_drive"], self.mod_dial_values["filt_sat"], self.mod_dial_values["fenv_amt"]]
            self.filt.process_block(self.osc_out[:frames], self.filt_out[:frames], self.fenv_out[:frames], filt_mod_buffers, filt_mod_values)

            # amplitude envelope
            env_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["env_att"])]
            env_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["env_dec"]))
            env_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["env_sus"]))
            env_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["env_rel"]))
            env_mod_values = [self.mod_dial_values["env_att"], self.mod_dial_values["env_dec"],
                            self.mod_dial_values["env_sus"], self.mod_dial_values["env_rel"]]
            self.env.process_block(self.filt_out[:frames], output, env_mod_buffers, env_mod_values)

            # output
            output *= self.velocity
        else:
            output *= 0.0
        if (self.env.state[0] == 0.0) and (self.status > 0):  
            self.status = 0
    
    def assign_mod_buffer(self, mode):
        if mode == 0:
            return self.no_mod
        elif mode == 1:
            return self.lfo1.output
        elif mode == 2:
            return self.lfo2.output
        elif mode == 3:
            return self.menv1.output
        elif mode == 4:
            return self.menv2.output
