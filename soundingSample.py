import numpy as np
import processor
import math

class SoundingSample:
    def __init__(self, controller, code, name, options):
        self.code = code
        self.controller = controller
        self.name = name
        self.options = options.copy()
        self._setDefaultOptions()
        self.over = False
        self.fadeout = 0
        self.timespan = 0
        self.volume = 1
        self.pointer = 0
        self._glidepointer = None
        self._lastnote = 'c0'

    def read(self, framescount):
        global pitches

        note = self.options['pitch']
        pitch = processor.getPitchCoefficient(note[0:2] + '1')

        if self.options['glide'] == True:
            if self._glidepointer == None:
                _glidepointer = pitch
            else:
                self._glidepointer += (pitch - self._glidepointer) * self.options['glidespeed'] 
                pitch = self._glidepointer

        frames = math.floor(framescount * pitch)
        
        sound = self.controller.getSample(self.name, self.options['pitch'])
        samplesize = len(sound)
        sound = sound[self.pointer:self.pointer + frames]
        
        if pitch != 1:
            sound = processor.fastResample(sound, pitch)

        length = len(sound)
        if length < framescount:
            sound = np.pad(sound, (0, framescount - length), 'constant')

        self.timespan += 1
        self.pointer += frames
        if self.pointer >= samplesize:
            if self.options['loop'] == 'once':
                self.over = True
            else:
                self.pointer = self.pointer % samplesize

        if self.fadeout > 0:
            self.volume -= self.fadeout * 0.01
            if self.volume <= 0.01:
                self.volume = 0
                self.over = True

        return sound * self.volume

    def wheelVolume(self, relative):
        self.volume += relative
        if self.volume > 1:
            self.volume = 1
        if self.volume <= 0:
            self.volume = 0
            self.over = True

    def setGlideTarget(self, note):
        self._glidetarget = note

    def _setDefaultOptions(self):
        if not 'loop' in self.options:
            self.options['loop'] = 'once'
        if not 'pitch' in self.options:
            self.options['pitch'] = 'c0'
        if not 'glide' in self.options:
            self.options['glide'] = False
        if not 'glidespeed' in self.options:
            self.options['glidespeed'] = 0.9