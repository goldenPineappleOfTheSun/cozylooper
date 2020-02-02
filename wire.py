import numpy as np
import sounddevice as sd
import time

def _defaultWireCallback(indata, outdata, frames, timeinfo, status):
    outdata[:] = indata


class Wire():
    def __init__(self, 
               inputDevice = sd.default.device,
               outputDevice = sd.default.device,
               samplerate = 44100):
        self.inputDevice = inputDevice
        self.outputDevice = outputDevice
        self.samplerate = samplerate
        self.callback = None
        self.stream = None


    def start(self, callback = None): 
        self.callback = callback
        self.stream = sd.Stream(device=(self.inputDevice, self.outputDevice), 
                                channels=2,
                                samplerate=self.samplerate, 
                                callback = self.callback)
        self.stream.start()

    def stop(self):
        self.stream.close()