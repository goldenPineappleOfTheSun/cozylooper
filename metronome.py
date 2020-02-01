import enum
import math
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

        if (self.state == MetronomeState.work or self.state == MetronomeState.blink) and _elapsedTicks != self._elapsedTicks:
            self._elapsedTicks = _elapsedTicks
            self.playSound()
            # todo fire event       

        if needRedraw == True or _elapsedTicks <= 1:
            self.redraw(None)

    def playSound(self):
        sd.play(self.sound * 0.2, self.soundSamplerate)

    def enable(self):
        self.state = MetronomeState.work 

    def redraw(self, store):
        draw.clearRect(self.left, self.top, self.WIDTH, self.HEIGHT)
        self.redrawIndicator()
        self.redrawText()

    def redrawIndicator(self):
        outerStyles = {
            MetronomeState.idle: '#444444',
            MetronomeState.work: '#444444',
            MetronomeState.blink: '#444444',
            MetronomeState.set: '#ffeb3b',
        }
        innerStyles = {
            MetronomeState.idle: '#666666',
            MetronomeState.work: '#666666',
            MetronomeState.blink: '#ffffff',
            MetronomeState.set: '#ffeb3b',
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

        x = str(self.left + 1) + 'cw + 6'
        y = self.top + 0.5
        draw.clearRect(self.left + 1, self.top, self.WIDTH - 1, 1)
        draw.text(str(self.bpm) + 'bpm', x, y, styles[self.state])
