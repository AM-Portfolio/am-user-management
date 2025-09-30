"""Main FastAPI application - App factory: mounts only enabled module routers"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting AM User Management API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Enabled modules: {feature_flags.get_enabled_modules()}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AM User Management API")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    # Setup logging
    setup_logging()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.title,
        description=settings.description,
        version=settings.version,
        debug=settings.debug,
        docs_url="/docs" if feature_flags.enable_swagger_docs else None,
        redoc_url="/redoc" if feature_flags.enable_swagger_docs else None,
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
    )
    
    # Add global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception handler caught: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "type": "internal_error"}
        )
    
    # Health check endpoint
    if feature_flags.enable_health_checks:
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "environment": settings.environment,
                "version": settings.version,
                "modules": feature_flags.get_enabled_modules()
            }
    
    # Mount module routers based on feature flags
    mount_routers(app)
    
    return app


def mount_routers(app: FastAPI) -> None:
    """Mount module routers based on enabled features"""
    
    # Account Management routes
    if feature_flags.enable_account_management:
        try:
            from modules.account_management.api.public.auth_router import router as auth_router
            app.include_router(
                auth_router,
                prefix="/api/v1/auth",
                tags=["Authentication"]
            )
            logger.info("Mounted account management routes")
        except ImportError as e:
            logger.warning(f"Could not import account management routes: {e}")
    
    # User Profile routes
    if feature_flags.enable_user_profile:
        try:
            from modules.user_profile.api.public.profile_router import router as profile_router
            app.include_router(
                profile_router,
                prefix="/api/v1/profile",
                tags=["User Profile"]
            )
            logger.info("Mounted user profile routes")
        except ImportError as e:
            logger.warning(f"Could not import user profile routes: {e}")
    
    # Subscription routes
    if feature_flags.enable_subscription:
        try:
            from modules.subscription.api.public.subscription_router import router as subscription_router
            app.include_router(
                subscription_router,
                prefix="/api/v1/subscription",
                tags=["Subscription"]
            )
            logger.info("Mounted subscription routes")
        except ImportError as e:
            logger.warning(f"Could not import subscription routes: {e}")
    
    # Permissions & Roles routes
    if feature_flags.enable_permissions_roles:
        try:
            from modules.permissions_roles.api.public.roles_router import router as roles_router
            app.include_router(
                roles_router,
                prefix="/api/v1/roles",
                tags=["Roles & Permissions"]
            )
            logger.info("Mounted permissions & roles routes")
        except ImportError as e:
            logger.warning(f"Could not import permissions & roles routes: {e}")


# Create the application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.logging.level.lower()
    )