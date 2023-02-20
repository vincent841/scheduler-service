from abc import *


class ENSBackend(metaclass=ABCMeta):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def fire(self) -> None:
        pass
