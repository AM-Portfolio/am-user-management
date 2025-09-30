"""Email not verified domain exception"""


class EmailNotVerifiedError(Exception):
    """Raised when user attempts action requiring verified email"""
    
    def __init__(self, email: str, message: str = None):
        self.email = email
        self.message = message or f"Email '{email}' is not verified"
        super().__init__(self.message)


class VerificationTokenExpiredError(Exception):
    """Raised when email verification token has expired"""
    
    def __init__(self, message: str = "Email verification token has expired"):
        super().__init__(message)


class VerificationTokenInvalidError(Exception):
    """Raised when email verification token is invalid"""
    
    def __init__(self, message: str = "Invalid email verification token"):
        super().__init__(message)