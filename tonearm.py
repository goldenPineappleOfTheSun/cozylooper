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
        self._size = 44100

    def redraw(self):
        y = self.top + 1 + self.pos
        draw.clearRect(self.left, y - 0.2, self.WIDTH, y + 0.2)
        draw.line(self.left, y, self.left + self.WIDTH, y, '#000000')

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
        pixelContains = self._size / (draw.ch * 16)
        if abs(self._pointer - self._lastPosition) > pixelContains:
            self._lastPosition = self._pointer
            self.pos = self._pointer / (self._size / 16)
            self.redraw()

