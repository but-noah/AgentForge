"""HTTP Endpoint routes for AgentForge API."""

from typing import List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models import HTTPEndpoint
from app.schemas import (
    HTTPEndpointCreate, HTTPEndpointRead, HTTPEndpointUpdate,
    HTTPEndpointTestRequest
)
from app.services import HTTPExecutor
from app.users import current_active_user, User

router = APIRouter(prefix="/endpoints", tags=["http-endpoints"])


@router.post("/", response_model=HTTPEndpointRead, status_code=status.HTTP_201_CREATED)
async def create_http_endpoint(
    endpoint_data: HTTPEndpointCreate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Create a new HTTP endpoint."""
    endpoint = HTTPEndpoint(**endpoint_data.model_dump())
    db.add(endpoint)
    await db.commit()
    await db.refresh(endpoint)

    return endpoint


@router.get("/{endpoint_id}", response_model=HTTPEndpointRead)
async def get_http_endpoint(
    endpoint_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Get an HTTP endpoint by ID."""
    result = await db.execute(
        select(HTTPEndpoint).where(HTTPEndpoint.id == endpoint_id)
    )
    endpoint = result.scalar_one_or_none()

    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="HTTP endpoint not found"
        )

    return endpoint


@router.get("/", response_model=List[HTTPEndpointRead])
async def list_http_endpoints(
    workspace_id: UUID | None = None,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """List all HTTP endpoints."""
    query = select(HTTPEndpoint)

    if workspace_id:
        query = query.where(HTTPEndpoint.workspace_id == workspace_id)

    result = await db.execute(query)
    endpoints = result.scalars().all()

    return list(endpoints)


@router.put("/{endpoint_id}", response_model=HTTPEndpointRead)
async def update_http_endpoint(
    endpoint_id: UUID,
    endpoint_data: HTTPEndpointUpdate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Update an HTTP endpoint."""
    result = await db.execute(
        select(HTTPEndpoint).where(HTTPEndpoint.id == endpoint_id)
    )
    endpoint = result.scalar_one_or_none()

    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="HTTP endpoint not found"
        )

    # Update fields
    update_data = endpoint_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(endpoint, field, value)

    await db.commit()
    await db.refresh(endpoint)

    return endpoint


@router.delete("/{endpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_http_endpoint(
    endpoint_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Delete an HTTP endpoint."""
    result = await db.execute(
        select(HTTPEndpoint).where(HTTPEndpoint.id == endpoint_id)
    )
    endpoint = result.scalar_one_or_none()

    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="HTTP endpoint not found"
        )

    await db.delete(endpoint)
    await db.commit()


@router.post("/{endpoint_id}/test")
async def test_http_endpoint(
    endpoint_id: UUID,
    test_request: HTTPEndpointTestRequest,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
) -> Dict[str, Any]:
    """Test an HTTP endpoint with variables."""
    # Get endpoint
    result = await db.execute(
        select(HTTPEndpoint).where(HTTPEndpoint.id == endpoint_id)
    )
    endpoint = result.scalar_one_or_none()

    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="HTTP endpoint not found"
        )

    # Execute request
    executor = HTTPExecutor()
    try:
        result = await executor.test_endpoint(
            method=endpoint.method.value,
            url=endpoint.url,
            headers=endpoint.headers,
            body_template=endpoint.body_template,
            variables=test_request.variables,
            auth_config=endpoint.auth_config,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing endpoint: {str(e)}"
        )
    finally:
        await executor.close()


@router.get("/{endpoint_id}/schema")
async def get_endpoint_schema(
    endpoint_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
) -> List[Dict[str, Any]]:
    """Get variable schema for an HTTP endpoint."""
    # Get endpoint
    result = await db.execute(
        select(HTTPEndpoint).where(HTTPEndpoint.id == endpoint_id)
    )
    endpoint = result.scalar_one_or_none()

    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="HTTP endpoint not found"
        )

    # Get schema
    executor = HTTPExecutor()
    schema = executor.get_variable_schema(
        url=endpoint.url,
        body_template=endpoint.body_template,
        headers=endpoint.headers,
    )

    return schema
