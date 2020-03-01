from area import Area
import time

areas = {
    'main': Area(0, 0, 10, 10, needHighlight = False),
    "console": Area(1, 26, 32, 1)
}

currentArea = "main"
lastChangeTime = time.time()

def changeArea(new):
    global lastChangeTime
    global areas
    global currentArea

    now = time.time()
    if now - lastChangeTime < 0.1:
        return
    lastChangeTime = now

    if new in areas:
        areas[currentArea].clearHighlight()
        currentArea = new
        print('select' + currentArea)
        areas[currentArea].highlight()