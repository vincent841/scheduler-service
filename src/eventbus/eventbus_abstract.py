from abc import *


class EventBus(metaclass=ABCMeta):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def connect(self, **kargs):
        pass

    @abstractmethod
    def trigger(self, **kargs):
        pass
