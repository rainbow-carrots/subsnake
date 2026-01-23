import numpy as np
from numba import njit

class StereoDelay():
    def __init__(self, fs, delay_time=0.5, delay_feedback=0.5, mix=.5):
        samples = fs*2      #2s delay buffer
        self.fs = fs
        self.buffer = np.zeros((samples, 2), dtype=np.float32)
        self.delay_time = delay_time
        self.delay_feedback = delay_feedback
        self.write_heads = [0, 0]
        self.offset = 22050
        self.offset_smooth = [22050, 22050]
        self.mix_level = mix

    def process_block(self, input, output):
        self.offset = self.delay_time*self.fs
        self.delay_block(input, output, self.buffer, self.offset, self.offset_smooth, self.write_heads, self.delay_feedback, self.mix_level)

    @staticmethod
    @njit(nogil=True, fastmath=True)
    def delay_block(input, output, buffer, offset_raw, offset_smooth, write_heads, feedback, mix):
        frames = len(output)
        buffer_size = len(buffer)
        alpha = .0001
        for c in range (0, 2):
            for n in range(0, frames):
                #integate offset & calculate whole/fractional parts
                offset_smooth[c] = offset_smooth[c]*(1.0 - alpha) + offset_raw*alpha
                offset = int(offset_smooth[c])
                offset_frac = offset_smooth[c] - offset

                #calculate read head position & wrap
                read_head = write_heads[c] - offset
                if (read_head < 0):
                    read_head = read_head + buffer_size

                #interpolate sample
                if (read_head + 1 < buffer_size):
                    delayed_sample = (1.0-offset_frac)*buffer[read_head, c] + offset_frac*buffer[read_head + 1, c]
                else:
                    delayed_sample = (1.0-offset_frac)*buffer[read_head, c] + offset_frac*buffer[0, c]

                #write to output buffer & increment/wrap write head
                buffer[write_heads[c], c] = delayed_sample*feedback + input[n, c]
                write_heads[c] += 1
                if (write_heads[c] >= buffer_size):
                    write_heads[c] = 0

                #output
                output[n, c] = (1.0-mix)*input[n, c] + mix*delayed_sample

    #helpers
    def update_time(self, new_time):
        self.delay_time = new_time

    def update_feedback(self, new_feedback):
        self.delay_feedback = new_feedback

    def update_mix(self, new_mix):
        self.mix_level = new_mix


class AudioRecorder():
    def __init__(self, fs):
        self.fs = fs
        self.max_buffer_samples = 4*fs*60*5
        self.record_buffer = np.zeros((self.max_buffer_samples, 2), dtype=np.float32)
        self.play_head = 0
        self.record_head = 0
        self.paused = False
        self.record = False
        self.loop = False
    
    def play(self):
        self.paused = False

    def pause(self):
        self.paused = True

    def stop(self):
        self.record = False
        self.play_head = 0
        self.record_head = 0

    def set_record(self, record_flag):
        self.record = record_flag
    
    def set_loop(self, loop_flag):
        self.loop = loop_flag

    def process_block(self, indata, outdata):
        in_frames = len(indata)
        out_frames = len(outdata)
        if (self.play_head + out_frames) < self.max_buffer_samples:
            outdata = self.record_buffer[self.play_head:self.play_head+out_frames]  #read from buffer
            self.play_head += out_frames
        if (self.record_head + in_frames) < self.max_buffer_samples:
            if (self.record):
                self.record_buffer[self.play_head:self.play_head+in_frames] = indata    #write to buffer
            self.record_head += in_frames

            
