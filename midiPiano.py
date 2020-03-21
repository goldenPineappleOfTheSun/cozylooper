import numpy as np
import drawing as draw
import math
from utils import interpolate

class MidiPiano():

    def __init__(self, n, sampler):
        self.n = n
        self.samples = np.full((9 * 12), None)
        self.sampler = sampler
        self.volume = 0.5
        self.left = 1
        self.top = 19
        self.KEYBOARDLEFT = 7
        self.WIDTH = 32
        self.HEIGHT = 6
        self.camera = 36
        self.selectedType = 'note'
        self.selected = 12
        self.inputpointer = 0

    """ for wide """
    def redrawTitle(self):
        draw.clearRect(self.left, self.top, self.WIDTH, 1);
        draw.rectangle(self.left, self.top, self.WIDTH, 1, '@neutral')
        draw.text('Пианино ' + str(self.n), self.left, interpolate('{self.top}ch + 2p'), '#ffffff console topleft')

    """ in wide """
    def redraw(self):        
        kl = self.KEYBOARDLEFT
        draw.clearRect(self.left, self.top + 1, self.WIDTH, self.HEIGHT);
        draw.rectangle(self.left, self.top + 1, self.WIDTH, 1, '@light')
        draw.rectangle(self.left, self.top + self.HEIGHT, self.WIDTH, 1, '@light')
        draw.rectangle(self.left + self.WIDTH - 1, self.top + 1, 1, self.HEIGHT, '@light')
        draw.rectangle(self.left, self.top + 1, kl, self.HEIGHT, '@light')
        draw.rectangle(self.left + kl, self.top + 2, 24, self.HEIGHT - 2, '@clear')
        self.redrawKeys()
        self.select('note', 11)

    def redrawKeys(self):
        kl = self.KEYBOARDLEFT
        for i in range(1, 24):
            draw.line(self.left + kl + i, self.top + 4, self.left + kl + i, self.top + self.HEIGHT, '@neutral')
        for i in [3, 7, 10, 14, 17, 21]:
            draw.line(self.left + kl + i, self.top + 2, self.left + kl + i, self.top + self.HEIGHT - 2, '@neutral')

        draw.rectangle(self.left + kl + 0 + 0.5, self.top + 2, 2, self.HEIGHT - 4, '@neutral')
        draw.rectangle(self.left + kl + 3 + 0.5, self.top + 2, 3, self.HEIGHT - 4, '@neutral')
        draw.rectangle(self.left + kl + 7 + 0.5, self.top + 2, 2, self.HEIGHT - 4, '@neutral')
        draw.rectangle(self.left + kl + 10 + 0.5, self.top + 2, 3, self.HEIGHT - 4, '@neutral')
        draw.rectangle(self.left + kl + 14 + 0.5, self.top + 2, 2, self.HEIGHT - 4, '@neutral')
        draw.rectangle(self.left + kl + 17 + 0.5, self.top + 2, 3, self.HEIGHT - 4, '@neutral')
        draw.rectangle(self.left + kl + 21 + 0.5, self.top + 2, 2, self.HEIGHT - 4, '@neutral')

        for i in [1, 4, 5, 8, 11, 12, 15, 18, 19, 20, 22]:
            draw.line(self.left + kl + i + 0.5, self.top + 2, self.left + kl + i + 0.5, self.top + self.HEIGHT - 2, '@clear')

    def redrawKey(self, n, isselected = False):
        if self.isWhiteKey(n):
            self.redrawWhiteKey(n, isselected)
        else:
            self.redrawBlackKey(n, isselected)

    def redrawWhiteKey(self, n, isselected = False):
        text = self.samples[n + self.camera]
        kl = self.KEYBOARDLEFT
        style = '@clear' if isselected == False else '@set'
        rect = self.getKeyRect(n)
        draw.clearRect(rect[0], rect[1], rect[2], rect[3])
        draw.rectangle(rect[0], rect[1], rect[2], rect[3], style)

        textrect = self.getKeyRectAsNums(n)
        textcolor = '@neutral' if isselected == False else '@dark'

        if text != None:
            draw.text(text[0], textrect[0] + 0.5, textrect[1] + 1, textcolor + ' console center')
            draw.text(text[1:3], textrect[0] + 0.5, textrect[1] + 1.6, textcolor + ' tiny center')

    def redrawBlackKey(self, n, isselected = False):
        text = self.samples[n + self.camera]
        kl = self.KEYBOARDLEFT
        style = '@neutral' if isselected == False else '@set'
        rect = self.getKeyRect(n)
        draw.clearRect(rect[0], rect[1], rect[2], rect[3])
        draw.rectangle(rect[0], rect[1], rect[2], rect[3], style)

        textrect = self.getKeyRectAsNums(n)
        textcolor = '@clear' if isselected == False else '@dark'
        if text != None:
            draw.text(text[0], textrect[0] + 0.5, textrect[1] + 0.7, textcolor + ' console center')
            draw.text(text[1:3], textrect[0] + 0.5, textrect[1] + 1.3, textcolor + ' tiny center')

    def isWhiteKey(self, n):
        return (n % 12) in [0, 2, 4, 5, 7, 9, 11]

    def getKeyRect(self, n):
        positions = [0, 0.5, 1, 1.5, 2, 3, 3.5, 4, 4.5, 5, 5.5, 6]
        x = str(self.left + self.KEYBOARDLEFT + math.floor(n / 12) * 7 + positions[n % 12]) + 'cw + 1p'
        w = '1cw - ' + str(1 if self.isWhiteKey(n) else 2) + 'p'
        return (x, self.top + (4 if self.isWhiteKey(n) else 2), w, 2)

    def getKeyRectAsNums(self, n):
        positions = [0, 0.5, 1, 1.5, 2, 3, 3.5, 4, 4.5, 5, 5.5, 6]
        x = self.left + self.KEYBOARDLEFT + math.floor(n / 12) * 7 + positions[n % 12]
        w = 1
        return (x, self.top + (4 if self.isWhiteKey(n) else 2), w, 2)

    def select(self, type, n):
        if self.selectedType != type or self.selected != n:
            if self.selectedType == 'note':
                self.redrawKey(self.selected)
            self.inputpointer = 0

        self.selectedType = 'note'
        self.selected = n

        if type == 'note':
            self.redrawKey(n, True)

    def setBankForSelectedKey(self, bank):
        sel = self.selected + self.camera
        text = self.samples[sel]
        if text == None:
            text = bank + '01'
        else:
            text = bank + text[1:3]
        self.samples[sel] = text
        self.select('note', self.selected)
        self.inputpointer = 0

    # wide events

    def enterPressed(self):
        self.sampler.play(self.samples[self.selected + self.camera])

    def rightPressed(self):
        self.select('note', self.selected + 1)

    def leftPressed(self):
        self.select('note', self.selected - 1)

    def digitPressed(self, n):
        if self.selectedType == 'note':
            sel = self.selected + self.camera
            if self.samples[sel] == None:
                return

            text = self.samples[sel]

            if self.inputpointer == 0 and n < 2:
                self.samples[sel] = text[0:1] + str(n) + text[2:3]
                self.inputpointer = 1
                self.select('note', self.selected)
            elif self.inputpointer == 1 and n < 7 and (n != 0 or text[1:2] != '0'):
                self.samples[sel] = text[0:2] + str(n)
                self.inputpointer = 0
                self.select('note', self.selected)

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