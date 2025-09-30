"""Database configuration and session management"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
import os

from modules.account_management.infrastructure.models.user_account_orm import Base


class DatabaseConfig:
    """Database configuration"""
    
    def __init__(self):
        # Get database URL from environment - prefer PostgreSQL
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            # Build from individual components
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = os.getenv('DB_PORT', '5432')
            db_name = os.getenv('DB_NAME', 'am_user_management')
            db_user = os.getenv('DB_USER', 'munishm')
            db_password = os.getenv('DB_PASSWORD', '')
            
            # Build URL - handle empty password
            if db_password:
                database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
            else:
                database_url = f'postgresql://{db_user}@{db_host}:{db_port}/{db_name}'
        
        # Convert PostgreSQL URL to async if needed
        if database_url.startswith('postgresql://'):
            self.database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
        else:
            self.database_url = database_url
        
        print(f"🔗 Connecting to database: {self.database_url}")
        
        # Create async engine
        self.engine: AsyncEngine = create_async_engine(
            self.database_url,
            echo=os.getenv('DB_ECHO', 'false').lower() == 'true',
            pool_size=int(os.getenv('DB_POOL_SIZE', '5')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '10')),
            pool_timeout=int(os.getenv('DB_POOL_TIMEOUT', '30'))
        )
        
        # Create async session factory
        self.async_session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def create_tables(self):
        """Create database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self):
        """Drop database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session"""
        async with self.async_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self):
        """Close database engine"""
        await self.engine.dispose()


# Global database instance
db_config = DatabaseConfig()