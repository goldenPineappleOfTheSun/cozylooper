import keyboard
from area import Area
import looperAreas

def simple(name, callback, area):
	keyboard.on_press_key(name, checkAreaAndCallSimple(callback, area))

def add(str, callback, area):
	keyboard.add_hotkey(str, checkAreaAndCallHotkey(callback, area))

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