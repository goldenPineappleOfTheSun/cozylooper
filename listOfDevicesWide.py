from areaWide import AreaWide
import drawing as draw
import sounddevice as sd
from utils import interpolate

class ListOfDevicesWide(AreaWide):
    def __init__(self, left = 1, top = 19):
        super().__init__(left, top)        
        self.page = 0
    
    def redraw(self):
        draw.clearRect(self.left, self.top + 1, self.WIDTH, self.HEIGHT);
        draw.rectangle(self.left, self.top + 1, self.WIDTH, self.HEIGHT, '@light')
        devices = sd.query_devices()
        for index in range(self.page * 6, self.page * 6 + 6):            
            if index < len(devices):
                dev = devices[index]
                text = str(index) + ': ' + dev['name']
                draw.text(text, self.left, self.top + 1 + index % 6, '#333333 console topleft')

    def redrawTitle(self):
        draw.clearRect(self.left, self.top, self.WIDTH, 1);
        draw.rectangle(self.left, self.top, self.WIDTH, 1, '@neutral')
        draw.text('Список доступных устройств', self.left, interpolate('{self.top}ch + 2p'), '#ffffff console topleft')