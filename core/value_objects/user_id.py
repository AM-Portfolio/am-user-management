"""User ID value object - Immutable UUID wrapper"""
from uuid import UUID, uuid4
from typing import Union


class UserId:
    """Immutable user identifier using UUID"""
    
    def __init__(self, value: Union[str, UUID]) -> None:
        if isinstance(value, str):
            self._value = UUID(value)
        elif isinstance(value, UUID):
            self._value = value
        else:
            raise TypeError("UserId must be initialized with str or UUID")
    
    @classmethod
    def generate(cls) -> "UserId":
        """Generate a new unique user ID"""
        return cls(uuid4())
    
    @property
    def value(self) -> UUID:
        """Get the UUID value"""
        return self._value
    
    def __str__(self) -> str:
        return str(self._value)
    
    def __repr__(self) -> str:
        return f"UserId('{self._value}')"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UserId):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)