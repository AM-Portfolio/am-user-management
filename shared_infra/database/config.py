"""Database configuration and session management"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from modules.account_management.infrastructure.models.user_account_orm import Base

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig:
    """Database configuration"""
    
    def __init__(self):

        print('Environment variables:')
        print(f'DATABASE_URL: {os.getenv("DATABASE_URL")}')
        print(f'DB_HOST: {os.getenv("DB_HOST")}')
        print(f'DB_PORT: {os.getenv("DB_PORT")}')
        print(f'DB_NAME: {os.getenv("DB_NAME")}')
        print(f'DB_USER: {os.getenv("DB_USER")}')
        print(f'DB_PASSWORD: {os.getenv("DB_PASSWORD")}')
                # Get database URL from environment - prefer PostgreSQL
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            # Build from individual components
            db_host = os.getenv('DB_HOST')
            db_port = os.getenv('DB_PORT')
            db_name = os.getenv('DB_NAME')
            db_user = os.getenv('DB_USER')
            db_password = os.getenv('DB_PASSWORD')

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
    
    async def test_connection(self):
        """Test database connection"""
        from sqlalchemy import text
        async with self.engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.fetchone()
    
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
"""Database configuration and session management"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from modules.account_management.infrastructure.models.user_account_orm import Base
from modules.account_management.infrastructure.models.registered_service_orm import RegisteredServiceORM

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig:
    """Database configuration"""
    
    def __init__(self):

        print('Environment variables:')
        print(f'DATABASE_URL: {os.getenv("DATABASE_URL")}')
        print(f'DB_HOST: {os.getenv("DB_HOST")}')
        print(f'DB_PORT: {os.getenv("DB_PORT")}')
        print(f'DB_NAME: {os.getenv("DB_NAME")}')
        print(f'DB_USER: {os.getenv("DB_USER")}')
        print(f'DB_PASSWORD: {os.getenv("DB_PASSWORD")}')
                # Get database URL from environment - prefer PostgreSQL
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            # Build from individual components
            db_host = os.getenv('DB_HOST')
            db_port = os.getenv('DB_PORT')
            db_name = os.getenv('DB_NAME')
            db_user = os.getenv('DB_USER')
            db_password = os.getenv('DB_PASSWORD')

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
        
        # Remove sslmode parameter as asyncpg doesn't support it in query string
        if '?sslmode=' in self.database_url:
            self.database_url = self.database_url.split('?sslmode=')[0]
        
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
    
    async def test_connection(self):
        """Test database connection"""
        from sqlalchemy import text
        async with self.engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.fetchone()
    
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