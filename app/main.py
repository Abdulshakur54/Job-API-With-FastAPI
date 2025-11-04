from fastapi import FastAPI
from contextlib import asynccontextmanager
from .dependencies.db import create_db_and_tables
from app.routers import user_router, job_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(user_router.router, prefix="/user", tags=["user"])
app.include_router(job_router.router, prefix="/jobs", tags=["jobs"])
