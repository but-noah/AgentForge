# AgentForge 🤖

Open-source AI Agent Builder platform with natural language capabilities, MCP protocol support, and multi-tenancy.

## Features

- 🎯 **Natural Language Agent Creation** - Describe your agent in plain English and let AI build it
- 🔧 **MCP Server Integration** - Connect to Model Context Protocol servers for extended capabilities
- 🌐 **HTTP Endpoint Configuration** - Create custom HTTP integrations with variable substitution
- 🧠 **Vector Database** - Built-in knowledge management with Qdrant
- 👥 **Multi-Tenant Architecture** - Workspace isolation for teams and organizations
- 🚀 **FastAPI Backend** - High-performance async Python backend
- ⚡ **Next.js Frontend** - Modern React-based UI with TypeScript
- 🐳 **Docker Compose** - One-command deployment

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database for structured data
- **Qdrant** - Vector database for semantic search
- **Redis** - Caching and session management
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **shadcn/ui** - Beautiful UI components
- **Tailwind CSS** - Utility-first CSS framework

### AI Integration
- **OpenAI API** - GPT models for agent execution
- **Anthropic API** - Claude models for agent execution
- **MCP Protocol** - Model Context Protocol support

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.12+ (for local backend development)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd AgentForge
```

### 2. Configure Environment Variables

```bash
# Backend environment
cp fastapi_backend/.env.example fastapi_backend/.env
# Edit fastapi_backend/.env and add your API keys
```

**Required API Keys:**
- `OPENAI_API_KEY` - Get from https://platform.openai.com
- `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com

### 3. Start Services with Docker Compose

```bash
docker-compose up -d
```

This will start:
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **Qdrant**: localhost:6333
- **Redis**: localhost:6379
- **MailHog**: http://localhost:8025

### 4. Run Database Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### 5. Access the Application

Open http://localhost:3000 in your browser.

## Architecture

```
AgentForge/
├── fastapi_backend/          # Python FastAPI backend
│   ├── app/
│   │   ├── models.py        # SQLAlchemy database models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── routes/          # API endpoints
│   │   │   ├── agents.py
│   │   │   ├── workspaces.py
│   │   │   ├── mcp_servers.py
│   │   │   ├── http_endpoints.py
│   │   │   └── vectors.py
│   │   ├── services/        # Business logic
│   │   │   ├── agent_service.py
│   │   │   ├── vector_store.py
│   │   │   ├── mcp_client.py
│   │   │   ├── http_executor.py
│   │   │   └── redis_cache.py
│   │   └── main.py          # FastAPI app
│   └── alembic_migrations/  # Database migrations
├── nextjs-frontend/          # Next.js frontend
│   ├── app/                 # Next.js app directory
│   ├── components/          # React components
│   └── lib/                 # Utilities
└── docker-compose.yml       # Docker services
```

## API Endpoints

### Agents

- `POST /api/agents/create-from-prompt` - Create agent from natural language
- `POST /api/agents` - Create agent manually
- `GET /api/agents/{id}` - Get agent details
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent
- `POST /api/agents/{id}/execute` - Execute agent
- `GET /api/agents/{id}/executions` - Get execution history

### Workspaces

- `POST /api/workspaces` - Create workspace
- `GET /api/workspaces` - List workspaces
- `GET /api/workspaces/{id}` - Get workspace
- `PUT /api/workspaces/{id}` - Update workspace
- `DELETE /api/workspaces/{id}` - Delete workspace

### MCP Servers

- `POST /api/mcp/servers` - Register MCP server
- `GET /api/mcp/servers/{id}/tools` - List available tools
- `POST /api/mcp/servers/{id}/execute` - Execute MCP tool

### HTTP Endpoints

- `POST /api/endpoints` - Create HTTP endpoint
- `POST /api/endpoints/{id}/test` - Test endpoint
- `GET /api/endpoints/{id}/schema` - Get variable schema

### Vector Database

- `POST /api/vectors/collections` - Create vector collection
- `POST /api/vectors/documents` - Add document
- `POST /api/vectors/search` - Semantic search

## Usage Examples

