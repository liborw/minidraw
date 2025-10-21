from abc import ABC, abstractmethod
from typing import Iterable
from minidraw.primitives import Primitive


class Shape(ABC):
    """
    Abstract base class for all procedural or composite geometric shapes.
    Shapes do not store primitives directly; instead they *generate* them
    lazily when elements() is called.
    """

    @abstractmethod
    def elements(self) -> Iterable[Primitive]:
        """Return an iterable of primitives composing this shape."""
        ...
