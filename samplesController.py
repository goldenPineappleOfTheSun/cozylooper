import numpy as np
import math
from utils import interpolate
from soundingSample import SoundingSample
import random

class SamplesController:
    def __init__(self, soundbank):
        self.soundbank = soundbank
        self.finals = dict.fromkeys(soundbank.names, [])
        self.suspendModes = dict.fromkeys(soundbank.names, 'sus chord')
        self._possibleSuspendModes = ['stop oct', 'stop samp', 'stop note', 'chaos', 'sus solo', 'sus portm', 'sus chord']
        self.sizes = dict.fromkeys(soundbank.names, [])
        self.currents = []

    """ очистить все over == True. надо иногда вызывать """
    def cleanUp(self):
        pass

    def generateSoundCode(self, channel, key, samplename, info = {}, options = {}):
        """susMode = info['susMode']
        if susMode == 'sus solo' or susMode == 'sus portm' or susMode == 'stop samp':
            samplename = 'None'
        print(interpolate('chn={channel}&key={key}&smp={samplename}'))"""
        return interpolate('chn={channel}&key={key}&smp={samplename}')

    def play(self, samplename, options = {}, channel = 99, key = 36):
        if (not samplename in self.finals) or len(self.finals[samplename]) < 100:
            return
        notes = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
        octaves = ['S', 'C', 'B', '0', '1', '2', '3', '4', '5']
        note = notes[key % 12] + octaves[math.floor(key / 12)]
        options['pitch'] = note

        options['loop'] = 'once'
        susMode = self.suspendModes[samplename]
        if susMode == 'sus chord' or susMode == 'sus portm' or susMode == 'sus solo':
            options['loop'] = 'loop'

        info = {'susMode': susMode}
        code = self.generateSoundCode(channel, key, samplename, info, options)

        self.currents.append(SoundingSample(self, code, samplename, options))

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

    def stop(self, samplename, options = {}, channel = 99, key = 36):
        if (not samplename in self.finals) or len(self.finals[samplename]) < 100:
            return

        susMode = self.suspendModes[samplename]
        info = {'susMode': susMode}
        code =self.generateSoundCode(channel, key, samplename, info, options)

        for sound in filter(lambda x: x.code == code, self.currents):
            sound.fadeout = 0.1

    def setSuspendMode(self, sample, mode):
        if mode in  self._possibleSuspendModes:
            self.suspendModes[sample] = mode

    def load(self, path, console):
        pass

    def updateSample(self, name):
        self.finals[name] = self.soundbank.read(name)
        self.sizes[name] = self.soundbank.read(name).shape[0]

    def stopAll(self):
        self.currents = []
