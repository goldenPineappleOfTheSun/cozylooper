from area import Area
import time

areas = {
    'main': Area(0, 0, 10, 10, needHighlight = False),
    'side': Area(16, 3, 17, 15),
    'wide': Area(1, 19, 32, 7),
    "console": Area(1, 27, 32, 2)
}

currentArea = "main"
lastChangeTime = time.time()

def changeArea(new, func = None):
    global lastChangeTime
    global areas
    global currentArea

    now = time.time()
    if now - lastChangeTime < 0.1:
        return
    lastChangeTime = now

    if func != None:
        func()

    if new in areas:
        areas[currentArea].clearHighlight()
        currentArea = new
        print('select ' + currentArea)
        areas[currentArea].highlight()