### 1. Create an Agent from Natural Language

```bash
curl -X POST http://localhost:8000/api/agents/create-from-prompt \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "your-workspace-id",
    "prompt": "Create a customer support agent that can search our documentation and create support tickets"
  }'
```

### 2. Execute an Agent

```bash
curl -X POST http://localhost:8000/api/agents/{agent_id}/execute \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "message": "How do I reset my password?"
    }
  }'
```

### 3. Add Knowledge to Agent

```bash
curl -X POST http://localhost:8000/api/vectors/documents \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "your-workspace-id",
    "agent_id": "your-agent-id",
    "content": "To reset your password, go to Settings > Security > Reset Password",
    "vector_collection_id": "your-collection-id"
  }'
```

## Database Schema

### Core Models

- **Workspace** - Multi-tenant workspace
- **User** - User accounts
- **Agent** - AI agent configurations
- **AgentVersion** - Agent version history
- **AgentExecution** - Execution logs
- **MCPServer** - MCP server connections
- **HTTPEndpoint** - HTTP endpoint configurations
- **Tool** - Agent tools
- **VectorCollection** - Vector collections
- **Document** - Knowledge base documents

## Development

### Backend Development

```bash
cd fastapi_backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start dev server
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd nextjs-frontend
npm install
npm run dev
```

### Run Tests

```bash
# Backend tests
cd fastapi_backend
pytest

# Frontend tests
cd nextjs-frontend
npm test
```

## Deployment

### Hetzner Cloud Deployment

1. Create a Hetzner Cloud server
2. Install Docker and Docker Compose
3. Clone the repository
4. Set environment variables
5. Run `docker-compose up -d`
6. Configure reverse proxy (nginx/caddy)
7. Setup SSL certificates (Let's Encrypt)

### Environment Variables for Production

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/agentforge

# Redis
REDIS_URL=redis://redis:6379

# Qdrant
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=your-production-key

# AI APIs
OPENAI_API_KEY=sk-prod-...
ANTHROPIC_API_KEY=sk-ant-prod-...

# Security
ACCESS_SECRET_KEY=your-secure-secret
RESET_PASSWORD_SECRET_KEY=your-secure-secret
VERIFICATION_SECRET_KEY=your-secure-secret

# Frontend
FRONTEND_URL=https://your-domain.com

# CORS
CORS_ORIGINS=["https://your-domain.com"]
```

## Multi-Tenancy

AgentForge uses workspace-based multi-tenancy:

- Each user can own multiple workspaces
- Workspaces have members with different roles
- All resources (agents, documents, etc.) belong to a workspace
- Data isolation is enforced at the database level

## MCP Protocol Support

Connect to MCP servers for extended capabilities:

```python
# MCP server configuration
{
  "name": "GitHub MCP",
  "url": "ws://localhost:8080/mcp",
  "auth_config": {
    "type": "bearer",
    "token": "your-token"
  }
}
```

## HTTP Endpoint Variables

Create dynamic HTTP endpoints with variable substitution:

```json
{
  "name": "Create Ticket",
  "method": "POST",
  "url": "https://api.example.com/tickets",
  "body_template": "{\"title\": \"{{ticket_title}}\", \"priority\": \"{{priority}}\"}",
  "variables": [
    {"name": "ticket_title", "type": "string", "required": true},
    {"name": "priority", "type": "string", "required": true}
  ]
}
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- GitHub Issues: https://github.com/your-repo/issues
- Documentation: https://docs.agentforge.dev
- Discord: https://discord.gg/agentforge

## Roadmap

- [ ] Web-based agent playground
- [ ] Agent marketplace
- [ ] Pre-built agent templates
- [ ] Advanced analytics dashboard
- [ ] WebSocket support for real-time updates
- [ ] Agent-to-agent communication
- [ ] Custom tool SDK
- [ ] Multi-language support

## Credits

Built with:
- [vintasoftware/nextjs-fastapi-template](https://github.com/vintasoftware/nextjs-fastapi-template)
- [Qdrant](https://qdrant.tech/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [shadcn/ui](https://ui.shadcn.com/)
