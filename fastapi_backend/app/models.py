from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import (
    Column, String, Integer, ForeignKey, DateTime, Text, Boolean,
    JSON, Enum as SQLEnum, Float, Table
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from uuid import uuid4
from datetime import datetime
import enum


class Base(DeclarativeBase):
    pass


# Enums
class WorkspaceRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class ToolType(str, enum.Enum):
    MCP = "mcp"
    HTTP = "http"
    VECTOR_SEARCH = "vector_search"
    CUSTOM = "custom"


class HTTPMethod(str, enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class DistanceMetric(str, enum.Enum):
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot"


# Association table for workspace members
workspace_members = Table(
    'workspace_members',
    Base.metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column('workspace_id', UUID(as_uuid=True), ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
    Column('user_id', UUID(as_uuid=True), ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
    Column('role', SQLEnum(WorkspaceRole), nullable=False, default=WorkspaceRole.MEMBER),
    Column('permissions', JSON, nullable=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
)


# Models
class User(SQLAlchemyBaseUserTableUUID, Base):
    workspaces = relationship("Workspace", secondary=workspace_members, back_populates="members")
    owned_workspaces = relationship("Workspace", back_populates="owner", foreign_keys="Workspace.owner_id")


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    settings = Column(JSON, nullable=True, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="owned_workspaces", foreign_keys=[owner_id])
    members = relationship("User", secondary=workspace_members, back_populates="workspaces")
    agents = relationship("Agent", back_populates="workspace", cascade="all, delete-orphan")
    mcp_servers = relationship("MCPServer", back_populates="workspace", cascade="all, delete-orphan")
    http_endpoints = relationship("HTTPEndpoint", back_populates="workspace", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="workspace", cascade="all, delete-orphan")
    vector_collections = relationship("VectorCollection", back_populates="workspace", cascade="all, delete-orphan")


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=False)
    tools = Column(JSON, nullable=True, default=[])  # List of tool configurations
    settings = Column(JSON, nullable=True, default={})  # Model, temperature, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    workspace = relationship("Workspace", back_populates="agents")
    versions = relationship("AgentVersion", back_populates="agent", cascade="all, delete-orphan")
    executions = relationship("AgentExecution", back_populates="agent", cascade="all, delete-orphan")
    agent_tools = relationship("Tool", back_populates="agent", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="agent", cascade="all, delete-orphan")


class AgentVersion(Base):
    __tablename__ = "agent_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    config = Column(JSON, nullable=False)  # Snapshot of agent config at this version
    deployed_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)

    # Relationships
    agent = relationship("Agent", back_populates="versions")


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default="pending")  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    agent = relationship("Agent", back_populates="executions")


class MCPServer(Base):
    __tablename__ = "mcp_servers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(String(512), nullable=False)
    capabilities = Column(JSON, nullable=True, default=[])
    auth_config = Column(JSON, nullable=True)  # Encrypted auth credentials
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    workspace = relationship("Workspace", back_populates="mcp_servers")
    tools = relationship("Tool", back_populates="mcp_server", cascade="all, delete-orphan")


class HTTPEndpoint(Base):
    __tablename__ = "http_endpoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    method = Column(SQLEnum(HTTPMethod), nullable=False, default=HTTPMethod.GET)
    url = Column(String(512), nullable=False)
    headers = Column(JSON, nullable=True, default={})
    body_template = Column(Text, nullable=True)
    variables = Column(JSON, nullable=True, default=[])  # List of variable definitions
    auth_config = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    workspace = relationship("Workspace", back_populates="http_endpoints")
    tools = relationship("Tool", back_populates="http_endpoint", cascade="all, delete-orphan")


class Tool(Base):
    __tablename__ = "tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    type = Column(SQLEnum(ToolType), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    config = Column(JSON, nullable=False)  # Tool-specific configuration
    mcp_server_id = Column(UUID(as_uuid=True), ForeignKey("mcp_servers.id", ondelete="SET NULL"), nullable=True)
    http_endpoint_id = Column(UUID(as_uuid=True), ForeignKey("http_endpoints.id", ondelete="SET NULL"), nullable=True)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    agent = relationship("Agent", back_populates="agent_tools")
    mcp_server = relationship("MCPServer", back_populates="tools")
    http_endpoint = relationship("HTTPEndpoint", back_populates="tools")


class VectorCollection(Base):
    __tablename__ = "vector_collections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    dimension = Column(Integer, nullable=False, default=1536)
    distance_metric = Column(SQLEnum(DistanceMetric), nullable=False, default=DistanceMetric.COSINE)
    qdrant_collection_name = Column(String(255), nullable=False, unique=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    workspace = relationship("Workspace", back_populates="vector_collections")
    documents = relationship("Document", back_populates="vector_collection", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=True)
    vector_collection_id = Column(UUID(as_uuid=True), ForeignKey("vector_collections.id", ondelete="CASCADE"), nullable=True)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    embeddings_id = Column(String(255), nullable=True)  # Qdrant point ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    workspace = relationship("Workspace", back_populates="documents")
    agent = relationship("Agent", back_populates="documents")
    vector_collection = relationship("VectorCollection", back_populates="documents")
