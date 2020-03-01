from utils import interpolate
import drawing as draw

class Console:
    def __init__(self, x, y, w):
        self.left = x
        self.top = y
        self.WIDTH = w
        self.active = False

    def redraw(self):
        style = '@dark 1p @clear' if self.active else '@light 1p @clear'
        draw.clearRect(self.left, self.top, self.WIDTH, 1)
        draw.rectangle(self.left, self.top, self.WIDTH, 1, style)

    def activate(self):
        self.active = True
        self.redraw()

    def deactivate(self):
        self.active = False
        self.redraw()