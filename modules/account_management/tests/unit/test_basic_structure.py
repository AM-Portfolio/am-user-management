"""Test basic structure and imports"""
import pytest
from core.value_objects.user_id import UserId
from core.value_objects.email import Email
from core.value_objects.phone_number import PhoneNumber


def test_user_id_creation():
    """Test UserId value object creation"""
    user_id = UserId.generate()
    assert user_id is not None
    assert str(user_id) is not None


def test_email_validation():
    """Test Email value object validation"""
    # Valid email
    email = Email("test@example.com")
    assert str(email) == "test@example.com"
    
    # Invalid email should raise error
    with pytest.raises(ValueError):
        Email("invalid-email")


def test_phone_number_formatting():
    """Test PhoneNumber value object formatting"""
    # US number
    phone = PhoneNumber("+1234567890")
    assert str(phone) == "+1234567890"
    
    # Auto-format US number
    phone2 = PhoneNumber("2345678901")
    assert str(phone2) == "+12345678901"


if __name__ == "__main__":
    test_user_id_creation()
    test_email_validation() 
    test_phone_number_formatting()
    print("All basic tests passed!")