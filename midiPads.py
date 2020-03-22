import numpy as np
import drawing as draw
import math
from utils import interpolate

class MidiPads():

    def __init__(self, n, sampler):
        self.n = n
        self.samples = np.full((4 * 16), None)
        self.colors = np.full((4 * 16), None)
        self.COLORS = ['@neutral', '#92504f', '#f97b6a', '#90a8d0', '#035084', '#96dbde', '#9896a3', '#de4831', '#b28e6a', '#76c453']
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

    def press(self, note, strengh):
        n = note - 48
        if n < 0 or n > len(self.samples):
            return
        self.sampler.play(self.samples[n], channel = self.n, key = note)

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
        #self.select('key', 0)

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

        textrect = (x, y, 1, 1)
        textcolor = '@clear' if isselected == False else '@dark'
        if text != None:
            draw.text(text, textrect[0], textrect[1], textcolor + ' console topleft')

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

    def setBankForSelectedKey(self, bank):
        sel = self.selected + self.page * 16
        text = self.samples[sel]
        if text == None:
            text = bank + '01'
        else:
            text = bank + text[1:3]
        self.samples[sel] = text
        self.select('key', self.selected)
        self.inputpointer = 0

    # wide events

    def rightPressed(self):
        if self.selected % 4 > 2:
            return
        self.select('key', self.selected + 1)

    def leftPressed(self):
        if self.selected % 4 < 1:
            return
        self.select('key', self.selected - 1)

    def upPressed(self):
        if self.selected < 4:
            return
        self.select('key', self.selected - 4)

    def downPressed(self):
        if self.selected > 11:
            return
        self.select('key', self.selected + 4)

    def digitPressed(self, n):
        if self.selectedType == 'key':
            sel = self.selected + self.page * 16
            if self.samples[sel] == None:
                return

            text = self.samples[sel]

            if self.inputpointer == 0 and n < 2:
                self.samples[sel] = text[0:1] + str(n) + text[2:3]
                self.inputpointer = 1
                self.select('key', self.selected)
            elif self.inputpointer == 1 and n < 7 and (n != 0 or text[1:2] != '0'):
                self.samples[sel] = text[0:2] + str(n)
                self.inputpointer = 0
                self.select('key', self.selected)

    def aPressed(self):
        self.setBankForSelectedKey('a')

    def bPressed(self):
        self.setBankForSelectedKey('b')

    def cPressed(self):
        self.setBankForSelectedKey('c')

    def dPressed(self):
        self.setBankForSelectedKey('d')

    def rPressed(self):
        self.setBankForSelectedKey('r')