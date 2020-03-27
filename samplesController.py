import numpy as np
import math
from utils import interpolate
from soundingSample import SoundingSample
import random

class SamplesController:
    def __init__(self, soundbank):
        self.soundbank = soundbank
        self.finals = dict.fromkeys(soundbank.names, [])
        self.sizes = dict.fromkeys(soundbank.names, [])
        self.currents = []

    """ очистить все over == True. надо иногда вызывать """
    def cleanUp(self):
        pass

    def play(self, name, options = {}, channel = 99, key = 36):
        code = interpolate('{channel}-{key}')
        if (not name in self.finals) or len(self.finals[name]) < 100:
            return
        notes = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
        octaves = ['S', 'C', 'B', '0', '1', '2', '3', '4', '5']
        note = notes[key % 12] + octaves[math.floor(key / 12)]
        self.currents.append(SoundingSample(self, code, name, {'pitch': note}))

    def read(self, frames):
        result = np.zeros(frames)
        currentscount = 0
        for sound in self.currents:
            if sound.over == False:
                currentscount += 1
                wave = sound.read(frames)
                if wave.any():
                    result += wave
        if currentscount > 4:
            for cur in self.currents:
                if sound.over == False:
                    cur.wheelVolume((currentscount - 4) * math.pow(cur.timespan, 1.5) * -0.0001)
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
