from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Rect:
    x: int
    y: int
    x2: int
    y2: int

    @property
    def width(self) -> int:
        return self.x2 - self.x

    @property
    def height(self) -> int:
        return self.y2 - self.y

class PresentationStrategy(ABC):
    """
    An abstract base class that defines how to apply presentation
    attributes (e.g., width, height) to SGML or HTML nodes.
    """

    @abstractmethod
    def move_position(self, sgml_element, pos: Rect):
        pass

