from abc import ABC, abstractmethod
import random
from exceptions import InvalidNameError


class TrackableNode(ABC):

    def __init__(self, name):
        # self._status = status
        # self._progress = progress
        if not isinstance(name, str):
            raise InvalidNameError("Name must be a string")
        if len(name) == 0:
            raise InvalidNameError("Name cannot be empty")
        self._name = name
        

    @property
    def name(self):
        return self._name

    @property
    @abstractmethod
    def progress(self):
        pass

    @property
    @abstractmethod
    def status(self):
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} name='{self.name}'>"

    def __eq__(self, other):
        if not isinstance(other, TrackableNode):
            return False
        return self.__class__ == other.__class__ and self._name == other._name

    

class DummyNode(TrackableNode):
    @property   #decorator to make the method a property, if not then it will give address of the method
    def progress(self):
        return random.randint(0, 100)

    @property       #same here for the status method
    def status(self):  
        return random.choice(["In Progress", "Completed", "Pending", "Failed"])



