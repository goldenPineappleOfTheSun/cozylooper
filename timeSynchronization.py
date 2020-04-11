import math

syncBpm = 120
syncSamplerate = 44100
""" numerator of time signature """
signature = 4
""" beat size in samples  """
beatSize = 1000 
""" loop size in samples """
loopSize = 1000
""" number of loops (full paths of tonearm) from begining of program """
loop = 0
""" number of bars from begining of current loop """
bar = 0
""" number of beats from begining of current loop """
beat = 0
""" time from begining of the program """
timeWhole = 0
""" time from begining of the loop """
timeLoop = 0
""" time from begining of the bar """
timeBar = 0
""" time from begining of the beat """
timeBeat = 0

def onBpmChanged(bpm, samplerate):
    global syncBpm 
    global syncSamplerate 
    global loopSize
    global beatSize
    syncBpm = bpm
    syncSamplerate = samplerate
    beatsCount = 16
    loopSize = int(syncSamplerate * (60 / syncBpm) * beatsCount)
    beatSize = int(syncSamplerate * (60 / syncBpm))

def onLoopRestarted():
    global loop
    global bar
    global beat
    global timeLoop
    global timeBar
    global timeBeat
    loop = 0
    bar = 0
    beat = 0
    timeLoop = 0
    timeBar = 0
    timeBeat = 0

def move(frames):
    global timeWhole
    global timeLoop
    global timeBar
    global timeBeat
    global bar
    global beat
    global loop
    global loopSize
    global beatSize
    timeWhole += frames
    timeLoop += frames
    if timeLoop > loopSize:
        timeLoop = timeLoop % loopSize
        loop ++ 1
    timeBar = timeLoop % (beatSize * signature)
    bar = math.floor(timeLoop / (beatSize * signature))
    timeBeat = timeLoop % beatSize
    beat = math.floor(timeLoop / beatSize)

def fractionToString(num):
    fracs = {'1': '1', '0.5': '1/2', '0.25': '1/4', '0.125': '1/8', '0.0625': '1/16', '0.03125': '1/32'}
    return fracs[str(num)]

""" returns number of samples that lay between precise point and current time """
def getDelta(precision = None):
    return _getDelta(precision, 'samples')

""" returns difference (0 to 0.5) between precise point and current time """
def getAccuracy(precision = None):
    return _getDelta(precision, 'fraction')

def _getDelta(precision = None, units = 'samples'):
    if precision == None:
        return _getUniversalDelta(units)

    beatsCount = 16
    precs = {'loop': 0.25 * beatsCount, 'bar': 0.25 * signature, 'beat': 0.25, '1/2': 0.25/2, '1/4': 0.25/4, '1/8': 0.25/8, '1/16': 0.25/16, '1/32': 0.25/32}
    prec = precs[precision]
    fullSize = prec * beatSize
    pos = timeLoop % fullSize
    d = pos if pos < fullSize * 0.5 else pos - fullSize
    if units == 'samples':
        return d
    elif units == 'fraction': 
        return d / fullSize

def _getUniversalDelta(units = 'samples'):
    precs = {'1': '1', '0.5': '1/2', '0.25': '1/4', '0.125': '1/8', '0.0625': '1/16', '0.03125': '1/32'}
    prec = 0.03125
    fullSize = prec * beatSize
    pos = beatTime % fullSize
    lastdiff = pos if pos < fullSize * 0.5 else pos - fullSize
    d = abs(lastdiff / fullSize)

    while prec < 0.5:
        prec *= 2
        fullSize = prec * beatSize
        pos = beatTime % fullSize
        diff = pos if pos < fullSize * 0.5 else pos - fullSize
        d = abs(diff / fullSize)
        if d > 0.25:
            return lastdiff
        else:
            lastdiff = diff

    return lastdiff
