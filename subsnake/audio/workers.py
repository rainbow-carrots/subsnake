from PySide6.QtCore import QRunnable
import time

class KeyPressWorker(QRunnable):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.press_queue = engine.key_press_events

    def run(self):
        while self.engine.run_threads:
            if not self.press_queue.empty():
                press_event = self.press_queue.get_nowait()
            else:
                press_event = None
            if press_event is not None:
                note, velocity, sample_offset = press_event
                new_voice = self.assign_voice(note)
                if new_voice is not None:
                    new_pitch = 440.0 * 2**((float(note))/12.0 + self.engine.pitch_offset_1)
                    new_pitch2 = 440.0 * 2**((float(note))/12.0 + self.engine.pitch_offset_2) + self.engine.detune*new_voice.detune_offset
                    new_voice.osc.update_pitch(new_pitch)
                    new_voice.osc2.update_pitch(new_pitch2)
                    new_voice.velocity = float(velocity)/127.0
                    new_voice.env.update_attack_start(sample_offset)
                    new_voice.env.update_gate(True)
                    new_voice.fenv.update_attack_start(sample_offset)
                    new_voice.fenv.update_gate(True)
                    new_voice.status = 2
                    new_voice.base_note = note
            time.sleep(0.00290249433)

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
        else:                               #steal oldest voice
            first_note = next(iter(self.engine.note_to_voice))
            first_voice_index = self.engine.note_to_voice.pop(first_note)
            first_voice = self.engine.voices[first_voice_index]
            self.engine.note_to_voice.update({note: first_voice_index})
            return first_voice
        
class KeyReleaseWorker(QRunnable):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.release_queue = engine.key_release_events

    def run(self):
        while self.engine.run_threads:
            if not self.release_queue.empty():
                release_event = self.release_queue.get_nowait()
            else:
                release_event = None
            if release_event is not None:
                note, sample_offset = release_event
                if note in self.engine.note_to_voice: 
                    voice_index = self.engine.note_to_voice.get(note)
                    self.engine.voices[voice_index].env.update_release_start(sample_offset)
                    self.engine.voices[voice_index].env.update_gate(False)
                    self.engine.voices[voice_index].fenv.update_release_start(sample_offset)
                    self.engine.voices[voice_index].fenv.update_gate(False)
                    self.engine.voices[voice_index].status = 1
            time.sleep(0.00290249433)
