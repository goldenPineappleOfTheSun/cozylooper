import pygame
import drawing as draw

""" Main Loop """

def start():
    style = '#ff8877 1p #00eeff'
    draw.rectangle(1, 1, 5, 5, style);
    draw.rectangle('2cw', '2ch', 3, 3, style);
    draw.rectangle('2cw + 8', '2ch + 8', '3cw - 16', '3ch - 16', style);

def update():
    a = 0

def main():
    pygame.init()
    draw.init(20, 16)
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