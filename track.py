import enum
import math
import queue
import numpy as np
import sounddevice as sd
import drawing as draw

class TrackState(enum.Enum):
    error = 0,
    default = 1,
    setSize = 2,
    record = 3,
    play = 4

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
        self.bufferSize = sd.default.blocksize
        self.memory = np.empty([2000, 64, 2], )

    def toggleChangeSize(self):
        if self.state == TrackState.default: 
            self.state = TrackState.setSize
        elif self.state == TrackState.setSize: 
            self.state = TrackState.default
        self.redraw()

    def toggleRecord(self):
        self.cancel()
        self.state = TrackState.record if self.state != TrackState.record else TrackState.default
        self.redraw()

    def togglePlay(self):
        self.cancel()
        self.state = TrackState.play if self.state != TrackState.play else TrackState.default
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
        if self.state == TrackState.setSize:
            self.size = self._inputSize
            self.state = TrackState.default
            self.redraw()

    def cancel(self):
        if self.state == TrackState.setSize:
            self._inputSize = self.size
            self.state = TrackState.default
            self.redraw()

    def update(self):
        needredraw = not self._initDraw
        if needredraw:
            self.redraw()
            self._initDraw = True

    def write(self, 
              time,
              bpm,
              samplerate = 44100,   
              blocksize = sd.default.blocksize, 
              channels = 2):
        self.memory[0] = 0 

    def read(self, 
             time,
             bpm,
             samplerate = 44100,   
             blocksize = sd.default.blocksize, 
             channels = 2):
        return np.empty(blocksize)

    def canWrite(self):
        return self.state == TrackState.record

    def canRead(self):
        return self.state == TrackState.play

    """
    deviceParams = (samplerate, blocksize, channels)
    """
    def resetMemory(self, 
                    bpm,
                    samplerate = 44100,   
                    blocksize = sd.default.blocksize, 
                    channels = 2):
        size = int(samplerate * ((60 / bpm) * 16))
        self.memory = np.empty([size, blocksize, channels], )

    def redraw(self):
        draw.clearRect(self.left, self.top, self.WIDTH, self.HEIGHT)
        self.redrawTrackHeader()
        self.redrawTrack()
        self.drawMeasures()

    def redrawTrackHeader(self):
        styles = {
            TrackState.default: '#dac1a3 1p #ffffff',
            TrackState.setSize: '#f5cb55 1p #ffffff',
            TrackState.record: '#f78181 1p #ffffff',
            TrackState.play: '#acd872 1p #ffffff'
        }

        draw.clearRect(self.left, self.top, self.WIDTH, 1)
        draw.rectangle(self.left, self.top, 1, 1, styles[self.state])

    def redrawTrack(self):
        styles = {
            TrackState.default: '#ab9b87 1p #ffffff',
            TrackState.setSize: '#f5cb55 1p #ffffff',
            TrackState.record: '#f78181 1p #ffffff',
            TrackState.play: '#acd872 1p #ffffff'
        }

        size = self.size if self.state != TrackState.setSize else self._inputSize

        draw.clearRect(self.left, self.top + 1, self.WIDTH, self.HEIGHT - 1)
        draw.rectangle(self.left, self.top + 1, 1, size, styles[self.state])

    def drawMeasures(self):
        draw.line(self.left + 0.4, self.top + 1 + 8, self.left + 0.6, self.top + 1 + 8, '#ffffff')
        draw.line(self.left + 0.45, self.top + 1 + 4, self.left + 0.55, self.top + 1 + 4, '#ffffff')
        draw.line(self.left + 0.45, self.top + 1 + 12, self.left + 0.55, self.top + 1 + 12, '#ffffff')

