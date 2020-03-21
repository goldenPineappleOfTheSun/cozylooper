import numpy as np

class MidiController:
    def __init__(self):
        self.channels = np.array([None, None, None, None, None, None, None, None, None, None, None, None])

    def appendChannel(self, n, midiInstrument):
        if n < 0 or n > 15:
            return
        self.channels[n] = midiInstrument