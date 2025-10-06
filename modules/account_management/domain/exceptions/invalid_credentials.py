"""Invalid credentials domain exception"""


class InvalidCredentialsError(Exception):
    """Raised when authentication credentials are invalid"""
    
    def __init__(self, message: str = "Invalid credentials provided"):
        self.message = message
        super().__init__(self.message)


class InvalidPasswordError(InvalidCredentialsError):
    """Raised when password is incorrect"""
    
    def __init__(self, message: str = "Invalid password"):
        super().__init__(message)


class InvalidEmailError(InvalidCredentialsError):
    """Raised when email is not found or invalid"""
    
    def __init__(self, email: str):
        super().__init__(f"Invalid email: {email}")


class AccountLockedError(InvalidCredentialsError):
    """Raised when account is locked due to too many failed attempts"""
    
    def __init__(self, message: str = "Account is temporarily locked"):
        super().__init__(message)