"""Agent routes for AgentForge API."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models import Agent, AgentExecution, Workspace
from app.schemas import (
    AgentCreate, AgentRead, AgentUpdate, AgentCreateFromPrompt,
    AgentExecuteRequest, AgentExecuteResponse, AgentExecutionRead
)
from app.services import AgentService
from app.users import current_active_user, User

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/create-from-prompt", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
async def create_agent_from_prompt(
    agent_data: AgentCreateFromPrompt,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Create an agent from a natural language prompt."""
    # Verify workspace access
    result = await db.execute(
        select(Workspace).where(Workspace.id == agent_data.workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Create agent using service
    agent_service = AgentService()
    agent_config = await agent_service.create_agent_from_prompt(
        prompt=agent_data.prompt,
        workspace_id=agent_data.workspace_id,
    )

    # Create agent in database
    agent = Agent(
        workspace_id=agent_data.workspace_id,
        name=agent_config["name"],
        description=agent_config["description"],
        system_prompt=agent_config["system_prompt"],
        tools=agent_config["tools"],
        settings=agent_config["settings"],
    )

    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    return agent


@router.post("/", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Create a new agent."""
    # Verify workspace access
    result = await db.execute(
        select(Workspace).where(Workspace.id == agent_data.workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    agent = Agent(**agent_data.model_dump())
    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    return agent


@router.get("/{agent_id}", response_model=AgentRead)
async def get_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Get an agent by ID."""
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    return agent


@router.get("/", response_model=List[AgentRead])
async def list_agents(
    workspace_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """List all agents, optionally filtered by workspace."""
    query = select(Agent)

    if workspace_id:
        query = query.where(Agent.workspace_id == workspace_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    agents = result.scalars().all()

    return list(agents)


@router.put("/{agent_id}", response_model=AgentRead)
async def update_agent(
    agent_id: UUID,
    agent_data: AgentUpdate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Update an agent."""
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # Update fields
    update_data = agent_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    await db.commit()
    await db.refresh(agent)

    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Delete an agent."""
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    await db.delete(agent)
    await db.commit()


@router.post("/{agent_id}/execute", response_model=AgentExecuteResponse)
async def execute_agent(
    agent_id: UUID,
    request: AgentExecuteRequest,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Execute an agent with the given input."""
    # Get agent
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    if not agent.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent is not active"
        )

    # Create execution record
    execution = AgentExecution(
        agent_id=agent_id,
        input_data=request.input_data,
        status="running",
        metadata=request.metadata,
    )
    db.add(execution)
    await db.commit()
    await db.refresh(execution)

    # Execute agent
    agent_service = AgentService()
    result = await agent_service.execute_agent(
        agent=agent,
        input_data=request.input_data,
    )

    # Update execution record
    execution.output_data = result.get("output_data")
    execution.tokens_used = result.get("tokens_used")
    execution.duration_ms = result.get("duration_ms")
    execution.status = result.get("status")
    execution.error_message = result.get("error_message")
    execution.completed_at = db.func.now()

    await db.commit()
    await db.refresh(execution)

    return AgentExecuteResponse(
        execution_id=execution.id,
        status=execution.status,
        output_data=execution.output_data,
        tokens_used=execution.tokens_used,
        duration_ms=execution.duration_ms,
    )


@router.get("/{agent_id}/executions", response_model=List[AgentExecutionRead])
async def list_agent_executions(
    agent_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """List execution history for an agent."""
    # Verify agent exists
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # Get executions
    query = select(AgentExecution).where(
        AgentExecution.agent_id == agent_id
    ).order_by(
        AgentExecution.created_at.desc()
    ).offset(skip).limit(limit)

    result = await db.execute(query)
    executions = result.scalars().all()

    return list(executions)
