import pygame
import drawing as draw

""" Main Loop """

def start():
    style = '#ff8877 1p #00eeff'
    draw.rectangle(1, 1, 5, 5, style);
    draw.rectangle('2cw', '2ch', 3, 3, style);
    draw.rectangle('2cw + 8', '2ch + 8', '3cw - 16', '3ch - 16', style);

    draw.line(7, 1, 7 + 5, 1 + 5, '#ffaaaa')
    draw.line(7, 1 + 5, 7 + 5, 1, '#aaffaa')
    draw.line(7 + 2, 1 + 2.5, 7 + 3, 1 + 2.5, '5p #fafaaf')
    draw.line(7 + 2.5, 1 + 2, 7 + 2.5, 1 + 3, '5p #afffaf')

def update():
    a = 0

def main():
    pygame.init()
    draw.init(12, 12)
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