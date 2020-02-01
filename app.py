import pygame
import drawing as draw
import keyboard
from metronome import Metronome
from track import Track
from tonearm import Tonearm

""" Main Loop """

metronome = Metronome(120, left = 16, top = 1)
tracks = [
    Track(0, 1, 1),
    Track(1, 2, 1),
    Track(2, 3, 1),
    Track(3, 4, 1),
    Track(4, 6, 1),
    Track(5, 7, 1),
    Track(6, 8, 1),
    Track(7, 9, 1),
    Track(8, 11, 1),
    Track(9, 12, 1),
    Track(10, 13, 1),
    Track(11, 14, 1),]
tonearmA = Tonearm(size = 16, left = 5, top = 1)
tonearmB = Tonearm(size = 16, left = 10, top = 1)
clock = pygame.time.Clock()

def start():    
    draw.setNewFont('open-sans', 'open-sans 12')
    draw.setDefaultFont('open-sans')

def update():
    ticks = pygame.time.get_ticks()
    metronome.update(ticks)
    tonearmA.setPos(metronome.bpm, ticks / 1000)
    tonearmA.update()
    tonearmB.setPos(metronome.bpm, ticks / 1000)
    tonearmB.update()
    for track in tracks:
        track.update()
    draw.update()

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

keyboard.add_hotkey('s + f1', lambda: tracks[0].toggleChangeSize())
keyboard.add_hotkey('s + f2', lambda: tracks[1].toggleChangeSize())
keyboard.add_hotkey('s + f3', lambda: tracks[2].toggleChangeSize())
keyboard.add_hotkey('s + f4', lambda: tracks[3].toggleChangeSize())
keyboard.add_hotkey('s + f5', lambda: tracks[4].toggleChangeSize())
keyboard.add_hotkey('s + f6', lambda: tracks[5].toggleChangeSize())
keyboard.add_hotkey('s + f7', lambda: tracks[6].toggleChangeSize())
keyboard.add_hotkey('s + f8', lambda: tracks[7].toggleChangeSize())
keyboard.add_hotkey('s + f9', lambda: tracks[8].toggleChangeSize())
keyboard.add_hotkey('s + f10', lambda: tracks[9].toggleChangeSize())
keyboard.add_hotkey('s + f11', lambda: tracks[10].toggleChangeSize())
keyboard.add_hotkey('s + f12', lambda: tracks[11].toggleChangeSize())

keyboard.on_press_key('backspace', backspacePressed)
keyboard.on_press_key('enter', enterPressed)
keyboard.on_press_key('space', spacePressed)
keyboard.on_press_key('esc', escPressed)

def main():
    pygame.init()
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
                running = False

if __name__=="__main__":
    main()