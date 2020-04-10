from multiprocessing import Process
import pygame
import os
import shutil
import pygame.midi
import numpy as np
import time
from area import Area
import looperAreas
import drawing as draw
import keyboard
import utils
from utils import interpolate
import hotkeys
import sounddevice as sd
import customevents as events
from wire import Wire
from metronome import Metronome
from track import Track
from tonearm import Tonearm
from loopDefault import LoopDefault
from console import Console
import globalSettings as settings
from listOfCommandsWide import ListOfCommandsWide
from listOfDevicesWide import ListOfDevicesWide
import processor
from soundbank import Soundbank
from samplesController import SamplesController
from samplesPanelWide import SamplesPanelWide
from midiController import MidiController 
from midiPiano import MidiPiano
from midiPads import MidiPads
import autoplayController as autoplay
import timeSynchronization as sync

""" Main Loop """
streamTimeStart = 0
keyboardMap = []
_suspitiousFunctionKeysLag = 10

def selectArea(areaname):
    if not areaname in areas:
        return
    currentArea = areaname

marginTop = 1

#TODO: возможность выбора устройств
wire = Wire(inputDevice = 8, outputDevice = 8)
if (sd.query_devices(wire.inputDevice)['name'] != 'Yamaha Steinberg USB ASIO'):
    raise Exception('NOPE! ' + sd.query_devices(wire.inputDevice)['name'])
wireTempData = {
    'audio': [],
    'cursor': 0,
    'midi-audio': []
}


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
console = Console(1, 27, 32)
soundbank = Soundbank()
sampler = SamplesController(soundbank)
samplesControlPanel = SamplesPanelWide(sampler)
midi = MidiController(sampler)


"""Wides"""
listOfCommandsWide = ListOfCommandsWide()
listOfDevicesWide = ListOfDevicesWide()
currentWide = None
currentSide = None

def start():   
    global metronome
    global soundbank

    bpmChanged(metronome.bpm)
    wire.start(callback = wireCallback) 
    draw.setNewFont('open-sans', 'open-sans 12')
    draw.setDefaultFont('open-sans')
    metronome.redraw()
    console.redraw()
    autoplay.setSubscribers([midi, sampler])

def update():
    ticks = pygame.time.get_ticks()
    for track in tracks:
        track.update()
    metronome.update()
    draw.update()

    global _suspitiousFunctionKeysLag
    _suspitiousFunctionKeysLag -= 1

def close():
    wire.stop()
    print('stop!')

def load(foldername):
    global console

    path = 'saves/' + foldername
    if not os.path.exists(path):
        return

    dict = utils.readSaveFile(path + '/app.save')
    wide = dict['current_wide']
    side = dict['current_side']

    soundbank.savesLoad(path, console)
    sampler.load(path, console)
    midi.load(path, console)

    if wide != None:
        data = wide.split(' ')
        if data[0] == 'midiPiano':
            n = data[1]
            console.emulate(interpolate('piano {n}'))

    if side != None:
        data = side.split(' ')
        if data[0] == 'midiPads':
            n = data[1]
            console.emulate(interpolate('pads {n}'))

def save(foldername):
    path = 'saves/' + foldername
    if not os.path.exists(path):
        os.mkdir(path)
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        try:
            if os.path.isfile(filepath) or os.path.islink(filepath):
                os.unlink(filepath)
            elif os.path.isdir(filepath):
                shutil.rmtree(filepath)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (filepath, e))

    global currentWide
    global currentSide
    cwide = currentWide.getSaveName() if currentWide != None else 'None'
    cside = currentSide.getSaveName() if currentSide != None else 'None'
    file = open(path + '/app.save', 'w+')
    file.write(interpolate('current_wide: {cwide}\n'))
    file.write(interpolate('current_side: {cside}\n'))
    file.close()

    soundbank.savesSave(path)
    sampler.save(path)
    midi.save(path)

