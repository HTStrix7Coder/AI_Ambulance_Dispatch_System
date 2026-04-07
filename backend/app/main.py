from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
import asyncio
from sqlalchemy import text
from .routers import triage, medicalchat, maps, vapi, admin
from .database import Base, engine, SessionLocal

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(title="AI Medical Dispatch")

# Request logging middleware - only log errors
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            # Only log slow requests (>1s) or errors
            if process_time > 1.0:
                logger.warning(f"⚠️ Slow request: {request.method} {request.url.path} - {process_time:.3f}s")
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"❌ Error: {request.method} {request.url.path} - {str(e)} - {process_time:.3f}s")
            raise

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# --- CORS Configuration ---
origins = [
    "http://localhost:3000",   # React development server (create-react-app default)
    "http://localhost:3001",   # Alternative React port
    "http://localhost:5173",   # Vite default port
    "http://localhost:5174",   # Alternative Vite port
    "http://localhost:8080",   # Common development port
    "http://127.0.0.1:3000",   # Alternative localhost notation
    "http://127.0.0.1:5173",   # Alternative localhost notation
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for VAPI webhooks (ngrok URLs are dynamic)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    # Explicitly expose the custom header to the frontend
    expose_headers=["X-LLM-Response-Text"]
)

# Create DB tables
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(triage.router)
app.include_router(medicalchat.router)
app.include_router(maps.router, prefix="/maps", tags=["maps"])
app.include_router(vapi.router, tags=["vapi"])
app.include_router(admin.router)   

# --- Background task: auto-complete old pending cases ---

async def _auto_complete_old_cases_loop():
    """Periodically mark Pending/Assigned cases older than 10 minutes as Completed."""
    while True:
        try:
            # Run every 60 seconds
            await asyncio.sleep(60)
            db = SessionLocal()
            try:
                # Use raw SQL to avoid ORM issues if column not yet migrated
                # Update cases to Completed and corresponding patients to Admitted
                db.execute(text(
                    """
                    UPDATE cases c
                    INNER JOIN patients p ON c.patient_id = p.id
                    SET c.status = 'Completed',
                        p.patient_status = 'Admitted'
                    WHERE c.status IN ('Pending', 'Assigned')
                      AND c.created_at IS NOT NULL
                      AND c.created_at < (NOW() - INTERVAL 10 MINUTE)
                    """
                ))
                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Auto-complete job failed: {e}")


@app.on_event("startup")
async def startup_tasks():
    # Ensure DB schema is compatible (add created_at if missing)
    try:
        db = SessionLocal()
        try:
            db.execute(text(
                """
                CREATE TABLE IF NOT EXISTS __dummy__(id INT PRIMARY KEY) -- no-op to ensure connection
                """
            ))
            # Conditionally add created_at column if it's missing
            result = db.execute(text(
                """
                SELECT COUNT(*) AS cnt
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'cases'
                  AND COLUMN_NAME = 'created_at'
                """
            ))
            cnt = list(result)[0][0]
            if cnt == 0:
                db.execute(text(
                    """
                    ALTER TABLE cases
                    ADD COLUMN created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
                    """
                ))
                db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Schema check failed: {e}")

    # Fire-and-forget background loop
    asyncio.create_task(_auto_complete_old_cases_loop())