"""Bcrypt password hasher implementation"""
import bcrypt
from ...application.services.password_hasher import PasswordHasherInterface


class BcryptPasswordHasher(PasswordHasherInterface):
    """Bcrypt implementation of password hasher"""
    
    def __init__(self, rounds: int = 12):
        """Initialize with bcrypt rounds (default 12 is secure)"""
        self.rounds = rounds
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False