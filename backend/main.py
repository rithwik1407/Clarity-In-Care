from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config.settings import API_TITLE, API_VERSION, API_DESCRIPTION
from database.models import init_db
from app.schemas import HealthResponse
from app.api import patients, predictions

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients.router)
app.include_router(predictions.router)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Try to import model to check if it's loadable
        from models.dr_model import DRDetectionModel
        model_loaded = True
    except:
        model_loaded = False
    
    return HealthResponse(
        status="ok",
        version=API_VERSION,
        model_loaded=model_loaded,
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Clarity in Care - DR Detection API",
        "version": API_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    from config.settings import HOST, PORT, DEBUG
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
    )
