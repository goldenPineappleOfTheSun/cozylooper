import numpy as np
from utils import interpolate
from soundingSample import SoundingSample

class SamplesController:
    def __init__(self, soundbank):
        self.soundbank = soundbank
        self.finals = dict.fromkeys(soundbank.names, [])
        self.sizes = dict.fromkeys(soundbank.names, [])
        self.currents = []

    """ очистить все over == True. надо иногда вызывать """
    def cleanUp(self):
        pass

    def play(self, name, options = {}, channel = 99, key = 0):
        code = interpolate('{channel}-{key}')
        if (not name in self.finals) or len(self.finals[name]) < 100:
            return
        self.currents.append(SoundingSample(self, code, name, options))

    def read(self, frames):
        result = np.zeros(frames)
        for sound in self.currents:
            if sound.over == False:
                wave = sound.read(frames)
                if wave.any():
                    result += wave
        return result

    def save(self, path):    
        file = open(path + '/sampler.save', 'w+')
        file.close()

    def load(self, path, console):
        pass


    def updateSample(self, name):
        self.finals[name] = self.soundbank.read(name)
        self.sizes[name] = self.soundbank.read(name).shape[0]

    def stopAll(self):
        self.currents = []
