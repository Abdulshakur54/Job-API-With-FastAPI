from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlmodel import select
from app.dependencies.db import get_session
from app.dependencies.user_dependency import get_username
from app.models.job_model import Job, JobBase, JobUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.models.user_model import User


async def get_job(session: AsyncSession, job_id: UUID) -> Job:
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


async def get_jobs(session: AsyncSession = Depends(get_session)) -> list[Job]:
    result = await session.execute(select(Job))
    jobs = result.scalars().all()  # convert Result to list of Job instances
    return jobs


async def get_user_jobs(
    username: str = Depends(get_username), session: AsyncSession = Depends(get_session)
) -> list[Job]:
    result = await session.execute(select(Job).where(Job.createdBy == username))
    jobs = result.scalars().all()  # convert Result to list of Job instances
    return jobs


async def create_job(
    username: Annotated[str, Depends(get_username)],
    job: JobBase,
    session: AsyncSession = Depends(get_session),
) -> Job:
    try:
        val_job = Job(company=job.company, position=job.position, createdBy=username)
        session.add(val_job)
        await session.commit()
        await session.refresh(val_job)
        return val_job
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}",
        )


async def update_job(
    username: Annotated[str, Depends(get_username)],
    job_id: UUID,
    job: JobUpdate,
    session: AsyncSession = Depends(get_session),
) -> Job:
    try:
        old_job = await get_job(session, job_id)
        if not old_job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Authorization check
        if old_job.createdBy != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to update this job",
            )

        job_data = job.model_dump(exclude_unset=True)
        old_job.sqlmodel_update(job_data)
        session.add(old_job)
        await session.commit()
        await session.refresh(old_job)
        return old_job

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job: {str(e)}",
        )


async def delete_job(
    username: Annotated[str, Depends(get_username)],
    job_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Job:
    try:
        old_job = await get_job(session, job_id)
        if not old_job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Authorization check
        if old_job.createdBy != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to delete this job",
            )

        await session.delete(old_job)
        await session.commit()
        return old_job

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job: {str(e)}",
        )
