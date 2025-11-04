from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.db import get_session
from app.models.job_model import Job, JobBase, JobUpdate
from app.dependencies import job_dependency

router = APIRouter(
    prefix="/jobs",
    responses={404: {"description": "Job not found"}},
)


@router.post(
    "/",
    response_model=Job,
    summary="Create a new job post",
    description="""
### 🧾 Create Job Post
Create a new job posting.  
Only authenticated users can create jobs.
    """,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Job created successfully"},
        400: {"description": "Bad request — invalid job data"},
        401: {"description": "Unauthorized — invalid or missing token"},
        500: {"description": "Internal server error — failed to create job"},
    },
    tags=["private"],
)
async def create_job(add_job: Job = Depends(job_dependency.create_job)):
    """
    Create a new job listing associated with the logged-in user.
    """
    return add_job


@router.patch(
    "/{job_id}",
    response_model=Job,
    summary="Update an existing job",
    description="""
### ✏️ Update Job
Update a job you have previously created.  
You can modify the company name, position, or status.
    """,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Job updated successfully"},
        400: {"description": "Bad request — invalid data"},
        401: {"description": "Unauthorized — invalid or missing token"},
        403: {"description": "Forbidden — you cannot update another user's job"},
        404: {"description": "Job not found"},
        500: {"description": "Internal server error — failed to update job"},
    },
    tags=["private"],
)
async def update_job(
    job_id: UUID,
    job_update: Job = Depends(job_dependency.update_job),
):
    """
    Update details of an existing job by its unique ID.
    """
    return job_update


@router.delete(
    "/{job_id}",
    response_model=Job,
    summary="Delete a job",
    description="""
### 🗑️ Delete Job
Remove a job that you created.  
Only the job owner can delete their job posting.
    """,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Job deleted successfully"},
        401: {"description": "Unauthorized — invalid or missing token"},
        403: {"description": "Forbidden — you cannot delete another user's job"},
        404: {"description": "Job not found"},
        500: {"description": "Internal server error — failed to delete job"},
    },
    tags=["private"],
)
async def delete_job(
    job_id: UUID,
    job_delete: Job = Depends(job_dependency.delete_job),
):
    """
    Delete a job posting by its ID if you are the owner.
    """
    return job_delete


@router.get(
    "/",
    response_model=list[Job],
    summary="Get all job listings",
    description="""
### 📋 Get All Jobs
Retrieve all available job postings.  
This endpoint is public and does not require authentication.
    """,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Jobs retrieved successfully"},
        500: {"description": "Internal server error — failed to load jobs"},
    },
    tags=["public"],
)
async def get_jobs(read_jobs: list[Job] = Depends(job_dependency.get_jobs)):
    """
    Get a list of all job postings in the system.
    """
    return read_jobs


@router.get(
    "/user",
    response_model=list[Job],
    summary="Get jobs created by the logged-in user",
    description="""
### 👤 My Jobs
Retrieve all jobs posted by the authenticated user.
    """,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User jobs retrieved successfully"},
        401: {"description": "Unauthorized — invalid or missing token"},
        500: {"description": "Internal server error — failed to load jobs"},
    },
    tags=["private"],
)
async def get_user_jobs(
    read_jobs: list[Job] = Depends(job_dependency.get_user_jobs),
):
    """
    Retrieve all job postings created by the authenticated user.
    """
    return read_jobs


@router.get(
    "/{job_id}",
    response_model=Job,
    summary="Get job details by ID",
    description="""
### 🔍 Get Job Details
Retrieve details of a specific job posting using its unique ID.
    """,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Job details retrieved successfully"},
        404: {"description": "Job not found"},
        500: {"description": "Internal server error"},
    },
    tags=["public"],
)
async def get_job(
    job_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """
    Retrieve detailed information for a single job by its unique identifier.
    """
    return await job_dependency.get_job(session, job_id)
