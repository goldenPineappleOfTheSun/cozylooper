import enum
import drawing as draw
import soundfile as sf

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

    def playSound(self):
        sd.play(data * 0.2, fs) 

    def redraw(self, store):
        self.redrawIndicator(MetronomeState.idle)
        self.redrawText(MetronomeState.idle)

    def redrawIndicator(self, state):
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

        draw.rectangle(self.left, self.top, 1, 1, outerStyles[state])
        draw.rectangle(self.left + 0.25, self.top + 0.25, 0.5, 0.5, innerStyles[state])

    def redrawText(self, state):
        styles = {
            MetronomeState.idle: '#444444',
            MetronomeState.work: '#444444',
            MetronomeState.blink: '#444444',
            MetronomeState.set: '#ff9800',
        }

        x = str(self.left + 1) + 'cw + 6'
        y = self.top + 0.5
        draw.text(str(self.bpm) + 'bpm', x, y, styles[state])
