import enum
import math
import drawing as draw

class TrackState(enum.Enum):
    error = 0,
    default = 1,
    setSize = 2

class Track:
    def __init__(self, n, left = 0, top = 0):
        self.n = n
        self.left = left
        self.top = top
        self.WIDTH = 1
        self.HEIGHT = 17
        self._initDraw = False

    def update(self):
        needredraw = not self._initDraw
        if needredraw:
            self.redraw()
            self._initDraw = True

    def redraw(self):
        draw.clearRect(self.left, self.top, self.WIDTH, self.HEIGHT)
        self.redrawTrackHeader()
        self.redrawTrack()

    def redrawTrackHeader(self):
        draw.clearRect(self.left, self.top, self.WIDTH, 1)
        draw.rectangle(self.left, self.top, 1, 1, '#6e5971 1p #ffffff')

    def redrawTrack(self):
        draw.clearRect(self.left, self.top + 1, self.WIDTH, self.HEIGHT - 1)
        draw.rectangle(self.left, self.top + 1, 1, self.HEIGHT - 1, '#a397a5 1p #ffffff')

