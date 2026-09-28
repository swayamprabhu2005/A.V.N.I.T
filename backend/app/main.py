import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import CORS_ORIGINS
from .database import init_db
from .seed_data import seed_demo_database
from .api.routes import router as api_router
from .api.websocket import ws_router

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[AVNIT] Initializing database and verifying demo scenarios...")
    init_db()
    seed_demo_database()

    # Generate synthetic demo videos if not already present
    from ..test_samples.generate_demo_assets import generate_all_scenarios
    from ..config import TEST_SAMPLES_DIR
    if not any(TEST_SAMPLES_DIR.glob("*.mp4")):
        try:
            generate_all_scenarios()
        except Exception as e:
            print(f"[AVNIT] Notice: Could not generate synthetic demo videos automatically: {e}")
    yield

app = FastAPI(
    title="A.V.N.I.T. API",
    description="AI-Based Vehicle Number Plate and Identity Tampering Detection System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pathlib import Path
from fastapi.staticfiles import StaticFiles

# Include Routers
app.include_router(api_router)
app.include_router(ws_router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Mount pre-built Vue frontend if dist exists
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    print(f"[A.V.N.I.T.] Serving Vue 3 frontend from: {FRONTEND_DIST}")
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "system": "A.V.N.I.T.",
            "description": "AI-Based Vehicle Number Plate and Identity Tampering Detection System",
            "status": "online",
            "docs_url": "/docs"
        }

