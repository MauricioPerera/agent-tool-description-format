#!/usr/bin/env python3
"""
MCP-ATDF Bridge Server
======================

This server acts as a bridge between ATDF (Agent Tool Description Format)
and MCP (Model Context Protocol), allowing n8n MCP Client Tool nodes to
access ATDF-formatted tools.

Features:
- Converts ATDF tools to MCP format
- Supports Server-Sent Events (SSE) for n8n compatibility
- Maintains ATDF metadata and localization
- Provides tool discovery and execution

Usage:
    python mcp_atdf_bridge.py --port 8001 --atdf-server http://localhost:8000
"""

import argparse
import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientSession, web
from aiohttp.web import Request, Response, StreamResponse
from aiohttp_sse import sse_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """MCP Tool representation"""

    name: str
    description: str
    inputSchema: Dict[str, Any]


class ATDFToMCPConverter:
    """Converts ATDF tools to MCP format"""

    @staticmethod
    def convert_tool(atdf_tool: Dict[str, Any]) -> MCPTool:
        """Convert a single ATDF tool to MCP format"""

        # Extract basic information
        name = atdf_tool.get("tool_id", "unknown_tool")
        description = atdf_tool.get("description", "")

        # Add when_to_use information to description if available
        when_to_use = atdf_tool.get("when_to_use", "")
        if when_to_use:
            description = f"{description}\n\nWhen to use: {when_to_use}"

        # Convert input schema
        input_schema = atdf_tool.get("input_schema", {})

        # Ensure the schema has the required MCP structure
        if not input_schema.get("type"):
            input_schema["type"] = "object"

        if not input_schema.get("properties"):
            input_schema["properties"] = {}

        return MCPTool(
            name=name, description=description.strip(), inputSchema=input_schema
        )

    @staticmethod
    def convert_tools(atdf_tools: List[Dict[str, Any]]) -> List[MCPTool]:
        """Convert multiple ATDF tools to MCP format"""
        return [ATDFToMCPConverter.convert_tool(tool) for tool in atdf_tools]


