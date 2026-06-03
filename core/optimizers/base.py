from abc import ABC, abstractmethod


class BaseFeedOptimizer(ABC):
    """Contract for feed optimization engines."""

    @abstractmethod
    def optimize(self, ingredients, constraints):
        raise NotImplementedError
