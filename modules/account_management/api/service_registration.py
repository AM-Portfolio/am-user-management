from fastapi import APIRouter, HTTPException, Header, Depends, status
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict
import secrets
import hashlib
import re
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared_infra.database.config import db_config
from modules.account_management.infrastructure.models.registered_service_orm import RegisteredServiceORM

router = APIRouter(prefix="/api/v1/service", tags=["Service Registration"])

VALID_SCOPES = ["profile:read", "data:read", "data:write", "admin:full"]


async def get_db():
    """Get database session dependency"""
    async for session in db_config.get_session():
        yield session


class ServiceRegistrationRequest(BaseModel):
    service_name: str = Field(..., min_length=1, max_length=50)
    service_id: str = Field(..., min_length=3, max_length=64)
    primary_contact_name: str = Field(..., min_length=1, max_length=100)
    admin_email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=20)
    secondary_email: Optional[EmailStr] = None
    scopes: List[str]
    scope_justifications: Dict[str, str]
    
    @validator('service_id')
    def validate_service_id(cls, v):
        if not re.match(r'^[a-z0-9_-]{3,64}$', v):
            raise ValueError('service_id must match pattern: ^[a-z0-9_-]{3,64}$')
        return v
    
    @validator('scopes')
    def validate_scopes(cls, v):
        if not v:
            raise ValueError('At least one scope must be requested')
        invalid_scopes = [s for s in v if s not in VALID_SCOPES]
        if invalid_scopes:
            raise ValueError(f'Invalid scopes: {invalid_scopes}. Valid scopes: {VALID_SCOPES}')
        return v
    
    @validator('scope_justifications')
    def validate_justifications(cls, v, values):
        if 'scopes' in values:
            for scope in values['scopes']:
                if scope not in v or not v[scope].strip():
                    raise ValueError(f'Justification required for scope: {scope}')
        return v


class ServiceRegistrationResponse(BaseModel):
    service_id: str
    consumer_key: str
    consumer_secret: str
    scopes: List[str]
    message: str


class ServiceUpdateRequest(BaseModel):
    primary_contact_name: Optional[str] = Field(None, min_length=1, max_length=100)
    admin_email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    secondary_email: Optional[EmailStr] = None
    allowed_ips: Optional[List[str]] = None


class ServiceStatusResponse(BaseModel):
    service_id: str
    service_name: str
    is_active: bool
    scopes: List[str]
    created_at: datetime
    last_access_at: Optional[datetime]


class ServiceValidationRequest(BaseModel):
    consumer_key: str
    consumer_secret: str


class ServiceValidationResponse(BaseModel):
    valid: bool
    service_id: Optional[str] = None
    scopes: Optional[List[str]] = None
    message: Optional[str] = None


def generate_consumer_key() -> str:
    """Generate a secure consumer key"""
    return f"ck_{secrets.token_urlsafe(32)}"


def hash_secret(secret: str) -> str:
    """Hash consumer secret using SHA-256"""
    return hashlib.sha256(secret.encode()).hexdigest()


def generate_consumer_secret() -> str:
    """Generate a secure consumer secret"""
    return f"cs_{secrets.token_urlsafe(48)}"


@router.post("/register", response_model=ServiceRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_service(
    request: ServiceRegistrationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new OAuth 2.0 service/application.
    Returns consumer_key and consumer_secret (store securely - shown only once).
    """
    result = await db.execute(
        select(RegisteredServiceORM).where(RegisteredServiceORM.service_id == request.service_id)
    )
    existing_service = result.scalar_one_or_none()
    
    if existing_service:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Service ID '{request.service_id}' already registered"
        )
    
    consumer_key = generate_consumer_key()
    consumer_secret = generate_consumer_secret()
    consumer_secret_hash = hash_secret(consumer_secret)
    
    import json
    justifications_json = json.dumps(request.scope_justifications)
    
    new_service = RegisteredServiceORM(
        service_id=request.service_id,
        service_name=request.service_name,
        consumer_key=consumer_key,
        consumer_secret_hash=consumer_secret_hash,
        primary_contact_name=request.primary_contact_name,
        admin_email=request.admin_email,
        phone_number=request.phone_number,
        secondary_email=request.secondary_email,
        scopes=request.scopes,
        scope_justifications=justifications_json,
        is_active=True
    )
    
    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)
    
    return ServiceRegistrationResponse(
        service_id=new_service.service_id,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        scopes=new_service.scopes,
        message="Service registered successfully. Store consumer_secret securely - it won't be shown again."
    )


@router.put("/{service_id}/update", response_model=dict)
async def update_service(
    service_id: str,
    request: ServiceUpdateRequest,
    x_consumer_key: str = Header(..., alias="X-Consumer-Key"),
    x_consumer_secret: str = Header(..., alias="X-Consumer-Secret"),
    db: AsyncSession = Depends(get_db)
):
    """
    Update non-immutable service fields.
    Requires consumer_key and consumer_secret in headers.
    """
    result = await db.execute(
        select(RegisteredServiceORM).where(RegisteredServiceORM.service_id == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    if service.consumer_key != x_consumer_key or hash_secret(x_consumer_secret) != service.consumer_secret_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if request.primary_contact_name:
        service.primary_contact_name = request.primary_contact_name
    if request.admin_email:
        service.admin_email = request.admin_email
    if request.phone_number is not None:
        service.phone_number = request.phone_number
    if request.secondary_email is not None:
        service.secondary_email = request.secondary_email
    if request.allowed_ips is not None:
        service.allowed_ips = request.allowed_ips
    
    service.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(service)
    
    return {"message": "Service updated successfully", "service_id": service.service_id}


@router.get("/{service_id}/status", response_model=ServiceStatusResponse)
async def get_service_status(
    service_id: str,
    x_consumer_key: str = Header(..., alias="X-Consumer-Key"),
    x_consumer_secret: str = Header(..., alias="X-Consumer-Secret"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get service registration status and active scopes.
    Requires consumer_key and consumer_secret in headers.
    """
    result = await db.execute(
        select(RegisteredServiceORM).where(RegisteredServiceORM.service_id == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    if service.consumer_key != x_consumer_key or hash_secret(x_consumer_secret) != service.consumer_secret_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return ServiceStatusResponse(
        service_id=service.service_id,
        service_name=service.service_name,
        is_active=service.is_active,
        scopes=service.scopes,
        created_at=service.created_at,
        last_access_at=service.last_access_at
    )


@router.post("/validate-credentials", response_model=ServiceValidationResponse)
async def validate_service_credentials(
    request: ServiceValidationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Validate service consumer_key and consumer_secret.
    Used by other services to verify service identity.
    """
    result = await db.execute(
        select(RegisteredServiceORM).where(RegisteredServiceORM.consumer_key == request.consumer_key)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        return ServiceValidationResponse(
            valid=False,
            message="Invalid consumer_key"
        )
    
    if hash_secret(request.consumer_secret) != service.consumer_secret_hash:
        return ServiceValidationResponse(
            valid=False,
            message="Invalid consumer_secret"
        )
    
    if not service.is_active:
        return ServiceValidationResponse(
            valid=False,
            message="Service is inactive"
        )
    
    service.last_access_at = datetime.now(timezone.utc)
    await db.commit()
    
    return ServiceValidationResponse(
        valid=True,
        service_id=service.service_id,
        scopes=service.scopes,
        message="Service validated successfully"
    )
