import pygame
from utils import interpolate
import drawing as draw
import customevents as events

class Console:
    def __init__(self, x, y, w):
        self.left = x
        self.top = y
        self.WIDTH = w
        self.active = False
        self.text = ''
        self.out = ''
        self.commands = {
            'set-bpm': self.c_changeBpm,
            'set-track-size': self.c_setTrackLength,
            'set-samplerate': self.c_setSamplerate,
            'commands': self.c_listCommands,
            'devices': self.c_listDevices,
            'load-bank': self.c_loadBank,
            'load-tapes': self.c_loadTapes,
            'create-instrument': self.c_createInstrument,
            'wire-midi': self.c_wireMidi,
            'piano': self.c_piano,
            'pads': self.c_pads,
            'save': self.c_save,
            'load': self.c_load,
            'sampler': self.c_sampler
        }
        self.history = []
        self._historyPointer = 0

    def activate(self):
        self.active = True
        self.redraw()

    def deactivate(self):
        self.active = False
        self.text = ''
        self.redraw()

    def emulate(self, cmd, saveHistory = False):
        print('"' + cmd + '"')
        parts = cmd.split(' ')
        if not parts[0] in self.commands:
            self.out = 'ERROR: no such command!'
            if saveHistory:
                self.history.append(cmd)
                self._historyPointer = -1
                self.text = ''
            self.redraw()
            return

        self.out = self.commands[parts[0]](parts[1:])
        self.history.append(self.text)
        self._historyPointer = -1
        self.text = ''
        self.redraw()

    def redraw(self):
        style = '@dark 1p @clear' if self.active else '@light 1p @clear'
        draw.clearRect(self.left, self.top, self.WIDTH, 2)
        draw.rectangle(self.left, self.top, self.WIDTH, 2, style)
        if self.active:
            draw.text(' > ' + self.text, self.left, interpolate('{self.top}ch + 1p'), '@clear console topleft')
        if self.out != '':
            outstyle = '@clear console topleft' if self.active else '@dark console topleft'
            draw.text(' output: ' + self.out, self.left, self.top + 1, outstyle)

    def input(self, key):
        if key == 'backspace':
            self.text = self.text[:-1]
            self.redraw()
            return
        if key == 'prev':
            self.prevCommand()
            return
        if key == 'next':
            self.nextCommand()
            return
        self.text += key
        self.redraw()

    def print(self, text):
        self.out = text
        self.redraw()

    def processCommand(self):
        self.emulate(self.text,True)

    def prevCommand(self):
        if len(self.history) == 0:
            return
        if self._historyPointer > 0:
            self._historyPointer -= 1
        if self._historyPointer == -1:
            self._historyPointer = len(self.history) - 1
        self.text = self.history[self._historyPointer]
        self.redraw()

    def nextCommand(self):
        if len(self.history) == 0:
            return
        if self._historyPointer < len(self.history) - 1:
            self._historyPointer += 1
        self.text = self.history[self._historyPointer]
        self.redraw()

    # commands

    def c_changeBpm(self, arguments):
        bpm = int(arguments[0])

        if not type(bpm) == int:
            return 'ERROR: wrong bpm value'
            raise Exception('wrong bpm value')

        events.emit('DEMAND_CHANGE_BPM', {'value': bpm})  
        return 'bpm changed'

    def c_setTrackLength(self, arguments):
        _args = consoleParser(arguments)
        n = int(_args['named']['n'])
        l = int(_args['named']['l'])

        if type(n) != int or n < 1 or n > 12:
            return 'ERROR: wrong track number'
            raise Exception('wrong track number')

        if type(l) != int or n < 1 or n > 16:
            return 'ERROR: wrong length'
            raise Exception('wrong length')

        events.emit('DEMAND_CHANGE_TRACK_SIZE', {'n': (n-1), 'length': l})
        return 'track ' + str(n) + ' length changed'

    def c_setSamplerate(self, arguments):
        rates = [8000, 11025, 22050, 32000, 48000, 44100]
        _args = consoleParser(arguments)
        s = int(arguments[0])

        if not type(s) == int or s not in rates:
            return 'ERROR: wrong samplerate value'
            raise Exception('wrong samplerate value')

        events.emit('DEMAND_CHANGE_SAMPLERATE', {'value': s})  
        return 'samplerate changed'

    def c_listCommands(self, arguments):
        events.emit('SHOW_LIST_OF_COMMANDS', {'commands': self.commands.keys()})
        return 'list of commands shown'

    def c_listDevices(self, arguments):
        events.emit('SHOW_LIST_OF_DEVICES', {})
        return 'list of devices shown'

    def c_loadBank(self, arguments):
        _args = consoleParser(arguments)
        _named = _args['named']
        path = arguments[0]
        n = _args['named'] if 'n' in _named else None
        if n == None:
            events.emit('LOAD_FOLDER', {'path': path})
            return 'all banks from ' + path + ' have been loaded'
        else:
            events.emit('LOAD_BANK', {'path': path, 'bank': n})
            return 'all banks ' + n + ' from ' + path + ' have been loaded'

    def c_loadTapes(self, arguments):
        _args = consoleParser(arguments)
        _named = _args['named']
        path = arguments[0]
        events.emit('LOAD_TAPES', {'path': path})
        return 'all tracks from ' + path + ' have been loaded'


    def c_createInstrument(self, arguments):
        _args = consoleParser(arguments)
        t = arguments[0]
        n = arguments[1]
        if t == None:
            return 'need to specify type'
        if n == None:
            return 'need to specify channel'
        events.emit('CREATE_INSTRUMENT', {'type': t, 'n': int(n)})
        return t + ' been created'

    def c_wireMidi(self, arguments):
        _args = consoleParser(arguments)
        instrument = int(arguments[0])
        device = int(arguments[1])
        events.emit('WIRE_MIDI', {'instrument': instrument, 'device': device})
        return str(instrument) + ' wired to ' + str(device)

    def c_piano(self, arguments):
        _args = consoleParser(arguments)
        t = 'piano'
        n = arguments[0] if len(arguments) > 0 else 0
        events.emit('CREATE_INSTRUMENT', {'type': t, 'n': int(n)})
        return t + ' has been created'

    def c_pads(self, arguments):
        _args = consoleParser(arguments)
        t = 'pads'
        n = arguments[0] if len(arguments) > 0 else 0
        events.emit('CREATE_INSTRUMENT', {'type': t, 'n': int(n)})
        return t + ' had been created'

    def c_save(self, arguments):
        _args = consoleParser(arguments)
        name = arguments[0]
        events.emit('SAVE', {'name': name})
        return 'saved as ' + name

    def c_load(self, arguments):
        _args = consoleParser(arguments)
        name = arguments[0]
        events.emit('LOAD', {'name': name})
        return name + ' loaded'

    def c_sampler(self, arguments):
        _args = consoleParser(arguments)
        events.emit('SHOW_SAMPLER', {})
        return 'sampler displayed'


def consoleParser(arguments):
    positional = []
    named = {}
    mode = 'none'
    _argName = ''
    for a in arguments:
        if mode == 'named':
            named[_argName] = a
            mode = 'none'
            continue
        elif mode == 'none' and a[0] == '-':
            mode = 'named'
            _argName = a[1:]
            continue
        else:
            positional.append(a)
            continue
    return {
        "positional": positional,
        "named": named
    }
