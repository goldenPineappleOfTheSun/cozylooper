import pygame
import drawing as draw

""" Main Loop """

#metronome = Metronome(120, left = 17, top = 1)

def start():
    draw.text('Hello', 1, 1, '#222222')
    draw.text('Hello', 1, 2, '#222222 default')
    draw.setNewFont('open-sans-bold', 'open-sans-bold 12')
    draw.setNewFont('open-sans-bold-big', 'open-sans-bold 24')
    draw.text('Doggy', 1, 3, '#ff66ff open-sans-bold')
    draw.text('DOGGY', 1, 5, '#66ff66 open-sans-bold-big')
    draw.text('left', 3, 6, '#222222 default midleft')
    draw.text('center', 3, 7, '#222222 default center')
    draw.text('right', 3, 8, '#222222 default midright')
    #metronome.redraw(None)

def update():
    a = 0

def main():
    pygame.init()
    draw.init(20, 13)
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