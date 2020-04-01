import numpy as np
import drawing as draw
import math
import utils
from utils import interpolate
from areaWide import AreaWide
import customevents as events

class MidiPiano(AreaWide):

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
        self.COLORS = [draw.paintColors[2], draw.paintColors[4], draw.paintColors[9], draw.paintColors[7], draw.paintColors[8]]
        self.camera = 36
        self.selectedType = 'note'
        self.selected = 12
        self.inputpointer = 0
        self.samplesColors = {}
        self.drawingMap = {}
        self._lastDrawingMap = {}
        self._initDrawingMap()

    """def getKeyRect(self, n):
        positions = [0, 0.5, 1, 1.5, 2, 3, 3.5, 4, 4.5, 5, 5.5, 6]
        x = str(self.left + self.KEYBOARDLEFT + math.floor(n / 12) * 7 + positions[n % 12]) + 'cw + 1p'
        w = '1cw - ' + str(1 if self.isWhiteKey(n) else 2) + 'p'
        return (x, self.top + (4 if self.isWhiteKey(n) else 2), w, 2)"""

    def getKeyRect(self, n):
        positions = [0, 0.5, 1, 1.5, 2, 3, 3.5, 4, 4.5, 5, 5.5, 6]
        x = self.left + self.KEYBOARDLEFT + math.floor(n / 12) * 7 + positions[n % 12]
        w = 1
        return (x, self.top + (4 if self.isWhiteKey(n) else 2), w, 2)

    def getSaveName(self):
        return 'midiPiano ' + str(self.n)

    def getType(self):
        return 'piano'

    def isWhiteKey(self, n):
        return (n % 12) in [0, 2, 4, 5, 7, 9, 11]

    def load(self, filename, console):
        dict = utils.readSaveFile(filename)
        for i in range(0, len(self.samples)):
            x = 'map ' + str(i)
            if x in dict:
                #print(x)
                self.samples[i] = dict[x]

        self.deselectOctave(self.camera / 12)
        self.updateSamplesColors()
        self.updateKeysDrawingMap()
        events.emit('REDRAW_PIANO', {'step': 1})
        #self.redraw()

    def press(self, note, strengh):
        self.sampler.play(self.samples[note], channel = self.n, key = note - 12)

    def release(self, note, strengh):
        self.sampler.stop(self.samples[note], channel = self.n, key = note - 12)

    """ for wide """
    def redrawTitle(self):
        draw.clearRect(self.left, self.top, self.WIDTH, 1);
        draw.rectangle(self.left, self.top, self.WIDTH, 1, '@neutral')
        draw.text('Пианино ' + str(self.n), self.left, interpolate('{self.top}ch + 2p'), '#ffffff console topleft')

    """ for wide """
    def initDraw(self):
        self._initDrawingMap()
        kl = self.KEYBOARDLEFT
        draw.clearRect(self.left, self.top + 1, self.WIDTH, self.HEIGHT, clearColor = '@neutral');
        draw.rectangle(self.left, self.top + 1, self.WIDTH, 1, '@light')
        draw.rectangle(self.left, self.top + self.HEIGHT, self.WIDTH, 1, '@light')
        draw.rectangle(self.left + self.WIDTH - 4, self.top + 1, 4, self.HEIGHT, '@light')
        draw.rectangle(self.left, self.top + 1, kl, self.HEIGHT, '@light')
        draw.rectangle(self.left + kl, self.top + 2, 21, self.HEIGHT - 2, '@clear')

        for i in range(1, 21):
            draw.line(self.left + kl + i, self.top + 4, self.left + kl + i, self.top + self.HEIGHT, '@neutral')
        for i in [3, 7, 10, 14, 17]:
            draw.line(self.left + kl + i, self.top + 2, self.left + kl + i, self.top + self.HEIGHT - 2, '@neutral')

        draw.rectangle(self.left + kl + 0 + 0.5, self.top + 2, 2, self.HEIGHT - 4, '@neutral')
        draw.rectangle(self.left + kl + 3 + 0.5, self.top + 2, 3, self.HEIGHT - 4, '@neutral')
        draw.rectangle(self.left + kl + 7 + 0.5, self.top + 2, 2, self.HEIGHT - 4, '@neutral')
        draw.rectangle(self.left + kl + 10 + 0.5, self.top + 2, 3, self.HEIGHT - 4, '@neutral')
        draw.rectangle(self.left + kl + 14 + 0.5, self.top + 2, 2, self.HEIGHT - 4, '@neutral')
        draw.rectangle(self.left + kl + 17 + 0.5, self.top + 2, 3, self.HEIGHT - 4, '@neutral')

        for i in [1, 4, 5, 8, 11, 12, 15, 18, 19, 20]:
            draw.line(self.left + kl + i + 0.5, self.top + 2, self.left + kl + i + 0.5, self.top + self.HEIGHT - 2, '@clear')

    """ draw in wide """
    def redraw(self):        
        events.emit('REDRAW_PIANO', {'step': 1})    
        """kl = self.KEYBOARDLEFT
        self.redrawKeys()#needRedraw = False)
        self.redrawOctaves()#needRedraw = False)
        self.redrawInfo()#needRedraw = False)
        self._lastDrawingMap = self.drawingMap.copy()"""

    def redrawStep1(self):
        self.redrawOctaves()
        events.emit('REDRAW_PIANO', {'step': 2})

    def redrawStep2(self):
        self.redrawKeys(fr = 0, to = 12)
        events.emit('REDRAW_PIANO', {'step': 3})

    def redrawStep3(self):
        self.redrawKeys(fr = 12, to = 24)
        events.emit('REDRAW_PIANO', {'step': 4})

    def redrawStep4(self):
        self.redrawKeys(fr = 24, to = 36)
        self.redrawInfo()
        events.emit('REDRAW_PIANO', {'step': 5})

    def redrawStep5(self):
        self._lastDrawingMap = self.drawingMap.copy()

    def redrawKeys(self, fr = 0, to = 36):
        kl = self.KEYBOARDLEFT

        for i in range(fr, to):
            key = 'key-' + str(i)
            if self.drawingMap[key] != self._lastDrawingMap[key]:
                args = self.drawingMap[key].split(' ')
                selected = args[0] == '1'
                samplename = args[1] if args[1] != 'None' else None
                color = args[2]
                self.redrawKey(i, selected, samplename, color)

        #if needRedraw == True:
        #    draw.clearRect(self.left + kl, self.top + 2, 21, self.HEIGHT - 2);

        """

        for i in [1, 4, 5, 8, 11, 12, 15, 18, 19, 20]:
            draw.line(self.left + kl + i + 0.5, self.top + 2, self.left + kl + i + 0.5, self.top + self.HEIGHT - 2, '@clear')

        for i in range(0, 24):
            self.redrawKey(i)"""

    def redrawInfo(self):
        kl = self.KEYBOARDLEFT
        for i in range(0, 5):
            key = 'colortable-' + str(i)
            if self.drawingMap[key] != self._lastDrawingMap[key]:
                args = self.drawingMap[key].split(' ')
                draw.clearRect(self.left + kl + 7 * 3 + 0.5, self.top + 1.5 + i, 3, 1, '@light')
                draw.rectangle(self.left + kl + 7 * 3 + 0.5, self.top + 1.5 + i + 0.25, 0.5, 0.5, args[0])
        """index = 0
        for key in self.samplesColors:
            draw.rectangle(kl + 12 * 3 + 0.5, 2 + index + 0.25, 1, 0.5, self.samplesColors[key])
            draw.text(key, kl + 12 * 3 + 1.75, 2 + index + 0.25, '@neutral default midleft') 
            index += 1"""

    def redrawOctaves(self):
        kl = self.KEYBOARDLEFT

        for i in range(0, 9):
            key = 'octave-' + str(i)
            if self.drawingMap[key] != self._lastDrawingMap[key]:
                draw.clearRect(self.left + kl + 6 + i, self.top + 1, 1, 1, '@light')
                if self.drawingMap[key] == '0':
                    draw.rectangle(self.left + kl + 6 + 0.1 + i, self.top + 1.25, 0.8, 0.5, '@neutral')
                elif self.drawingMap[key] == '1': 
                    draw.rectangle(self.left + kl + 6 + 0.1 + i, self.top + 1.25, 0.8, 0.25, '@set')
                    draw.rectangle(self.left + kl + 6 + 0.1 + i, self.top + 1.5, 0.8, 0.25, '@clear')
                elif self.drawingMap[key] == '2': 
                    draw.rectangle(self.left + kl + 6 + 0.1 + i, self.top + 1.25, 0.8, 0.5, '@set')

        #if needRedraw == True:
        #    draw.clearRect(self.left + kl + 6, self.top + 1.25, 9, 0.5, clearColor = '@light');

        """octave = self.camera / 12
        for i in range(0, 9):
            if octave <= i and octave + 3 > i:
                if self.selectedType == 'octave':
                    draw.rectangle(self.left + kl + 6 + 0.1 + i, self.top + 1.25, 0.8, 0.5, '@set')
                else:
                    draw.rectangle(self.left + kl + 6 + 0.1 + i, self.top + 1.25, 0.8, 0.25, '@set')
                    draw.rectangle(self.left + kl + 6 + 0.1 + i, self.top + 1.5, 0.8, 0.25, '@clear')
            else:
                draw.rectangle(self.left + kl + 6 + 0.1 + i, self.top + 1.25, 0.8, 0.5, '@neutral')"""

    def redrawKey(self, n, selected, samplename, color):
        if self.isWhiteKey(n):
            self.redrawWhiteKey(n, selected, samplename, color)
        else:
            self.redrawBlackKey(n, selected, samplename, color)

    def redrawWhiteKey(self, n, selected, samplename, color):
        kl = self.KEYBOARDLEFT
        key = n + self.camera
        color = color if color != 'None' else '@clear' if not selected else '@set'
        textcolor = '@neutral' if selected == False else '@dark'
        bg = '@clear' if selected == False else '@set'
        text = samplename

        rect = self.getKeyRect(n)
        draw.clearRect(str(rect[0]) + 'cw + 1p', rect[1], str(rect[2]) + 'cw - 2p', rect[3], bg)
        
        if selected and samplename != None:
            draw.text(samplename[0], rect[0] + 0.5, rect[1] + 1, textcolor + ' console center')
            draw.text(samplename[1:3], rect[0] + 0.5, rect[1] + 1.6, textcolor + ' tiny center')
        else:
            draw.rectangle(rect[0] + 0.25, rect[1] + 1.5, 0.5, 0.25, color)
        
        """
        rect = self.getKeyRect(n)
        draw.clearRect(rect[0], rect[1], rect[2], rect[3])
        draw.rectangle(rect[0], rect[1], rect[2], rect[3], style)

        color = '@neutral'
        sample = self.samples[key]
        if sample in self.samplesColors:
            color = self.samplesColors[sample]

        rect2 = self.getKeyRectAsNums(n)
        draw.rectangle(rect2[0] + 0.25, rect2[1] + 1.5, 0.5, 0.25, color)"""

        #textrect = self.getKeyRectAsNums(n)
        #textcolor = '@neutral' if isselected == False else '@dark'
        #if text != None:
        #    draw.text(text[0], textrect[0] + 0.5, textrect[1] + 1, textcolor + ' console center')
        #    draw.text(text[1:3], textrect[0] + 0.5, textrect[1] + 1.6, textcolor + ' tiny center')

    def redrawBlackKey(self, n, selected, samplename, color):
        kl = self.KEYBOARDLEFT
        key = n + self.camera
        color = color if color != 'None' else '@neutral' if not selected else '@set'
        bg = '@neutral' if selected == False else '@set'
        textcolor = '@clear' if selected == False else '@dark'
        text = samplename

        rect = self.getKeyRect(n)
        draw.clearRect(str(rect[0]) + 'cw + 1p', rect[1], str(rect[2]) + 'cw - 2p', rect[3], bg)
        
        if selected and samplename != None:
            draw.text(samplename[0], rect[0] + 0.5, rect[1] + 1, textcolor + ' console center')
            draw.text(samplename[1:3], rect[0] + 0.5, rect[1] + 1.6, textcolor + ' tiny center')
        else:
            draw.rectangle(rect[0] + 0.25, rect[1] + 1.5, 0.5, 0.25, color)

        """key = n + self.camera
        text = self.samples[key]
        kl = self.KEYBOARDLEFT
        style = '@neutral' if isselected == False else '@set'
        rect = self.getKeyRect(n)
        draw.clearRect(rect[0], rect[1], rect[2], rect[3])
        draw.rectangle(rect[0], rect[1], rect[2], rect[3], style)

        color = '@light'
        sample = self.samples[key]
        if sample in self.samplesColors:
            color = self.samplesColors[sample]

        rect2 = self.getKeyRectAsNums(n)
        draw.rectangle(rect2[0] + 0.25, rect2[1] + 1.5, 0.5, 0.25, color)

        #textrect = self.getKeyRectAsNums(n)
        #textcolor = '@clear' if isselected == False else '@dark'
        #if text != None:
        #    draw.text(text[0], textrect[0] + 0.5, textrect[1] + 0.7, textcolor + ' console center')
        #    draw.text(text[1:3], textrect[0] + 0.5, textrect[1] + 1.3, textcolor + ' tiny center')"""

    def save(self, path):
        file = open(path, 'a')
        file.write(interpolate('type: piano\n'))
        for i, s in enumerate(self.samples):
            if s == None:
                continue
            file.write(interpolate('map {i}: {s}\n'))
        file.close()

    """def select(self, type, n):
        if self.selectedType != type or self.selected != n:
            if self.selectedType == 'note':
                self.redrawKey(self.selected)
            self.inputpointer = 0

        self.selectedType = 'note'
        self.selected = n

        if type == 'note':
            self.redrawKey(n, True)"""

    def selectNote(self, note):
        if self.selectedType == 'note' and self.selected == note:
            return
        self._dm_keyChanged(self.selected, selected = False)
        self.selectedType = 'note'
        self.selected = note
        self._dm_keyChanged(note, selected = True)
        self.redraw()

    def selectOctave(self, leftoctave):
        self.selectedType = 'octave'
        x = int(leftoctave)
        self._dm_octavesChanged(('0' * x) + ('2' * 3) + ('0' * (6 - x)))
        self.updateKeysDrawingMap()
        self.redraw()

    def deselectOctave(self, leftoctave):
        self.selectedType = 'note'
        x = int(leftoctave)
        self._dm_octavesChanged(('0' * x) + ('1' * 3) + ('0' * (6 - x)))
        self.updateKeysDrawingMap()
        self.redraw()

    def setBankForSelectedKey(self, bank):
        if self.selectedType != 'note':
            return
        sel = self.selected + self.camera
        text = self.samples[sel]
        if text == None:
            text = bank + '01'
        else:
            text = bank + text[1:3]
        self.samples[sel] = text
        self.updateSamplesColors()
        #self.selectNote(self.selected)
        self._dm_keyChanged(self.selected, samplename = text)
        self.inputpointer = 0
        self.redraw()

    def updateSamplesColors(self):
        counts = dict.fromkeys(self.sampler.finals, (-1, 0))

        for index, name in enumerate(self.samples):
            if name != None:
                counts[name] = (
                    index if counts[name][0] == -1 else counts[name][0], 
                    counts[name][1] + 1)
        filtered = sorted(counts.items(), key=lambda item: item[1][0] * 1e3 + item[1][1], reverse = True)

        old = self.samplesColors.copy()

        self.samplesColors = {
            filtered[0][0]: self.COLORS[0],
            filtered[1][0]: self.COLORS[1],
            filtered[2][0]: self.COLORS[2],
            filtered[3][0]: self.COLORS[3],
            filtered[4][0]: self.COLORS[4]}

        for i in range(0, 12 * 3):
            sample = self.samples[i + self.camera]
            added = sample in old and not sample in self.samplesColors
            removed = not sample in old and sample in self.samplesColors
            changed = sample in old and old[sample] != self.samplesColors[sample]
            if added or removed or changed:
                color = self.samplesColors[sample] if sample in self.samplesColors else 'None'
                self._dm_keyChanged(i, color = color)

        self.redraw()

    def updateKeysDrawingMap(self):
        for i in range(self.camera, self.camera + 12 * 3):
            samplename = self.samples[i]
            color = self.samplesColors[samplename] if samplename in self.samplesColors else 'None'
            self._dm_keyChanged(i - self.camera, samplename = 'None', color = color)

    def _dm_keyChanged(self, note, selected = None, samplename = None, color = None):
        key = 'key-' + str(note)
        """if not key in self.drawingMap:
            self.drawingMap[key] = '0 None None'"""
        args = self.drawingMap[key].split(' ')
        sel = args[0] if selected == None else '1' if selected == True else '0'
        sam = args[1] if samplename == None else samplename
        col = args[2] if color == None else color
        self.drawingMap[key] = interpolate('{sel} {sam} {col}')

    def _dm_octavesChanged(self, bitmask):
        for i in range(0, len(bitmask)):
            key = 'octave-' + str(i)
            self.drawingMap[key] = bitmask[i]

    def _initDrawingMap(self):
        for i in range(0, 12*3):
            self.drawingMap['key-' + str(i)] = '0 None None'
            self._lastDrawingMap['key-' + str(i)] = '0 None None'
        for i in range(0, 5):
            self.drawingMap['colortable-' + str(i)] = self.COLORS[i] + ' '
            self._lastDrawingMap['colortable-' + str(i)] = '@clear '
        for i in range(0, 9):
            self.drawingMap['octave-' + str(i)] = '0'
            self._lastDrawingMap['octave-' + str(i)] = '-'
        self.drawingMap['octave-3'] = '1'
        self.drawingMap['octave-4'] = '1'
        self.drawingMap['octave-5'] = '1'


    # wide events

    def enterPressed(self):
        self.sampler.play(self.samples[self.selected + self.camera], channel = 99, key = self.selected + self.camera)

    def rightPressed(self):
        if self.selectedType == 'note':
            if self.selected > 34:
                return
            self.selectNote(self.selected + 1)
        elif self.selectedType == 'octave':
            if self.camera >= 72:
                return
            else:
                self.camera += 12
                self.selectOctave(self.camera / 12)
                #self.redrawOctaves()
                #self.redrawKeys(needRedraw = False)

    def leftPressed(self):
        if self.selectedType == 'note':
            if self.selected < 1:
                return
            self.selectNote(self.selected - 1)
        elif self.selectedType == 'octave':
            if self.camera < 1:
                return
            else:
                self.camera -= 12
                self.selectOctave(self.camera / 12)
                #self.redrawOctaves()
                #self.redrawKeys(needRedraw = False)

    def upPressed(self):
        if self.selectedType == 'note':
            #self.selectedType = 'octave'
            #self.redrawOctaves()
            #self.redrawKey(self.selected)
            self.selectOctave(self.camera / 12)

    def downPressed(self):
        if self.selectedType == 'octave':
            #self.selectedType = 'note'
            #self.redrawOctaves()            
            self.deselectOctave(self.camera / 12)
            self.selectNote(self.selected)

    def digitPressed(self, n):
        if self.selectedType == 'note':
            sel = self.selected + self.camera
            if self.samples[sel] == None:
                return

            text = self.samples[sel]

            if self.inputpointer == 0 and n < 2:
                self.samples[sel] = text[0:1] + str(n) + text[2:3]
                self.inputpointer = 1
                self.selectNote(self.selected)
            elif self.inputpointer == 1 and n < 7 and (n != 0 or text[1:2] != '0'):
                self.samples[sel] = text[0:2] + str(n)
                self.inputpointer = 0
                self.selectNote(self.selected)

            self.updateSamplesColors()

    def aPressed(self):
        if self.selectedType == 'note':
            self.setBankForSelectedKey('a')

    def bPressed(self):
        if self.selectedType == 'note':
            self.setBankForSelectedKey('b')

    def cPressed(self):
        if self.selectedType == 'note':
            self.setBankForSelectedKey('c')

    def dPressed(self):
        if self.selectedType == 'note':
            self.setBankForSelectedKey('d')

    def rPressed(self):
        if self.selectedType == 'note':
            self.setBankForSelectedKey('r')