class MCPATDFBridge:
    """MCP-ATDF Bridge Server"""

    def __init__(self, atdf_server_url: str):
        self.atdf_server_url = atdf_server_url.rstrip("/")
        self.tools_cache: List[MCPTool] = []
        self.cache_timestamp: Optional[datetime] = None
        self.cache_ttl = 300  # 5 minutes

    async def fetch_atdf_tools(self) -> List[Dict[str, Any]]:
        """Fetch tools from ATDF server"""
        try:
            async with ClientSession() as session:
                async with session.get(f"{self.atdf_server_url}/tools") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("tools", [])
                    else:
                        logger.error(f"Failed to fetch ATDF tools: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching ATDF tools: {e}")
            return []

    async def get_tools(self) -> List[MCPTool]:
        """Get tools with caching"""
        now = datetime.now()

        # Check if cache is valid
        if (
            self.cache_timestamp
            and (now - self.cache_timestamp).seconds < self.cache_ttl
            and self.tools_cache
        ):
            return self.tools_cache

        # Fetch fresh tools
        atdf_tools = await self.fetch_atdf_tools()
        self.tools_cache = ATDFToMCPConverter.convert_tools(atdf_tools)
        self.cache_timestamp = now

        logger.info(f"Cached {len(self.tools_cache)} tools from ATDF server")
        return self.tools_cache

    async def call_atdf_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call a tool on the ATDF server"""
        try:
            # Map tool names to their specific endpoints
            endpoint_map = {
                "hotel_reservation": "/api/hotel/reserve",
                "flight_booking": "/api/flight/book",
            }

            endpoint = endpoint_map.get(tool_name)
            if not endpoint:
                return {
                    "error": f"Unknown tool: {tool_name}",
                    "details": f"Available tools: {list(endpoint_map.keys())}",
                }

            async with ClientSession() as session:
                async with session.post(
                    f"{self.atdf_server_url}{endpoint}",
                    json=arguments,
                    headers={"Content-Type": "application/json"},
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        return {
                            "error": f"ATDF server error: {response.status}",
                            "details": error_text,
                        }
        except Exception as e:
            logger.error(f"Error calling ATDF tool {tool_name}: {e}")
            return {"error": f"Failed to call tool: {str(e)}"}


# Global bridge instance
bridge: Optional[MCPATDFBridge] = None


async def handle_mcp_request(request: Request) -> Response:
    """Handle MCP JSON-RPC requests"""
    try:
        data = await request.json()
        method = data.get("method")
        params = data.get("params", {})
        request_id = data.get("id")

        logger.info(f"MCP Request: {method}")

        if method == "tools/list":
            tools = await bridge.get_tools()
            tools_list = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                }
                for tool in tools
            ]

            response_data = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools_list},
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if not tool_name:
                response_data = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params: tool name required",
                    },
                }
            else:
                result = await bridge.call_atdf_tool(tool_name, arguments)
                response_data = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, indent=2)}
                        ]
                    },
                }

        elif method == "initialize":
            response_data = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "ATDF-MCP Bridge", "version": "1.0.0"},
                },
            }

        else:
            response_data = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }

        return web.json_response(response_data)

    except Exception as e:
        logger.error(f"Error handling MCP request: {e}")
        return web.json_response(
            {
                "jsonrpc": "2.0",
                "id": data.get("id") if "data" in locals() else None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            },
            status=500,
        )


async def handle_sse(request: Request) -> StreamResponse:
    """Handle Server-Sent Events for n8n compatibility"""
    async with sse_response(request) as resp:
        # Send initial connection message
        await resp.send(
            json.dumps(
                {
                    "type": "connection",
                    "status": "connected",
                    "server": "ATDF-MCP Bridge",
                    "timestamp": datetime.now().isoformat(),
                }
            )
        )

        # Keep connection alive
        try:
            while True:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                await resp.send(
                    json.dumps(
                        {"type": "heartbeat", "timestamp": datetime.now().isoformat()}
                    )
                )
        except asyncio.CancelledError:
            logger.info("SSE connection closed")

    return resp


async def handle_health(request: Request) -> Response:
    """Health check endpoint"""
    tools = await bridge.get_tools()

    health_data = {
        "status": "healthy",
        "server": "ATDF-MCP Bridge",
        "version": "1.0.0",
        "atdf_server": bridge.atdf_server_url,
        "tools_count": len(tools),
        "cache_timestamp": (
            bridge.cache_timestamp.isoformat() if bridge.cache_timestamp else None
        ),
        "timestamp": datetime.now().isoformat(),
    }

    return web.json_response(health_data)


async def handle_tools_info(request: Request) -> Response:
    """Get detailed tools information"""
    tools = await bridge.get_tools()

    tools_info = {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema,
            }
            for tool in tools
        ],
        "count": len(tools),
        "cache_timestamp": (
            bridge.cache_timestamp.isoformat() if bridge.cache_timestamp else None
        ),
    }

    return web.json_response(tools_info)


def create_app(atdf_server_url: str) -> web.Application:
    """Create the web application"""
    global bridge
    bridge = MCPATDFBridge(atdf_server_url)

    app = web.Application()

    # MCP endpoints
    app.router.add_post("/mcp", handle_mcp_request)
    app.router.add_get("/sse", handle_sse)

    # Info endpoints
    app.router.add_get("/health", handle_health)
    app.router.add_get("/tools", handle_tools_info)

    # CORS support
    @web.middleware
    async def cors_handler(request, handler):
        response = await handler(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    app.middlewares.append(cors_handler)

    return app


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MCP-ATDF Bridge Server")
    parser.add_argument(
        "--port", type=int, default=8001, help="Server port (default: 8001)"
    )
    parser.add_argument(
        "--host", default="localhost", help="Server host (default: localhost)"
    )
    parser.add_argument(
        "--atdf-server",
        default="http://localhost:8000",
        help="ATDF server URL (default: http://localhost:8000)",
    )

    args = parser.parse_args()

    app = create_app(args.atdf_server)

    logger.info(f"Starting MCP-ATDF Bridge Server on {args.host}:{args.port}")
    logger.info(f"ATDF Server: {args.atdf_server}")
    logger.info(f"MCP Endpoint: http://{args.host}:{args.port}/mcp")
    logger.info(f"SSE Endpoint: http://{args.host}:{args.port}/sse")
    logger.info(f"Health Check: http://{args.host}:{args.port}/health")

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, args.host, args.port)
    await site.start()

    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
