from abc import ABC, abstractmethod

class AreaWide():

    def __init__(self, left = 1, top = 19):    
        self.left = left
        self.top = top
        self.WIDTH = 32
        self.HEIGHT = 6

    @abstractmethod
    def redrawTitle():
        pass