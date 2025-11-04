from uuid import UUID
from app.dependencies.db import get_session
from app.models.job_model import Job
from fastapi import APIRouter, Depends
from app.dependencies import job_dependency
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/", response_model=Job)
async def create_job(add_job: Job = Depends(job_dependency.create_job)):
    return add_job


@router.patch("/{job_id}", response_model=Job)
async def update_job(job_update: Job = Depends(job_dependency.update_job)):
    return job_update


@router.delete("/{job_id}", response_model=Job)
async def delete_job(job_delete: Job = Depends(job_dependency.delete_job)):
    return job_delete


@router.get("/", response_model=list[Job])
async def get_jobs(read_jobs: list[Job] = Depends(job_dependency.get_jobs)):
    return read_jobs


@router.get("/user", response_model=list[Job])
async def get_user_jobs(read_jobs: list[Job] = Depends(job_dependency.get_user_jobs)):
    return read_jobs


@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: UUID, session: AsyncSession = Depends(get_session)):
    return job_dependency.get_job(session, job_id)
