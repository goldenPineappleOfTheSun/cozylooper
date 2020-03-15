import numpy as np

def stereoToMono(data, n):
    return np.array(data[:, n])

def monoToStereo(data):
    return np.column_stack((data, data))