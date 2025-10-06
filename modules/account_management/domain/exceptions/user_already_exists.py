"""User already exists domain exception"""


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user that already exists"""
    
    def __init__(self, identifier: str, message: str = None):
        self.identifier = identifier
        self.message = message or f"User already exists with identifier: {identifier}"
        super().__init__(self.message)


class EmailAlreadyExistsError(UserAlreadyExistsError):
    """Raised when email is already registered"""
    
    def __init__(self, email: str):
        super().__init__(
            identifier=email,
            message=f"User with email '{email}' already exists"
        )


class PhoneAlreadyExistsError(UserAlreadyExistsError):
    """Raised when phone number is already registered"""
    
    def __init__(self, phone: str):
        super().__init__(
            identifier=phone,
            message=f"User with phone '{phone}' already exists"
        )