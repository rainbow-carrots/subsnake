from PySide6.QtCore import QTimer

class UpdateSliders(QTimer):
    def __init__(self, engine, window):
        super().__init__()
        self.engine = engine
        self.window = window
        self.row_ccs = window.midi_group.row_ccs
        self.cc_values = engine.midi_cc_values
        self.cc_sliders = window.midi_cc_sliders
        self.setInterval(17)   #~60fps
        self.timeout.connect(self.update_sliders)


    def update_sliders(self):
        for cc in self.row_ccs.values():
            if (cc in self.cc_values) and (cc in self.cc_sliders):
                slider_range = self.cc_sliders[cc].maximum() - self.cc_sliders[cc].minimum()
                scaled_value = int((float(self.cc_values[cc])/127.0)*slider_range) + self.cc_sliders[cc].minimum()
                if scaled_value != self.cc_sliders[cc].value():
                    self.cc_sliders[cc].blockSignals(True)
                    self.cc_sliders[cc].setValue(scaled_value)
                    self.cc_sliders[cc].blockSignals(False)

    def assign_cc_slider(self, module, param):
        cc_slider = None
        if (module == "oscillator 1"):
            if (param == "pitch"):
                cc_slider = self.window.osc_group.osc_freq_slider
            elif (param == "level"):
                cc_slider = self.window.osc_group.osc_amp_slider
            elif (param == "width"):
                cc_slider = self.window.osc_group.osc_width_slider
        elif (module == "oscillator 2"):
            if (param == "pitch"):
                cc_slider = self.window.osc2_group.osc2_freq_slider
            elif (param == "detune"):
                cc_slider = self.window.osc2_group.osc2_det_slider
            elif (param == "level"):
                cc_slider = self.window.osc2_group.osc2_amp_slider
            elif (param == "width"):
                cc_slider = self.window.osc2_group.osc2_width_slider
        elif (module == "filter"):
            if (param == "cutoff"):
                cc_slider = self.window.filt_group.filt_freq_slider
            elif (param == "feedback"):
                cc_slider = self.window.filt_group.filt_res_slider
            elif (param == "drive"):
                cc_slider = self.window.filt_group.filt_drive_slider
            elif (param == "saturate"):
                cc_slider = self.window.filt_group.filt_sat_slider
        elif (module == "filter env"):
            if (param == "attack"):
                cc_slider = self.window.fenv_group.fenv_att_slider
            elif (param == "decay"):
                cc_slider = self.window.fenv_group.fenv_dec_slider
            elif (param == "sustain"):
                cc_slider = self.window.fenv_group.fenv_sus_slider
            elif (param == "release"):
                cc_slider = self.window.fenv_group.fenv_rel_slider
            elif (param == "depth"):
                cc_slider = self.window.fenv_group.fenv_amt_slider
        elif (module == "envelope"):
            if (param == "attack"):
                cc_slider = self.window.env_group.adsr_att_slider
            elif (param == "decay"):
                cc_slider = self.window.env_group.adsr_dec_slider
            elif (param == "sustain"):
                cc_slider = self.window.env_group.adsr_sus_slider
            elif (param == "release"):
                cc_slider = self.window.env_group.adsr_rel_slider
        return cc_slider