import numpy as np


class SoundingSample:
    def __init__(self, controller, code, name, options):
        self.code = code
        self.controller = controller
        self.name = name
        self.options = options
        self._setDefaultOptions()
        self.over = False
        self.pointer = 0

    def read(self, frames):
        sound = self.controller.finals[self.name][self.pointer:self.pointer + frames]
        length = len(sound)
        if length < frames:
            sound = np.pad(sound, (0, frames - length), 'constant')
            if self.options['loop'] == 'once':
                self.over = True
        self.pointer = (self.pointer + frames) % self.controller.sizes[self.name]
        return sound

    def _setDefaultOptions(self):
        if not 'loop' in self.options:
            self.options['loop'] = 'once'