def tick():    
    tonearmA.update()
    tonearmB.update()

def wireCallback(indata, outdata, frames, timeinfo, status):
    global wireTempData
    global streamTimeStart
    outdata[:] = indata

    mask, fromSamples, fromSamplesSum = sampler.read(frames)

    wireTempData['audio'] = indata
    wireTempData['midi-audio'] = [[]] * 16
    for i in range(0, len(mask)):
        if mask[i]:
            wireTempData['midi-audio'][i] = fromSamples[i]

    if streamTimeStart == 0:
        streamTimeStart = timeinfo.inputBufferAdcTime
    elapsed = timeinfo.inputBufferAdcTime - streamTimeStart

    for track in tracks:
        if track.canWrite():
            #data = processor.stereoToMono(indata, 1)
            track.write(wireTempData, elapsed, frames = frames, samplerate = settings.samplerate)
        if track.canRead():
            read = track.read(elapsed, frames = frames, samplerate = settings.samplerate)         
            data = processor.monoToStereo(read)
            outdata += reshapeSound(data, outdata.shape)
        """ 
        TODO: smooth
        track.fade(indata, elapsed, frames = frames)
        """
    read = metronome.readSound(frames)
    outdata += reshapeSound(read, outdata.shape)
    outdata += reshapeSound(processor.monoToStereo(fromSamplesSum), outdata.shape)

    tonearmA.moveBy(frames, metronome.bpm, samplerate = settings.samplerate)
    tonearmB.moveBy(frames, metronome.bpm, samplerate = settings.samplerate)
    metronome.moveBy(frames, samplerate = settings.samplerate)

    sync.move(frames)
    autoplay.move(frames)

def samplerateChanged(rate):
    for track in tracks:
        track.resetMemory(samplerate = settings.samplerate)
    tonearmA.resetSize(metronome.bpm, samplerate = settings.samplerate)
    tonearmB.resetSize(metronome.bpm, samplerate = settings.samplerate)

def reshapeSound(sound, shape):
    if sound.shape[0] != shape[0]:
        sound = np.resize(sound, [shape[0], shape[1]])
    return sound

def loadTapesFromFolder(path):
    for file in os.listdir('samples/' + path):
        if file.endswith(".wav") or file.endswith(".mp3"):
            names = ['track' + str(x + 1) for x in range(0, 12)]
            name = os.path.basename(file.split('.')[0])
            if name in names:
                n = int(name[5:]) - 1
                sound = processor.stereoToMono(soundbank.readDataFromFile(path +'/' + file)[0], 0)
                tracks[n].writeFiledata(sound)

def mainTabbed(event):
    looperAreas.changeArea('side')

def sideTabbed(event):
    looperAreas.changeArea('wide')

def wideTabbed(event):
    def lmbd():
        console.activate()
        if "deactivate" in dir(currentWide):
            currentWide.deactivate()
    looperAreas.changeArea('console', func = lmbd)

def consoleTabbed(event):
    looperAreas.changeArea('main', func = lambda: console.deactivate())

def mainReTabbed():
    looperAreas.changeArea('console')

def sideReTabbed():
    looperAreas.changeArea('main')

def wideReTabbed():
    looperAreas.changeArea('side', func = lambda: console.activate())

def consoleReTabbed():
    looperAreas.changeArea(
        'wide',
        func = lambda: console.deactivate())

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
        track.resetMemory(samplerate = settings.samplerate)
    tonearmA.resetSize(bpm, samplerate = settings.samplerate)
    tonearmB.resetSize(bpm, samplerate = settings.samplerate)
    autoplay.updateBpm(bpm, samplerate = settings.samplerate)
    sync.onBpmChanged(bpm, samplerate = settings.samplerate)

def processConsoleCommand(event):
    console.processCommand()

def bPressed(event):
    metronome.toggle()

def setBpmPressed():
    metronome.configureBpm()

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

def wideEsc(event):
    if "escPressed" in dir(currentWide):
        currentWide.escPressed() 

