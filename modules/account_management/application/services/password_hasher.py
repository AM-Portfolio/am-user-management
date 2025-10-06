"""Password hashing service - Argon2/bcrypt wrapper"""
import secrets
from abc import ABC, abstractmethod
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, HashingError


class PasswordHasherInterface(ABC):
    """Abstract password hasher interface"""
    
    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        pass
    
    @abstractmethod
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        pass


class Argon2PasswordHasher(PasswordHasherInterface):
    """Argon2 password hasher implementation"""
    
    def __init__(self):
        self._hasher = PasswordHasher(
            time_cost=3,       # Number of iterations
            memory_cost=65536, # Memory usage in KiB (64MB)
            parallelism=1,     # Number of parallel threads
            hash_len=32,       # Hash length
            salt_len=16        # Salt length
        )
    
    def hash_password(self, password: str) -> str:
        """Hash a password using Argon2"""
        if not password:
            raise ValueError("Password cannot be empty")
        
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        try:
            return self._hasher.hash(password)
        except HashingError as e:
            raise ValueError(f"Failed to hash password: {str(e)}")
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its Argon2 hash"""
        if not password or not hashed_password:
            return False
        
        try:
            self._hasher.verify(hashed_password, password)
            return True
        except VerifyMismatchError:
            return False
        except Exception:
            return False
    
    def needs_rehash(self, hashed_password: str) -> bool:
        """Check if password hash needs to be updated"""
        try:
            return self._hasher.check_needs_rehash(hashed_password)
        except Exception:
            return True


class PasswordGenerator:
    """Secure password generator"""
    
    @staticmethod
    def generate_password(length: int = 16) -> str:
        """Generate a secure random password"""
        if length < 8:
            raise ValueError("Password length must be at least 8 characters")
        
        # Define character sets
        lowercase = 'abcdefghijklmnopqrstuvwxyz'
        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        digits = '0123456789'
        special = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        
        # Ensure at least one character from each set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]
        
        # Fill the rest with random characters from all sets
        all_chars = lowercase + uppercase + digits + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(length)