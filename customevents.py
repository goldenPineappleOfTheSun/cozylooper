import pygame

def emit(name, data):
    data['_eventname'] = name
    pygame.event.post(pygame.event.Event(pygame.USEREVENT, data))

def check(event, name):
    return event.type == pygame.USEREVENT and event.dict['_eventname'] == name