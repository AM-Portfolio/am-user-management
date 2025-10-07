"""Authentication router - POST /users, POST /login, POST /reset-password"""
from typing import Annotated
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from shared_infra.config.feature_flags import require_module
from .schemas import (
    CreateUserRequest, CreateUserResponse, 
    LoginRequest, LoginResponse,
    PasswordResetRequest, PasswordResetResponse
)
from ...application.use_cases.create_user import CreateUserUseCase
from ...application.use_cases.login import LoginUseCase
from ...application.use_cases.reset_password import ResetPasswordUseCase
from ...domain.exceptions.user_already_exists import EmailAlreadyExistsError
from ...domain.exceptions.invalid_credentials import InvalidCredentialsError
from ...domain.exceptions.email_not_verified import EmailNotVerifiedError


router = APIRouter()


@router.post(
    "/register", 
    response_model=CreateUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password"
)
@require_module("account_management")
async def register_user(
    request: CreateUserRequest,
    create_user_use_case: Annotated[CreateUserUseCase, Depends()]
) -> CreateUserResponse:
    """Register a new user"""
    try:
        result = await create_user_use_case.execute(request.to_use_case_request())
        return CreateUserResponse.from_use_case_response(result)
        
    except EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": str(e),
                "type": "email_already_exists",
                "field": "email"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": str(e),
                "type": "validation_error"
            }
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User login",
    description="Authenticate user with email and password"
)
@require_module("account_management")
async def login_user(
    request: LoginRequest,
    login_use_case: Annotated[LoginUseCase, Depends()]
) -> LoginResponse:
    """Authenticate user login"""
    try:
        result = await login_use_case.execute(request.to_use_case_request())
        print(f"[AUTH_ROUTER] Use case result has access_token: {hasattr(result, 'access_token')} value: {getattr(result, 'access_token', 'MISSING')[:50] if hasattr(result, 'access_token') else 'N/A'}")
        response = LoginResponse.from_use_case_response(result)
        print(f"[AUTH_ROUTER] Pydantic response model_dump: {response.model_dump()}")
        return response
        
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    except EmailNotVerifiedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": str(e),
                "type": "email_not_verified",
                "requires_verification": True
            }
        )
    except Exception as e:
        logging.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


@router.post(
    "/password-reset",
    response_model=PasswordResetResponse,
    summary="Request password reset",
    description="Send password reset email to user"
)
@require_module("account_management")
async def request_password_reset(
    request: PasswordResetRequest,
    reset_password_use_case: Annotated[ResetPasswordUseCase, Depends()]
) -> PasswordResetResponse:
    """Request password reset"""
    try:
        result = await reset_password_use_case.execute(request.to_use_case_request())
        return PasswordResetResponse.from_use_case_response(result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": str(e),
                "type": "validation_error"
            }
        )


@router.post(
    "/verify-email",
    summary="Verify email address",
    description="Verify user email with verification token"
)
@require_module("account_management")
async def verify_email(token: str):
    """Verify user email"""
    # TODO: Implement email verification use case
    return {"message": "Email verification not implemented yet"}


@router.post(
    "/logout",
    summary="User logout",
    description="Logout user and invalidate session"
)
@require_module("account_management")
async def logout_user():
    """Logout user"""
    # TODO: Implement logout use case
    return {"message": "Logout successful"}