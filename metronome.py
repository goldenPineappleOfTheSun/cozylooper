import enum
import math
import keyboard
import pygame
import soundfile as sf
import sounddevice as sd
import numpy as np
import drawing as draw
import customevents as events

class MetronomeState(enum.Enum):
    error = 0,
    idle = 1,
    work = 2,
    blink = 3,
    set = 4

class Metronome:
    def __init__(self, bpm = 120, left = 0, top = 0):
        self.bpm = bpm
        self._inputBpm = bpm
        self.left = left
        self.top = top
        self.WIDTH = 5
        self.HEIGHT = 1
        self.sound, self.soundSamplerate = sf.read('metronome_tick.wav', dtype='float32')
        self._soundSize = np.shape(self.sound)[0]
        self.highPitchSound = np.concatenate((self.sound[0::2], [[0, 0] for _ in range(math.floor(len(self.sound) / 2))]))
        self.state = MetronomeState.idle
        self.highPitched = False
        self.bias = 0
        self.beatNumber = 0
        self.maxBeats = 16
        self._flip = False
        self._pointer = 0
        self._soundTonearm = 0
        self._size = 1000
        self.resetSize(bpm)
        self._readyToSound = True

    def backspaceBpmDigit(self):
        if self._inputBpm > 9:
            self._inputBpm = math.floor(self._inputBpm / 10)
            self.redrawText(None)
        else:
            self._inputBpm = 0
            self.redrawText(None)

    def confirm(self):
        if self.bpm == self._inputBpm:
            return
        self.setBpm(self._inputBpm)
        if self.state == MetronomeState.set:
            self.state = MetronomeState.idle
        self.redraw()
        self.enable()

    def cancel(self):
        self._inputBpm = self.bpm
        if self.state == MetronomeState.set:
            self.state = MetronomeState.idle
        self.redraw()

    def configureBpm(self):
        self._inputBpm = 0
        self.state = MetronomeState.set

    def disable(self):
        self.state = MetronomeState.idle 

    def enable(self):
        self.state = MetronomeState.work 

    def inputBpmDigit(self, n):
        if self._inputBpm < 100:
            self._inputBpm = self._inputBpm * 10 + n
            self.redrawText()

    def moveBy(self, 
               step,
               samplerate = 44100,   
               channels = 2):
        self._pointer = (self._pointer + step) % self._size

    def onBeat(self):   
        self.highPitched = False if self.beatNumber % 4 != 0 else True
        events.emit('BPM_TICK', {'beat': self.beatNumber})
        self._readyToSound = True

    def onHalfBeat(self):   
        events.emit('BPM_HALF_TICK', {'beat': self.beatNumber})

    def playSound(self):
        self._soundTonearm = 0

    def redraw(self):
        draw.clearRect(self.left, self.top, self.WIDTH, self.HEIGHT)
        self.redrawIndicator()
        self.redrawText()

    def redrawIndicator(self):
        outerStyles = {
            MetronomeState.idle: '@neutral',
            MetronomeState.work: '@neutral',
            MetronomeState.blink: '@neutral',
            MetronomeState.set: '@set',
        }
        innerStyles = {
            MetronomeState.idle: '@neutral',
            MetronomeState.work: '@light',
            MetronomeState.blink: '@clear',
            MetronomeState.set: '@set',
        }

        draw.clearRect(self.left, self.top, 1, 1)
        draw.rectangle(self.left, self.top, 1, 1, outerStyles[self.state])
        draw.rectangle(self.left + 0.25, self.top + 0.25, 0.5, 0.5, innerStyles[self.state])

    def redrawText(self, needclear = True):
        styles = {
            MetronomeState.idle: '@fore',
            MetronomeState.work: '@fore',
            MetronomeState.blink: '@fore',
            MetronomeState.set: '@darkset',
        }

        bpm = self.bpm if self.state != MetronomeState.set else self._inputBpm

        x = str(self.left + 1) + 'cw + 6p'
        y = self.top + 0.5
        draw.clearRect(self.left + 1, self.top, self.WIDTH - 1, 1)
        draw.text(str(bpm) + 'bpm', x, y, styles[self.state])

    def resetSize(self, 
                  bpm,
                  samplerate = 44100,   
                  channels = 2):
        size = int(samplerate * (60 / bpm) * 16)
        self._size = size

    def setBpm(self, bpm):
        if bpm < 20:
            bpm = 20
        self.bpm = bpm
        self.redraw()
        self.resetSize(self.bpm)
        events.emit('BPM_CHANGED', {'bpm': self.bpm})
        #pygame.event.post(pygame.event.Event(events.BPM_CHANGED_EVENT, {'bpm': self.bpm}))

    def readSound(self, frames):
        if self._soundTonearm > self._soundSize:
            return np.array([])
        sound = self.sound if not self.highPitched else self.highPitchSound 
        result = np.array(sound[self._soundTonearm:self._soundTonearm+frames])
        self._soundTonearm = self._soundTonearm + frames
        return result

    def toggle(self):
        if self.state == MetronomeState.idle or self.state == MetronomeState.set:
            self.enable()
        else:
            self.disable()
        self.redraw()

    def update(self):
        beatContains = self._size / 16
        bias = self.bias
        beat = (self._pointer + bias) / beatContains
        self.beatNumber = int(beat)

        if self._flip == False and beat % 1 <= 0.5:
            self._flip = True
            self.onBeat()
            self.redrawIndicator() 

        if self._flip == True and beat % 1 > 0.5:
            self._flip = False
            self.onHalfBeat()
            self.redrawIndicator() 

        if (bias == 0 and self._readyToSound) or (bias < 0 and (beat % 1) > (1 + self.bias) and self._readyToSound) or (bias > 0 and (beat % 1) > (self.bias) and self._readyToSound):
            metronomeEnabled = self.state == MetronomeState.work or self.state == MetronomeState.blink     
            if metronomeEnabled:
                self.playSound()
                self._readyToSound = False