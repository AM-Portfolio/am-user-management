"""Mock email service for development"""
from typing import Optional
from core.value_objects.email import Email
from ...application.services.email_service import EmailServiceInterface, EmailMessage


class MockEmailService(EmailServiceInterface):
    """Mock email service for development and testing"""
    
    def __init__(self):
        self.sent_emails = []
    
    async def send_email(self, message: EmailMessage) -> bool:
        """Mock sending generic email"""
        email_data = {
            "to": str(message.to),
            "subject": message.subject,
            "text_content": message.text_content,
            "html_content": message.html_content,
            "from_email": message.from_email,
            "type": "generic"
        }
        self.sent_emails.append(email_data)
        print(f"[MOCK EMAIL] Email sent to {message.to}: {message.subject}")
        return True
    
    async def send_verification_email(self, to: Email, token: str) -> bool:
        """Mock sending verification email"""
        message = EmailMessage(
            to=to,
            subject="Verify your email address",
            text_content=f"Verification token: {token}",
            html_content=f"<p>Verification token: <strong>{token}</strong></p>"
        )
        email_data = {
            "to": str(to),
            "subject": "Verify your email address",
            "token": token,
            "type": "verification"
        }
        self.sent_emails.append(email_data)
        print(f"[MOCK EMAIL] Verification email sent to {to} with token: {token}")
        return True
    
    async def send_password_reset_email(self, to: Email, token: str) -> bool:
        """Mock sending password reset email"""
        message = EmailMessage(
            to=to,
            subject="Reset your password",
            text_content=f"Password reset token: {token}",
            html_content=f"<p>Password reset token: <strong>{token}</strong></p>"
        )
        email_data = {
            "to": str(to),
            "subject": "Reset your password",
            "token": token,
            "type": "password_reset"
        }
        self.sent_emails.append(email_data)
        print(f"[MOCK EMAIL] Password reset email sent to {to} with token: {token}")
        return True
    
    async def send_welcome_email(self, to: Email, name: Optional[str] = None) -> bool:
        """Mock sending welcome email"""
        email_data = {
            "to": str(to),
            "subject": "Welcome to AM User Management!",
            "name": name,
            "type": "welcome"
        }
        self.sent_emails.append(email_data)
        print(f"[MOCK EMAIL] Welcome email sent to {to}")
        return True
    
    def get_sent_emails(self):
        """Get all sent emails (for testing)"""
        return self.sent_emails.copy()
    
    def clear_sent_emails(self):
        """Clear sent emails (for testing)"""
        self.sent_emails.clear()