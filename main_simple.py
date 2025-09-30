"""Simple FastAPI application for testing"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="AM User Management API",
    description="User management system with modular architecture",
    version="0.1.0",
    debug=True,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "AM User Management API",
        "status": "running",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Application is running successfully"
    }

# Simple auth endpoints placeholder
@app.get("/api/v1/auth/status")
async def auth_status():
    return {"status": "Account management module ready for implementation"}

@app.post("/api/v1/auth/register")
async def register_placeholder():
    return {"message": "User registration endpoint - coming soon"}

@app.post("/api/v1/auth/login")  
async def login_placeholder():
    return {"message": "User login endpoint - coming soon"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )