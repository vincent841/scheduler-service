from abc import *


class EventTriggerMethod(metaclass=ABCMeta):

    ###################################
    # Properties
    ###################################

    ###################################
    # Abstraction Functions
    ###################################

    # prepare somthings to use this method
    @abstractmethod
    def prepare(self, **kargs):
        pass

    # trigger events with the defined method
    @abstractmethod
    def trigger(self, *args):
        pass
