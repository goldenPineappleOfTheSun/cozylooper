
import pygame
import drawing

""" Main Loop """

def update():
    a = 0

def main():
    pygame.init()
    drawing.init()
    logo = pygame.image.load("Г. Мясоедов Осеннее утро. 1893.jpg")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("Looper")
     
    screen = pygame.display.set_mode((240,180))
     
    running = True
     
    # main loop
    while running:  
        update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state = State.exit
                bpmTimer.cancel()
                running = False

if __name__=="__main__":
    main()