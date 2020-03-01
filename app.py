from multiprocessing import Process
import pygame
import pygame.midi
import numpy as np
import time
from area import Area
import looperAreas
import drawing as draw
import keyboard
import hotkeys
import sounddevice as sd
import customevents as events
from wire import Wire
from metronome import Metronome
from track import Track
from tonearm import Tonearm
from loopDefault import LoopDefault
from console import Console

""" Main Loop """
streamTimeStart = 0
keyboardMap = []
_suspitiousFunctionKeysLag = 10

def selectArea(areaname):
    if not areaname in areas:
        return
    currentArea = areaname

marginTop = 1
wire = Wire(inputDevice = 8, outputDevice = 8)
metronome = Metronome(120, left = 16, top = marginTop)
tracks = [
    Track(0, LoopDefault, 1, marginTop),
    Track(1, LoopDefault, 2, marginTop),
    Track(2, LoopDefault, 3, marginTop),
    Track(3, LoopDefault, 4, marginTop),
    Track(4, LoopDefault, 6, marginTop),
    Track(5, LoopDefault, 7, marginTop),
    Track(6, LoopDefault, 8, marginTop),
    Track(7, LoopDefault, 9, marginTop),
    Track(8, LoopDefault, 11, marginTop),
    Track(9, LoopDefault, 12, marginTop),
    Track(10, LoopDefault, 13, marginTop),
    Track(11, LoopDefault, 14, marginTop),]
tonearmA = Tonearm(size = 16, left = 5, top = marginTop)
tonearmB = Tonearm(size = 16, left = 10, top = marginTop)
clock = pygame.time.Clock()
console = Console(1, 26, 32)

def start():   
    global metronome
    bpmChanged(metronome.bpm)
    wire.start(callback = wireCallback) 
    draw.setNewFont('open-sans', 'open-sans 12')
    draw.setDefaultFont('open-sans')
    console.redraw()

def update():
    ticks = pygame.time.get_ticks()
    for track in tracks:
        track.update()
    metronome.update()
    draw.update()

    global _suspitiousFunctionKeysLag
    _suspitiousFunctionKeysLag -= 1

def tick():    
    tonearmA.update()
    tonearmB.update()

def close():
    wire.stop()
    print('stop!')

def wireCallback(indata, outdata, frames, timeinfo, status):
    global streamTimeStart
    outdata[:] = indata
    if streamTimeStart == 0:
        streamTimeStart = timeinfo.inputBufferAdcTime
    elapsed = timeinfo.inputBufferAdcTime - streamTimeStart
    for track in tracks:
        if track.canWrite():
            track.write(indata, elapsed, frames = frames, samplerate = 44100)
        if track.canRead():
            read = track.read(elapsed, frames = frames, samplerate = 44100)            
            outdata += reshapeSound(read, outdata.shape)
        """ 
        TODO: smooth
        track.fade(indata, elapsed, frames = frames)
        """
    read = metronome.readSound(frames)
    outdata += reshapeSound(read, outdata.shape)

    tonearmA.moveBy(frames, metronome.bpm)
    tonearmB.moveBy(frames, metronome.bpm)
    metronome.moveBy(frames)

def reshapeSound(sound, shape):
    if sound.shape[0] != shape[0]:
        sound = np.resize(sound, [shape[0], shape[1]])
    return sound

def mainTabbed(event):
    looperAreas.changeArea('console')

def consoleTabbed(event):
    looperAreas.changeArea('main')

def playTrack(n, e):
    if keyboard.is_pressed('space'):
        return
    if keyboard.is_pressed('s'):
        return
    if _suspitiousFunctionKeysLag < 0:
        tracks[n].togglePlay()

def bpmChanged(bpm):
    for track in tracks:
        track.setBpm(bpm)
        track.resetMemory(samplerate = 44100)
    tonearmA.resetSize(bpm, samplerate = 44100)
    tonearmB.resetSize(bpm, samplerate = 44100)

def consolePressed(event):
    print('~')

def bPressed(event):
    metronome.toggle()

def setBpmPressed():
    metronome.changeBpm()

def digitPressed(event):
    # some strange arrows bug !!!
    if (event.name == 'up'
    or event.name == 'down'
    or event.name == 'left'
    or event.name == 'right'
    or event.name == 'page up'
    or event.name == 'page down'):
        return
    metronome.inputBpmDigit(int(event.name))

def arrowUpPressed(event):
    for track in tracks:
        track.decreaseSize()

def arrowDownPressed(event):
    for track in tracks:
        track.increaseSize()

def backspacePressed(event):     
    metronome.backspaceBpmDigit()

def enterPressed(event):
    metronome.confirm()
    for track in tracks:
        track.confirm()

def spacePressed(event):
    metronome.confirm()
    for track in tracks:
        track.confirm()

def escPressed(event):
    metronome.cancel()
    for track in tracks:
        track.cancel()

