import drawing as draw

class Area:
    def __init__(self, x, y, w, h, needHighlight = True):
        self.left = x
        self.top = y
        self.width = w
        self.height = h
        self.needHighlight = needHighlight

    def clearHighlight(self):
        if not self.needHighlight:
            return

        draw.clearRect(str(self.left) + 'cw - 5p', self.top, '0cw + 5p', self.height)
        draw.clearRect(self.left + self.width, self.top, '0cw + 5p', self.height)
        draw.clearRect(str(self.left) + 'cw - 5p', str(self.top) + 'ch - 5p', str(self.width) + 'cw + 10p', '0ch + 5p')
        draw.clearRect(str(self.left) + 'cw - 5p', self.top + self.height, str(self.width) + 'cw + 10p', '0ch + 5p')

    def highlight(self):
        if not self.needHighlight:
            return
        self.clearHighlight()
        draw.rectangle(
            str(self.left) + 'cw - 3p', 
            str(self.top) + 'ch - 3p', 
            str(self.width) + 'cw + 6p', 
            str(self.height) + 'ch + 6p', 
            '@transparent 5p @highlight')