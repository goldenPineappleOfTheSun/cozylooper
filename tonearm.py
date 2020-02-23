import drawing as draw
import math

class Tonearm:
    def __init__(self, left, top, size = 16, width = 1):
        self.size = size
        self.left = left
        self.top = top
        self.WIDTH = width
        self.pos = 0
        self._pointer = 0
        self._lastPosition = 0
        self._size = 1000

    def redraw(self):
        pos = (self.pos - 0) % 16
        y = self.top + 1 + math.floor(pos)
        #prevy = self.top + 1 + math.floor((pos - 1) % 16)
        #draw.clearRect(self.left, prevy, self.WIDTH, y)
        draw.clearRect(self.left, y, self.WIDTH, 1)
        draw.rectangle(self.left + 0.25, y + 0.3, 0.6, 0.6, '@neutral')

    def redrawWhole(self):
        #pos = (self.pos - 0) % 16
        #y = self.top + 1 + math.floor(pos)
        draw.clearRect(self.left, self.top + 1, self.WIDTH, 16)
        #draw.rectangle(self.left + 0.25, y + 0.3, 0.6, 0.6, '@neutral')

    def resetSize(self, 
                  bpm,
                  samplerate = 44100,   
                  channels = 2):
        size = int(samplerate * (60 / bpm) * 16)
        self._size = size
        self.redrawWhole()

    def moveBy(self, 
               step,
               bpm,
               samplerate = 44100,   
               channels = 2):
        prev = self._pointer
        self._pointer = (self._pointer + step) % self._size
        if prev > self._pointer:
            self.redrawWhole()

    def update(self):        
        pixelContains = self._size / (draw.ch * 16)
        if abs(self._pointer - self._lastPosition) > pixelContains:
            self._lastPosition = self._pointer
            self.pos = self._pointer / (self._size / 16)
            self.redraw()

