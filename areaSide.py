from abc import ABC, abstractmethod

class AreaSide():

    def __init__(self, left = 1, top = 19):   
        self.WIDTH = 17
        self.HEIGHT = 15

    @abstractmethod
    def redrawTitle(self):
        pass