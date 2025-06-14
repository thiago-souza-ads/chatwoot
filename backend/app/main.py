from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings
# Optional: Add CORS middleware if frontend will be on a different domain
# from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Optional: Set all CORS enabled origins
# if settings.BACKEND_CORS_ORIGINS:
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

app.include_router(api_router, prefix=settings.API_V1_STR)

# Optional: Add a root endpoint for health check or basic info
@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

# Optional: Add initial database setup logic here or via a separate script/command
# from app.db import base
# from app.db.session import engine
# def init_db():
#     base.Base.metadata.create_all(bind=engine)
# init_db()

