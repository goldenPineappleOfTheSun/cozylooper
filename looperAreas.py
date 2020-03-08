from area import Area
import time

areas = {
    'main': Area(0, 0, 10, 10, needHighlight = False),
    'wide': Area(1, 19, 32, 6),
    "console": Area(1, 26, 32, 2)
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