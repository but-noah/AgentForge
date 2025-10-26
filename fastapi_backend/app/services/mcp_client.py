"""MCP (Model Context Protocol) client service."""

import json
from typing import Dict, Any, List, Optional
import websockets
import asyncio


class MCPClient:
    """Client for communicating with MCP servers via WebSocket."""

    def __init__(self, server_url: str, auth_config: Optional[Dict[str, Any]] = None):
        self.server_url = server_url
        self.auth_config = auth_config or {}
        self.websocket = None
        self.connected = False

    async def connect(self) -> bool:
        """Establish WebSocket connection to MCP server."""
        try:
            headers = {}
            if self.auth_config.get("type") == "bearer":
                headers["Authorization"] = f"Bearer {self.auth_config.get('token')}"
            elif self.auth_config.get("type") == "api_key":
                headers[self.auth_config.get("header_name", "X-API-Key")] = self.auth_config.get("api_key")

            self.websocket = await websockets.connect(
                self.server_url,
                extra_headers=headers,
            )
            self.connected = True
            return True
        except Exception as e:
            print(f"Error connecting to MCP server: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Close WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False

    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a request to the MCP server."""
        if not self.connected or not self.websocket:
            raise ConnectionError("Not connected to MCP server")

        request = {
            "jsonrpc": "2.0",
            "id": str(asyncio.current_task().get_name()),
            "method": method,
            "params": params or {},
        }

        try:
            await self.websocket.send(json.dumps(request))
            response = await self.websocket.recv()
            return json.loads(response)
        except Exception as e:
            print(f"Error sending MCP request: {e}")
            raise

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools from MCP server."""
        try:
            response = await self.send_request("tools/list")

            if "error" in response:
                raise Exception(f"MCP error: {response['error']}")

            return response.get("result", {}).get("tools", [])
        except Exception as e:
            print(f"Error listing tools: {e}")
            raise

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool on the MCP server."""
        try:
            response = await self.send_request(
                "tools/call",
                {
                    "name": tool_name,
                    "arguments": arguments,
                }
            )

            if "error" in response:
                raise Exception(f"MCP error: {response['error']}")

            return response.get("result", {})
        except Exception as e:
            print(f"Error executing tool: {e}")
            raise

    async def get_server_info(self) -> Dict[str, Any]:
        """Get information about the MCP server."""
        try:
            response = await self.send_request("server/info")

            if "error" in response:
                raise Exception(f"MCP error: {response['error']}")

            return response.get("result", {})
        except Exception as e:
            print(f"Error getting server info: {e}")
            raise

    async def get_resources(self) -> List[Dict[str, Any]]:
        """Get list of available resources from MCP server."""
        try:
            response = await self.send_request("resources/list")

            if "error" in response:
                raise Exception(f"MCP error: {response['error']}")

            return response.get("result", {}).get("resources", [])
        except Exception as e:
            print(f"Error listing resources: {e}")
            raise

    async def read_resource(self, resource_uri: str) -> Dict[str, Any]:
        """Read a resource from the MCP server."""
        try:
            response = await self.send_request(
                "resources/read",
                {"uri": resource_uri}
            )

            if "error" in response:
                raise Exception(f"MCP error: {response['error']}")

            return response.get("result", {})
        except Exception as e:
            print(f"Error reading resource: {e}")
            raise


class MCPManager:
    """Manager for multiple MCP client connections."""

    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}

    async def add_server(
        self,
        server_id: str,
        server_url: str,
        auth_config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add and connect to an MCP server."""
        try:
            client = MCPClient(server_url, auth_config)
            connected = await client.connect()

            if connected:
                self.clients[server_id] = client
                return True
            return False
        except Exception as e:
            print(f"Error adding MCP server: {e}")
            return False

    async def remove_server(self, server_id: str):
        """Remove and disconnect from an MCP server."""
        if server_id in self.clients:
            await self.clients[server_id].disconnect()
            del self.clients[server_id]

    def get_client(self, server_id: str) -> Optional[MCPClient]:
        """Get an MCP client by server ID."""
        return self.clients.get(server_id)

    async def execute_tool_on_server(
        self,
        server_id: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool on a specific MCP server."""
        client = self.get_client(server_id)
        if not client:
            raise ValueError(f"MCP server {server_id} not found")

        return await client.execute_tool(tool_name, arguments)

    async def disconnect_all(self):
        """Disconnect from all MCP servers."""
        for client in self.clients.values():
            await client.disconnect()
        self.clients.clear()
