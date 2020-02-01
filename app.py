import pygame
import drawing as draw
import keyboard
from metronome import Metronome
from track import Track

""" Main Loop """

metronome = Metronome(120, left = 16, top = 1)
tracks = [Track(0, 1, 1),
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
clock = pygame.time.Clock()

def start():    
    draw.setNewFont('open-sans', 'open-sans 12')
    draw.setDefaultFont('open-sans')

def update():
    ticks = pygame.time.get_ticks()
    metronome.update(None, ticks)
    for track in tracks:
        track.update()
    draw.update()

def bPressed(event):
    metronome.toggle()

keyboard.on_press_key('b', bPressed)

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