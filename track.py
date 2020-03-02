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
        self.memory = np.empty([2000, 2], )

        """ 
        TODO: smooth
        # smoother transitions
        # fade in has pointer so no need to use queries
        # fade out pointer counts time before stop
        self.fadeInMemory = np.empty([100, 2])
        self._fadeInPointer = 0
        self.fadeOutMemory = np.empty([100, 2])
        self._fadeOutPointer = 0
        self.fadesEnabled = True
        """
        
        self._pos = 0
        self._memorySize = 0
        self.behaviour = behaviour
        self.playAfterRecord = False
        self.histogram = [0] * 16

    """ 
    TODO: smooth
    def appendFades(self):
        fadeLength = len(self.fadeOutMemory)
        for i in range(0, np.shape(self.fadeOutMemory)[0]):
            self.memory[i] = self.memory[i] + self.fadeOutMemory[i] * ((fadeLength - i) / fadeLength)
        for i in range(0, np.shape(self.fadeInMemory)[0]):
            self.memory[len(self.memory) - (fadeLength - i)] = self.memory[i] + self.fadeInMemory[i] * (1 - ((fadeLength - i) / fadeLength))
    """

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
            self.resetMemory(samplerate = 44100)
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

    def drawHistogram(self, start, end, color):
        for i in range(end - start):
            vol = self.histogram[i + start]
            if vol > 0:
                draw.rectangle(self.left + 0.55 - abs(vol) / 4 + ((i + start) % 2 - 0.5) * 0.02, self.top + 1 + i + start, abs(vol / 2), 1, color)

    def increaseSize(self):
        if self.state != TrackState.setSize:
            return
        self._inputSize += 1
        if (self._inputSize > 16):
            self._inputSize = 16
        self.redraw()    

    def setSize(self, n):
        self.state = TrackState.setSize
        self._inputSize = n
        if (self._inputSize > 16):
            self._inputSize = 16
        if (self._inputSize < 1):
            self._inputSize = 1
        self.confirm()

    def resetMemory(self, 
                    samplerate = 44100,   
                    blocksize = sd.default.blocksize, 
                    channels = 2):
        size = int(samplerate * (60 / self.bpm) * self.size)
        self._memorySize = size
        self.memory = np.empty([size + blocksize, channels], )
        self.histogram = [0] * 16
        samplesPerFade = int(samplerate * 0.1)
        self.fadeInMemory = np.zeros([samplesPerFade, channels], )
        self._fadeInPointer = 0
        self.fadeOutMemory = np.zeros([samplesPerFade, channels], )
        self._fadeOutPointer = -1
        self.redraw()

    def read(self, 
             timeinfo,
             samplerate = 44100,   
             frames = sd.default.blocksize, 
             channels = 2):
        result = np.array(self.memory[self._pos:self._pos+frames])
        self._pos = (self._pos + frames) % self._memorySize
        return result

    def redraw(self):
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
            TrackState.record: '@record',
            TrackState.readyToRecord: '@record 1p @record' if not self._isHalfBeat else '@lightrecord 1p @record',
            TrackState.play: '@play',
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

            if self.state == TrackState.default:
                self.drawHistogram(0, 16, '@set')
        else:
            if self.beat == 0:
                draw.clearRect(self.left, self.top + 1, self.WIDTH, self.HEIGHT - 1)
                draw.rectangle(self.left, self.top + self.beat + 1, 1, size - self.beat, backstyles[self.state]) 
                self.drawHistogram(0, 15, '@darkplay' if self.state == TrackState.play else '@darkrecord')
            else:
                draw.clearRect(self.left, self.top + 1 + self.beat - 1, self.WIDTH, 1)
                self.drawHistogram(self.beat, 15, '@darkplay' if self.state == TrackState.play else '@darkrecord')
                draw.rectangle(self.left, self.top + 1 + self.beat - 1, self.WIDTH, 1, styles[self.state])  
                self.drawHistogram(self.beat - 1, self.beat, '@darkplay' if self.state == TrackState.play else '@darkrecord')      

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

    """ 
    TODO: smooth
    def fade(self,
             indata, 
             timeinfo,
             samplerate = 44100,   
             frames = sd.default.blocksize, 
             channels = 2):
        if not self.fadesEnabled:
            return
        
        for i in range(0, frames):
            #self.fadeInMemory[:][self._fadeInPointer] = 0
            a = self.fadeInMemory[:][self._fadeInPointer]
            self._fadeInPointer = (self._fadeInPointer + 1) % len(self.fadeInMemory)

            if self._fadeOutPointer > 0:
                self.fadeOutMemory[len(self.fadeOutMemory) - self._fadeOutPointer] = indata[i]
            elif self._fadeOutPointer == 0:
                self.appendFades()
                self._fadeOutPointer = -1
        """



    def write(self,
              indata, 
              timeinfo,
              samplerate = 44100,   
              frames = sd.default.blocksize, 
              channels = 2):
        for i in range(0, frames):
            if len(self.memory) > self._pos + i:
                self.memory[self._pos + i] = indata[i]
        self._pos = (self._pos + frames)
        volmul = 5
        maxvol = np.amax(np.abs(indata)) * volmul
        if self.histogram[self.beat] < maxvol:
            self.histogram[self.beat] += 0.01
        else:
            self.histogram[self.beat] -= 0.000

        if self.histogram[self.beat] > 0.9:
            self.histogram[self.beat] = 0.9

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

