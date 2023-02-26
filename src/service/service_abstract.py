from abc import *


class Serivce(metaclass=ABCMeta):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def connect(self, **kargs):
        pass

    @abstractmethod
    def run(self, **kargs):
        pass
