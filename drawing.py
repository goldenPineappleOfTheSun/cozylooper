import pygame
import utils

cw = 16
ch = 16
width = 16
height = 16
canvas = None
clearColor = '#ffffff'

colors = {
    '@clear': '#ffffff',
    '@neutral': '#ab9b87',
    '@fore': '#444444',
    '@light': '#dac1a3',
    '@set': '#f5cb55',
    '@lightset': '#fbd979',
    '@darkset': '#ff9800',
    '@play': '#acd872',
    '@lightplay': '#c5ea93',
    '@darkplay': '#80a550',
    '@record': '#f78181',
    '@lightrecord': '#ff90aa',
    '@darkrecord': '#c34f4f'
}

_fonts = {
    'open-sans': 'fonts/OpenSans-Regular.ttf',
    'open-sans-bold': 'fonts/OpenSans-Bold.ttf'
}

fontsCollection = {}

updates = []

def init(w, h, cellWidth = 16, cellHeight = 16, initialCanvas = None):
    global width
    global height
    global cw
    global ch
    global canvas
    width = w
    height = h
    cw = cellWidth
    ch = cellHeight
    canvas = initialCanvas
    fontsCollection['default'] = pygame.font.Font(None, 16)

def setCanvas(value):
    global canvas
    canvas = value
    clearCanvas()

def setClearColor(value):
    clearColor = value
    pygame.display.update()

def setNewFont(key, style):
    if (key in fontsCollection):
        raise Exception('this font is already in collection')
    fontsCollection[key] = _styleFont(style)

def setDefaultFont(value):
    fontsCollection['default'] = fontsCollection[value]

class DrawStyle:
    def __init__(self, 
            fill = 'white', line = 'black', fore = 'black',
            lineWidth = 0, font = 'default', align = 'midleft'):
        self.line = line
        self.fill = fill
        self.fore = fore
        self.lineWidth = lineWidth
        self.font = font
        self.align = align

    def setLine(self, value):
        color = self._transformColor(value)
        self.line = color
        return self

    def setFill(self, value):
        color = self._transformColor(value)
        self.fill = color
        return self

    def setColor(self, value):
        color = self._transformColor(value)
        self.fore = color
        return self

    def setLineWidth(self, value):
        self.lineWidth = value
        return self

    def setFont(self, value):
        self.font = value
        return self

    def setAlign(self, value):
        self.align = value
        return self

    def _transformColor(self, value):
        result = (0, 0, 0)
        if _isHexColor(value):
            result = _tupleFromHexColor(value)
        elif _isAliasColor(value):
            result = self._transformColor(colors[value])
        else:
            raise Exception('unknown color format')
        return result

class Coords:
    def x(self, value):
        return _transformX(value)
    def y(self, value):
        return _transformY(value) 

coords = Coords()

defaultDrawStyle = DrawStyle(
    line = 'black',
    fill = 'white',
    fore = 'black',
    lineWidth = 0,
    font = 'default')

def rectangle(left, top, width, height, style):
    x = coords.x(left)
    y = coords.y(top)
    w = coords.x(width)
    h = coords.y(height)

    drawStyle = _styleRect(style)

    pygame.draw.rect(canvas, drawStyle.fill, (x, y, w, h))
    if (drawStyle.lineWidth > 0):
        pygame.draw.rect(canvas, drawStyle.line, (x, y, w, h), drawStyle.lineWidth)
    

def line(x1, y1, x2, y2, style):
    fx = coords.x(x1)
    fy = coords.y(y1)
    tx = coords.x(x2)
    ty = coords.y(y2)

    drawStyle = _styleLine(style)
    pygame.draw.line(canvas, drawStyle.line, (fx, fy), (tx, ty), drawStyle.lineWidth)

def text(txt, left, top, style):
    x = coords.x(left)
    y = coords.y(top)

    aligns = {
        'midleft': lambda t, _x, _y: todraw.get_rect(midleft=(_x, _y)),
        'center': lambda t, _x, _y: todraw.get_rect(center=(_x, _y)),
        'midright': lambda t, _x, _y: todraw.get_rect(midright=(_x, _y))
    }

    drawStyle = _styleText(style)

    todraw = fontsCollection[drawStyle.font].render(txt, 1, drawStyle.fore)
    place = aligns[drawStyle.align](todraw, x, y)
    canvas.blit(todraw, place)

def clearCanvas():
    pygame.draw.rect(canvas, _tupleFromHexColor(clearColor), (0, 0, width * cw, height * ch))
    appendUpdateRect(0, 0, width, height)

def clearRect(x, y, w, h):
    pygame.draw.rect(canvas, _tupleFromHexColor(clearColor), (coords.x(x), coords.y(y), coords.x(w), coords.y(h)))
    appendUpdateRect(x, y, w, h)

