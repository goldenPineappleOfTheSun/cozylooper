import keyboard
from string import ascii_lowercase
import utils
from area import Area
import looperAreas

def simple(name, callback, area):
	keyboard.on_press_key(name, checkAreaAndCallSimple(callback, area))

def add(str, callback, area):
	keyboard.add_hotkey(str, checkAreaAndCallHotkey(callback, area))

""" very undone but works by now """
def processText(callback, area):
    for c in ascii_lowercase:
        keyboard.add_hotkey('shift + ' + c, checkAreaAndCallKeyboardKey_h(callback, area, c.upper()))
        keyboard.on_press_key(c, checkAreaAndCallKeyboardKey_p(callback, area, c))

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
        if keyboard.is_pressed('shift'):
            return
        # some strange arrows bug !!!
        if (event.name == 'up'
        or event.name == 'down'
        or event.name == 'left'
        or event.name == 'right'
        or event.name == 'page up'
        or event.name == 'page down'):
            return
        if area == looperAreas.currentArea:
            callback(key)
    return cb

def checkAreaAndCallKeyboardKey_h(callback, area, key):
    def cb():
        if area == looperAreas.currentArea:
            callback(key)
    return cb