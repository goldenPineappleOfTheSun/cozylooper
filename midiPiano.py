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
        self.repeats = dict.fromkeys(sampler.finals, None)
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
        self.noteSettings = {
            'row': 'None',
            'col': 0
        }

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
                self.samples[i] = dict[x]
                
        events.emit('REDRAW_PIANO', {'step': 1})

    def press(self, note, strengh):
        options = {}
        samplename = self.samples[note]
        if self.repeats[samplename] != None:
            options['repeat'] = self.repeats[samplename]
        self.sampler.play(samplename, options = options, channel = self.n, key = note - 12)

    def release(self, note, strengh):
        samplename = self.samples[note]
        self.sampler.stop(samplename, channel = self.n, key = note - 12)

    def _redraw(self):        
        self.redrawStep1() 
        self.redrawStep2() 
        self.redrawStep3() 
        self.redrawStep4() 
        self.redrawStep5() 

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

    def redrawInfo(self):
        kl = self.KEYBOARDLEFT
        x = self.left + kl + 7 * 3
        y = self.top + 1.5
        fullRedraw = False

        def changed(name):
            return self.drawingMap[name] != self._lastDrawingMap[name]

        if changed('info'):
            draw.clearRect(x, y, 4, 5, '@light')
            fullRedraw = True

        if self.drawingMap['info'] == 'display':
            if fullRedraw or changed('info-sample-color'):
                color = self.drawingMap['info-sample-color']
                draw.clearRect(x + 0.5, y + 0.25, 0.5, 0.5, '@light')
                draw.rectangle(x + 0.5, y + 0.25, 0.5, 0.5, color)
            if fullRedraw or changed('info-sample-name'):
                name = self.drawingMap['info-sample-name']
                draw.clearRect(x + 1.25, y + 0.25, 1.5, 0.5, '@light')
                draw.text(name, x + 1.25, y + 0.45, '@dark tiny midleft')

        if self.drawingMap['info'] == 'settings':
            cursor = self.drawingMap['info-sample-settings-cursor']
            if changed('info-sample-settings-cursor'):
                fullRedraw = True
            if fullRedraw or changed('info-sample-color'):
                color = self.drawingMap['info-sample-color']
                if color != 'None':
                    draw.clearRect(x + 0.5, y + 0.25, 0.5, 0.5, '@light')
                    draw.rectangle(x + 0.5, y + 0.25, 0.5, 0.5, color)
            if fullRedraw or changed('info-sample-name'):
                name = self.drawingMap['info-sample-name']
                draw.clearRect(x + 1.25, y + 0.25, 1.5, 0.5, '@light')
                draw.text(name, x + 1.25, y + 0.45, '@dark tiny midleft')
            if fullRedraw or changed('info-sample-repeat'):
                text = self.drawingMap['info-sample-repeat']
                print(text)
                text = text if text != 'None' else '-'
                draw.clearRect(x, y + 1, 4, 1, '@light')
                if cursor == '0 0':
                    draw.rectangle(x + 0.5, y + 1.15, 1.5, 0.7, '@set')
                draw.text('repeat', x + 0.25, y + 1.45, '@dark tiny midleft')
                draw.rectangle(x + 2.40, y + 1.15, 1.3, 0.7, '@set' if cursor == '0 1' else '@clear')
                draw.text(text, x + 3, y + 1.45, '@dark tiny center')


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

    def save(self, path):
        file = open(path, 'a')
        file.write(interpolate('type: piano\n'))
        for i, s in enumerate(self.samples):
            if s == None:
                continue
            file.write(interpolate('map {i}: {s}\n'))
        file.close()

    def selectNote(self, note):

        sample = self.samples[note + self.camera]
        self._dm_keyChanged(note, selected = True)
        if sample != None:
            self._dm_infoChanged(mode = 'display', samplecolor = self.samplesColors[sample], samplename = sample)
        else:
            self._dm_infoChanged(mode = 'None')

        if self.selectedType == 'note' and self.selected == note:
            return

        self._dm_keyChanged(self.selected, selected = False)
        self._dm_infoChanged(selectedSettings = 'None')
        self.selectedType = 'note'
        self.selected = note
        self._redraw()

    def deselectNotes(self):
        self._dm_keyChanged(self.selected, selected = False)
        self._dm_infoChanged(mode = 'None')

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

    def selectNoteSettings(self, note):
        self.selectedType = 'settings'
        self._dm_infoChanged(mode = 'settings', selectedSettings = 'repeat')
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
        self.updateKeysDrawingMap()
        self.inputpointer = 0
        self._redraw()

    def settingsTableRight(self):
        if self.selectedType != 'settings':
            return

        if self.noteSettings['row'] == 'None':
            self.noteSettings['row'] = 'repeat'

        if self.noteSettings['row'] == 'repeat':
            self.noteSettings['col'] += 1
            if self.noteSettings['col'] > 1:
                self.noteSettings['col'] = 1
        self._dm_infoChanged(selectedSettings = self.noteSettings['row'], selectedCol = self.noteSettings['col'])
        self.redraw()

    def settingsTableLeft(self):
        if self.selectedType != 'settings':
            return

        if self.noteSettings['row'] == 'None':
            self.noteSettings['row'] = 'repeat'

        if self.noteSettings['row'] == 'repeat':
            self.noteSettings['col'] -= 1
            if self.noteSettings['col'] < 0:
                self.noteSettings['col'] = 0
        self._dm_infoChanged(selectedSettings = self.noteSettings['row'], selectedCol = self.noteSettings['col'])
        self.redraw()

    def settingsTableUp(self):
        if self.selectedType != 'settings':
            return

        if self.noteSettings['row'] == 'None':
            self.noteSettings['row'] = 'repeat'

        if self.noteSettings['row'] == 'repeat':
            sets = [64, 32, 16, 8, 4, 2, None]
            samplename = self.samples[self.selected + self.camera]
            n = sets.index(self.repeats[samplename])
            n = n - 1 if n > 0 else 0
            self.repeats[samplename] = sets[n]
            reps = '1/' + str(sets[n])
            self._dm_infoChanged(repeats = reps)
        self.redraw()

    def settingsTableDown(self):
        if self.selectedType != 'settings':
            return

        if self.noteSettings['row'] == 'None':
            self.noteSettings['row'] = 'repeat'

        if self.noteSettings['row'] == 'repeat':
            sets = [64, 32, 16, 8, 4, 2, None]
            samplename = self.samples[self.selected + self.camera]
            n = sets.index(self.repeats[samplename])
            n = n + 1 if n < 6 else 6
            self.repeats[samplename] = sets[n]
            reps = '1/' + str(sets[n]) if n != 6 else 'None'
            self._dm_infoChanged(repeats = reps)
        self.redraw()

    def updateSamplesColors(self):
        counts = dict.fromkeys(self.sampler.finals, (-1, 0))

        for index, name in enumerate(self.samples):
            if name != None:
                counts[name] = (
                    index if counts[name][0] == -1 else counts[name][0], 
                    counts[name][1] + 1)
        sort = sorted(counts.items(), key=lambda item: item[1][0] * 1e3 + item[1][1], reverse = True)

        old = self.samplesColors.copy()

        keys = [sort[x][0] if sort[x][1][1] != 0 else 'None ' + str(x) for x in range(0, 5)]

        self.samplesColors = {
            keys[0]: self.COLORS[0],
            keys[1]: self.COLORS[1],
            keys[2]: self.COLORS[2],
            keys[3]: self.COLORS[3],
            keys[4]: self.COLORS[4]}

        for i in range(0, 12 * 3):
            sample = self.samples[i + self.camera]
            added = sample in old and not sample in self.samplesColors
            removed = not sample in old and sample in self.samplesColors
            changed = sample in old and old[sample] != self.samplesColors[sample]
            if added or removed or changed:
                color = self.samplesColors[sample] if sample in self.samplesColors else 'None'
                self._dm_keyChanged(i, color = color)

        self._redraw()

    def updateKeysDrawingMap(self):
        for i in range(self.camera, self.camera + 12 * 3):
            samplename = self.samples[i] if self.samples[i] != None else 'None'
            color = self.samplesColors[samplename] if samplename in self.samplesColors else 'None'
            self._dm_keyChanged(i - self.camera, samplename = samplename, color = color)

    def _dm_keyChanged(self, note, selected = None, samplename = None, color = None):
        key = 'key-' + str(note)
        args = self.drawingMap[key].split(' ')
        sel = args[0] if selected == None else '1' if selected == True else '0'
        sam = args[1] if samplename == None else samplename
        col = args[2] if color == None else color
        self.drawingMap[key] = interpolate('{sel} {sam} {col}')

    def _dm_octavesChanged(self, bitmask):
        for i in range(0, len(bitmask)):
            key = 'octave-' + str(i)
            self.drawingMap[key] = bitmask[i]

    def _dm_infoChanged(self, mode = None, samplecolor = None, samplename = None, selectedSettings = None, selectedCol = None, repeats = None):
        if mode != None:
            self.drawingMap['info'] = mode
        if samplecolor != None:
            self.drawingMap['info-sample-color'] = samplecolor
        if samplename != None:
            self.drawingMap['info-sample-name'] = samplename
        if repeats != None:
            self.drawingMap['info-sample-repeat'] = repeats
        if selectedSettings != None:
            sets = {'repeat': 0}
            set = sets[selectedSettings if selectedSettings != 'None' else 'repeat']
            col = selectedCol if selectedCol != None else 0
            self.drawingMap['info-sample-settings-cursor'] = interpolate('{set} {col}')

    def _initDrawingMap(self):
        for i in range(0, 12*3):
            self.drawingMap['key-' + str(i)] = '0 None None'
            self._lastDrawingMap['key-' + str(i)] = '0 None None'
        self.drawingMap['info'] = '0'
        self.drawingMap['info-sample-color'] = 'None'
        self.drawingMap['info-sample-name'] = 'None'
        self.drawingMap['info-sample-repeat'] = 'None'
        self._lastDrawingMap['info'] = '0'
        self._lastDrawingMap['info-sample-color'] = 'None'
        self._lastDrawingMap['info-sample-name'] = 'None'
        self._lastDrawingMap['info-sample-repeat'] = 'None'
        for i in range(0, 9):
            self.drawingMap['octave-' + str(i)] = '0'
            self._lastDrawingMap['octave-' + str(i)] = '-'
        self.drawingMap['octave-3'] = '1'
        self.drawingMap['octave-4'] = '1'
        self.drawingMap['octave-5'] = '1'

    """ abstract wide """

    def deactivate(self):
        self._dm_keyChanged(self.selected, selected = False)
        self.redraw()

    def redrawTitle(self):
        draw.clearRect(self.left, self.top, self.WIDTH, 1);
        draw.rectangle(self.left, self.top, self.WIDTH, 1, '@neutral')
        draw.text('Пианино ' + str(self.n), self.left, interpolate('{self.top}ch + 2p'), '#ffffff console topleft')
        
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

        self._initDrawingMap()
        self.deselectOctave(self.camera / 12)
        self.updateSamplesColors()
        self.updateKeysDrawingMap()

    def redraw(self):        
        events.emit('REDRAW_PIANO', {'step': 1})    


    # wide events

    def escPressed(self):
        self.selectNote(self.selected)
        self._redraw()

    def enterPressed(self):
        #self.sampler.play(self.samples[self.selected + self.camera], channel = 99, key = self.selected + self.camera)
        if self.samples[self.selected + self.camera] != None:
            self.selectNoteSettings(self.samples[self.selected + self.camera])

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
        elif self.selectedType == 'settings':
            self.settingsTableRight()

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
        elif self.selectedType == 'settings':
            self.settingsTableLeft()

    def upPressed(self):
        if self.selectedType == 'note':
            self.deselectNotes()
            self.selectOctave(self.camera / 12)
        elif self.selectedType == 'settings':
            self.settingsTableUp()

    def downPressed(self):
        if self.selectedType == 'octave':         
            self.deselectOctave(self.camera / 12)
            self.selectNote(self.selected)
        elif self.selectedType == 'settings':
            self.settingsTableDown()

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
                self._dm_keyChanged(self.selected, samplename = self.samples[sel])

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