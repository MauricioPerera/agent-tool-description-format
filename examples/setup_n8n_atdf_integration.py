#!/usr/bin/env python3
"""
Setup Script for n8n-ATDF Integration
=====================================

This script sets up the complete integration between n8n and ATDF using the MCP bridge.

Features:
- Installs required dependencies
- Configures the MCP-ATDF bridge
- Provides n8n workflow templates
- Tests the integration

Usage:
    python setup_n8n_atdf_integration.py
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import aiohttp


class N8NATDFSetup:
    """Setup class for n8n-ATDF integration"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.examples_dir = Path(__file__).parent

    def print_step(self, step: str):
        """Print setup step"""
        print(f"\n🔧 {step}")
        print("=" * (len(step) + 3))

    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")

    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")

    def print_info(self, message: str):
        """Print info message"""
        print(f"ℹ️  {message}")

    def check_requirements(self):
        """Check system requirements"""
        self.print_step("Checking System Requirements")

        # Check Python version
        if sys.version_info < (3.8, 0):
            self.print_error("Python 3.8+ is required")
            return False
        self.print_success(f"Python {sys.version.split()[0]} ✓")

        # Check n8n installation
        try:
            n8n_binary = shutil.which("n8n")
            if not n8n_binary:
                raise FileNotFoundError("n8n not found")
            result = subprocess.run(
                [n8n_binary, "version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if result.returncode == 0:
                self.print_success("n8n is installed ✓")
            else:
                self.print_error("n8n is not properly installed")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.print_error("n8n is not installed or not in PATH")
            self.print_info("Install n8n with: npm install -g n8n")
            return False

        # Check Node.js
        try:
            node_binary = shutil.which("node")
            if not node_binary:
                raise FileNotFoundError("node not found")
            result = subprocess.run(
                [node_binary, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if result.returncode == 0:
                self.print_success(f"Node.js {result.stdout.strip()} ✓")
            else:
                self.print_error("Node.js is not installed")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.print_error("Node.js is not installed")
            return False

        return True

    def install_dependencies(self):
        """Install Python dependencies"""
        self.print_step("Installing Python Dependencies")

        dependencies = ["aiohttp", "aiohttp-sse", "requests"]

        for dep in dependencies:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep],
                    check=True,
                    capture_output=True,
                    timeout=120,
                )
                self.print_success(f"Installed {dep}")
            except subprocess.TimeoutExpired:
                self.print_error(f"Timed out while installing {dep}")
                return False
            except subprocess.CalledProcessError as exc:
                self.print_error(f"Failed to install {dep}: {exc}")
                return False

        return True

    async def test_atdf_server(self):
        """Test ATDF server connectivity"""
        self.print_step("Testing ATDF Server")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.print_success(
                            f"ATDF Server is running (version {data.get('version', 'unknown')})"
                        )
                        return True
                    else:
                        self.print_error(
                            f"ATDF Server returned status {response.status}"
                        )
                        return False
        except Exception as e:
            self.print_error(f"Cannot connect to ATDF Server: {e}")
            self.print_info(
                "Make sure the ATDF server is running on http://localhost:8000"
            )
            self.print_info("Start it with: python examples/fastapi_mcp_integration.py")
            return False

    def create_bridge_service(self):
        """Create bridge service script"""
        self.print_step("Creating MCP-ATDF Bridge Service")

        service_script = self.examples_dir / "start_mcp_bridge.py"

        script_content = '''#!/usr/bin/env python3
"""
MCP-ATDF Bridge Service Starter
"""

import asyncio
import sys
from pathlib import Path

# Add the examples directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_atdf_bridge import main

if __name__ == '__main__':
    print("🚀 Starting MCP-ATDF Bridge Server...")
    print("📡 Bridge will be available at: http://localhost:8001")
    print("🔗 SSE Endpoint: http://localhost:8001/sse")
    print("❤️  Health Check: http://localhost:8001/health")
    print("\\n🛑 Press Ctrl+C to stop")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n👋 Bridge server stopped")
'''

        with open(service_script, "w") as f:
            f.write(script_content)

        # Make executable on Unix systems
        if os.name != "nt":
            os.chmod(service_script, 0o750)

        self.print_success("Created bridge service script")
        return True

    def create_n8n_workflow_template(self):
        """Create n8n workflow template"""
        self.print_step("Creating n8n Workflow Template")

        template_file = self.examples_dir / "n8n_atdf_workflow_template.json"

        workflow_template = {
            "name": "ATDF Tools Workflow",
            "nodes": [
                {
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "atdf-tools",
                        "responseMode": "responseNode",
                        "options": {},
                    },
                    "id": "webhook-start",
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [240, 300],
                    "webhookId": "atdf-tools-webhook",
                },
                {
                    "parameters": {
                        "sseEndpoint": "http://localhost:8001/sse",
                        "authentication": "none",
                        "toolsToInclude": "all",
                        "options": {"timeout": 30000},
                    },
                    "id": "mcp-atdf-client",
                    "name": "ATDF MCP Client",
                    "type": "n8n-nodes-langchain.toolMcp",
                    "typeVersion": 1,
                    "position": [460, 300],
                },
                {
                    "parameters": {
                        "model": "gpt-4",
                        "options": {
                            "systemMessage": "You are an AI assistant with access to ATDF tools. Use the available tools to help users accomplish their tasks. Always explain what tools you're using and why.",
                            "temperature": 0.7,
                            "maxTokens": 2000,
                        },
                        "prompt": "={{ $json.body.message || 'Hello! How can I help you today?' }}",
                    },
                    "id": "ai-agent-atdf",
                    "name": "AI Agent with ATDF",
                    "type": "n8n-nodes-langchain.agent",
                    "typeVersion": 1,
                    "position": [680, 300],
                },
                {
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": {
                            "success": True,
                            "response": "={{ $json.output }}",
                            "tools_used": "={{ $json.toolsUsed || [] }}",
                            "timestamp": "={{ new Date().toISOString() }}",
                        },
                    },
                    "id": "webhook-response",
                    "name": "Response",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [900, 300],
                },
            ],
            "connections": {
                "Webhook": {
                    "main": [
                        [{"node": "AI Agent with ATDF", "type": "main", "index": 0}]
                    ]
                },
                "AI Agent with ATDF": {
                    "main": [[{"node": "Response", "type": "main", "index": 0}]]
                },
            },
            "settings": {"executionOrder": "v1"},
            "staticData": {},
            "tags": ["ATDF", "MCP", "AI", "Tools"],
            "triggerCount": 1,
            "updatedAt": "2024-01-15T10:00:00.000Z",
            "versionId": "1",
        }

        with open(template_file, "w") as f:
            json.dump(workflow_template, f, indent=2)

        self.print_success("Created n8n workflow template")
        return True

    def create_documentation(self):
        """Create integration documentation"""
        self.print_step("Creating Documentation")

        doc_file = self.examples_dir / "N8N_ATDF_INTEGRATION.md"

        documentation = """# n8n-ATDF Integration Guide

## Overview

This integration allows n8n workflows to use ATDF (Agent Tool Description Format) tools through a Model Context Protocol (MCP) bridge.

## Architecture

```
ATDF Tools → ATDF Server → MCP Bridge → n8n MCP Client Tool → AI Agent
```

## Setup Steps

### 1. Start the ATDF Server

```bash
# Start the ATDF server
python examples/fastapi_mcp_integration.py
```

The ATDF server will be available at `http://localhost:8000`

### 2. Start the MCP-ATDF Bridge

```bash
# Start the bridge server
python examples/start_mcp_bridge.py
```

The bridge will be available at:
- MCP Endpoint: `http://localhost:8001/mcp`
- SSE Endpoint: `http://localhost:8001/sse`
- Health Check: `http://localhost:8001/health`

### 3. Configure n8n Workflow

1. Open n8n (usually at `http://localhost:5678`)
2. Create a new workflow
3. Import the template from `n8n_atdf_workflow_template.json`
4. Or manually add:
   - **MCP Client Tool** node with SSE endpoint: `http://localhost:8001/sse`
   - **AI Agent** node connected to the MCP client
   - **Webhook** trigger for external access

### 4. Test the Integration

```bash
# Test the workflow
curl -X POST http://localhost:5678/webhook/atdf-tools \\
  -H "Content-Type: application/json" \\
  -d '{"message": "What tools are available?"}'
```

## Available Endpoints

### MCP Bridge Endpoints

- `GET /health` - Health check and status
- `GET /tools` - List available ATDF tools
- `GET /sse` - Server-Sent Events for n8n
- `POST /mcp` - MCP JSON-RPC endpoint

### ATDF Server Endpoints

- `GET /health` - ATDF server health
- `GET /tools` - Raw ATDF tools
- `POST /tools/call` - Execute ATDF tool

## Configuration Options

### MCP Client Tool Node

- **SSE Endpoint**: `http://localhost:8001/sse`
- **Authentication**: None (for local development)
- **Tools to Include**: All
- **Timeout**: 30000ms

### AI Agent Node

- **Model**: gpt-4 (or your preferred model)
- **System Message**: Configure to explain ATDF tool usage
- **Temperature**: 0.7
- **Max Tokens**: 2000

## Troubleshooting

### Common Issues

1. **Bridge cannot connect to ATDF server**
   - Ensure ATDF server is running on port 8000
   - Check firewall settings

2. **n8n cannot connect to bridge**
   - Verify bridge is running on port 8001
   - Check SSE endpoint configuration

3. **Tools not appearing in n8n**
   - Check bridge health endpoint
   - Verify ATDF server has tools loaded

### Debug Commands

```bash
# Check ATDF server
curl http://localhost:8000/health

# Check bridge server
curl http://localhost:8001/health

# List available tools
curl http://localhost:8001/tools
```

## Advanced Configuration

### Custom Port Configuration

```bash
# Start bridge on custom port
python examples/mcp_atdf_bridge.py --port 8002 --atdf-server http://localhost:8000
```

### Multiple ATDF Servers

You can run multiple bridge instances for different ATDF servers:

```bash
# Bridge for server 1
python examples/mcp_atdf_bridge.py --port 8001 --atdf-server http://localhost:8000

# Bridge for server 2  
python examples/mcp_atdf_bridge.py --port 8002 --atdf-server http://localhost:8010
```

## Security Considerations

- Use authentication for production deployments
- Configure CORS properly for web access
- Monitor tool execution logs
- Implement rate limiting if needed

## Examples

See the `examples/` directory for:
- Complete workflow templates
- Tool usage examples
- Integration tests
"""

        with open(doc_file, "w") as f:
            f.write(documentation)

        self.print_success("Created integration documentation")
        return True

    async def run_setup(self):
        """Run the complete setup process"""
        print("🚀 n8n-ATDF Integration Setup")
        print("=" * 35)

        # Check requirements
        if not self.check_requirements():
            self.print_error("Requirements check failed")
            return False

        # Install dependencies
        if not self.install_dependencies():
            self.print_error("Dependency installation failed")
            return False

        # Test ATDF server
        if not await self.test_atdf_server():
            self.print_error("ATDF server test failed")
            return False

        # Create bridge service
        if not self.create_bridge_service():
            self.print_error("Bridge service creation failed")
            return False

        # Create workflow template
        if not self.create_n8n_workflow_template():
            self.print_error("Workflow template creation failed")
            return False

        # Create documentation
        if not self.create_documentation():
            self.print_error("Documentation creation failed")
            return False

        # Success message
        self.print_step("Setup Complete! 🎉")
        print("\nNext steps:")
        print("1. Start the MCP-ATDF bridge:")
        print("   python examples/start_mcp_bridge.py")
        print("\n2. Open n8n and import the workflow template:")
        print("   examples/n8n_atdf_workflow_template.json")
        print("\n3. Test the integration:")
        print("   curl -X POST http://localhost:5678/webhook/atdf-tools \\")
        print("     -H 'Content-Type: application/json' \\")
        print('     -d \'{"message": "What tools are available?"}\'')
        print("\n📖 Read the full guide: examples/N8N_ATDF_INTEGRATION.md")

        return True


async def main():
    """Main setup function"""
    setup = N8NATDFSetup()
    success = await setup.run_setup()

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
