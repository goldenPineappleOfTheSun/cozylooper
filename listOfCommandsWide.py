from areaWide import AreaWide
import drawing as draw
from utils import interpolate

class ListOfCommandsWide(AreaWide):
    def __init__(self):
        super().__init__(1, 19)
        self.commands = {
            'set-bpm': '[ударов в сек]',
            'set-track-size': 'n [номер] -s [размер]',
            'set-samplerate': '[частота сэмплирования]',
            'commands': 'список команд',
            'devices': 'список устройств',
            'load-bank': '[папка] -n [буква]',
            'create-instrument': '[инструмент piano] [канал 0-15]'
        }
        self.page = 0

    def setCommands(self, list):
        for cmd in list:
            if not cmd in self.commands:
                self.commands[cmd] = ''

    def redraw(self):
        draw.clearRect(self.left, self.top + 1, self.WIDTH, self.HEIGHT);
        draw.rectangle(self.left, self.top + 1, self.WIDTH, self.HEIGHT, '@light')
        keys = self.commands.keys()
        index = 0
        for key in keys:
            if index >= self.page * 6 and index < self.page * 6 + 6 and index < len(keys):
                value = self.commands[key]
                draw.text(interpolate('{key} - {value}'), self.left, self.top + 1 + index % 6, '#333333 console topleft')
            index += 1

    def redrawTitle(self):
        draw.clearRect(self.left, self.top, self.WIDTH, 1);
        draw.rectangle(self.left, self.top, self.WIDTH, 1, '@neutral')
        draw.text('Список команд', self.left, interpolate('{self.top}ch + 2p'), '#ffffff console topleft')

    def rightPressed(self):
        if (self.page + 1) * 6 < len(self.commands):
            self.page += 1
            self.redraw()

    def leftPressed(self):
        if self.page > 0:
            self.page -= 1
            self.redraw()