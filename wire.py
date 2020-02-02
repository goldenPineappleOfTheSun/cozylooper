import numpy as np
import sounddevice as sd
import time

start_idx = 0
START_TIME = time.time()
notes = [207.65, 277.18, 349.23]

def _defaultWireCallback(indata, outdata, frames, timeinfo, status):
    current_time = time.time()
    global start_idx
    pitch = notes[int(current_time - START_TIME) % 3]
    t = (start_idx + np.arange(frames)) / 44100
    t = t.reshape(-1, 1)
    s = (t * pitch) % 1
    outdata[:] = 0.02 * s
    start_idx += frames


class Wire():
    def __init__(self, 
               inputDevice = sd.default.device,
               outputDevice = sd.default.device,
               callback = _defaultWireCallback, 
               samplerate = 44100):
        self.inputDevice = inputDevice
        self.outputDevice = outputDevice
        self.samplerate = samplerate
        self.callback = callback
        self.stream = None


    def start(self):     
        self.stream = sd.Stream(device=(self.inputDevice, self.outputDevice), 
                                channels=2,
                                samplerate=self.samplerate, 
                                callback = self.callback)
        self.stream.start()

    def stop(self):
        self.stream.close()