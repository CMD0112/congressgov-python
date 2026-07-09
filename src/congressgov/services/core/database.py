"""
`SQLAlchemyHelper` manages database session lifecycle: thread-safe sessions
via `scoped_session`, context-manager cleanup, and a base registry that
keeps ORM metadata from colliding across storage backends.
"""

from __future__ import annotations

from typing import Any
from contextlib import contextmanager

# SQLAlchemy is optional - only required for storage features
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# Global registry to prevent proliferation and ensure consistency
_base_registry: dict[str, Any] = {}


class SQLAlchemyHelper:
    """Sets up a SQLAlchemy engine/session with proper lifecycle management:
    thread-safe sessions via ``scoped_session``, and a context manager that
    commits on success and rolls back on exception.

    Example:
        helper = SQLAlchemyHelper("sqlite:///mydb.sqlite")
        
        # Recommended: Use context manager
        with helper.session_scope() as session:
            session.add(obj)
            # Automatic commit on success, rollback on exception
        
        # Manual session management (if needed)
        session = helper.get_session()
        try:
            session.add(obj)
            session.commit()
        finally:
            session.close()
    """

    def __init__(self, db_url: str = "sqlite:///:memory:", **engine_kwargs):
        """
        Initialize SQLAlchemy helper with database connection.
        
        Args:
            db_url: SQLAlchemy database URL (default: in-memory SQLite)
            engine_kwargs: Additional arguments passed to create_engine
            
        Raises:
            ImportError: If SQLAlchemy is not installed
        """
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError(
                "SQLAlchemy is required for storage features. "
                "Install it with: pip install sqlalchemy"
            )
        
        # Store db_url for Base registry key
        self.db_url = db_url
        
        # Create engine with connection pooling
        self.engine = create_engine(db_url, **engine_kwargs)
        
        # Use scoped_session for thread-safety
        # Each thread gets its own session instance
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        
        # Reuse Base from registry to avoid metadata conflicts
        # Each unique db_url gets exactly one declarative_base instance
        if db_url not in _base_registry:
            _base_registry[db_url] = declarative_base()
        self.Base = _base_registry[db_url]

    @contextmanager
    def session_scope(self) -> Any:
        """
        Provide a transactional scope around a series of operations.
        
        Automatically commits on success, rolls back on exception,
        and closes session in finally block. This is the recommended way
        to use sessions.
        
        Yields:
            SQLAlchemy session instance
            
        Example:
            with helper.session_scope() as session:
                session.add(my_object)
                # Commit happens automatically if no exception
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_session(self) -> Any:
        """
        Get a new session instance.
        
        Caller is responsible for closing the session.
        Prefer using session_scope() context manager instead.
        
        Returns:
            SQLAlchemy session instance
            
        Example:
            >>> session = helper.get_session()
            >>> try:
            ...     session.add(my_object)
            ...     session.commit()
            ... finally:
            ...     session.close()
        """
        return self.Session()

    def close(self) -> None:
        """
        Close all sessions and dispose of the engine.
        
        Call this when completely done with the helper to free resources.
        This frees all database connections and cleans up thread-local sessions.
        
        Example:
            >>> helper = SQLAlchemyHelper("sqlite:///mydb.sqlite")
            >>> # ... use helper ...
            >>> helper.close()  # Clean up when done
        """
        self.Session.remove()
        self.engine.dispose()


# ============================================================================
# PUBLIC API - ADVANCED FEATURES
# ============================================================================

def get_base_registry() -> dict[str, Any]:
    """
    Get the global base registry.
    
    This is an advanced feature for users working directly with SQLAlchemy.
    Most users should use StorageManager or SQLAlchemyHelper instead.
    
    The base registry ensures that each unique database URL gets exactly one
    declarative_base instance, preventing metadata conflicts when working with
    multiple databases or when sharing ORM classes across sessions.
    
    Returns:
        Dictionary mapping db_url to declarative_base instances
        
    Example:
        >>> registry = get_base_registry()
        >>> print(registry.keys())  # Shows all database URLs with registered bases
    """
    return _base_registry

