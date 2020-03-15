import numpy as np
import soundfile as sf
import processor
import os

class Soundbank:
    def __init__(self):
        self.samples = {
            "a01": [],
            "a02": [],
            "a03": [],
            "a04": [],
            "a05": [],
            "a06": [],
            "a07": [],
            "a08": [],
            "a09": [],
            "a10": [],
            "a11": [],
            "a12": [],
            "a13": [],
            "a14": [],
            "a15": [],
            "a16": [],
            "b01": [],
            "b02": [],
            "b03": [],
            "b04": [],
            "b05": [],
            "b06": [],
            "b07": [],
            "b08": [],
            "b09": [],
            "b10": [],
            "b11": [],
            "b12": [],
            "b13": [],
            "b14": [],
            "b15": [],
            "b16": [],
            "c01": [],
            "c02": [],
            "c03": [],
            "c04": [],
            "c05": [],
            "c06": [],
            "c07": [],
            "c08": [],
            "c09": [],
            "c10": [],
            "c11": [],
            "c12": [],
            "c13": [],
            "c14": [],
            "c15": [],
            "c16": [],
            "d01": [],
            "d02": [],
            "d03": [],
            "d04": [],
            "d05": [],
            "d06": [],
            "d07": [],
            "d08": [],
            "d09": [],
            "d10": [],
            "d11": [],
            "d12": [],
            "d13": [],
            "d14": [],
            "d15": [],
            "d16": []
        }   
        self.samplerates = {
            "a01": 44100,
            "a02": 44100,
            "a03": 44100,
            "a04": 44100,
            "a05": 44100,
            "a06": 44100,
            "a07": 44100,
            "a08": 44100,
            "a09": 44100,
            "a10": 44100,
            "a11": 44100,
            "a12": 44100,
            "a13": 44100,
            "a14": 44100,
            "a15": 44100,
            "a16": 44100,
            "b01": 44100,
            "b02": 44100,
            "b03": 44100,
            "b04": 44100,
            "b05": 44100,
            "b06": 44100,
            "b07": 44100,
            "b08": 44100,
            "b09": 44100,
            "b10": 44100,
            "b11": 44100,
            "b12": 44100,
            "b13": 44100,
            "b14": 44100,
            "b15": 44100,
            "b16": 44100,
            "c01": 44100,
            "c02": 44100,
            "c03": 44100,
            "c04": 44100,
            "c05": 44100,
            "c06": 44100,
            "c07": 44100,
            "c08": 44100,
            "c09": 44100,
            "c10": 44100,
            "c11": 44100,
            "c12": 44100,
            "c13": 44100,
            "c14": 44100,
            "c15": 44100,
            "c16": 44100,
            "d01": 44100,
            "d02": 44100,
            "d03": 44100,
            "d04": 44100,
            "d05": 44100,
            "d06": 44100,
            "d07": 44100,
            "d08": 44100,
            "d09": 44100,
            "d10": 44100,
            "d11": 44100,
            "d12": 44100,
            "d13": 44100,
            "d14": 44100,
            "d15": 44100,
            "d16": 44100
        }   
        self.sizes = {
            "a01": 44100,
            "a02": 44100,
            "a03": 44100,
            "a04": 44100,
            "a05": 44100,
            "a06": 44100,
            "a07": 44100,
            "a08": 44100,
            "a09": 44100,
            "a10": 44100,
            "a11": 44100,
            "a12": 44100,
            "a13": 44100,
            "a14": 44100,
            "a15": 44100,
            "a16": 44100,
            "b01": 44100,
            "b02": 44100,
            "b03": 44100,
            "b04": 44100,
            "b05": 44100,
            "b06": 44100,
            "b07": 44100,
            "b08": 44100,
            "b09": 44100,
            "b10": 44100,
            "b11": 44100,
            "b12": 44100,
            "b13": 44100,
            "b14": 44100,
            "b15": 44100,
            "b16": 44100,
            "c01": 44100,
            "c02": 44100,
            "c03": 44100,
            "c04": 44100,
            "c05": 44100,
            "c06": 44100,
            "c07": 44100,
            "c08": 44100,
            "c09": 44100,
            "c10": 44100,
            "c11": 44100,
            "c12": 44100,
            "c13": 44100,
            "c14": 44100,
            "c15": 44100,
            "c16": 44100,
            "d01": 44100,
            "d02": 44100,
            "d03": 44100,
            "d04": 44100,
            "d05": 44100,
            "d06": 44100,
            "d07": 44100,
            "d08": 44100,
            "d09": 44100,
            "d10": 44100,
            "d11": 44100,
            "d12": 44100,
            "d13": 44100,
            "d14": 44100,
            "d15": 44100,
            "d16": 44100
        }      

    def folderExists(self, path):
        return os.path.exists('samples/' + path)

    def fileExists(self, path):
        if os.path.isFile('samples/' + path):
            if file.endswith(".wav") or file.endswith(".mp3"):
                sample = os.path.basename(file.split('.')[0])
                if sample in self.samples and sample[0] == bank:
                    return True
        return False

    def load(self, sample, path):
        sound, soundSamplerate = sf.read('samples' + path, dtype='float32')  
        sound = processor.stereoToMono(sound, 0)
        self.samples[sample] = sound
        self.samplerates[sample] = soundSamplerate
        self.sizes[sample] = np.shape(sound)
        print(sample + ' ' + path + ' ' + str(self.sizes[sample][0]))

    def loadFolder(self, path):
        for file in os.listdir('samples/' + path):
            if file.endswith(".wav") or file.endswith(".mp3"):
                sample = os.path.basename(file.split('.')[0])
                if sample in self.samples:
                    self.load(sample, '/' + path + '/' + file)

    def loadBankFromFolder(self, path, bank):
        for file in os.listdir('samples/' + path):
            if file.endswith(".wav") or file.endswith(".mp3"):
                sample = os.path.basename(file.split('.')[0])
                if sample in self.samples and sample[0] == bank:
                    self.load(sample, '/' + path + '/' + file)