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
        y = self.top + 1 + math.floor(self.pos)
        prevy = self.top + 1 + math.floor((self.pos - 1) % 16)
        draw.clearRect(self.left, prevy, self.WIDTH, y)
        draw.clearRect(self.left, y, self.WIDTH, y)
        draw.rectangle(self.left + 0.15, y + 0.2, 0.8, 0.8, '#ab9b87')

    def resetSize(self, 
                  bpm,
                  samplerate = 44100,   
                  channels = 2):
        size = int(samplerate * (60 / bpm) * 16)
        self._size = size

    def moveBy(self, 
               step,
               bpm,
               samplerate = 44100,   
               channels = 2):
        self._pointer = (self._pointer + step) % self._size

    def update(self):        
        pixelContains = self._size / (draw.ch * 16)
        if abs(self._pointer - self._lastPosition) > pixelContains:
            self._lastPosition = self._pointer
            self.pos = self._pointer / (self._size / 16)
            self.redraw()

