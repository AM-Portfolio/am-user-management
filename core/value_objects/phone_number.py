"""Phone number value object - E.164 formatted"""
import re
from typing import Optional


class PhoneNumber:
    """E.164 formatted phone number value object"""
    
    # E.164 format: +[1-9][0-9]{1,14}
    E164_REGEX = re.compile(r'^\+[1-9]\d{1,14}$')
    
    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Phone number must be a string")
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', value.strip())
        
        if not cleaned:
            raise ValueError("Phone number cannot be empty")
        
        # Ensure it starts with +
        if not cleaned.startswith('+'):
            # Assume US number if no country code
            if len(cleaned) == 10:
                cleaned = '+1' + cleaned
            elif len(cleaned) == 11 and cleaned.startswith('1'):
                cleaned = '+' + cleaned
            else:
                raise ValueError("Phone number must include country code or be a valid US number")
        
        if not self.E164_REGEX.match(cleaned):
            raise ValueError(f"Invalid phone number format. Must be E.164 format: {cleaned}")
        
        self._value = cleaned
    
    @property
    def value(self) -> str:
        """Get the E.164 formatted phone number"""
        return self._value
    
    @property
    def country_code(self) -> str:
        """Extract country code from phone number"""
        # Simple extraction - in production, use a proper library
        if self._value.startswith('+1'):
            return '+1'
        elif self._value.startswith('+44'):
            return '+44'
        elif self._value.startswith('+91'):
            return '+91'
        else:
            # Extract first 1-3 digits after +
            match = re.match(r'^(\+\d{1,3})', self._value)
            return match.group(1) if match else '+1'
    
    @property
    def national_number(self) -> str:
        """Get the national number part"""
        country_code = self.country_code
        return self._value[len(country_code):]
    
    def formatted(self, style: str = 'international') -> str:
        """Format phone number for display"""
        if style == 'international':
            return self._value
        elif style == 'national' and self.country_code == '+1':
            number = self.national_number
            return f"({number[:3]}) {number[3:6]}-{number[6:]}"
        else:
            return self._value
    
    def __str__(self) -> str:
        return self._value
    
    def __repr__(self) -> str:
        return f"PhoneNumber('{self._value}')"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PhoneNumber):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)