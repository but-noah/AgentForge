"""Workspace routes for AgentForge API."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models import Workspace
from app.schemas import WorkspaceCreate, WorkspaceRead, WorkspaceUpdate
from app.users import current_active_user, User

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("/", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Create a new workspace."""
    workspace = Workspace(
        **workspace_data.model_dump(),
        owner_id=user.id,
    )
    db.add(workspace)
    await db.commit()
    await db.refresh(workspace)

    return workspace


@router.get("/{workspace_id}", response_model=WorkspaceRead)
async def get_workspace(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Get a workspace by ID."""
    result = await db.execute(
        select(Workspace).where(Workspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    return workspace


@router.get("/", response_model=List[WorkspaceRead])
async def list_workspaces(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """List all workspaces for the current user."""
    query = select(Workspace).where(
        Workspace.owner_id == user.id
    ).offset(skip).limit(limit)

    result = await db.execute(query)
    workspaces = result.scalars().all()

    return list(workspaces)


@router.put("/{workspace_id}", response_model=WorkspaceRead)
async def update_workspace(
    workspace_id: UUID,
    workspace_data: WorkspaceUpdate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Update a workspace."""
    result = await db.execute(
        select(Workspace).where(Workspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Update fields
    update_data = workspace_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workspace, field, value)

    await db.commit()
    await db.refresh(workspace)

    return workspace


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Delete a workspace."""
    result = await db.execute(
        select(Workspace).where(Workspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    if workspace.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this workspace"
        )

    await db.delete(workspace)
    await db.commit()
