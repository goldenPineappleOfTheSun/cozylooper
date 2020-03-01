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
            'set-bpm': self.c_changeBpm
        }

    def activate(self):
        self.active = True
        self.redraw()

    def deactivate(self):
        self.active = False
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
        self.text += key
        self.redraw()

    def processCommand(self):
        parts = self.text.split(' ')
        if not parts[0] in self.commands:
            raise Exception('no such command: ' + parts[0])

        self.out = self.commands[parts[0]](parts[1:])
        self.text = ''
        self.redraw()

    # commands

    def c_changeBpm(self, arguments):
        bpm = int(arguments[0])

        if not type(bpm) == int:
            return 'ERROR: wrong bpm value'
            raise Exception('wrong bpm value')

        pygame.event.post(pygame.event.Event(events.DEMAND_CHANGE_BPM, {'value': bpm}))  
        return 'bpm changed'


