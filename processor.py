import numpy as np

octaves = {'S': -3, 'C': -2, 'B': -1, '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5}
notes = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}

def fastInterpolate(data, factor):
    length = len(data)
    x = np.arange(0, length, factor)
    xp = np.arange(0, length)
    return np.interp(x, xp, data)

def getPitchCoefficient(note):
    global octaves
    global notes
    octave = octaves[note[-1:]]
    tone = notes[note[0:1]]
    for i in note[1:-1]:
        if i == '#':
            tone += 1
        elif i == 'b':
            tone -= 1
    return 1 * pow(2, (tone + 12 * octave)/12)

def monoToStereo(data):
    return np.column_stack((data, data))

def stereoToMono(data, n):
    if data.ndim == 2:
        return np.array(data[:, n])
    else:
        return np.array(data)