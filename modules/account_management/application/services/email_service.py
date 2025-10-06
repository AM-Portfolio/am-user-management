"""Email service - Sends verification/reset emails"""
import smtplib
from abc import ABC, abstractmethod
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dataclasses import dataclass

from core.value_objects.email import Email


@dataclass
class EmailMessage:
    """Email message data class"""
    to: Email
    subject: str
    text_content: str
    html_content: Optional[str] = None
    from_email: Optional[str] = None


class EmailServiceInterface(ABC):
    """Abstract email service interface"""
    
    @abstractmethod
    async def send_email(self, message: EmailMessage) -> bool:
        """Send an email message"""
        pass
    
    @abstractmethod
    async def send_verification_email(self, to: Email, token: str) -> bool:
        """Send email verification message"""
        pass
    
    @abstractmethod
    async def send_password_reset_email(self, to: Email, token: str) -> bool:
        """Send password reset message"""
        pass


class SMTPEmailService(EmailServiceInterface):
    """SMTP email service implementation"""
    
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        from_email: str = None
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.from_email = from_email or username
    
    async def send_email(self, message: EmailMessage) -> bool:
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = message.from_email or self.from_email
            msg['To'] = str(message.to)
            
            # Add text content
            text_part = MIMEText(message.text_content, 'plain')
            msg.attach(text_part)
            
            # Add HTML content if provided
            if message.html_content:
                html_part = MIMEText(message.html_content, 'html')
                msg.attach(html_part)
            
            # Send the message
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    async def send_verification_email(self, to: Email, token: str) -> bool:
        """Send email verification message"""
        verification_url = f"https://yourdomain.com/verify-email?token={token}"
        
        text_content = f"""
        Welcome to AM User Management!
        
        Please verify your email address by clicking the link below:
        {verification_url}
        
        If you didn't create this account, you can safely ignore this email.
        
        This link will expire in 24 hours.
        
        Best regards,
        AM User Management Team
        """
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Verify Your Email</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                <h2 style="color: #333;">Welcome to AM User Management!</h2>
                <p>Please verify your email address by clicking the button below:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background-color: #007bff; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 4px; display: inline-block;">
                        Verify Email Address
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">
                    If you didn't create this account, you can safely ignore this email.<br>
                    This link will expire in 24 hours.
                </p>
                <hr style="border: 1px solid #eee; margin: 20px 0;">
                <p style="color: #999; font-size: 12px;">
                    Best regards,<br>
                    AM User Management Team
                </p>
            </div>
        </body>
        </html>
        """
        
        message = EmailMessage(
            to=to,
            subject="Verify Your Email Address",
            text_content=text_content,
            html_content=html_content
        )
        
        return await self.send_email(message)
    
    async def send_password_reset_email(self, to: Email, token: str) -> bool:
        """Send password reset message"""
        reset_url = f"https://yourdomain.com/reset-password?token={token}"
        
        text_content = f"""
        Password Reset Request
        
        You have requested to reset your password for your AM User Management account.
        
        Click the link below to reset your password:
        {reset_url}
        
        If you didn't request this password reset, you can safely ignore this email.
        
        This link will expire in 1 hour for security reasons.
        
        Best regards,
        AM User Management Team
        """
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset Request</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                <h2 style="color: #333;">Password Reset Request</h2>
                <p>You have requested to reset your password for your AM User Management account.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #dc3545; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 4px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">
                    If you didn't request this password reset, you can safely ignore this email.<br>
                    This link will expire in 1 hour for security reasons.
                </p>
                <hr style="border: 1px solid #eee; margin: 20px 0;">
                <p style="color: #999; font-size: 12px;">
                    Best regards,<br>
                    AM User Management Team
                </p>
            </div>
        </body>
        </html>
        """
        
        message = EmailMessage(
            to=to,
            subject="Password Reset Request",
            text_content=text_content,
            html_content=html_content
        )
        
        return await self.send_email(message)


class MockEmailService(EmailServiceInterface):
    """Mock email service for testing"""
    
    def __init__(self):
        self.sent_emails = []
    
    async def send_email(self, message: EmailMessage) -> bool:
        """Mock send email - just store the message"""
        self.sent_emails.append(message)
        print(f"Mock email sent to {message.to}: {message.subject}")
        return True
    
    async def send_verification_email(self, to: Email, token: str) -> bool:
        """Mock send verification email"""
        message = EmailMessage(
            to=to,
            subject="Verify Your Email Address",
            text_content=f"Verification token: {token}"
        )
        return await self.send_email(message)
    
    async def send_password_reset_email(self, to: Email, token: str) -> bool:
        """Mock send password reset email"""
        message = EmailMessage(
            to=to,
            subject="Password Reset Request",
            text_content=f"Password reset token: {token}"
        )
        return await self.send_email(message)