def wideEnter(event):
    if "enterPressed" in dir(currentWide):
        currentWide.enterPressed()    

def wideRight(event):
    if "rightPressed" in dir(currentWide):
        currentWide.rightPressed()

def wideLeft(event):
    if "leftPressed" in dir(currentWide):
        currentWide.leftPressed()

def wideUp(event):
    if "upPressed" in dir(currentWide):
        currentWide.upPressed()

def wideDown(event):
    if "downPressed" in dir(currentWide):
        currentWide.downPressed()

def wideDigit(event):
    # some strange arrows bug !!!
    if (event.name == 'up'
    or event.name == 'down'
    or event.name == 'left'
    or event.name == 'right'
    or event.name == 'page up'
    or event.name == 'page down'):
        return
    if "digitPressed" in dir(currentWide):
        currentWide.digitPressed(int(event.name))

def wideA(event):
    if "aPressed" in dir(currentWide):
        currentWide.aPressed()

def wideB(event):
    if "bPressed" in dir(currentWide):
        currentWide.bPressed()

def wideC(event):
    if "cPressed" in dir(currentWide):
        currentWide.cPressed()

def wideD(event):
    if "dPressed" in dir(currentWide):
        currentWide.dPressed()

def wideR(event):
    if "rPressed" in dir(currentWide):
        currentWide.rPressed()

def sideEnter(event):
    if "enterPressed" in dir(currentSide):
        currentSide.enterPressed()    

def sideRight(event):
    if "rightPressed" in dir(currentSide):
        currentSide.rightPressed()

def sideLeft(event):
    if "leftPressed" in dir(currentSide):
        currentSide.leftPressed()

def sideUp(event):
    if "upPressed" in dir(currentSide):
        currentSide.upPressed()

def sideDown(event):
    if "downPressed" in dir(currentSide):
        currentSide.downPressed()

def sideDigit(event):
    # some strange arrows bug !!!
    if (event.name == 'up'
    or event.name == 'down'
    or event.name == 'left'
    or event.name == 'right'
    or event.name == 'page up'
    or event.name == 'page down'):
        return
    if "digitPressed" in dir(currentSide):
        currentSide.digitPressed(int(event.name))

def sideA(event):
    if "aPressed" in dir(currentSide):
        currentSide.aPressed()

def sideB(event):
    if "bPressed" in dir(currentSide):
        currentSide.bPressed()

def sideC(event):
    if "cPressed" in dir(currentSide):
        currentSide.cPressed()

def sideD(event):
    if "dPressed" in dir(currentSide):
        currentSide.dPressed()

def sideR(event):
    if "rPressed" in dir(currentSide):
        currentSide.rPressed()

def consoleKeyboardInput(key):
    console.input(key)

def prevCommand(event):
    console.input('prev')

def nextCommand(event):
    console.input('next')

hotkeys.simple('b', bPressed, "main")
hotkeys.simple('tab', mainTabbed, "main")
hotkeys.simple('tab', sideTabbed, "side")
hotkeys.simple('tab', wideTabbed, "wide")
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

hotkeys.simple('enter', sideEnter, "side")
hotkeys.simple('right', sideRight, "side")
hotkeys.simple('left', sideLeft, "side")
hotkeys.simple('up', sideUp, "side")
hotkeys.simple('down', sideDown, "side")
hotkeys.simple('1', sideDigit, "side")
hotkeys.simple('2', sideDigit, "side")
hotkeys.simple('3', sideDigit, "side")
hotkeys.simple('4', sideDigit, "side")
hotkeys.simple('5', sideDigit, "side")
hotkeys.simple('6', sideDigit, "side")
hotkeys.simple('7', sideDigit, "side")
hotkeys.simple('8', sideDigit, "side")
hotkeys.simple('9', sideDigit, "side")
hotkeys.simple('0', sideDigit, "side")
hotkeys.simple('a', sideA, "side")
hotkeys.simple('b', sideB, "side")
hotkeys.simple('c', sideC, "side")
hotkeys.simple('d', sideD, "side")
hotkeys.simple('r', sideR, "side")

