import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ARRAY, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as GUID
from shared_infra.database.base import Base


class RegisteredServiceORM(Base):
    """SQLAlchemy ORM model for registered OAuth 2.0 services/applications"""
    
    __tablename__ = "registered_services"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    service_id = Column(String(64), unique=True, nullable=False, index=True)
    service_name = Column(String(50), nullable=False)
    
    consumer_key = Column(String(64), unique=True, nullable=False, index=True)
    consumer_secret_hash = Column(String(255), nullable=False)
    
    primary_contact_name = Column(String(100), nullable=False)
    admin_email = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    secondary_email = Column(String(255), nullable=True)
    
    scopes = Column(ARRAY(String), nullable=False)
    scope_justifications = Column(Text, nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    allowed_ips = Column(ARRAY(String), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_access_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<RegisteredServiceORM(service_id={self.service_id}, service_name={self.service_name}, is_active={self.is_active})>"
