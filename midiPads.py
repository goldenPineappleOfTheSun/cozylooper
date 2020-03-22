import numpy as np
import drawing as draw
import math
from utils import interpolate

class MidiPads():

    def __init__(self, n, sampler):
        self.n = n
        self.samples = np.full((9 * 12), None)
        self.sampler = sampler
        self.volume = 0.5
        self.left = 16
        self.top = 3
        self.KEYBOARDLEFT = 5
        self.KEYBOARDTOP = 6
        self.WIDTH = 17
        self.HEIGHT = 15
        self.page = 0
        self.selectedType = 'key'
        self.selected = 0
        self.inputpointer = 0

    """ for side """
    def redrawTitle(self):
        draw.clearRect(self.left, self.top, self.WIDTH, 1)
        draw.rectangle(self.left, self.top, self.WIDTH, 1, '@neutral')
        draw.text('Падики ' + str(self.n), self.left, interpolate('{self.top}ch + 2p'), '#ffffff console topleft')

    """ in side """
    def redraw(self):        
        kl = self.KEYBOARDLEFT
        draw.clearRect(self.left, self.top + 1, self.WIDTH, self.HEIGHT);
        draw.rectangle(self.left, self.top + 1, self.WIDTH, self.HEIGHT - 1, '@light')
        self.redrawKeys()
        self.select('key', 0)

    def redrawKey(self, n, isselected = False):
        text = self.samples[n + self.page * 16]
        kl = self.left + self.KEYBOARDLEFT
        kt = self.top + self.KEYBOARDTOP
        style = '@neutral' if isselected == False else '@set'
        x = kl + (n % 4) * 2
        y = kt + math.floor(n / 4) * 2
        rect = (str(x) + 'cw + 1p', str(y) + 'ch + 1p', '2cw - 1p', '2cw - 1p')
        draw.clearRect(rect[0], rect[1], rect[2], rect[3])
        draw.rectangle(rect[0], rect[1], rect[2], rect[3], style)

    def redrawKeys(self):
        left = self.KEYBOARDLEFT
        top = self.KEYBOARDTOP
        draw.clearRect(self.left + left, self.top + top, 2 * 4, 2 * 4)
        for x in range(0, 4):
            for y in range(0, 4):
                draw.rectangle(self.left + left + x * 2, self.top + top + y * 2, 2, 2, '@neutral')
                if x == 3:
                    draw.line(self.left + left, self.top + top + y * 2, self.left + left + 8, self.top + top + y * 2, '@light')
                if y == 3:
                    draw.line(self.left + left + x * 2, self.top + top, self.left + left + x * 2, self.top + top + 8, '@light')

    def select(self, type, n):
        if self.selectedType != type or self.selected != n:
            if self.selectedType == 'key':
                self.redrawKey(self.selected)
            self.inputpointer = 0

        self.selectedType = 'key'
        self.selected = n

        if type == 'key':
            self.redrawKey(n, True)


    # wide events

    def rightPressed(self):
        self.select('key', self.selected + 1)

    def leftPressed(self):
        self.select('key', self.selected - 1)

    def upPressed(self):
        self.select('key', self.selected - 4)

    def downPressed(self):
        self.select('key', self.selected + 4)