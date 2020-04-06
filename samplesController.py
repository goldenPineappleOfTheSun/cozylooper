import numpy as np
import math
import processor
from utils import interpolate
from soundingSample import SoundingSample
import random

def zeroInterpolationFunction(x):
    return 0

"""
                       stop
             none   note  octave  sample
slide/sus      -      -      -      -
slide/pick     -      -      -      -
chord/sus    organ    -      -      -
chord/pick   chaos  piano  guitar   -
legato/sus     -      -      -    violin
legato/pick    -      -      -    sampler
solo/sus       -      -      -     flute
solo/pick      -      -      -    sampler

"""

class SamplesController:
    def __init__(self, soundbank):
        self.soundbank = soundbank
        """ словарь словарей 1 ключи - названия сэмплов, 2 ключи - названия октав (для быстрого ресэмплинга) """
        self.finals = dict.fromkeys(soundbank.names, {})
        self.suspendModes = dict.fromkeys(soundbank.names, 'sampler')
        self._possibleSuspendModes = ['organ', 'chaos', 'piano', 'guitar', 'violin', 'flute', 'sampler']
        self.currents = []

    def autoplayTick(self, n, fraction):
        possibleRepeats = [1, 2, 4, 8, 16, 32, 64]
        for sound in self.currents:
            repeat = sound.options['repeat']
            if sound.over == False and repeat in possibleRepeats:
                if n % (64 / repeat) == 0:
                    sound.restart() 

    """ очистить все over == True. надо иногда вызывать """
    def cleanUp(self):
        self.currents = list(filter(lambda x: not x.over, self.currents))

    def getSample(self, samplename, notename = 'c1'):
        return self.finals[samplename][notename[-1:]]

    def getSamplesNames(self):
        index = 0
        result = []
        for key in self.finals:
            if '1' in self.finals[key] and len(self.finals[key]['1']) > 10:
                result.append(key)
                index += 1
        return result

    def generateSoundCode(self, channel, key, samplename, options = {}):
        return interpolate('chn={channel}&key={key}&smp={samplename}')

    """ generates samples of note c in all octaves and returns it as dict
        note c expected as input """
    def generateSamplesForOctaves(self, data):
        return {
            '5': processor.slowResample(data, 0.0625),
            '4': processor.slowResample(data, 0.125),
            '3': processor.slowResample(data, 0.25),
            '2': processor.slowResample(data, 0.5),
            '1': processor.slowResample(data, 1),
            '0': processor.slowResample(data, 2),
            'B': processor.slowResample(data, 4),
            'C': processor.slowResample(data, 8),
            'S': processor.slowResample(data, 16),
        }

    def play(self, samplename, options = {}, channel = 99, key = 36):
        if (not samplename in self.finals) or len(self.finals[samplename]['1']) < 100:
            return
        notes = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
        octaves = ['S', 'C', 'B', '0', '1', '2', '3', '4', '5']
        note = notes[key % 12] + octaves[math.floor(key / 12)]
        options['pitch'] = note

        options['loop'] = 'once'
        susMode = self.suspendModes[samplename]
        if susMode == 'organ' or susMode == 'violin' or susMode == 'flute':
            options['loop'] = 'loop'

        if susMode == 'flute' or susMode == 'sampler' or susMode == 'violin':
            self.stopSome(lambda x: x.name == samplename)
        elif susMode == 'guitar':
            self.stopSome(lambda x: x.atStartInfo['octave'] == octaves[math.floor(key / 12)])
        elif susMode == 'piano':
            self.stopSome(lambda x: x.atStartInfo['key'] == key)

        code = self.generateSoundCode(channel, key, samplename, options)

        atStartInfo = {'key': key, 'note': notes[key % 12], 'octave': octaves[math.floor(key / 12)]}

        self.currents.append(SoundingSample(self, channel, code, samplename, options, atStartInfo = atStartInfo))

    def read(self, frames):
        result = np.zeros(frames)
        channelsMask = [False] * 16
        channels = [None]
        currentscount = 0
        for sound in self.currents:
            if sound.over == False:
                currentscount += 1
                wave = sound.read(frames)
                if wave.any():
                    result += wave
                    if channelsMask[sound.channel] == False:
                        channelsMask[sound.channel] = True
                        channels[sound.channel] = np.zeros(frames)
                    channels[sound.channel] += wave
        if currentscount > 4:
            index = 0
            for cur in self.currents:
                if sound.over == False:
                    cur.wheelVolume((currentscount - 4) * math.pow(cur.timespan, 1.2) * index * -1e-8)
                    index += 1
        return channelsMask, channels, result

    def save(self, path):    
        file = open(path + '/sampler.save', 'w+')
        file.close()

    def stop(self, samplename, options = {}, channel = 99, key = 36):
        if (not samplename in self.finals) or len(self.finals[samplename]['1']) < 100:
            return

        if self.suspendModes[samplename] == 'pedal':
            return

        code = self.generateSoundCode(channel, key, samplename, options)

        for sound in filter(lambda x: x.code == code, self.currents):
            sound.fadeout = 0.5
        
    def stopAll(self):
        self.currents = []

    def stopSome(self, func):
        for cur in self.currents:
            if func(cur) == True:
                cur.fadeout = 0.5

    def setSuspendMode(self, sample, mode):
        if mode in  self._possibleSuspendModes:
            self.suspendModes[sample] = mode

    def load(self, path, console):
        pass

    def updateSample(self, name):
        self.finals[name] = self.generateSamplesForOctaves(self.soundbank.read(name))
