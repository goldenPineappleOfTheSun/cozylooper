import numpy as np
import processor
import math

class SoundingSample:
    def __init__(self, controller, code, name, options):
        self.code = code
        self.controller = controller
        self.name = name
        self.options = options
        self._setDefaultOptions()
        self.over = False
        self.pointer = 0

    def read(self, framescount):
        global pitches

        note = self.options['pitch']
        pitch = processor.getPitchCoefficient(note)
        frames = math.floor(framescount * pitch)
        sound = self.controller.finals[self.name][self.pointer:self.pointer + frames]
        samplesize = self.controller.sizes[self.name]
        if pitch != 1:
            sound = processor.fastInterpolate(sound, pitch)
        length = len(sound)
        if length < frames:
            sound = np.pad(sound, (0, framescount - length), 'constant')
        self.pointer += frames
        if self.pointer > samplesize:
            if self.options['loop'] == 'once':
                self.over = True
            else:
                self.pointer = self.pointer % samplesize
        return sound

    def _setDefaultOptions(self):
        if not 'loop' in self.options:
            self.options['loop'] = 'once'
        if not 'pitch' in self.options:
            self.options['pitch'] = 'c0'