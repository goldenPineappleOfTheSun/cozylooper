import enum
import math
import keyboard
import soundfile as sf
import sounddevice as sd
import drawing as draw

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
        self._elapsedTicks = 0

    def update(self, store, ticks):
        interval = 60 / self.bpm
        elapsed = ticks / 1000
        _elapsedTicks = math.floor(elapsed / interval)

        needRedraw = False

        if self.state == MetronomeState.work and elapsed % interval <= interval / 10:
            self.state = MetronomeState.blink
            needRedraw = True
        if self.state == MetronomeState.blink and elapsed % interval > interval / 10:
            self.state = MetronomeState.work
            needRedraw = True
        if self.state == MetronomeState.set:
            needRedraw = True

        if _elapsedTicks != self._elapsedTicks:
            self._elapsedTicks = _elapsedTicks
            metronomeEnabled = self.state == MetronomeState.work or self.state == MetronomeState.blink
            if metronomeEnabled:
                self.playSound()
                # todo fire event       

        if needRedraw == True or _elapsedTicks <= 1:
            self.redraw()

    def playSound(self):
        sd.play(self.sound * 0.2, self.soundSamplerate)

    def enable(self):
        self.state = MetronomeState.work 

    def disable(self):
        self.state = MetronomeState.idle 

    def toggle(self):
        if self.state == MetronomeState.idle or self.state == MetronomeState.set:
            self.enable()
        else:
            self.disable()
        self.redraw()

    def changeBpm(self):
        self._inputBpm = 0
        self.state = MetronomeState.set

    def confirm(self):
        self.setBpm(self._inputBpm)
        self.state = MetronomeState.idle
        self.redraw()

    def cancel(self):
        self._inputBpm = self.bpm
        self.state = MetronomeState.idle
        self.redraw()

    def setBpm(self, bpm):
        if bpm < 20:
            bpm = 20
        self.bpm = bpm
        self.redraw()

    def inputBpmDigit(self, n):
        if self._inputBpm < 100:
            self._inputBpm = self._inputBpm * 10 + n
            self.redrawText()

    def backspaceBpmDigit(self):
        if self._inputBpm > 9:
            self._inputBpm = math.floor(self._inputBpm / 10)
            self.redrawText(None)
        else:
            self._inputBpm = 0
            self.redrawText(None)

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