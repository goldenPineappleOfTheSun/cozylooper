import math

""" count of 64s """
n = 0
""" samples since last 64 """
fraction = 0
ticks = 0
""" samples in beat """
size64 = 1000
size1 = 1000
samplerate = 44100
subscribers = []
nextBeat = False

def setSubscribers(list):
    global subscribers
    subscribers = list

def onBeat():
    pass

def updateBpm(bpm, samplerate = 44100):
    global size64
    global size1
    size1 = (samplerate / (bpm / 60)) * 4
    size64 = size1 / 64
    samplerate = samplerate

def move(frames):
    global beattime
    global n
    global samplerate
    global fraction
    global ticks
    global nextBeat
    global size64
    global size1
    fraction += frames
    ticks = (ticks + frames) % size1
    n = math.floor(ticks / size64)
    if fraction > size64:
        fraction = fraction % size64 
        for sub in subscribers:
            getattr(sub, 'autoplayTick')(n, fraction)

"""
def isReady():
    global ready
    return ready

def notifyAll(midiController, samplesController):
    global fraction
    global beattime
    global ready
    global fraction
    global n
    fraction = fraction % beattime
    midiController.autoplayTick(n, fraction / beattime)
    samplesController.autoplayTick(n, fraction / beattime)"""