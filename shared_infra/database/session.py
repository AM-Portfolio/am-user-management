"""SQLAlchemy session factory and database configuration"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from ..config.settings import settings
from .base import Base


class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self):
        self._engine = None
        self._session_factory = None
    
    def initialize(self) -> None:
        """Initialize database engine and session factory"""
        # Create async engine
        self._engine = create_async_engine(
            settings.database.url,
            echo=settings.database.echo,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_timeout=settings.database.pool_timeout,
            # Use StaticPool for SQLite in-memory databases
            poolclass=StaticPool if settings.database.url.startswith("sqlite") else None,
            connect_args={
                "check_same_thread": False
            } if settings.database.url.startswith("sqlite") else {}
        )
        
        # Create session factory
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def create_tables(self) -> None:
        """Create all database tables"""
        if not self._engine:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self) -> None:
        """Drop all database tables"""
        if not self._engine:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        if not self._session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self) -> None:
        """Close database connections"""
        if self._engine:
            await self._engine.dispose()


# Global database manager instance
db_manager = DatabaseManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async for session in db_manager.get_session():
        yield session


async def init_database() -> None:
    """Initialize database"""
    db_manager.initialize()
    await db_manager.create_tables()


async def close_database() -> None:
    """Close database connections"""
    await db_manager.close()