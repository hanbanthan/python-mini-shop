"""
Abstract base Repository - foundation for Repository Pattern

Why use Repository:
- Bussiness service can NOT write or call SQL queries directly, 
only Repository can know table structure and write SQL queries
- Seperate data access logic and business logic helping 
change the way of storing data (Sqlite-> Postgres, add caching,..) 
and not need change Service
- Allow to Fake or Mock Repository (implement with this interface)
so that we can unit test service without database access

Each repository implement this contract, and can add more method
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")

class BaseRepository(ABC, Generic[T]):

    @abstractmethod
    def add(self, entity: T) -> T:
        """Add an entity, return entitty with id"""
    
    @abstractmethod
    def get_by_id(self, entity_id: int) -> T:
        """Get an entity by id, return None if not found"""
    
    @abstractmethod
    def get_all(self) -> list[T]:
        """Get all entities, return empty list if not found"""
    
    @abstractmethod
    def update(self, entity: T) -> T:
        """Update an entity, return updated entity"""
    