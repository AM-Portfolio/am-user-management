"""Email value object - Validated email address"""
import re
from typing import Union


class Email:
    """Validated email address value object"""
    
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Email must be a string")
        
        value = value.strip().lower()
        if not value:
            raise ValueError("Email cannot be empty")
        
        if not self.EMAIL_REGEX.match(value):
            raise ValueError(f"Invalid email format: {value}")
        
        self._value = value
    
    @property
    def value(self) -> str:
        """Get the email address"""
        return self._value
    
    @property
    def domain(self) -> str:
        """Get the domain part of the email"""
        return self._value.split('@')[1]
    
    @property
    def local_part(self) -> str:
        """Get the local part of the email"""
        return self._value.split('@')[0]
    
    def __str__(self) -> str:
        return self._value
    
    def __repr__(self) -> str:
        return f"Email('{self._value}')"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Email):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)