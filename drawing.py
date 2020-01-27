import pygame
import utils

cw = 16
ch = 16
width = 16
height = 16
canvas = None
clearColor = 'white'

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


def setCanvas(value):
    global canvas
    canvas = value

def setClearColor(value):
    clearColor = value

class DrawStyle:
    def __init__(self, 
            fill = 'white', line = 'black', fore = 'black',
            lineWidth = 0):
        self.line = line
        self.fill = fill
        self.fore = fore
        self.lineWidth = lineWidth

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

    def _transformColor(self, value):
        result = (0, 0, 0)
        if (_isHexColor(value)):
            result = _tupleFromHexColor(value)
        else: 
            raise Exception('unknown color format')
        return result
        
defaultDrawStyle = DrawStyle(
    line = 'black',
    fill = 'white',
    fore = 'black',
    lineWidth = 0)

def rectangle(left, top, width, height, style):
    x =_transformX(left)
    y =_transformY(top)
    w =_transformX(width)
    h =_transformY(height)

    drawStyle = _styleRect(style)

    if (drawStyle.lineWidth > 0):
        pygame.draw.rect(canvas, drawStyle.fill, (x, y, w, h), drawStyle.lineWidth)
    else:
        pygame.draw.rect(canvas, drawStyle.fill, (x, y, w, h))

    pygame.display.update()

""" 
fill width [line]
#00ff00 1p 00ff00
#00ff00 0
"""
def _styleRect(style):
    drawStyle = DrawStyle();
    parsed = style.split(' ');
    s = 'fill'
    for x in parsed:
        if x == '':
            continue
        elif s == 'fill':
            drawStyle.setFill(x)
            s = 'lineWidth'
        elif s == 'lineWidth':
            if not _isPoints(x):
                raise Exception('wrong width format ("' + x + '")!' )
            w = int(x[:-1])
            drawStyle.setLineWidth(w)
            s = 'line' if w > 0 else 'exit'
        elif s == 'line':
            drawStyle.setLine(x)
            s = 'exit'
    return drawStyle

def _transformX(value):
    return utils.overload(value, string = _coordsFromString, integer = _xFromInteger)(value)

def _transformY(value):
    return utils.overload(value, string = _coordsFromString, integer = _yFromInteger)(value)

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
            result += _xFromInteger(int(x[:-2])) if x[-2:] == 'cw' else _yFromInteger(int(x[:-2]))
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


def _xFromInteger(value: int):
    return cw * value

def _yFromInteger(value: int):
    return ch * value

def _isHexColor(value):
    return value[:1] == '#'

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