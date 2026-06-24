from fastapi import APIRouter, status, HTTPException
from typing import List
import asyncio

from app.schemas.agent import AgentStatusResponse, JobRunResponse, RunNowResponse
from app.models.job_run import JobRun
from app.services.scheduler_service import run_agent_cycle, scheduler, get_scheduler_next_run

router = APIRouter()

@router.get("/status", response_model=AgentStatusResponse, status_code=status.HTTP_200_OK)
async def get_agent_status():
    """
    Get the operational status of the background job agent scheduler.
    """
    # Fetch the most recent JobRun log
    last_run_doc = await JobRun.find().sort("-started_at").first_or_none()
    
    last_run = None
    if last_run_doc:
        last_run = JobRunResponse(
            id=str(last_run_doc.id),
            run_id=last_run_doc.run_id,
            started_at=last_run_doc.started_at,
            completed_at=last_run_doc.completed_at,
            jobs_found=last_run_doc.jobs_found,
            matches_created=last_run_doc.matches_created,
            status=last_run_doc.status
        )
        
    return AgentStatusResponse(
        scheduler_running=scheduler.running,
        next_run_time=get_scheduler_next_run(),
        last_run=last_run
    )

@router.get("/runs", response_model=List[JobRunResponse], status_code=status.HTTP_200_OK)
async def list_agent_runs():
    """
    Get a list of all background agent execution logs.
    """
    runs = await JobRun.find().sort("-started_at").to_list()
    return [
        JobRunResponse(
            id=str(r.id),
            run_id=r.run_id,
            started_at=r.started_at,
            completed_at=r.completed_at,
            jobs_found=r.jobs_found,
            matches_created=r.matches_created,
            status=r.status
        )
        for r in runs
    ]

@router.post("/run-now", response_model=RunNowResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_run_now():
    """
    Manually trigger the background agent cycle immediately.
    """
    # Start task as background asyncio task so we return 202 Accepted immediately
    asyncio.create_task(run_agent_cycle())
    
    # Wait a fraction of a second to ensure the run model is created in DB
    await asyncio.sleep(0.1)
    
    # Fetch the most recent run (which should be the one we just started)
    active_run = await JobRun.find().sort("-started_at").first_or_none()
    
    run_id = active_run.run_id if active_run else "unknown"
    run_status = active_run.status if active_run else "started"
    
    return RunNowResponse(
        message="Background job agent execution run triggered successfully.",
        run_id=run_id,
        status=run_status
    )
