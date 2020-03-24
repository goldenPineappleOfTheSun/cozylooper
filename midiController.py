import numpy as np
import pygame
import utils
import os
import customevents as events
from utils import interpolate
import pygame.midi

class MidiController:

    def __init__(self, sampler):
        self.channels = np.full((16), None)
        self.inputs = np.full((16), None)
        self.wires = np.full((16), None)
        self.sampler = sampler

    def appendChannel(self, n, midiInstrument):
        if n < 0 or n > 15:
            return
        if self.channels[n] != None:
            raise 'channel is used!'
        self.channels[n] = midiInstrument

    def findDeviceByName(self, name):
        devices = []
        for i in range( 0, pygame.midi.get_count() ):
            if name == str(pygame.midi.get_device_info(i)):
                return i
        return None

    def isChannelUsed(self, n):
        return self.channels[n] != None

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
            """if self.channels[i] != None:
                self.channels[i].load(filename, console)"""


    def save(self, path):    
        for i in range(0, 16):
            channel = self.channels[i]
            if channel == None:
                continue
            device = str(pygame.midi.get_device_info(self.wires[i]))

            file = open(interpolate('{path}/channel_{i}.save'), 'w+')
            file.write(interpolate('channel: {i}\n'))
            file.write(interpolate('device: {device}\n'));
            file.close()

            self.channels[i].save(interpolate('{path}/channel_{i}.save'))


    def wireChannel(self, device, instr):
        self.inputs[device] = pygame.midi.Input(instr)
        self.wires[device] = instr

    def update(self):
        for i in range(0, 15):
            if self.channels[i] == None:
                continue
            if self.inputs[i] == None:
                continue
            for msg in self.inputs[i].read(100):
                command = (msg[0][0] & 240) >> 4
                if command == 8:
                    ch = msg[0][0] & 15
                    note = msg[0][1]
                if command == 9:
                    ch = msg[0][0] & 15
                    note = msg[0][1]
                    strength = msg[0][2]
                    instrument = self.channels[ch]
                    instrument.press(note, strength)
                    """sample = instrument.samples[note]
                    self.sampler.play(ch"""


