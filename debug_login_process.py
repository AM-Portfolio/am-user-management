#!/usr/bin/env python3
"""Debug login process step by step"""
import asyncio
import os
import logging
from pathlib import Path

# Add the project root to Python path
import sys
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from shared_infra.database.config import db_config
from modules.account_management.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from modules.account_management.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from modules.account_management.application.use_cases.login import LoginUseCase, LoginRequest
from shared_infra.events.mock_event_bus import MockEventBus

async def test_login():
    """Test the login process step by step"""
    
    # Setup database
    await db_config.create_tables()
    
    # Create dependencies
    password_hasher = BcryptPasswordHasher()
    event_bus = MockEventBus()
    
    # Create repository with actual session
    async for session in db_config.get_session():
        user_repository = SQLAlchemyUserRepository(session)
        
        # Test login use case
        login_use_case = LoginUseCase(
            user_repository=user_repository,
            password_hasher=password_hasher,
            event_bus=event_bus,
            require_email_verification=False  # Disable for testing
        )
        
        # Test login request
        login_request = LoginRequest(
            email="login_test@example.com",
            password="logintest123"
        )
        
        try:
            print(f"Testing login for: {login_request.email}")
            result = await login_use_case.execute(login_request)
            print(f"Login successful: {result}")
        except Exception as e:
            print(f"Login failed: {str(e)}")
            import traceback
            traceback.print_exc()
        break  # Only use the first session

if __name__ == "__main__":
    asyncio.run(test_login())