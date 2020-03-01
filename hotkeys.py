import keyboard
from string import ascii_lowercase
import utils
from area import Area
import looperAreas

def simple(name, callback, area):
	keyboard.on_press_key(name, checkAreaAndCallSimple(callback, area))

def add(str, callback, area):
	keyboard.add_hotkey(str, checkAreaAndCallHotkey(callback, area))

def processText(callback, area):
    for c in ascii_lowercase:
        keyboard.on_press_key(c, checkAreaAndCallKeyboardKey_p(callback, area, c))
        keyboard.add_hotkey('shift + ' + c, checkAreaAndCallKeyboardKey_h(callback, area, c.upper()))

    for c in [str(x) for x in range(0, 10)]:
        keyboard.on_press_key(c, checkAreaAndCallKeyboardKey_p(callback, area, c))

    keyboard.on_press_key('backspace', checkAreaAndCallKeyboardKey_p(callback, area, 'backspace'))
    
    keyboard.on_press_key('-', checkAreaAndCallKeyboardKey_p(callback, area, '-'))
    keyboard.on_press_key('=', checkAreaAndCallKeyboardKey_p(callback, area, '='))
    keyboard.on_press_key('.', checkAreaAndCallKeyboardKey_p(callback, area, '.'))
    keyboard.on_press_key(',', checkAreaAndCallKeyboardKey_p(callback, area, ','))
    keyboard.on_press_key('space', checkAreaAndCallKeyboardKey_p(callback, area, ' '))

def checkAreaAndCallSimple(callback, area):
	def cb(event):
		if area == looperAreas.currentArea:
			callback(event)
	return cb

def checkAreaAndCallHotkey(callback, area):
	def cb():
		if area == looperAreas.currentArea:
			callback()
	return cb

def checkAreaAndCallKeyboardKey_p(callback, area, key):
    def cb(event):
        if area == looperAreas.currentArea:
            callback(key)
    return cb

def checkAreaAndCallKeyboardKey_h(callback, area, key):
    def cb():
        if area == looperAreas.currentArea:
            callback(key)
    return cb