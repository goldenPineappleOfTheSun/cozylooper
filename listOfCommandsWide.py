import drawing as draw

class ListOfCommandsWide:
    def __init__(self, left = 1, top = 19):
        self.left = left
        self.top = top
        self.WIDTH = 32
        self.HEIGHT = 6
        self.commands = [
            'set-bpm - [ударов в сек]',
            'set-track-size - -n [номер] -s [размер]',
            'set-samplerate - [частота сэмплирования]',
            'commands - ',
            'set-bp - [ударов в сек]',
            'set-trak-size - -n [номер] -s [размер]',
            'set-samlerate - [частота сэмплирования]',
            'comands - '
        ]
        self.page = 0
    
    def redraw(self):
        draw.clearRect(self.left, self.top, self.WIDTH, self.HEIGHT);
        draw.rectangle(self.left, self.top, self.WIDTH, self.HEIGHT, '@light')
        for index in range(self.page * 6, self.page * 6 + 6):
            if index < len(self.commands):
                draw.text(self.commands[index], self.left, self.top + index % 6, '@dark console topleft')