def appendUpdateRect(x, y, w, h):
    rect = pygame.Rect(x * cw, y * ch, w * cw, h * ch)
    for r in updates:
        newFullyContains = r.left >= rect.left and r.right <= rect.right and r.top >= rect.top and r.bottom <= rect.bottom 
        oldFullyContains = r.left <= rect.left and r.right >= rect.right and r.top <= rect.top and r.bottom >= rect.bottom
        
        if oldFullyContains:
            return

        if newFullyContains:
            r = r.union(rect)
            return

        isLeftAndRightMatches = r.left == rect.left and r.right == rect.right
        isUnionableByHor = isLeftAndRightMatches and (r.top < rect.bottom and r.bottom > rect.top)

        isTopAndBottomMatches = r.top == rect.top and r.bottom == rect.bottom
        isUnionableByVer = isTopAndBottomMatches and (r.left < rect.right and r.right > rect.left)

        if isUnionableByHor or isUnionableByVer:
            r = r.union(rect)
            return

    updates.append(rect)

def update():
    pygame.display.update(updates)
    updates.clear()    

""" 
fill width [line]
#00ff00 1p #00ff00
#00ff00 0
"""
def _styleRect(style):
    drawStyle = DrawStyle()
    parsed = style.split(' ')
    s = 'fill'
    for x in parsed:
        if x == '':
            continue
        elif s == 'fill':
            drawStyle.setFill(x)
            s = 'lineWidth'
        elif s == 'lineWidth':
            if not _isPoints(x):
                raise Exception('wrong width format ("' + style + '")!' )
            w = int(x[:-1])
            drawStyle.setLineWidth(w)
            s = 'line' if w > 0 else 'exit'
        elif s == 'line':
            drawStyle.setLine(x)
            s = 'exit'
    return drawStyle

""" 
#ffaaaa
5p #ffaaaa
"""
def _styleLine(style):
    drawStyle = DrawStyle(lineWidth = 1);
    parsed = style.split(' ')
    s = 'width' if _isPoints(parsed[0]) else 'color'
    for x in parsed:
        if x == '':
            continue
        elif s == 'width':
            if not _isPoints(x):
                raise Exception('wrong width format ("' + style + '")!' )
            w = int(x[:-1])
            drawStyle.setLineWidth(w)
            s = 'color'
        elif s == 'color':
            drawStyle.setLine(x)
            s = 'exit'
    return drawStyle

"""
color fontname align
#ff44ee 
#ff44ee default
#ff44ee open-sans
#ff44ee open-sans midleft
#ff44ee open-sans center
"""
def _styleText(style):
    drawStyle = DrawStyle(lineWidth = 1, font = 'default')
    parsed = style.split(' ')
    s = 'color'
    for x in parsed:
        if x == '':
            continue
        elif s == 'color':
            drawStyle.setColor(x)
            s = 'font'
        elif s == 'font':
            drawStyle.setFont(x)
            s = 'align'
        elif s == 'align':
            drawStyle.setAlign(x)
            s = 'exit'
    return drawStyle

"""
filename size
open-sans 16
open-sans-big 18
"""
def _styleFont(style):
    filename = None
    size = 16
    parsed = style.split(' ')
    s = 'filename'  
    for x in parsed:
        if x == '':
            continue
        elif s == 'filename':
            filename = _fonts[x] if x != 'default' else None
            s = 'size'
        elif s == 'size':
            size = int(x)
            s = 'exit'
    return pygame.font.Font(filename, size) 


def _transformX(value):
    return utils.overload(value, string = _coordsFromString, number = _xFromNumber)(value)

def _transformY(value):
    return utils.overload(value, string = _coordsFromString, number = _yFromNumber)(value)

def _coordsFromString(value):
    parts = value.split(' ')
    n = 0
    result = 0
    sign = 1
    for i in range(0, len(parts)):
        if i == 0:
            x = parts[i]
            if not _isCells(x):
                raise Exception('wrong cells format ("' + value + '")!')
            result += _xFromNumber(int(x[:-2])) if x[-2:] == 'cw' else _yFromNumber(int(x[:-2]))
        elif i == 1:
            x = parts[i]
            if not _isUnaryOperator(x):
                raise Exception('wrong operator format!')
            sign = 1 if x == '+' else -1 if x == '-' else 0
        elif i == 2:
            result += sign * int(parts[i])
        else:
            raise Exception('wrong format')
    return result


def _xFromNumber(value: int):
    return cw * value

def _yFromNumber(value: int):
    return ch * value

def _isHexColor(value):
    return value[:1] == '#'

def _isAliasColor(value):
    return value[:1] == '@'

def _isPoints(value):
    # this check may possible be stronger
    return value[-1:] == 'p'   

def _isCells(value):
    # this check may possible be stronger
    return value[-2:] == 'cw' or value[-2:] == 'ch'

def _isUnaryOperator(value):
    # this check may possible be stronger
    return value == '+' or value == '-'

def _tupleFromHexColor(value):
    return (int(value[1:3], 16), int(value[3:5], 16), int(value[5:], 16))