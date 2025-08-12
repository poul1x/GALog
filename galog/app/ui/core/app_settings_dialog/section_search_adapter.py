from abc import ABC, abstractmethod

from PyQt5.QtWidgets import QWidget


class SectionSearchAdapter(ABC):
    @abstractmethod
    def key(self) -> str:
        pass

    @abstractmethod
    def value(self) -> QWidget:
        pass
