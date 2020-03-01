import drawing as draw

class Console:
    def __init__(self, x, y, w):
        self.left = x
        self.top = y
        self.WIDTH = w

    def redraw(self):
        style = '@light 1p @clear'
        draw.clearRect(self.left, self.top, self.WIDTH, 1)
        draw.rectangle(self.left, self.top, self.WIDTH, 1, style)