"""HTTP Endpoint executor service with variable replacement."""

import re
import json
from typing import Dict, Any, List, Optional
import httpx


class HTTPExecutor:
    """Service for executing HTTP endpoints with variable substitution."""

    VARIABLE_PATTERN = re.compile(r'\{\{([^}]+)\}\}')

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def parse_variables(self, template: str) -> List[str]:
        """Extract variable names from a template string."""
        matches = self.VARIABLE_PATTERN.findall(template)
        return [match.strip() for match in matches]

    def replace_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """Replace {{variable}} patterns with actual values."""
        if not template:
            return template

        def replacer(match):
            var_name = match.group(1).strip()
            value = variables.get(var_name)

            if value is None:
                raise ValueError(f"Missing value for variable: {var_name}")

            # Convert value to string
            if isinstance(value, (dict, list)):
                return json.dumps(value)
            return str(value)

        return self.VARIABLE_PATTERN.sub(replacer, template)

    def replace_variables_in_dict(
        self,
        data: Dict[str, Any],
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Replace variables in dictionary values recursively."""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.replace_variables(value, variables)
            elif isinstance(value, dict):
                result[key] = self.replace_variables_in_dict(value, variables)
            elif isinstance(value, list):
                result[key] = [
                    self.replace_variables(item, variables) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def validate_variables(
        self,
        template: str,
        variables: Dict[str, Any],
        variable_schema: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Validate that all required variables are provided."""
        required_vars = self.parse_variables(template)
        missing = []

        for var in required_vars:
            if var not in variables:
                missing.append(var)

        # Validate against schema if provided
        if variable_schema:
            for var_def in variable_schema:
                var_name = var_def.get("name")
                if var_def.get("required", False) and var_name not in variables:
                    if var_name not in missing:
                        missing.append(var_name)

        return missing

    async def execute(
        self,
        method: str,
        url: str,
        variables: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        body_template: Optional[str] = None,
        auth_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute HTTP request with variable substitution."""
        try:
            # Replace variables in URL
            final_url = self.replace_variables(url, variables)

            # Replace variables in headers
            final_headers = {}
            if headers:
                final_headers = self.replace_variables_in_dict(headers, variables)

            # Add authentication
            if auth_config:
                auth_type = auth_config.get("type")
                if auth_type == "bearer":
                    token = self.replace_variables(auth_config.get("token", ""), variables)
                    final_headers["Authorization"] = f"Bearer {token}"
                elif auth_type == "api_key":
                    header_name = auth_config.get("header_name", "X-API-Key")
                    api_key = self.replace_variables(auth_config.get("api_key", ""), variables)
                    final_headers[header_name] = api_key
                elif auth_type == "basic":
                    username = self.replace_variables(auth_config.get("username", ""), variables)
                    password = self.replace_variables(auth_config.get("password", ""), variables)
                    auth = (username, password)
                else:
                    auth = None
            else:
                auth = None

            # Prepare body
            body = None
            if body_template:
                body_str = self.replace_variables(body_template, variables)
                try:
                    body = json.loads(body_str)
                except json.JSONDecodeError:
                    # If not valid JSON, send as string
                    body = body_str

            # Execute request
            response = await self.client.request(
                method=method.upper(),
                url=final_url,
                headers=final_headers,
                json=body if isinstance(body, dict) else None,
                content=body if isinstance(body, str) else None,
                auth=auth if auth_config and auth_config.get("type") == "basic" else None,
            )

            # Parse response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"text": response.text}

            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response_data,
                "success": response.is_success,
            }

        except httpx.RequestError as e:
            return {
                "status_code": 0,
                "error": str(e),
                "success": False,
            }
        except Exception as e:
            return {
                "status_code": 0,
                "error": f"Unexpected error: {str(e)}",
                "success": False,
            }

    async def test_endpoint(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body_template: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        auth_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Test an HTTP endpoint configuration."""
        # Use empty dict if no variables provided
        test_variables = variables or {}

        # Validate variables
        missing_vars = []
        if body_template:
            missing_vars.extend(self.validate_variables(body_template, test_variables))
        missing_vars.extend(self.validate_variables(url, test_variables))

        if missing_vars:
            return {
                "success": False,
                "error": f"Missing required variables: {', '.join(set(missing_vars))}",
                "missing_variables": list(set(missing_vars)),
            }

        # Execute request
        result = await self.execute(
            method=method,
            url=url,
            variables=test_variables,
            headers=headers,
            body_template=body_template,
            auth_config=auth_config,
        )

        return result

    def get_variable_schema(
        self,
        url: str,
        body_template: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """Extract variable schema from URL, headers, and body template."""
        variables = set()

        # Extract from URL
        variables.update(self.parse_variables(url))

        # Extract from headers
        if headers:
            for value in headers.values():
                variables.update(self.parse_variables(value))

        # Extract from body
        if body_template:
            variables.update(self.parse_variables(body_template))

        return [
            {
                "name": var,
                "type": "string",
                "required": True,
                "description": f"Variable: {var}"
            }
            for var in sorted(variables)
        ]
