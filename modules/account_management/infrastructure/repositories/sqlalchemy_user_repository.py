"""SQLAlchemy implementation of UserRepository"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from core.interfaces.repository import UserRepository
from core.value_objects.user_id import UserId
from ..models.user_account_orm import UserAccountORM
from ...domain.models.user_account import UserAccount
from ...domain.exceptions.user_already_exists import EmailAlreadyExistsError, PhoneAlreadyExistsError


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of user repository"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, user_account: UserAccount) -> UserAccount:
        """Save user account to database"""
        try:
            # Check if this is an update (user already exists)
            existing = await self._session.get(UserAccountORM, user_account.id.value)
            
            if existing:
                # Update existing record
                existing.email = str(user_account.email)
                existing.password_hash = user_account.password_hash
                existing.status = user_account.status
                existing.phone_number = str(user_account.phone_number) if user_account.phone_number else None
                existing.updated_at = user_account.updated_at
                existing.verified_at = user_account.verified_at
                existing.last_login_at = user_account.last_login_at
                existing.failed_login_attempts = user_account.failed_login_attempts
                existing.locked_until = user_account.locked_until
                
                await self._session.commit()
                await self._session.refresh(existing)
                return existing.to_domain()
            else:
                # Create new record
                orm_user = UserAccountORM.from_domain(user_account)
                self._session.add(orm_user)
                await self._session.commit()
                await self._session.refresh(orm_user)
                return orm_user.to_domain()
                
        except IntegrityError as e:
            await self._session.rollback()
            if "email" in str(e).lower():
                raise EmailAlreadyExistsError(str(user_account.email))
            elif "phone" in str(e).lower():
                raise PhoneAlreadyExistsError(str(user_account.phone_number) if user_account.phone_number else "")
            raise
        except Exception as e:
            await self._session.rollback()
            raise
    
    async def get_by_id(self, user_id: UserId) -> Optional[UserAccount]:
        """Get user by ID"""
        orm_user = await self._session.get(UserAccountORM, user_id.value)
        return orm_user.to_domain() if orm_user else None
    
    async def get_by_email(self, email: str) -> Optional[UserAccount]:
        """Get user by email"""
        stmt = select(UserAccountORM).where(UserAccountORM.email == email)
        result = await self._session.execute(stmt)
        orm_user = result.scalar_one_or_none()
        return orm_user.to_domain() if orm_user else None
    
    async def get_by_phone(self, phone_number: str) -> Optional[UserAccount]:
        """Get user by phone number"""
        stmt = select(UserAccountORM).where(UserAccountORM.phone_number == phone_number)
        result = await self._session.execute(stmt)
        orm_user = result.scalar_one_or_none()
        return orm_user.to_domain() if orm_user else None
    
    async def delete(self, user_id: UserId) -> bool:
        """Delete user by ID"""
        orm_user = await self._session.get(UserAccountORM, user_id.value)
        if orm_user:
            await self._session.delete(orm_user)
            await self._session.commit()
            return True
        return False
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[UserAccount]:
        """Get all users with pagination"""
        stmt = select(UserAccountORM).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        orm_users = result.scalars().all()
        return [orm_user.to_domain() for orm_user in orm_users]
    
    async def exists(self, user_id: UserId) -> bool:
        """Check if user exists by ID"""
        orm_user = await self._session.get(UserAccountORM, user_id.value)
        return orm_user is not None
    
    async def list_active_users(self, limit: int = 100, offset: int = 0) -> List[UserAccount]:
        """List active users with pagination"""
        from ...domain.enums.user_status import UserStatus
        stmt = select(UserAccountORM).where(
            UserAccountORM.status == UserStatus.ACTIVE
        ).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        orm_users = result.scalars().all()
        return [orm_user.to_domain() for orm_user in orm_users]
    
    async def count(self) -> int:
        """Count total users"""
        from sqlalchemy import func
        stmt = select(func.count(UserAccountORM.id))
        result = await self._session.execute(stmt)
        return result.scalar()