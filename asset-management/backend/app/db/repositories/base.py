"""Base repository class using SQLAlchemy ORM."""
import logging
from typing import TypeVar, Generic, Type, Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models import Base

logger = logging.getLogger('db.repository')

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations.
    
    Repositories now receive a session via dependency injection
    rather than creating connections themselves.
    """
    
    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session
    
    def get_by_id(self, id_value) -> Optional[ModelType]:
        """Get a single record by primary key."""
        return self.session.get(self.model, id_value)
    
    def get_all(self) -> List[ModelType]:
        """Get all records."""
        stmt = select(self.model)
        return list(self.session.scalars(stmt).all())
    
    def create(self, obj: ModelType) -> ModelType:
        """Create a new record."""
        self.session.add(obj)
        self.session.flush()
        return obj
    
    def update(self, obj: ModelType) -> ModelType:
        """Update an existing record."""
        self.session.flush()
        return obj
    
    def delete(self, obj: ModelType) -> None:
        """Delete a record."""
        self.session.delete(obj)
        self.session.flush()
    
    def commit(self) -> None:
        """Commit the current transaction."""
        self.session.commit()
    
    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.session.rollback()