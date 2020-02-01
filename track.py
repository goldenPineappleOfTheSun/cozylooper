import enum
import math
import drawing as draw

class TrackState(enum.Enum):
    error = 0,
    default = 1,
    setSize = 2

class Track:
    def __init__(self, n, left = 0, top = 0):
        self.n = n
        self.left = left
        self.top = top
        self.size = 16
        self.state = TrackState.default
        self._inputSize = 16
        self.WIDTH = 1
        self.HEIGHT = 17
        self._initDraw = False

    def changeSize(self):
        self.state = TrackState.setSize
        self.redraw()

    def decreaseSize(self):
        if self.state != TrackState.setSize:
            return
        self._inputSize -= 1
        if (self._inputSize < 1):
            self._inputSize = 1
        self.redraw()

    def increaseSize(self):
        if self.state != TrackState.setSize:
            return
        self._inputSize += 1
        if (self._inputSize > 16):
            self._inputSize = 16
        self.redraw()

    def confirm(self):
        self.size = self._inputSize
        self.state = TrackState.default
        self.redraw()

    def cancel(self):
        self._inputSize = self.size
        self.state = TrackState.default
        self.redraw()

    def update(self):
        needredraw = not self._initDraw
        if needredraw:
            self.redraw()
            self._initDraw = True

    def redraw(self):
        draw.clearRect(self.left, self.top, self.WIDTH, self.HEIGHT)
        self.redrawTrackHeader()
        self.redrawTrack()
        self.drawMeasures()

    def redrawTrackHeader(self):
        styles = {
            TrackState.default: '#dac1a3 1p #ffffff',
            TrackState.setSize: '#f5cb55 1p #ffffff',
        }

        draw.clearRect(self.left, self.top, self.WIDTH, 1)
        draw.rectangle(self.left, self.top, 1, 1, styles[self.state])

    def redrawTrack(self):
        styles = {
            TrackState.default: '#ab9b87 1p #ffffff',
            TrackState.setSize: '#f5cb55 1p #ffffff',
        }

        size = self.size if self.state != TrackState.setSize else self._inputSize

        draw.clearRect(self.left, self.top + 1, self.WIDTH, self.HEIGHT - 1)
        draw.rectangle(self.left, self.top + 1, 1, size, styles[self.state])

    def drawMeasures(self):
        draw.line(self.left + 0.4, self.top + 1 + 8, self.left + 0.6, self.top + 1 + 8, '#ffffff')
        draw.line(self.left + 0.45, self.top + 1 + 4, self.left + 0.55, self.top + 1 + 4, '#ffffff')
        draw.line(self.left + 0.45, self.top + 1 + 12, self.left + 0.55, self.top + 1 + 12, '#ffffff')

