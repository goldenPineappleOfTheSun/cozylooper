import pygame

"""BPM_CHANGED_EVENT = pygame.USEREVENT + 1
BPM_TICK = pygame.USEREVENT + 2
BPM_HALF_TICK = pygame.USEREVENT + 3
DEMAND_CHANGE_BPM = pygame.USEREVENT + 4
DEMAND_CHANGE_TRACK_SIZE = pygame.USEREVENT + 5
DEMAND_CHANGE_SAMPLERATE = pygame.USEREVENT + 6
SHOW_LIST_OF_COMMANDS = pygame.USEREVENT + 7
SHOW_LIST_OF_DEVICES = pygame.USEREVENT + 8"""

def emit(name, data):
    data['_eventname'] = name
    pygame.event.post(pygame.event.Event(pygame.USEREVENT, data))

def check(event, name):
    return event.type == pygame.USEREVENT and event.dict['_eventname'] == name