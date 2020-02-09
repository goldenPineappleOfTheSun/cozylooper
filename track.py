import math
import queue
import types
import numpy as np
import sounddevice as sd
import drawing as draw
from trackStates import TrackState

class Track:
    def __init__(self, n, behaviour, left = 0, top = 0):
        self.n = n
        self.left = left
        self.top = top
        self.size = 16
        self.beat = 0
        self.state = TrackState.default
        self._inputSize = 16
        self.WIDTH = 1
        self.HEIGHT = 17
        self._initDraw = False
        self.bufferSize = sd.default.blocksize
        self.memory = np.empty([2000, 64, 2], )
        self._pos = 0
        self._memorySize = 0
        self.behaviour = behaviour

    def cancel(self):
        if self.state == TrackState.setSize:
            self._inputSize = self.size
            self.beat = 0
            self.state = TrackState.default
            self.redraw()

    def canWrite(self):
        return self.state == TrackState.record

    def canRead(self):
        return self.state == TrackState.play

    def confirm(self):
        if self.state == TrackState.setSize:
            self.size = self._inputSize
            self.state = TrackState.awaitingChanges
            self.redraw()

    def decreaseSize(self):
        if self.state != TrackState.setSize:
            return
        self._inputSize -= 1
        if (self._inputSize < 1):
            self._inputSize = 1
        self.redraw()

    def drawMeasures(self):
        draw.line(self.left + 0.4, self.top + 1 + 8, self.left + 0.6, self.top + 1 + 8, '#ffffff')
        draw.line(self.left + 0.45, self.top + 1 + 4, self.left + 0.55, self.top + 1 + 4, '#ffffff')
        draw.line(self.left + 0.45, self.top + 1 + 12, self.left + 0.55, self.top + 1 + 12, '#ffffff')

    def increaseSize(self):
        if self.state != TrackState.setSize:
            return
        self._inputSize += 1
        if (self._inputSize > 16):
            self._inputSize = 16
        self.redraw()

    def resetMemory(self, 
                    bpm,
                    samplerate = 44100,   
                    blocksize = sd.default.blocksize, 
                    channels = 2):
        size = int(samplerate * (60 / bpm) * 16)
        self._memorySize = size
        self.memory = np.empty([size + blocksize, channels], )

    def read(self, 
             timeinfo,
             bpm,
             samplerate = 44100,   
             frames = sd.default.blocksize, 
             channels = 2):
        result = np.array(self.memory[self._pos:self._pos+frames])
        self._pos = (self._pos + frames) % self._memorySize
        return result

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
            TrackState.readyToRecord: '#f78181 1p #f78181',
            TrackState.play: '#acd872 1p #ffffff',
            TrackState.readyToPlay: '#acd872 1p #acd872',
            TrackState.awaitingChanges: '#f5cb55 1p #f5cb55',
        }

        draw.clearRect(self.left, self.top, self.WIDTH, 1)
        draw.rectangle(self.left, self.top, 1, 1, styles[self.state])

    def redrawTrack(self):
        styles = {
            TrackState.default: '#ab9b87 1p #ffffff',
            TrackState.setSize: '#f5cb55 1p #ffffff',
            TrackState.record: '#f78181 1p #ffffff',
            TrackState.readyToRecord: '#ffffff 5p #f78181',
            TrackState.play: '#acd872 1p #ffffff',
            TrackState.readyToPlay: '#ffffff 5p #acd872',
            TrackState.awaitingChanges: '#ffffff 5p #f5cb55',
        }

        size = self.size if self.state != TrackState.setSize else self._inputSize

        draw.clearRect(self.left, self.top + 1, self.WIDTH, self.HEIGHT - 1)
        draw.rectangle(self.left, self.top + 1, 1, size, styles[self.state])

        if self.state == TrackState.play or self.state == TrackState.record:
            draw.rectangle(self.left + 0.4, self.top + 1 + 0.25 + self.beat, 0.3, size - self.beat - 0.7, '#ffffff')

    def setBehaviour(self, beh):        
        self.behaviour = beh

    def toggleChangeSize(self):
        if self.state == TrackState.default: 
            self.state = TrackState.setSize
        elif self.state == TrackState.setSize: 
            self.state = TrackState.default
        self.redraw()

    def toggleRecord(self):
        self.cancel()
        if self.state != TrackState.record:
            self.onRecordDemanded()
        else:
            self.onRecordDisabled()
        self._pos = 0

    def togglePlay(self):
        self.cancel()
        if self.state != TrackState.play:
            self.onPlayDemanded()
        else:
            self.onPlayStop()
        self._pos = 0

    def update(self):
        needredraw = not self._initDraw
        if needredraw:
            self.redraw()
            self._initDraw = True

    def write(self,
              indata, 
              timeinfo,
              bpm,
              samplerate = 44100,   
              frames = sd.default.blocksize, 
              channels = 2):
        for i in range(0, frames):
            # спорное решение..
            if len(self.memory) > self._pos + i:
                self.memory[self._pos + i] = indata[i]
        self._pos = (self._pos + frames) % self._memorySize

    ### Begaviour

    def onBeat(self):
        self.beat = (self.beat + 1) % self.size
        if self.beat == 0:
            self.onTrackEnded()
            self.onTrackStarted()
        if self.state == TrackState.play or self.state == TrackState.record:
            self.redraw()
        self.behaviour.onBeat(self)

    def onBar(self):
        self.behaviour.onBar(self)

    def onTrackStarted(self):
        self.behaviour.onTrackStarted(self)
 
    def onTrackEnded(self):
        self.behaviour.onTrackEnded(self)
 
    def onGlobalLoop(self):
        self.behaviour.onGlobalLoop(self)

    def onRecordDemanded(self):
        if self.state == TrackState.setSize or self.state == TrackState.awaitingChanges:
            return 
        self.behaviour.onRecordDemanded(self)

    def onRecordDisabled(self):
        if self.state == TrackState.setSize or self.state == TrackState.awaitingChanges:
            return 
        self.behaviour.onRecordDisabled(self)

    def onPlayDemanded(self):
        if self.state == TrackState.setSize or self.state == TrackState.awaitingChanges:
            return 
        self.behaviour.onPlayDemanded(self)

    def onPlayStop(self):
        if self.state == TrackState.setSize or self.state == TrackState.awaitingChanges:
            return 
        self.behaviour.onPlayStop(self)

