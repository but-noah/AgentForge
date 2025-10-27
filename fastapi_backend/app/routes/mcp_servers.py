"""MCP Server routes for AgentForge API."""

from typing import List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models import MCPServer
from app.schemas import MCPServerCreate, MCPServerRead, MCPServerUpdate
from app.services import MCPClient
from app.users import current_active_user, User

router = APIRouter(prefix="/mcp", tags=["mcp"])

# Global MCP manager (in production, use dependency injection)
from app.services.mcp_client import MCPManager
mcp_manager = MCPManager()


@router.post("/servers", response_model=MCPServerRead, status_code=status.HTTP_201_CREATED)
async def create_mcp_server(
    server_data: MCPServerCreate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Register a new MCP server."""
    server = MCPServer(**server_data.model_dump())
    db.add(server)
    await db.commit()
    await db.refresh(server)

    # Connect to the MCP server
    await mcp_manager.add_server(
        server_id=str(server.id),
        server_url=server.url,
        auth_config=server.auth_config,
    )

    return server


@router.get("/servers/{server_id}", response_model=MCPServerRead)
async def get_mcp_server(
    server_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Get an MCP server by ID."""
    result = await db.execute(
        select(MCPServer).where(MCPServer.id == server_id)
    )
    server = result.scalar_one_or_none()

    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP server not found"
        )

    return server


@router.get("/servers", response_model=List[MCPServerRead])
async def list_mcp_servers(
    workspace_id: UUID | None = None,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """List all MCP servers."""
    query = select(MCPServer)

    if workspace_id:
        query = query.where(MCPServer.workspace_id == workspace_id)

    result = await db.execute(query)
    servers = result.scalars().all()

    return list(servers)


@router.get("/servers/{server_id}/tools")
async def get_mcp_server_tools(
    server_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
) -> List[Dict[str, Any]]:
    """Get available tools from an MCP server."""
    # Verify server exists
    result = await db.execute(
        select(MCPServer).where(MCPServer.id == server_id)
    )
    server = result.scalar_one_or_none()

    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP server not found"
        )

    # Get client
    client = mcp_manager.get_client(str(server_id))
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP server not connected"
        )

    # List tools
    try:
        tools = await client.list_tools()
        return tools
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting tools: {str(e)}"
        )


@router.post("/servers/{server_id}/execute")
async def execute_mcp_tool(
    server_id: UUID,
    tool_name: str,
    arguments: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
) -> Dict[str, Any]:
    """Execute a tool on an MCP server."""
    # Verify server exists
    result = await db.execute(
        select(MCPServer).where(MCPServer.id == server_id)
    )
    server = result.scalar_one_or_none()

    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP server not found"
        )

    # Execute tool
    try:
        result = await mcp_manager.execute_tool_on_server(
            server_id=str(server_id),
            tool_name=tool_name,
            arguments=arguments,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing tool: {str(e)}"
        )


@router.delete("/servers/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcp_server(
    server_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Delete an MCP server."""
    result = await db.execute(
        select(MCPServer).where(MCPServer.id == server_id)
    )
    server = result.scalar_one_or_none()

    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP server not found"
        )

    # Disconnect from server
    await mcp_manager.remove_server(str(server_id))

    await db.delete(server)
    await db.commit()
