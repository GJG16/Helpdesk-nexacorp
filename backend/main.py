from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from loguru import logger

from backend.config.settings import settings
from backend.database import connect_db, close_db, get_database
from backend.routes import status_router
from backend.routes.auth import router as auth_router
from backend.routes.usuarios import router as usuarios_router
from backend.routes.tickets import router as tickets_router
from backend.routes.reports import router as reports_router
from backend.routes.kb import router as kb_router


# Configurar Logging Estructurado
logger.add("backend/logs/app.log", rotation="500 MB", retention="10 days", level="INFO")

# Lifecycle events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Iniciando conexión a base de datos...")
    await connect_db()
    logger.info("Aplicación iniciada correctamente")
    yield
    # Shutdown
    logger.info("Cerrando conexión a base de datos...")
    await close_db()
    logger.info("Aplicación detenida")

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan
)

# Añadir Rate Limiter al app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Error: {request.method} {request.url} - {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor. Por favor, intente más tarde."},
    )

from fastapi.staticfiles import StaticFiles

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")

# Registrar rutas
app.include_router(status_router)
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(tickets_router)
app.include_router(reports_router)
app.include_router(kb_router)
from backend.routes.macros import router as macros_router
app.include_router(macros_router)

# Ruta raíz
@app.get("/")
@limiter.limit("5/minute")
async def root(request: Request):
    return {
        "message": "Bienvenido a Helpdesk API",
        "docs": "/docs",
        "version": settings.app_version
    }

from fastapi import WebSocket, WebSocketDisconnect
from backend.security import decode_token
from backend.websockets import manager

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    user = decode_token(token)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    user_id = user.get("id")
    await manager.connect(websocket, user_id)
    try:
        while True:
            # We don't expect messages from client, but we keep connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
           "backend.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug
    )
