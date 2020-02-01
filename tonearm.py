import drawing as draw
import math

class Tonearm:
    def __init__(self, left, top, size = 16, width = 1):
        self.size = size
        self.left = left
        self.top = top
        self.WIDTH = width
        self._initDraw = False
        self.pos = 0
        self._lastPosition = 0

    def update(self):        
        needredraw = not self._initDraw

        if abs(self._lastPosition - self.pos) > 0:
            needredraw = True

        if needredraw:
            self.redraw()
            self._initDraw = True

    def setPos(self, bpm = 120, time = 0, pos = None):
        if pos == None:
            timePerBeat = 60 / bpm
            timePreTrack = timePerBeat * 16
            self.pos = (time % timePreTrack) / (timePerBeat * 16)
        else:
            self.pos = pos


    def redraw(self):
        lastY = self.top + 1 + self._lastPosition * self.size
        y = self.top + 1 + self.pos * self.size
        draw.clearRect(self.left, min(lastY, y), self.WIDTH, max(lastY, y))
        draw.line(self.left, y, self.left + 1, y, '#000000')
        self._lastPosition = self.pos