hotkeys.simple('b', bPressed, "main")
hotkeys.simple('tab', mainTabbed, "main")
hotkeys.simple('tab', consoleTabbed, "console")
hotkeys.add('s + b', setBpmPressed, "main")

hotkeys.simple('1', digitPressed, "main")
hotkeys.simple('2', digitPressed, "main")
hotkeys.simple('3', digitPressed, "main")
hotkeys.simple('4', digitPressed, "main")
hotkeys.simple('5', digitPressed, "main")
hotkeys.simple('6', digitPressed, "main")
hotkeys.simple('7', digitPressed, "main")
hotkeys.simple('8', digitPressed, "main")
hotkeys.simple('9', digitPressed, "main")
hotkeys.simple('0', digitPressed, "main")
hotkeys.simple('up', arrowUpPressed, "main")
hotkeys.simple('down', arrowDownPressed, "main")

hotkeys.add('s + f1', tracks[0].toggleChangeSize, "main")
hotkeys.add('s + f2', tracks[1].toggleChangeSize, "main")
hotkeys.add('s + f3', tracks[2].toggleChangeSize, "main")
hotkeys.add('s + f4', tracks[3].toggleChangeSize, "main")
hotkeys.add('s + f5', tracks[4].toggleChangeSize, "main")
hotkeys.add('s + f6', tracks[5].toggleChangeSize, "main")
hotkeys.add('s + f7', tracks[6].toggleChangeSize, "main")
hotkeys.add('s + f8', tracks[7].toggleChangeSize, "main")
hotkeys.add('s + f9', tracks[8].toggleChangeSize, "main")
hotkeys.add('s + f10', tracks[9].toggleChangeSize, "main")
hotkeys.add('s + f11', tracks[10].toggleChangeSize, "main")
hotkeys.add('s + f12', tracks[11].toggleChangeSize, "main")

hotkeys.add('space + f1', tracks[0].toggleRecord, "main")
hotkeys.add('space + f2', tracks[1].toggleRecord, "main")
hotkeys.add('space + f3', tracks[2].toggleRecord, "main")
hotkeys.add('space + f4', tracks[3].toggleRecord, "main")
hotkeys.add('space + f5', tracks[4].toggleRecord, "main")
hotkeys.add('space + f6', tracks[5].toggleRecord, "main")
hotkeys.add('space + f7', tracks[6].toggleRecord, "main")
hotkeys.add('space + f8', tracks[7].toggleRecord, "main")
hotkeys.add('space + f9', tracks[8].toggleRecord, "main")
hotkeys.add('space + f10', tracks[9].toggleRecord, "main")
hotkeys.add('space + f11', tracks[10].toggleRecord, "main")
hotkeys.add('space + f12', tracks[11].toggleRecord, "main")

hotkeys.simple('f1', lambda e: playTrack(0, e), "main")
hotkeys.simple('f2', lambda e: playTrack(1, e), "main")
hotkeys.simple('f3', lambda e: playTrack(2, e), "main")
hotkeys.simple('f4', lambda e: playTrack(3, e), "main")
hotkeys.simple('f5', lambda e: playTrack(4, e), "main")
hotkeys.simple('f6', lambda e: playTrack(5, e), "main")
hotkeys.simple('f7', lambda e: playTrack(6, e), "main")
hotkeys.simple('f8', lambda e: playTrack(7, e), "main")
hotkeys.simple('f9', lambda e: playTrack(8, e), "main")
hotkeys.simple('f10', lambda e: playTrack(9, e), "main")
hotkeys.simple('f11', lambda e: playTrack(10, e), "main")
hotkeys.simple('f12', lambda e: playTrack(11, e), "main")

hotkeys.simple('backspace', backspacePressed, "main")
hotkeys.simple('enter', enterPressed, "main")
hotkeys.simple('space', spacePressed, "main")
hotkeys.simple('esc', escPressed, "main")

def main():
    pygame.init()
    #pygame.midi.init()
    draw.init(34, 28)
    logo = pygame.image.load("Г. Мясоедов Осеннее утро. 1893.jpg")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("Looper")
     
    screen = pygame.display.set_mode((draw.cw * draw.width, draw.height * draw.ch))
    draw.setCanvas(screen)
     
    running = True

    start()
     
    # main loop
    while running:  
        clock.tick(60)
        update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
                running = False
            elif event.type == events.BPM_CHANGED_EVENT:
                bpmChanged(event.dict['bpm'])
            elif event.type == events.BPM_TICK:
                beat = event.dict['beat']
                tick()
                for track in tracks:
                    track.onBeat()
                    if (beat % 4) == 0:
                        track.onBar()
                    if (beat % 16) == 0:
                        track.onGlobalLoop()
            elif event.type == events.BPM_HALF_TICK:
                beat = event.dict['beat']
                for track in tracks:
                    track.onHalfBeat()

if __name__ == "__main__":
    main()