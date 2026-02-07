from PySide6.QtCore import QRunnable
import time

middle_a = 69
sleeptime = 0.00145125

class KeyEventWorker(QRunnable):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.midi_queue = engine.midi_in_queue
        self.frames_queue = engine.frame_times
        self.frame_width = 0
        self.frame_start = 0
        self.frame_end = 0
        self.frames = 2048
        self.pending_event = None

    def run(self):
        while self.engine.run_threads:
            if not self.midi_queue.empty():
                if self.pending_event is None:
                    self.pending_event = self.midi_queue.get_nowait()
            if self.pending_event is not None:
                message, timestamp = self.pending_event
                target_time = timestamp + self.engine.stream.latency
                if (target_time >= self.frame_end):
                    pass    #save pending event for next iteration
                else:
                    time_offset = timestamp - self.frame_start
                    sample_offset = max(0, int((time_offset/self.frame_width)*self.frames))
                    if (message.type == 'note_on') and (message.channel == self.engine.midi_channel):
                        if (message.velocity > 0):
                            self.key_pressed((message.note - middle_a, message.velocity, sample_offset))
                        else:
                            self.key_released((message.note - middle_a, sample_offset))
                    elif (message.type == 'note_off') and (message.channel == self.engine.midi_channel):
                        self.key_released((message.note - middle_a, sample_offset))
                    elif (message.type == "control_change") and (message.channel == self.engine.midi_channel):
                        if (message.control in self.engine.midi_cc_functions):
                            self.engine.midi_cc_values.update({message.control: message.value})
                            print(f"DEBUG: control change #{message.control}, value:{self.engine.midi_cc_values[message.control]}")
                            cc_update_function = self.engine.midi_cc_functions[message.control]
                            cc_update_function(message.value)
                    self.pending_event = None
            if not self.frames_queue.empty():
                new_frame_times = self.frames_queue.get_nowait()
                self.frame_width, self.frame_start, self.frame_end, self.frames = new_frame_times
            time.sleep(sleeptime)

    def key_pressed(self, press_event):
        note, velocity, sample_offset = press_event
        new_voice = self.assign_voice(note)
        if new_voice is not None:
            new_pitch = 440.0 * 2**((float(note))/12.0 + self.engine.pitch_offset_1)
            new_pitch2 = 440.0 * 2**((float(note))/12.0 + self.engine.pitch_offset_2) + self.engine.detune_2*new_voice.detune_offset_2
            new_pitch3 = 440.0 * 2**((float(note))/12.0 + self.engine.pitch_offset_3) + self.engine.detune_3*new_voice.detune_offset_3
            new_voice.osc.update_pitch(new_pitch)
            new_voice.osc2.update_pitch(new_pitch2)
            new_voice.osc3.update_pitch(new_pitch3)
            new_voice.velocity = float(velocity)/127.0
            new_voice.env.update_attack_start(sample_offset)
            new_voice.env.update_gate(True)
            new_voice.fenv.update_attack_start(sample_offset)
            new_voice.fenv.update_gate(True)
            new_voice.menv1.update_attack_start(sample_offset)
            new_voice.menv1.update_gate(True)
            new_voice.menv2.update_attack_start(sample_offset)
            new_voice.menv2.update_gate(True)

            new_voice.status = 2
            new_voice.base_note = note

    def key_released(self, release_event):
        note, sample_offset = release_event
        if note in self.engine.note_to_voice: 
            voice_index = self.engine.note_to_voice.get(note)
            self.engine.voices[voice_index].env.update_release_start(sample_offset)
            self.engine.voices[voice_index].env.update_gate(False)
            self.engine.voices[voice_index].fenv.update_release_start(sample_offset)
            self.engine.voices[voice_index].fenv.update_gate(False)
            self.engine.voices[voice_index].menv1.update_release_start(sample_offset)
            self.engine.voices[voice_index].menv1.update_gate(False)
            self.engine.voices[voice_index].menv2.update_release_start(sample_offset)
            self.engine.voices[voice_index].menv2.update_gate(False)
            self.engine.voices[voice_index].status = 1

    def assign_voice(self, note):
        if note in self.engine.note_to_voice:      #assign releasing voice of same note
            if (self.engine.voices[self.engine.note_to_voice[note]].status == 1):
                return self.engine.voices[self.engine.note_to_voice[note]]
        elif self.engine.stopped_voice_indeces:    #assign first stopped voice
            voice_index = self.engine.stopped_voice_indeces.pop(0)
            self.engine.note_to_voice.update({note: voice_index})
            return self.engine.voices[voice_index]
        elif self.engine.released_voice_indeces:   #assign oldest releasing voice
            voice_index = self.engine.released_voice_indeces.pop(0)
            if note in self.engine.note_to_voice:
                self.engine.note_to_voice.pop(note)
            self.engine.note_to_voice.update({note: voice_index})
            return self.engine.voices(voice_index)
        else:                                      #steal oldest voice
            first_note = next(iter(self.engine.note_to_voice))
            first_voice_index = self.engine.note_to_voice.pop(first_note)
            first_voice = self.engine.voices[first_voice_index]
            self.engine.note_to_voice.update({note: first_voice_index})
            return first_voice
