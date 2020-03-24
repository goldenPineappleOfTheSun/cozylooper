import numpy as np
import soundfile as sf
import processor
import customevents as events
import os

class Soundbank:
    def __init__(self):
        self.names = ["a01","a02","a03","a04","a05","a06","a07","a08","a09","a10","a11","a12","a13","a14","a15","a16","b01","b02","b03","b04","b05","b06","b07","b08","b09","b10","b11","b12","b13","b14","b15","b16","c01","c02","c03","c04","c05","c06","c07","c08","c09","c10","c11","c12","c13","c14","c15","c16","d01","d02","d03","d04","d05","d06","d07","d08","d09","d10","d11","d12","d13","d14","d15","d16"]
        self.samples = dict.fromkeys(self.names, [])
        self.samplerates = dict.fromkeys(self.names, [])
        self.sizes = dict.fromkeys(self.names, [])

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
        self._load(sample, 'samples' + path)

    def _load(self, sample, path):
        sound, soundSamplerate = sf.read(path, dtype='float32')  
        sound = processor.stereoToMono(sound, 0)
        self.samples[sample] = sound
        self.samplerates[sample] = soundSamplerate
        self.sizes[sample] = sound.shape[0]
        print(sample + ' ' + path + ' ' + str(self.sizes[sample]))
        events.emit('UPDATE_SAMPLE', {'name': sample})

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

    def read(self, name):
        if not name in self.names:
            return []
        return self.samples[name]

    def savesSave(self, foldername):
        path = foldername + '/samples/'
        if not os.path.exists(path):
            os.mkdir(path)
        for filename in os.listdir(path):
            filepath = os.path.join(path, filename)
            try:
                if os.path.isfile(filepath) or os.path.islink(filepath):
                    os.unlink(filepath)
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (filepath, e))

        for name in self.names:
            if len(self.samples[name]) > 0:
                sf.write(path + name + '.wav', self.samples[name], self.samplerates[name])

    def savesLoad(self, foldername, console):
        for file in os.listdir(foldername + '/samples'):
            if file.endswith(".wav") or file.endswith(".mp3"):
                sample = os.path.basename(file.split('.')[0])
                if sample in self.samples:
                    self._load(sample, foldername + '/samples/' + file)