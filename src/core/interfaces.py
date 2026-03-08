"""
Core interfaces defining the standard architecture for the Retrieve Edital ETL pipeline.
Follows SOLID principles: Open/Closed, dependency inversion.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Generic, TypeVar

# T represents the Type of the data structure (e.g. Dict, or a Domain Model)
T = TypeVar("T")

# R represents the Return Type of a transformation
R = TypeVar("R")


class ISource(ABC, Generic[T]):
    """
    Interface for data extraction (Extract).
    Responsible solely for fetching raw data from the external source.
    """
    
    @abstractmethod
    def read(self) -> List[T]:
        """Reads and extracts data from the origin."""
        pass


class ITransform(ABC, Generic[T, R]):
    """
    Interface for data normalization and business rules (Transform).
    Responsible solely for converting raw input into validated domain objects.
    """
    
    @abstractmethod
    def process(self, raw_data: T) -> R:
        """Processes raw data, cleans it, and maps it to a domain structure."""
        pass


class ISink(ABC, Generic[T]):
    """
    Interface for data persistence (Load).
    Responsible solely for writing the validated data into the final target.
    """
    
    @abstractmethod
    def write(self, items: List[T]) -> None:
        """Persists the items sequentially or in batch to the storage solution."""
        pass
