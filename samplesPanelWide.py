from areaWide import AreaWide
import drawing as draw
from utils import interpolate

class SamplesPanelWide(AreaWide):
    def __init__(self, sampler, left = 1, top = 19):
        super().__init__(left, top)        
        self.sampler = sampler
        self.samples = []
        self.update()
        self.selectedrow = 0
        self.selectedcol = 0
        self.camera = 0
    
    def redraw(self):
        draw.clearRect(self.left, self.top + 1, self.WIDTH, self.HEIGHT);
        draw.rectangle(self.left, self.top + 1, self.WIDTH, self.HEIGHT, '@light')
        count = 0
        index = 0

        if self.selectedcol == 0:
            draw.rectangle(self.left + 0.24, self.top + 2 + self.selectedrow - self.camera, 2, 1, '@set')
        """elif self.selectedcol == 1:
            draw.rectangle(self.left + 3, self.top + 2 + self.selectedrow - self.camera, 3, 1, '@set')"""

        self.update()

        draw.text('      Suspend mode', self.left, self.top + 1, '#333333 console topleft')

        for index in range(self.camera, self.camera + 5):
            if index < len(self.samples):
                sample = self.samples[index]
                top = self.top + 2 + index - self.camera
                draw.text(' ' + sample[0], self.left, top, '#333333 console topleft')
                draw.rectangle(self.left + 3, top, 4.5, 0.8, '@clear' if (self.selectedcol != 1 or self.selectedrow != sample[1]) else '@set')
                draw.text(self.sampler.suspendModes[sample[0]], self.left + 3, top, '#333333 console topleft')

    def redrawTitle(self):
        draw.clearRect(self.left, self.top, self.WIDTH, 1);
        draw.rectangle(self.left, self.top, self.WIDTH, 1, '@neutral')
        draw.text('Панель управления сэмплами', self.left, interpolate('{self.top}ch + 2p'), '#ffffff console topleft')

    def update(self):     
        self.samples = []   
        for name in self.sampler.getSamplesNames():
            self.samples.append(name, len(self.samples))

    def wheelSuspendMode(self, val):
        modes = ['stop oct', 'stop samp', 'stop note', 'chaos', 'sus solo', 'sus portm', 'sus chord']
        sampleIndex = self.samples[self.selectedrow][0]
        pos = modes.index(self.sampler.suspendModes[sampleIndex])
        pos += val
        if pos < 0:
            pos = 0
        if pos >= len(modes):
            pos = len(modes) - 1

        self.sampler.setSuspendMode(sampleIndex, modes[pos])
        self.redraw()

    # wide events

    def rightPressed(self):
        self.selectedcol += 1
        if self.selectedcol > 1:
            self.selectedcol = 1
        self.redraw()

    def leftPressed(self):
        self.selectedcol -= 1
        if self.selectedcol < 0:
            self.selectedcol = 0
        self.redraw()

    def upPressed(self):
        if self.selectedcol == 0:
            self.selectedrow -= 1
            if self.selectedrow < 0:
                self.selectedrow = 0
            if self.camera > self.selectedrow - 1:
                self.camera -= 1
            if self.camera < 0:
                self.camera = 0
            self.redraw()
        elif self.selectedcol == 1:
            self.wheelSuspendMode(-1)

    def downPressed(self):
        if self.selectedcol == 0:
            count = len(self.samples)
                
            self.selectedrow += 1
            if self.selectedrow > count - 1:
                self.selectedrow = count - 1
            if self.selectedrow - self.camera > 2:
                self.camera += 1
            if self.camera > count - 5:
                self.camera = count - 5
            #self.camera = self.selectedrow
            print(self.camera)
            self.redraw()
        elif self.selectedcol == 1:
            self.wheelSuspendMode(1)