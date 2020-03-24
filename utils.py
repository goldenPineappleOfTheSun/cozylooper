import sys

def overload(value, string = None, integer = None, real = None, number = None):
    if number != None and (type(value) == int or type(value) == float):
        return number if number != None else lambda x:x
    if type(value) == str:
        return string if string != None else lambda x:x
    elif type(value) == int:
        return integer if integer != None else lambda x:x
    elif type(value) == float:
        return real if real != None else lambda x:x
    else:
        raise Exception("cant find overload!")

def callOverload(value, string, integer, real, number = None):
    overload(value, string, integer, real, number)(value)

def countPositionalArguments(func):
    all_args = func.__code__.co_argcount

    if func.__defaults__ is not None:  #  in case there are no kwargs
        kwargs = len(func.__defaults__)
    else:
        kwargs = 0

    return all_args - kwargs

def interpolate(text):
    return text.format(**sys._getframe(1).f_locals)

def readSaveFile(path):
    result = {}
    file = open(path, 'r')
    for line in file:
        data = line.split(':')
        key = data[0].strip()
        value = data[1].strip()
        result[key] = value
    file.close()
    return result