import pygame
import drawing as draw
from metronome import Metronome

""" Main Loop """

metronome = Metronome(120, left = 17, top = 1)

def start():    
    draw.setNewFont('open-sans', 'open-sans 12')
    draw.setDefaultFont('open-sans')
    metronome.redraw(None)

def update():
    a = 0

def main():
    pygame.init()
    draw.init(26, 13)
    logo = pygame.image.load("Г. Мясоедов Осеннее утро. 1893.jpg")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("Looper")
     
    screen = pygame.display.set_mode((draw.cw * draw.width, draw.height * draw.ch))
    draw.setCanvas(screen)
     
    running = True

    start()
     
    # main loop
    while running:  
        update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

if __name__=="__main__":
    main()