import numpy as np
from .generators import WrappedOsc
from .filters import HalSVF, ZDFSVF
from .envelopes import ADSR
from .modulators import LFO, ModEnv
from .effects import Panner

fs = 44100

class Voice():
    def __init__(self, mod_dial_values, mod_dial_modes):
        #mod dial refs
        self.mod_dial_values = mod_dial_values
        self.mod_dial_modes = mod_dial_modes

        #audio buffers
        self.osc_out = np.ascontiguousarray(np.zeros((2048, 2), dtype=np.float32))
        self.osc2_out = np.ascontiguousarray(np.zeros((2048, 2), dtype=np.float32))
        self.osc3_out = np.ascontiguousarray(np.zeros((2048, 2), dtype=np.float32))
        self.filt_out = np.ascontiguousarray(np.zeros((2048, 2), dtype=np.float32))
        self.voice_output = np.ascontiguousarray(np.zeros((2048, 2), dtype=np.float32))

        #mod buffers
         #fenv i/o & no modulation
        self.fenv_in = np.ascontiguousarray(np.ones((2048, 2), dtype=np.float32))
        self.fenv_out = np.ascontiguousarray(np.zeros((2048, 2), dtype=np.float32))
        self.no_mod = np.ascontiguousarray(np.zeros((2048), dtype=np.float32))
         #modulators
          #lfo 1
        self.lfo1_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["lfo1_freq"])]
        self.lfo1_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["lfo1_phase"]))
          #lfo 2
        self.lfo2_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["lfo2_freq"])]
        self.lfo2_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["lfo2_phase"]))
          #menv 1
        self.menv1_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["menv1_att"])]
        self.menv1_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["menv1_rel"]))
          #menv 2
        self.menv2_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["menv2_att"])]
        self.menv2_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["menv2_rel"]))
         #oscillators
          #1
        self.osc1_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["osc_freq"])]
        self.osc1_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc_det"]))
        self.osc1_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc_amp"]))
        self.osc1_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc_width"]))
          #2
        self.osc2_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["osc2_freq"])]
        self.osc2_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc2_det"]))
        self.osc2_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc2_amp"]))
        self.osc2_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc2_width"]))
          #3
        self.osc3_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["osc3_freq"])]
        self.osc3_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc3_det"]))
        self.osc3_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc3_amp"]))
        self.osc3_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["osc3_width"]))
         #panners
        self.osc1_pan_buffer = [self.assign_mod_buffer(self.mod_dial_modes["osc_pan"])]
        self.osc2_pan_buffer = [self.assign_mod_buffer(self.mod_dial_modes["osc2_pan"])]
        self.osc3_pan_buffer = [self.assign_mod_buffer(self.mod_dial_modes["osc3_pan"])]
         #filter envelope
        self.fenv_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["fenv_att"])]
        self.fenv_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["fenv_dec"]))
        self.fenv_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["fenv_sus"]))
        self.fenv_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["fenv_rel"]))
         #filter
        self.filt_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["filt_freq"])]
        self.filt_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["filt_res"]))
        self.filt_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["filt_drive"]))
        self.filt_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["filt_sat"]))
        self.filt_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["fenv_amt"]))
         #amp. envelope
        self.env_mod_buffers = [self.assign_mod_buffer(self.mod_dial_modes["env_att"])]
        self.env_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["env_dec"]))
        self.env_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["env_sus"]))
        self.env_mod_buffers.append(self.assign_mod_buffer(self.mod_dial_modes["env_rel"]))

        #mod values
         #modulators
        self.lfo1_mod_values = [self.mod_dial_values["lfo1_freq"], self.mod_dial_values["lfo1_phase"]]
        self.lfo2_mod_values = [self.mod_dial_values["lfo2_freq"], self.mod_dial_values["lfo2_phase"]]
        self.menv1_mod_values = [self.mod_dial_values["menv1_att"], self.mod_dial_values["menv1_rel"]]
        self.menv2_mod_values = [self.mod_dial_values["menv2_att"], self.mod_dial_values["menv2_rel"]]
         #oscillators
        self.osc1_mod_values = [self.mod_dial_values["osc_freq"], self.mod_dial_values["osc_det"],
                            self.mod_dial_values["osc_amp"], self.mod_dial_values["osc_width"]]
        self.osc2_mod_values = [self.mod_dial_values["osc2_freq"], self.mod_dial_values["osc2_det"],
                            self.mod_dial_values["osc2_amp"], self.mod_dial_values["osc2_width"]]
        self.osc3_mod_values = [self.mod_dial_values["osc3_freq"], self.mod_dial_values["osc3_det"],
                            self.mod_dial_values["osc3_amp"], self.mod_dial_values["osc3_width"]]
         #panners
        self.osc1_pan_value = [self.mod_dial_values["osc_pan"]]
        self.osc2_pan_value = [self.mod_dial_values["osc2_pan"]]
        self.osc3_pan_value = [self.mod_dial_values["osc3_pan"]]
         #filter env
        self.fenv_mod_values = [self.mod_dial_values["fenv_att"], self.mod_dial_values["fenv_dec"],
                            self.mod_dial_values["fenv_sus"], self.mod_dial_values["fenv_rel"]]
         #filter
        self.filt_mod_values = [self.mod_dial_values["filt_freq"], self.mod_dial_values["filt_res"],
                            self.mod_dial_values["filt_drive"], self.mod_dial_values["filt_sat"], self.mod_dial_values["fenv_amt"]]
         #amp env
        self.env_mod_values = [self.mod_dial_values["env_att"], self.mod_dial_values["env_dec"],
                            self.mod_dial_values["env_sus"], self.mod_dial_values["env_rel"]]

        #modules
        self.osc = WrappedOsc(2, 0.5, 55, fs, .5)
        self.osc2 = WrappedOsc(2, 0.5, 55, fs, .5)
        self.osc3 = WrappedOsc(2, 0.5, 55, fs, .5)
        self.pan1 = Panner()
        self.pan2 = Panner()
        self.pan3 = Panner()
        self.filt = HalSVF(0.0, 3520, 10, 1.0)
        self.filt2 = ZDFSVF()
        self.env = ADSR(.01, 1.0, 0.5, 1.0)
        self.fenv = ADSR(.01, .5, .5, .5)
        self.lfo1 = LFO(fs, 5, 0, 0)
        self.lfo2 = LFO(fs, 5, 0, 1)
        self.menv1 = ModEnv(fs, 0.5, 0.5, 0)
        self.menv2 = ModEnv(fs, 0.5, 0.5, 1)

        #attributes
        self.filt_mode = 0
        self.base_note = 0
        self.velocity = 0.0
        self.status = 1
        self.index = 0
        self.detune_offset_1 = 0.0
        self.detune_offset_2 = 0.0
        self.detune_offset_3 = 0.0

    def callback(self, output, frames):
        if self.status != 0:
            #modulators
            # lfo 1
            self.lfo1.process_block(frames, self.lfo1_mod_buffers, self.lfo1_mod_values)
            # lfo 2
            self.lfo2.process_block(frames, self.lfo2_mod_buffers, self.lfo2_mod_values)
            # menv 1
            self.menv1.process_block(frames, self.menv1_mod_buffers, self.menv1_mod_values)
            # menv 2
            self.menv2.process_block(frames, self.menv2_mod_buffers, self.menv2_mod_values)

            #oscillators
            # 1
            self.osc.process_block(self.osc_out[:frames], self.osc1_mod_buffers, self.osc1_mod_values)
            self.pan1.process_block(self.osc_out[:frames], self.osc_out[:frames], self.osc1_pan_buffer[0], self.osc1_pan_value[0])
            self.osc_out *= 0.33
            # 2
            self.osc2.process_block(self.osc2_out[:frames], self.osc2_mod_buffers, self.osc2_mod_values)
            self.pan2.process_block(self.osc2_out[:frames], self.osc2_out[:frames], self.osc2_pan_buffer[0], self.osc2_pan_value[0])
            self.osc2_out *= 0.33
            # 3
            self.osc3.process_block(self.osc3_out[:frames], self.osc3_mod_buffers, self.osc3_mod_values)
            self.pan3.process_block(self.osc3_out[:frames], self.osc3_out[:frames], self.osc3_pan_buffer[0], self.osc3_pan_value[0])
            self.osc3_out *= 0.33
            # sum
            self.osc_out += self.osc2_out
            self.osc_out += self.osc3_out

            # filter envelope
            self.fenv.process_block(self.fenv_in[:frames], self.fenv_out[:frames], self.fenv_mod_buffers, self.fenv_mod_values)

            # filter
            if self.filt_mode == 0:
                self.filt.process_block(self.osc_out[:frames], self.filt_out[:frames], self.fenv_out[:frames], self.filt_mod_buffers, self.filt_mod_values)
            else:
                self.filt2.process_block(self.osc_out[:frames], self.filt_out[:frames], self.fenv_out[:frames], self.filt_mod_buffers, self.filt_mod_values)

            # amplitude envelope
            self.env.process_block(self.filt_out[:frames], output, self.env_mod_buffers, self.env_mod_values)

            # output
            output *= self.velocity
        else:
            output *= 0.0
        if (self.env.state[0] == 0.0) and (self.status > 0):  
            self.status = 0

    #mod dial helpers
    def update_mod_mode(self, name, mode):
        new_buffer = self.assign_mod_buffer(mode)
        if name.startswith("osc"):
            if "2" in name:
                if name.endswith("freq"):
                    self.osc2_mod_buffers[0] = new_buffer
                elif name.endswith("det"):
                    self.osc2_mod_buffers[1] = new_buffer
                elif name.endswith("amp"):
                    self.osc2_mod_buffers[2] = new_buffer
                elif name.endswith("width"):
                    self.osc2_mod_buffers[3] = new_buffer
                elif name.endswith("pan"):
                    self.osc2_pan_buffer[0] = new_buffer
            elif "3" in name:
                if name.endswith("freq"):
                    self.osc3_mod_buffers[0] = new_buffer
                elif name.endswith("det"):
                    self.osc3_mod_buffers[1] = new_buffer
                elif name.endswith("amp"):
                    self.osc3_mod_buffers[2] = new_buffer
                elif name.endswith("width"):
                    self.osc3_mod_buffers[3] = new_buffer
                elif name.endswith("pan"):
                    self.osc3_pan_buffer[0] = new_buffer
            else:
                if name.endswith("freq"):
                    self.osc1_mod_buffers[0] = new_buffer
                elif name.endswith("det"):
                    self.osc1_mod_buffers[1] = new_buffer
                elif name.endswith("amp"):
                    self.osc1_mod_buffers[2] = new_buffer
                elif name.endswith("width"):
                    self.osc1_mod_buffers[3] = new_buffer
                elif name.endswith("pan"):
                    self.osc1_pan_buffer[0] = new_buffer
        elif name.startswith("filt"):
            if name.endswith("freq"):
                self.filt_mod_buffers[0] = new_buffer
            elif name.endswith("res"):
                self.filt_mod_buffers[1] = new_buffer
            elif name.endswith("drive"):
                self.filt_mod_buffers[2] = new_buffer
            elif name.endswith("sat"):
                self.filt_mod_buffers[3] = new_buffer
        elif name.startswith("fenv"):
            if name.endswith("att"):
                self.fenv_mod_buffers[0] = new_buffer
            elif name.endswith("dec"):
                self.fenv_mod_buffers[1] = new_buffer
            elif name.endswith("sus"):
                self.fenv_mod_buffers[2] = new_buffer
            elif name.endswith("rel"):
                self.fenv_mod_buffers[3] = new_buffer
            elif name.endswith("amt"):
                self.filt_mod_buffers[4] = new_buffer
        elif name.startswith("env"):
            if name.endswith("att"):
                self.env_mod_buffers[0] = new_buffer
            elif name.endswith("dec"):
                self.env_mod_buffers[1] = new_buffer
            elif name.endswith("sus"):
                self.env_mod_buffers[2] = new_buffer
            elif name.endswith("rel"):
                self.env_mod_buffers[3] = new_buffer
        elif name.startswith("lfo"):
            if "1" in name:
                if name.endswith("freq"):
                    self.lfo1_mod_buffers[0] = new_buffer
                elif name.endswith("phase"):
                    self.lfo1_mod_buffers[1] = new_buffer
            elif "2" in name:
                if name.endswith("freq"):
                    self.lfo2_mod_buffers[0] = new_buffer
                elif name.endswith("phase"):
                    self.lfo2_mod_buffers[1] = new_buffer
        elif name.startswith("menv"):
            if "1" in name:
                if name.endswith("att"):
                    self.menv1_mod_buffers[0] = new_buffer
                elif name.endswith("rel"):
                    self.menv1_mod_buffers[1] = new_buffer
            elif "2" in name:
                if name.endswith("att"):
                    self.menv2_mod_buffers[0] = new_buffer
                elif name.endswith("rel"):
                    self.menv2_mod_buffers[1] = new_buffer

    def update_mod_value(self, name, value):
        if name.startswith("osc"):
            if "2" in name:
                if name.endswith("freq"):
                    self.osc2_mod_values[0] = value
                elif name.endswith("det"):
                    self.osc2_mod_values[1] = value
                elif name.endswith("amp"):
                    self.osc2_mod_values[2] = value
                elif name.endswith("width"):
                    self.osc2_mod_values[3] = value
                elif name.endswith("pan"):
                    self.osc2_pan_value[0] = value
            elif "3" in name:
                if name.endswith("freq"):
                    self.osc3_mod_values[0] = value
                elif name.endswith("det"):
                    self.osc3_mod_values[1] = value
                elif name.endswith("amp"):
                    self.osc3_mod_values[2] = value
                elif name.endswith("width"):
                    self.osc3_mod_values[3] = value
                elif name.endswith("pan"):
                    self.osc3_pan_value[0] = value
            else:
                if name.endswith("freq"):
                    self.osc1_mod_values[0] = value
                elif name.endswith("det"):
                    self.osc1_mod_values[1] = value
                elif name.endswith("amp"):
                    self.osc1_mod_values[2] = value
                elif name.endswith("width"):
                    self.osc1_mod_values[3] = value
                elif name.endswith("pan"):
                    self.osc1_pan_value[0] = value
        elif name.startswith("filt"):
            if name.endswith("freq"):
                self.filt_mod_values[0] = value
            elif name.endswith("res"):
                self.filt_mod_values[1] = value
            elif name.endswith("drive"):
                self.filt_mod_values[2] = value
            elif name.endswith("sat"):
                self.filt_mod_values[3] = value
        elif name.startswith("fenv"):
            if name.endswith("att"):
                self.fenv_mod_values[0] = value
            elif name.endswith("dec"):
                self.fenv_mod_values[1] = value
            elif name.endswith("sus"):
                self.fenv_mod_values[2] = value
            elif name.endswith("rel"):
                self.fenv_mod_values[3] = value
            elif name.endswith("amt"):
                self.filt_mod_values[4] = value
        elif name.startswith("env"):
            if name.endswith("att"):
                self.env_mod_values[0] = value
            elif name.endswith("dec"):
                self.env_mod_values[1] = value
            elif name.endswith("sus"):
                self.env_mod_values[2] = value
            elif name.endswith("rel"):
                self.env_mod_values[3] = value
        elif name.startswith("lfo"):
            if "1" in name:
                if name.endswith("freq"):
                    self.lfo1_mod_values[0] = value
                elif name.endswith("phase"):
                    self.lfo1_mod_values[1] = value
            elif "2" in name:
                if name.endswith("freq"):
                    self.lfo2_mod_values[0] = value
                elif name.endswith("phase"):
                    self.lfo2_mod_values[1] = value
        elif name.startswith("menv"):
            if "1" in name:
                if name.endswith("att"):
                    self.menv1_mod_values[0] = value
                elif name.endswith("rel"):
                    self.menv1_mod_values[1] = value
            elif "2" in name:
                if name.endswith("att"):
                    self.menv2_mod_values[0] = value
                elif name.endswith("rel"):
                    self.menv2_mod_values[1] = value

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