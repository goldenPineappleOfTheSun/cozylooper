import enum
import math
import keyboard
import pygame
import soundfile as sf
import sounddevice as sd
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
        self.state = MetronomeState.idle
        self.bias = 0.7
        self.beatNumber = 0
        self.maxBeats = 16
        self._lastBeatNumber = 0
        self._pointer = 0
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
        self.setBpm(self._inputBpm)
        if self.state == MetronomeState.set:
            self.state = MetronomeState.idle
        self.redraw()
        pygame.event.post(pygame.event.Event(events.BPM_CHANGED_EVENT, {'bpm': self.bpm}))
        self.needRedraw = True

    def cancel(self):
        self._inputBpm = self.bpm
        self.state = MetronomeState.idle
        self.redraw()

    def changeBpm(self):
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
        pygame.event.post(pygame.event.Event(events.BPM_TICK, {'beat': self.beatNumber}))  
        self._readyToSound = True 

    def playSound(self):
        #if self._midiPlayer == None:
        #    self._midiPlayer = pygame.midi.Output(0)
        #self._midiPlayer.set_instrument(0)
        #self._midiPlayer.note_on(64, 127)
        sd.play(self.sound * 0.2, self.soundSamplerate)

    def redraw(self):
        draw.clearRect(self.left, self.top, self.WIDTH, self.HEIGHT)
        self.redrawIndicator()
        self.redrawText()

    def redrawIndicator(self):
        outerStyles = {
            MetronomeState.idle: '#ab9b87',
            MetronomeState.work: '#ab9b87',
            MetronomeState.blink: '#ab9b87',
            MetronomeState.set: '#f5cb55',
        }
        innerStyles = {
            MetronomeState.idle: '#ab9b87',
            MetronomeState.work: '#dac1a3',
            MetronomeState.blink: '#ffffff',
            MetronomeState.set: '#f5cb55',
        }

        draw.clearRect(self.left, self.top, 1, 1)
        draw.rectangle(self.left, self.top, 1, 1, outerStyles[self.state])
        draw.rectangle(self.left + 0.25, self.top + 0.25, 0.5, 0.5, innerStyles[self.state])

    def redrawText(self, needclear = True):
        styles = {
            MetronomeState.idle: '#444444',
            MetronomeState.work: '#444444',
            MetronomeState.blink: '#444444',
            MetronomeState.set: '#ff9800',
        }

        bpm = self.bpm if self.state != MetronomeState.set else self._inputBpm

        x = str(self.left + 1) + 'cw + 6'
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
        if abs(self.beatNumber - self._lastBeatNumber) > 0:
            self._lastBeatNumber = self.beatNumber
            self.onBeat()
            self.redraw() 

        if (bias == 0 and self._readyToSound) or (bias < 0 and (beat % 1) > (1 + self.bias) and self._readyToSound) or (bias > 0 and (beat % 1) > (self.bias) and self._readyToSound):
            metronomeEnabled = self.state == MetronomeState.work or self.state == MetronomeState.blink     
            if metronomeEnabled:
                self.playSound()
                self._readyToSound = False