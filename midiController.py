import numpy as np
import pygame
import utils
import os
import customevents as events
from utils import interpolate
import pygame.midi

class MidiController:

    def __init__(self, sampler):
        """ instruments are instruments created inside the looper """
        self.instruments = np.full((16), None)
        self.enabled = np.full((16), True)
        """ inputs are devices from which midi messages are recieved. index is equal to midi channel """
        self.inputs = []
        """ channels are midi channels """
        #self.channels = np.full((16), None)
        """ wires are matchings between instruments and channels. key=channel value=instrument """
        self.wires = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        self.sampler = sampler

    def initDevices(self, array = None):
        if array == None:
            for i in range(0, pygame.midi.get_count()):
                if pygame.midi.get_device_info(i)[2] == 1:
                    self.inputs.append(pygame.midi.Input(i))

    def appendChannel(self, n, midiInstrument):
        if n < 0 or n > 15:
            return
        if self.instruments[n] != None:
            raise 'channel is used!'
        self.instruments[n] = midiInstrument

    def autoplayTick(self, n, fraction):
        pass

    def disable(self, n):
        self.enabled[n] = False

    def enable(self, n):
        self.enabled[n] = True

    def findDeviceByName(self, name):
        devices = []
        for i in range( 0, pygame.midi.get_count() ):
            if name[:-2] == str(pygame.midi.get_device_info(i))[:-2]:
                return i
        return None

    def isChannelUsed(self, n):
        return self.instruments[n] != None

    def load(self, path, console):
        for i in range(0, 16):
            filename = interpolate('{path}/channel_{i}.save')
            if not os.path.isfile(filename):
                continue

            dict = utils.readSaveFile(filename)
            t = dict['type']
            channel = dict['channel']
            device = self.findDeviceByName(dict['device'])
            console.emulate(interpolate('create-instrument {t} {channel}'))
            if device != None:
                console.emulate(interpolate('wire-midi {channel} {device}'))
            events.emit('LOAD_INSTRUMENT', {'n': i, 'filename': filename})
            """if self.instruments[i] != None:
                self.instruments[i].load(filename, console)"""

    def save(self, path):    
        for i in range(0, 16):
            channel = self.instruments[i]
            if channel == None:
                continue

            device = 'None'
            #if self.wires[i] != []:
            #    device = str(pygame.midi.get_device_info(self.wires[i]))

            file = open(interpolate('{path}/channel_{i}.save'), 'w+')
            file.write(interpolate('channel: {i}\n'))
            file.write(interpolate('device: {device}\n'));
            file.close()

            self.instruments[i].save(interpolate('{path}/channel_{i}.save'))


    def wireChannel(self, instrument, channel):
        self.wires[channel].append(instrument)

    def update(self):
        for inp in self.inputs:
            for msg in inp.read(100):
                command = (msg[0][0] & 240) >> 4
                if command == 8:
                    ch = msg[0][0] & 15
                    note = msg[0][1]
                    strength = msg[0][2]
                    for w in self.wires[ch]:
                        instrument = self.instruments[w]
                        instrument.release(note, 0)
                if command == 9:
                    ch = msg[0][0] & 15
                    note = msg[0][1]
                    strength = msg[0][2]
                    for w in self.wires[ch]:
                        if self.enabled[w]:
                            instrument = self.instruments[w]
                            instrument.press(note, strength)