hotkeys.simple('esc', wideEsc, "wide")
hotkeys.simple('enter', wideEnter, "wide")
hotkeys.simple('right', wideRight, "wide")
hotkeys.simple('up', wideUp, "wide")
hotkeys.simple('down', wideDown, "wide")
hotkeys.simple('left', wideLeft, "wide")
hotkeys.simple('1', wideDigit, "wide")
hotkeys.simple('2', wideDigit, "wide")
hotkeys.simple('3', wideDigit, "wide")
hotkeys.simple('4', wideDigit, "wide")
hotkeys.simple('5', wideDigit, "wide")
hotkeys.simple('6', wideDigit, "wide")
hotkeys.simple('7', wideDigit, "wide")
hotkeys.simple('8', wideDigit, "wide")
hotkeys.simple('9', wideDigit, "wide")
hotkeys.simple('0', wideDigit, "wide")
hotkeys.simple('a', wideA, "wide")
hotkeys.simple('b', wideB, "wide")
hotkeys.simple('c', wideC, "wide")
hotkeys.simple('d', wideD, "wide")
hotkeys.simple('r', wideR, "wide")

hotkeys.processText(consoleKeyboardInput, "console")
hotkeys.simple('enter', processConsoleCommand, "console")
hotkeys.simple('up', prevCommand, "console")
hotkeys.simple('down', nextCommand, "console")

