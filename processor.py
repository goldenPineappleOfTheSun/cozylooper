import numpy as np

def stereoToMono(data, n):
    if data.ndim == 2:
        return np.array(data[:, n])
    else:
        return np.array(data)

def monoToStereo(data):
    return np.column_stack((data, data))