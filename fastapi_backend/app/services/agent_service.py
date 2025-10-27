"""Agent service for creating and managing AI agents."""

import os
import json
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from app.models import Agent, ToolType


class AgentService:
    """Service for AI agent creation and management."""

    def __init__(self):
        self.anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def parse_agent_intent(self, prompt: str) -> Dict[str, Any]:
        """Parse natural language prompt to extract agent intent."""
        system_prompt = """You are an AI assistant that parses natural language descriptions of AI agents.
Extract the following information from the user's description:
- name: A concise name for the agent
- description: A brief description of what the agent does
- capabilities: List of capabilities the agent needs
- needs_storage: Boolean indicating if the agent needs database storage
- needs_knowledge: Boolean indicating if the agent needs a knowledge base
- tools_needed: List of tool types needed (mcp, http, vector_search)
- suggested_model: The AI model to use (claude-3-5-sonnet-20241022, gpt-4-turbo, etc.)

Return ONLY a JSON object with these fields. No markdown, no explanations."""

        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                temperature=0,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract JSON from response
            content = response.content[0].text
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()

            parsed = json.loads(content)
            return parsed

        except Exception as e:
            print(f"Error parsing agent intent: {e}")
            # Return a default structure
            return {
                "name": "Custom Agent",
                "description": prompt[:200],
                "capabilities": [],
                "needs_storage": False,
                "needs_knowledge": False,
                "tools_needed": [],
                "suggested_model": "claude-3-5-sonnet-20241022"
            }

    async def generate_system_prompt(self, parsed_intent: Dict[str, Any]) -> str:
        """Generate a system prompt for the agent based on parsed intent."""
        system_prompt = f"""You are an AI assistant helping with: {parsed_intent.get('description', 'various tasks')}.

Your capabilities include:
{chr(10).join('- ' + cap for cap in parsed_intent.get('capabilities', []))}

Guidelines:
- Be helpful, accurate, and concise
- Use the tools available to you when needed
- If you're unsure about something, ask for clarification
- Format your responses clearly and professionally
"""

        # Add knowledge base instructions if needed
        if parsed_intent.get('needs_knowledge'):
            system_prompt += """
- When answering questions, first search the knowledge base for relevant information
- Cite sources from the knowledge base when applicable
"""

        # Add storage instructions if needed
        if parsed_intent.get('needs_storage'):
            system_prompt += """
- Keep track of important information in the database
- Retrieve and update stored data as needed
"""

        return system_prompt.strip()

    async def suggest_tools(self, parsed_intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest tools based on parsed agent intent."""
        tools = []

        # Add vector search tool if knowledge base is needed
        if parsed_intent.get('needs_knowledge'):
            tools.append({
                "type": ToolType.VECTOR_SEARCH.value,
                "name": "search_knowledge_base",
                "description": "Search the agent's knowledge base for relevant information",
                "config": {
                    "enabled": True
                }
            })

        # Add tools based on explicit needs
        for tool_type in parsed_intent.get('tools_needed', []):
            if tool_type == "mcp":
                tools.append({
                    "type": ToolType.MCP.value,
                    "name": "mcp_tool",
                    "description": "Access MCP server capabilities",
                    "config": {
                        "enabled": True
                    }
                })
            elif tool_type == "http":
                tools.append({
                    "type": ToolType.HTTP.value,
                    "name": "http_request",
                    "description": "Make HTTP requests to external APIs",
                    "config": {
                        "enabled": True
                    }
                })

        return tools

    async def create_agent_from_prompt(
        self,
        prompt: str,
        workspace_id: UUID,
    ) -> Dict[str, Any]:
        """Create an agent configuration from natural language prompt."""
        # Parse the user's intent
        parsed = await self.parse_agent_intent(prompt)

        # Generate system prompt
        system_prompt = await self.generate_system_prompt(parsed)

        # Suggest tools
        tools = await self.suggest_tools(parsed)

        # Create agent config
        agent_config = {
            "name": parsed.get("name", "Custom Agent"),
            "description": parsed.get("description", prompt[:200]),
            "system_prompt": system_prompt,
            "tools": tools,
            "settings": {
                "model": parsed.get("suggested_model", "claude-3-5-sonnet-20241022"),
                "temperature": 0.7,
                "max_tokens": 4096,
            },
            "workspace_id": str(workspace_id),
            "metadata": {
                "created_from_prompt": True,
                "original_prompt": prompt,
                "parsed_intent": parsed,
            }
        }

        return agent_config

    async def execute_agent(
        self,
        agent: Agent,
        input_data: Dict[str, Any],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Execute an agent with the given input."""
        start_time = datetime.now()

        try:
            # Determine which client to use based on model
            model = agent.settings.get("model", "claude-3-5-sonnet-20241022")
            use_anthropic = model.startswith("claude")

            # Prepare messages
            user_message = input_data.get("message", "")
            if isinstance(input_data.get("context"), dict):
                user_message = f"Context: {json.dumps(input_data['context'])}\n\n{user_message}"

            if use_anthropic:
                # Use Anthropic API
                response = await self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=agent.settings.get("max_tokens", 4096),
                    temperature=agent.settings.get("temperature", 0.7),
                    system=agent.system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ]
                )

                output_text = response.content[0].text
                tokens_used = response.usage.input_tokens + response.usage.output_tokens

            else:
                # Use OpenAI API
                response = await self.openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": agent.system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                    temperature=agent.settings.get("temperature", 0.7),
                    max_tokens=agent.settings.get("max_tokens", 4096),
                )

                output_text = response.choices[0].message.content
                tokens_used = response.usage.total_tokens

            # Calculate duration
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            return {
                "output_data": {
                    "response": output_text,
                    "model": model,
                },
                "tokens_used": tokens_used,
                "duration_ms": duration_ms,
                "status": "completed",
            }

        except Exception as e:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return {
                "output_data": None,
                "tokens_used": 0,
                "duration_ms": duration_ms,
                "status": "failed",
                "error_message": str(e),
            }
