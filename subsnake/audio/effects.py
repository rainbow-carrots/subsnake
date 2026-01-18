import numpy as np
from numba import njit

class StereoDelay():
    def __init__(self, fs, delay_time=0.67, delay_feedback=0.5, mix=.5):
        samples = fs*5      #5s delay
        self.fs = fs
        self.buffer = np.zeros((samples, 2), dtype=np.float32)
        self.delay_time = delay_time
        self.delay_feedback = delay_feedback
        self.write_heads = [0, 0]
        self.offset = 22050
        self.mix_level = mix

    def process_block(self, input, output):
        self.offset = int(self.delay_time*self.fs)
        self.delay_block(input, output, self.buffer, self.offset, self.write_heads, self.delay_feedback, self.mix_level)

    @staticmethod
    @njit(nogil=True, fastmath=True)
    def delay_block(input, output, buffer, offset, write_heads, feedback, mix):
        frames = len(output)
        for c in range (0, 2):
            for n in range(0, frames):
                delayed_sample = buffer[write_heads[c], c]
                buffer[write_heads[c], c] = delayed_sample*feedback + input[n, c]
                write_heads[c] += 1
                if (write_heads[c] >= offset):
                    write_heads[c] -= offset
                output[n, c] = (1.0-mix)*input[n, c] + mix*buffer[write_heads[c], c]

    #helpers
    def update_time(self, new_time):
        self.delay_time = new_time
        self.offset = int(self.delay_time*self.fs)

    def update_feedback(self, new_feedback):
        self.delay_feedback = new_feedback

    def update_mix(self, new_mix):
        self.mix_level = new_mix
            

