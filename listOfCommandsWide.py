from areaWide import AreaWide
import drawing as draw
from utils import interpolate

class ListOfCommandsWide(AreaWide):
    def __init__(self, left = 1, top = 19):
        super().__init__(left, top)
        self.commands = [
            'set-bpm - [ударов в сек]',
            'set-track-size - -n [номер] -s [размер]',
            'set-samplerate - [частота сэмплирования]',
            'commands - список команд',
            'devices - список устройств',
        ]
        self.page = 0
    
    def redraw(self):
        draw.clearRect(self.left, self.top + 1, self.WIDTH, self.HEIGHT);
        draw.rectangle(self.left, self.top + 1, self.WIDTH, self.HEIGHT, '@light')
        for index in range(self.page * 6, self.page * 6 + 6):
            if index < len(self.commands):
                draw.text(self.commands[index], self.left, self.top + 1 + index % 6, '#333333 console topleft')

    def redrawTitle(self):
        draw.clearRect(self.left, self.top, self.WIDTH, 1);
        draw.rectangle(self.left, self.top, self.WIDTH, 1, '@neutral')
        draw.text('Список команд', self.left, interpolate('{self.top}ch + 2p'), '#ffffff console topleft')