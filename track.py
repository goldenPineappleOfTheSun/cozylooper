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
        self.bpm = 120
        self.state = TrackState.default
        self._inputSize = 16
        self._isHalfBeat = False
        self.WIDTH = 1
        self.HEIGHT = 17
        self._initDraw = True
        self.bufferSize = sd.default.blocksize
        self.memory = np.empty([2000, 64, 2], )
        self._pos = 0
        self._memorySize = 0
        self.behaviour = behaviour
        self.playAfterRecord = False

    def cancel(self):
        if self.state == TrackState.setSize:
            self._inputSize = self.size
            self.beat = 0
            self.state = TrackState.default
            self.redraw()
        if self.state == TrackState.record or self.state == TrackState.readyToRecord:
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
            self.resetMemory()
            self.redraw()

    def decreaseSize(self):
        if self.state != TrackState.setSize:
            return
        self._inputSize -= 1
        if (self._inputSize < 1):
            self._inputSize = 1
        self.redraw()

    def drawMeasures(self):
        draw.line(self.left + 0.4, self.top + 1 + 8, self.left + 0.6, self.top + 1 + 8, '@clear')
        draw.line(self.left + 0.45, self.top + 1 + 4, self.left + 0.55, self.top + 1 + 4, '@clear')
        draw.line(self.left + 0.45, self.top + 1 + 12, self.left + 0.55, self.top + 1 + 12, '@clear')

    def increaseSize(self):
        if self.state != TrackState.setSize:
            return
        self._inputSize += 1
        if (self._inputSize > 16):
            self._inputSize = 16
        self.redraw()

    def resetMemory(self, 
                    samplerate = 44100,   
                    blocksize = sd.default.blocksize, 
                    channels = 2):
        size = int(samplerate * (60 / self.bpm) * self.size)
        self._memorySize = size
        self.memory = np.empty([size + blocksize, channels], )

    def read(self, 
             timeinfo,
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
            TrackState.default: '@light 1p @clear',
            TrackState.setSize: '@set 1p @clear',
            TrackState.record: '@record 1p @clear',
            TrackState.readyToRecord: '@record 1p @record' if not self._isHalfBeat else '@lightrecord 1p @record',
            TrackState.play: '@play 1p @clear',
            TrackState.readyToPlay: '@play 1p @play' if not self._isHalfBeat else '@lightplay 1p @play',
            TrackState.awaitingChanges: '@set 1p @set',
        }

        style = styles[self.state]

        if self.playAfterRecord:
            style = styles[TrackState.readyToPlay]

        draw.clearRect(self.left, self.top, self.WIDTH, 1)
        draw.rectangle(self.left, self.top, 1, 1, style)

    def redrawTrack(self):
        styles = {
            TrackState.default: '@neutral 1p @clear',
            TrackState.setSize: '@set 1p @clear',
            TrackState.record: '@record 1p @clear',
            TrackState.readyToRecord: '@record 1p @record' if not self._isHalfBeat else '@lightrecord 1p @record',
            TrackState.play: '@play 1p @clear',
            TrackState.readyToPlay: '@play 1p @play' if not self._isHalfBeat else '@lightplay 1p @play',
            TrackState.awaitingChanges: '@set 1p @clear' if not self._isHalfBeat else '@lightset 1p @clear',
        }

        backstyles = {
            TrackState.record: '@lightrecord 1p @clear',
            TrackState.play: '@lightplay 1p @clear',
        }

        size = self.size if self.state != TrackState.setSize else self._inputSize

        tracked = self.state == TrackState.play or self.state == TrackState.record

        if not tracked:
            draw.clearRect(self.left, self.top + 1, self.WIDTH, self.HEIGHT - 1)
            draw.rectangle(self.left, self.top + 1, 1, size, styles[self.state])
        else:
            if self.beat == 0:
                draw.clearRect(self.left, self.top + 1, self.WIDTH, self.HEIGHT - 1)
            else:
                draw.clearRect(self.left, self.top + self.beat + 1 - 1, self.WIDTH, 2 if self.beat < 15 else 1)
            draw.rectangle(self.left, self.top + 1, 1, self.beat, styles[self.state])
            draw.rectangle(self.left, self.top + self.beat + 1, 1, size - self.beat, backstyles[self.state])

    def setBpm(self, value):
        self.bpm = value

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
        if self.state == TrackState.play:
            self.onPlayStop()
        elif self.state == TrackState.record:
            if self.playAfterRecord == False:
                self.playAfterRecord = True
            else:
                self.playAfterRecord = False
            self.redraw()
        elif self.state == TrackState.readyToRecord:
            if self.playAfterRecord == False:
                self.playAfterRecord = True
            else:
                self.playAfterRecord = False
            self.redraw()
        else:
            self.onPlayDemanded()
        self._pos = 0

    def update(self):
        needredraw = self._initDraw
        if needredraw:
            self.redraw()
            self._initDraw = False

    def write(self,
              indata, 
              timeinfo,
              samplerate = 44100,   
              frames = sd.default.blocksize, 
              channels = 2):
        for i in range(0, frames):
            if len(self.memory) > self._pos + i:
                self.memory[self._pos + i] = indata[i]
        self._pos = (self._pos + frames)# % self._memorySiz

    ### Begaviour

    def onBeat(self):
        self._isHalfBeat = False
        self.beat = (self.beat + 1) % self.size
        if self.beat == 0:
            self.onTrackEnded()
            self.onTrackStarted()
        needDraw = self.state == TrackState.play or self.state == TrackState.record or self.state == TrackState.readyToPlay or self.state == TrackState.readyToRecord or self.state == TrackState.awaitingChanges
        if needDraw:
            self.redraw()
        self.behaviour.onBeat(self)

    def onHalfBeat(self):
        self._isHalfBeat = True
        needDraw = self.state == TrackState.readyToPlay or self.state == TrackState.readyToRecord or self.state == TrackState.awaitingChanges
        if needDraw:
            self.redraw()

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

