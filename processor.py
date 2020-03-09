import numpy as np

def stereoToMono(data):
    return np.array(data[:, 1])

def monoToStereo(data):
    return np.column_stack((data, data))