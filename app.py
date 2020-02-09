from multiprocessing import Process
import pygame
import pygame.midi
import numpy as np
import time
import drawing as draw
import keyboard
import sounddevice as sd
import customevents as events
from wire import Wire
from metronome import Metronome
from track import Track
from tonearm import Tonearm
from loopDefault import LoopDefault

""" Main Loop """
streamTimeStart = 0
keyboardMap = []
_suspitiousFunctionKeysLag = 10

wire = Wire(inputDevice = 8, outputDevice = 8)
metronome = Metronome(120, left = 16, top = 1)
tracks = [
    Track(0, LoopDefault, 1, 1),
    Track(1, LoopDefault, 2, 1),
    Track(2, LoopDefault, 3, 1),
    Track(3, LoopDefault, 4, 1),
    Track(4, LoopDefault, 6, 1),
    Track(5, LoopDefault, 7, 1),
    Track(6, LoopDefault, 8, 1),
    Track(7, LoopDefault, 9, 1),
    Track(8, LoopDefault, 11, 1),
    Track(9, LoopDefault, 12, 1),
    Track(10, LoopDefault, 13, 1),
    Track(11, LoopDefault, 14, 1),]
tonearmA = Tonearm(size = 16, left = 5, top = 1)
tonearmB = Tonearm(size = 16, left = 10, top = 1)
clock = pygame.time.Clock()

def start():   
    global metronome
    bpmChanged(metronome.bpm)
    wire.start(callback = wireCallback) 
    draw.setNewFont('open-sans', 'open-sans 12')
    draw.setDefaultFont('open-sans')

def update():
    ticks = pygame.time.get_ticks()
    for track in tracks:
        track.update()
    metronome.update()
    tonearmA.update()
    tonearmB.update()
    draw.update()

    global _suspitiousFunctionKeysLag
    _suspitiousFunctionKeysLag -= 1

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
            track.write(indata, elapsed, metronome.bpm, frames = frames)
        if track.canRead():
            read = track.read(elapsed, metronome.bpm, frames = frames)
            if read.shape[0] != outdata.shape[0]:
                read = np.resize(read, [outdata.shape[0], outdata.shape[1]])
            outdata += read

    tonearmA.moveBy(frames, metronome.bpm)
    tonearmB.moveBy(frames, metronome.bpm)
    metronome.moveBy(frames)

def playTrack(n, e):
    if keyboard.is_pressed('space'):
        return
    if keyboard.is_pressed('s'):
        return
    if _suspitiousFunctionKeysLag < 0:
        tracks[n].togglePlay()

def bpmChanged(bpm):
    for track in tracks:
        track.resetMemory(bpm)
    tonearmA.resetSize(bpm)
    tonearmB.resetSize(bpm)

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

keyboard.on_press_key('b', bPressed)
keyboard.add_hotkey('s + b', setBpmPressed)

keyboard.on_press_key('1', digitPressed)
keyboard.on_press_key('2', digitPressed)
keyboard.on_press_key('3', digitPressed)
keyboard.on_press_key('4', digitPressed)
keyboard.on_press_key('5', digitPressed)
keyboard.on_press_key('6', digitPressed)
keyboard.on_press_key('7', digitPressed)
keyboard.on_press_key('8', digitPressed)
keyboard.on_press_key('9', digitPressed)
keyboard.on_press_key('0', digitPressed)
keyboard.on_press_key('up', arrowUpPressed)
keyboard.on_press_key('down', arrowDownPressed)

keyboard.add_hotkey('s + f1', tracks[0].toggleChangeSize)
keyboard.add_hotkey('s + f2', tracks[1].toggleChangeSize)
keyboard.add_hotkey('s + f3', tracks[2].toggleChangeSize)
keyboard.add_hotkey('s + f4', tracks[3].toggleChangeSize)
keyboard.add_hotkey('s + f5', tracks[4].toggleChangeSize)
keyboard.add_hotkey('s + f6', tracks[5].toggleChangeSize)
keyboard.add_hotkey('s + f7', tracks[6].toggleChangeSize)
keyboard.add_hotkey('s + f8', tracks[7].toggleChangeSize)
keyboard.add_hotkey('s + f9', tracks[8].toggleChangeSize)
keyboard.add_hotkey('s + f10', tracks[9].toggleChangeSize)
keyboard.add_hotkey('s + f11', tracks[10].toggleChangeSize)
keyboard.add_hotkey('s + f12', tracks[11].toggleChangeSize)

keyboard.add_hotkey('space + f1', tracks[0].toggleRecord)
keyboard.add_hotkey('space + f2', tracks[1].toggleRecord)
keyboard.add_hotkey('space + f3', tracks[2].toggleRecord)
keyboard.add_hotkey('space + f4', tracks[3].toggleRecord)
keyboard.add_hotkey('space + f5', tracks[4].toggleRecord)
keyboard.add_hotkey('space + f6', tracks[5].toggleRecord)
keyboard.add_hotkey('space + f7', tracks[6].toggleRecord)
keyboard.add_hotkey('space + f8', tracks[7].toggleRecord)
keyboard.add_hotkey('space + f9', tracks[8].toggleRecord)
keyboard.add_hotkey('space + f10', tracks[9].toggleRecord)
keyboard.add_hotkey('space + f11', tracks[10].toggleRecord)
keyboard.add_hotkey('space + f12', tracks[11].toggleRecord)

keyboard.on_press_key('f1', lambda e: playTrack(0, e))
keyboard.on_press_key('f2', lambda e: playTrack(1, e))
keyboard.on_press_key('f3', lambda e: playTrack(2, e))
keyboard.on_press_key('f4', lambda e: playTrack(3, e))
keyboard.on_press_key('f5', lambda e: playTrack(4, e))
keyboard.on_press_key('f6', lambda e: playTrack(5, e))
keyboard.on_press_key('f7', lambda e: playTrack(6, e))
keyboard.on_press_key('f8', lambda e: playTrack(7, e))
keyboard.on_press_key('f9', lambda e: playTrack(8, e))
keyboard.on_press_key('f10', lambda e: playTrack(9, e))
keyboard.on_press_key('f11', lambda e: playTrack(10, e))
keyboard.on_press_key('f12', lambda e: playTrack(11, e))

keyboard.on_press_key('backspace', backspacePressed)
keyboard.on_press_key('enter', enterPressed)
keyboard.on_press_key('space', spacePressed)
keyboard.on_press_key('esc', escPressed)

def main():
    pygame.init()
    #pygame.midi.init()
    draw.init(30, 20)
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
                for track in tracks:
                    track.onBeat()
                    if (beat % 4) == 0:
                        track.onBar()
                    if (beat % 16) == 0:
                        track.onGlobalLoop()

if __name__ == "__main__":
    main()