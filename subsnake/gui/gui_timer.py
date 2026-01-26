from PySide6.QtCore import QTimer

class UpdateGUI(QTimer):
    def __init__(self, engine, window):
        super().__init__()
        self.engine = engine
        self.window = window
        self.row_ccs = window.midi_group.row_ccs
        self.cc_values = engine.midi_cc_values
        self.cc_sliders = window.midi_cc_sliders
        self.cc_displays = window.midi_cc_displays
        self.rec_queue = engine.recorder.event_queue
        self.setInterval(17)   #~60fps
        self.timeout.connect(self.update_gui)


    def update_gui(self):
        for cc in self.row_ccs.values():
            if (cc in self.cc_values) and (cc in self.cc_sliders):
                slider_range = self.cc_sliders[cc].maximum() - self.cc_sliders[cc].minimum()
                scaled_value = int((float(self.cc_values[cc])/127.0)*slider_range) + self.cc_sliders[cc].minimum()
                if scaled_value != self.cc_sliders[cc].value():
                    self.cc_sliders[cc].blockSignals(True)
                    self.cc_sliders[cc].setValue(scaled_value)
                    self.cc_sliders[cc].blockSignals(False)
                    if cc in self.cc_displays:
                        display, module, param = self.cc_displays[cc]
                        self.update_cc_display(display, module, param, scaled_value)
        if not self.rec_queue.empty():
            rec_event = self.rec_queue.get_nowait()
            if rec_event == "stop":
                play_button = self.window.recorder.play_button
                if play_button.isChecked():
                    play_button.blockSignals(True)
                    play_button.setChecked(False)
                    play_button.blockSignals(False)
        window_recorder = self.window.recorder
        engine_recorder = self.engine.recorder
        current_mins, current_secs, max_mins, max_secs = engine_recorder.get_time()
        window_recorder.current_time_label.setText(f"{current_mins:02}:{current_secs:02}")
        window_recorder.end_time_label.setText(f"{max_mins:02}:{max_secs:02}")


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
    
    def assign_cc_display(self, module, param):
        cc_display = None
        if (module == "oscillator 1"):
            if (param == "pitch"):
                cc_display = self.window.osc_group.osc_freq_display
            elif (param == "level"):
                cc_display = self.window.osc_group.osc_amp_display
            elif (param == "width"):
                cc_display = self.window.osc_group.osc_width_display
        elif (module == "oscillator 2"):
            if (param == "pitch"):
                cc_display = self.window.osc2_group.osc2_freq_display
            elif (param == "detune"):
                cc_display = self.window.osc2_group.osc2_det_display
            elif (param == "level"):
                cc_display = self.window.osc2_group.osc2_amp_display
            elif (param == "width"):
                cc_display = self.window.osc2_group.osc2_width_display
        elif (module == "filter"):
            if (param == "cutoff"):
                cc_display = self.window.filt_group.filt_freq_display
            elif (param == "feedback"):
                cc_display = self.window.filt_group.filt_fback_display
            elif (param == "drive"):
                cc_display = self.window.filt_group.filt_drive_display
            elif (param == "saturate"):
                cc_display = self.window.filt_group.filt_sat_display
        elif (module == "filter env"):
            if (param == "attack"):
                cc_display = self.window.fenv_group.fenv_att_display
            elif (param == "decay"):
                cc_display = self.window.fenv_group.fenv_dec_display
            elif (param == "sustain"):
                cc_display = self.window.fenv_group.fenv_sus_display
            elif (param == "release"):
                cc_display = self.window.fenv_group.fenv_rel_display
            elif (param == "depth"):
                cc_display = self.window.fenv_group.fenv_amt_display
        elif (module == "envelope"):
            if (param == "attack"):
                cc_display = self.window.env_group.adsr_att_display
            elif (param == "decay"):
                cc_display = self.window.env_group.adsr_dec_display
            elif (param == "sustain"):
                cc_display = self.window.env_group.adsr_sus_display
            elif (param == "release"):
                cc_display = self.window.env_group.adsr_rel_display
        return cc_display
    
    def update_cc_display(self, display, module, param, value):
        if (module == "oscillator 1"):
            if (param == "pitch"):
                display_val = float(value)/100.0
            elif (param == "level"):
                display_val = float(value)/500.0
            elif (param == "width"):
                display_val = float(value)/500.0
            display.display(f"{display_val:.2f}")
        elif (module == "oscillator 2"):
            if (param == "pitch"):
                display_val = float(value)/100.0
            elif (param == "detune"):
                display_val = value/20.0
            elif (param == "level"):
                display_val = float(value)/500.0
            elif (param == "width"):
                display_val = float(value)/500.0
            display.display(f"{display_val:.2f}")
        elif (module == "filter"):
            if (param == "cutoff"):
                display_val = 27.5 * 2**(float(value)/100.0)
                display.display(f"{display_val:.1f}")
            elif (param == "feedback"):
                display_val = 10.0 / (10.0**(value/100.0))
                display.display(f"{1.0/display_val:.2f}")
            elif (param == "drive"):
                display_val = value/40.0
                display.display(f"{display_val:.2f}")
            elif (param == "saturate"):
                display_val = float(value)/100.0
                display.display(f"{display_val:.2f}")
        elif (module == "filter env"):
            if (param == "depth"):
                display_val = float(value)/100.0
            else:
                display_val = float(value)/1000.0
            display.display(f"{display_val:.2f}")
        elif (module == "envelope"):
            display_val = float(value)/1000.0
            display.display(f"{display_val:.2f}")
