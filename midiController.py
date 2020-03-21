import numpy as np
import pygame
import pygame.midi

class MidiController:
    def __init__(self, sampler):
        self.channels = np.full((16), None)
        self.inputs = np.full((16), None)
        self.sampler = sampler

    def appendChannel(self, n, midiInstrument):
        if n < 0 or n > 15:
            return
        self.channels[n] = midiInstrument

    def wireChannel(self, device, instr):
        print(instr)
        self.inputs[device] = pygame.midi.Input(instr)

    def update(self):
        for i in range(0, 15):
            if self.channels[i] == None:
                continue
            if self.inputs[i] == None:
                continue
            for msg in self.inputs[i].read(100):
                command = (msg[0][0] & 240) >> 4
                print(command)
                if command == 8:
                    ch = msg[0][0] & 15
                    note = msg[0][1]
                    print('off ' + str(note))
                if command == 9:
                    ch = msg[0][0] & 15
                    note = msg[0][1]
                    strength = msg[0][2]
                    instrument = self.channels[ch]
                    instrument.press(note, strength)
                    """sample = instrument.samples[note]
                    self.sampler.play(ch"""
                    print('on ' + str(note))