def main():
    global currentWide
    global currentSide
    global midi

    pygame.init()
    pygame.midi.init()
    midi.initDevices()
    draw.init(34, 30)
    logo = pygame.image.load("Г. Мясоедов Осеннее утро. 1893.jpg")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("Looper")
     
    screen = pygame.display.set_mode((draw.cw * draw.width, draw.height * draw.ch))
    screen.set_alpha(None)
    draw.setCanvas(screen)
     
    running = True

    start()
     
    # main loop
    while running:  
        clock.tick(60)
        midi.update()
        update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
                running = False
            elif events.check(event, 'EMULATE_CONSOLE'):
                console.emulate(event.dict['command'])
            elif events.check(event, 'BPM_CHANGED'):
                bpmChanged(event.dict['bpm'])
            elif events.check(event, 'BPM_TICK'):
                beat = event.dict['beat']
                tick()
                for track in tracks:
                    track.onBeat()
                    if (beat % 4) == 0:
                        track.onBar()
                    if (beat % 16) == 0:
                        track.onGlobalLoop()
                        sampler.cleanUp()
                autoplay.onBeat()
            elif events.check(event, 'BPM_HALF_TICK'):
                beat = event.dict['beat']
                for track in tracks:
                    track.onHalfBeat()
            elif events.check(event, 'DEMAND_CHANGE_BPM'):
                metronome.setBpm(event.dict['value'])
            elif events.check(event, 'DEMAND_CHANGE_TRACK_SIZE'):
                tracks[event.dict['n']].setSize(event.dict['length'])
            elif events.check(event, 'DEMAND_CHANGE_SAMPLERATE'):
                settings.samplerate = event.dict['value']
                samplerateChanged(event.dict['value'])
            elif events.check(event, 'SHOW_LIST_OF_COMMANDS'):
                currentWide = listOfCommandsWide                
                currentWide.redrawTitle()
                listOfCommandsWide.setCommands(event.dict['commands'])
                listOfCommandsWide.redraw()
            elif events.check(event, 'SHOW_LIST_OF_DEVICES'):
                currentWide = listOfDevicesWide
                currentWide.redrawTitle()
                listOfDevicesWide.redraw()
            elif events.check(event, 'LOAD_FOLDER'):
                if not soundbank.folderExists(event.dict['path']):
                    console.print('no such folder')
                soundbank.loadFolder(event.dict['path'])
            elif events.check(event, 'LOAD_BANK'):
                if not soundbank.folderExists(event.dict['path']):
                    console.print('no such folder')
                soundbank.loadBankFromFolder(event.dict['path'], event.dict['bank'])
            elif events.check(event, 'LOAD_TAPES'):
                if not soundbank.folderExists(event.dict['path']):
                    console.print('no such folder')
                loadTapesFromFolder(event.dict['path'])
            elif events.check(event, 'UPDATE_SAMPLE'):
                sampler.updateSample(event.dict['name'])
            elif events.check(event, 'WIRE_MIDI'):
                midi.wireChannel(event.dict['instrument'], event.dict['device'])
            elif events.check(event, 'CREATE_INSTRUMENT'):
                type = event.dict['type']
                n = event.dict['n']  
                widecreated = False
                sidecreated = False

                if not midi.isChannelUsed(n):
                    if type == 'piano':                  
                        piano = MidiPiano(n, sampler)
                        currentWide = piano
                        widecreated = True
                    elif type == 'pads':
                        pads = MidiPads(n, sampler)
                        currentSide = pads
                        sidecreated = True
                    else:
                        console.print('no such type of instrument')
                    
                    if widecreated:             
                        midi.appendChannel(n, currentWide)
                        currentWide.redrawTitle()
                        currentWide.initDraw()
                        currentWide.redraw()
                    if sidecreated:             
                        midi.appendChannel(n, currentSide)
                        currentSide.redrawTitle()
                        currentSide.initDraw()
                        currentSide.redraw()
                else:
                    if midi.instruments[n].getType() == type:
                        if type == 'piano':
                            currentWide = midi.instruments[n]
                            currentWide.redrawTitle()
                            currentWide.initDraw()
                            currentWide.redraw()
                        if type == 'pads':
                            currentSide = midi.instruments[n]
                            currentSide.redrawTitle()
                            currentSide.initDraw()
                            currentSide.redraw()
                        console.print('channel already exists. now displayed')
                    else:
                        console.print('channel is used')
            elif events.check(event, 'SAVE'):
                save(event.dict['name'])
            elif events.check(event, 'LOAD'):
                load(event.dict['name'])
            elif events.check(event, 'LOAD_INSTRUMENT'):
                if midi.channels[event.dict['n']] == None and (not 'repeats' in event.dict or event.dict['repeats'] < 10000):
                    repeats = events.dict['repeats'] if 'repeats' in event.dict else 10000
                    events.emit('LOAD_INSTRUMENT', {'n': events.dict['n'], 'filename': events.dict['filename'], 'repeats': repeats})
                elif 'repeats' in event.dict and event.dict['repeats'] >= 10000:
                    print('MANY REPEATS for LOAD_INSTRUMENT')
                else:
                    midi.channels[event.dict['n']].load(event.dict['filename'], console)
            elif events.check(event, 'SHOW_SAMPLER'):
                currentWide = samplesControlPanel
                currentWide.redrawTitle()
                currentWide.redraw()
            elif events.check(event, 'REDRAW_PIANO'):
                if currentWide.getType() == 'piano':
                    step = event.dict['step']
                    if step == 1:
                        currentWide.redrawStep1()
                    if step == 2:
                        currentWide.redrawStep2()
                    if step == 3:
                        currentWide.redrawStep3()
                    if step == 4:
                        currentWide.redrawStep4()
                    if step == 5:
                        currentWide.redrawStep5()
            elif events.check(event, 'DISABLE_INSTRUMENT'):
                midi.disable(int(event.dict['n']))
            elif events.check(event, 'ENABLE_INSTRUMENT'):
                midi.enable(int(event.dict['n']))
            elif events.check(event, 'WIRE_TRACK'):
                tracks[event.dict['track']].setMidiChannel(event.dict['instrument'])


if __name__ == "__main__":
    main()