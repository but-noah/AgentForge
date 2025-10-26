import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi_users import schemas
from pydantic import BaseModel, Field

from app.models import (
    WorkspaceRole, ToolType, HTTPMethod, DistanceMetric
)


# User Schemas
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


# Workspace Schemas
class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    settings: Optional[Dict[str, Any]] = {}


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    settings: Optional[Dict[str, Any]] = None


class WorkspaceRead(WorkspaceBase):
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Agent Schemas
class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    system_prompt: str = Field(..., min_length=1)
    tools: Optional[List[Dict[str, Any]]] = []
    settings: Optional[Dict[str, Any]] = {}
    is_active: bool = True


class AgentCreate(AgentBase):
    workspace_id: UUID


class AgentCreateFromPrompt(BaseModel):
    workspace_id: UUID
    prompt: str = Field(..., min_length=1, description="Natural language description of the agent")


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    system_prompt: Optional[str] = Field(None, min_length=1)
    tools: Optional[List[Dict[str, Any]]] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AgentRead(AgentBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentExecuteRequest(BaseModel):
    input_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class AgentExecuteResponse(BaseModel):
    execution_id: UUID
    status: str
    output_data: Optional[Dict[str, Any]] = None
    tokens_used: Optional[int] = None
    duration_ms: Optional[int] = None


# Agent Version Schemas
class AgentVersionRead(BaseModel):
    id: UUID
    agent_id: UUID
    version: int
    config: Dict[str, Any]
    deployed_at: datetime
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


# Agent Execution Schemas
class AgentExecutionRead(BaseModel):
    id: UUID
    agent_id: UUID
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    tokens_used: Optional[int] = None
    duration_ms: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# MCP Server Schemas
class MCPServerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., min_length=1, max_length=512)
    capabilities: Optional[List[Dict[str, Any]]] = []
    auth_config: Optional[Dict[str, Any]] = None
    is_active: bool = True


class MCPServerCreate(MCPServerBase):
    workspace_id: UUID


class MCPServerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = Field(None, min_length=1, max_length=512)
    capabilities: Optional[List[Dict[str, Any]]] = None
    auth_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class MCPServerRead(MCPServerBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# HTTP Endpoint Schemas
class HTTPEndpointBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    method: HTTPMethod = HTTPMethod.GET
    url: str = Field(..., min_length=1, max_length=512)
    headers: Optional[Dict[str, str]] = {}
    body_template: Optional[str] = None
    variables: Optional[List[Dict[str, Any]]] = []
    auth_config: Optional[Dict[str, Any]] = None


class HTTPEndpointCreate(HTTPEndpointBase):
    workspace_id: UUID


class HTTPEndpointUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    method: Optional[HTTPMethod] = None
    url: Optional[str] = Field(None, min_length=1, max_length=512)
    headers: Optional[Dict[str, str]] = None
    body_template: Optional[str] = None
    variables: Optional[List[Dict[str, Any]]] = None
    auth_config: Optional[Dict[str, Any]] = None


class HTTPEndpointRead(HTTPEndpointBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HTTPEndpointTestRequest(BaseModel):
    variables: Dict[str, Any]


# Tool Schemas
class ToolBase(BaseModel):
    type: ToolType
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    config: Dict[str, Any]
    mcp_server_id: Optional[UUID] = None
    http_endpoint_id: Optional[UUID] = None
    enabled: bool = True


class ToolCreate(ToolBase):
    agent_id: UUID


class ToolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class ToolRead(ToolBase):
    id: UUID
    agent_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# Vector Collection Schemas
class VectorCollectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    dimension: int = Field(default=1536, ge=1)
    distance_metric: DistanceMetric = DistanceMetric.COSINE
    metadata: Optional[Dict[str, Any]] = None


class VectorCollectionCreate(VectorCollectionBase):
    workspace_id: UUID


class VectorCollectionRead(VectorCollectionBase):
    id: UUID
    workspace_id: UUID
    qdrant_collection_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


# Document Schemas
class DocumentBase(BaseModel):
    content: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class DocumentCreate(DocumentBase):
    workspace_id: UUID
    agent_id: Optional[UUID] = None
    vector_collection_id: Optional[UUID] = None


class DocumentRead(DocumentBase):
    id: UUID
    workspace_id: UUID
    agent_id: Optional[UUID] = None
    vector_collection_id: Optional[UUID] = None
    embeddings_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Vector Search Schemas
class VectorSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    collection_id: UUID
    limit: int = Field(default=5, ge=1, le=100)


class VectorSearchResult(BaseModel):
    document_id: UUID
    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None


class VectorSearchResponse(BaseModel):
    results: List[VectorSearchResult]
