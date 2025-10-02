#!/usr/bin/env python3
"""
BMAD internal tooling generator
Generates documentation for the ATDF team's BMAD coordination assets
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def load_config():
    """Load BMAD configuration"""
    config_path = Path("bmad.config.yml")
    if not config_path.exists():
        print("❌ bmad.config.yml not found")
        return None
    
    # For simplicity, we'll create a basic config structure
    return {
        "project": {
            "name": "ATDF-BMAD Integration",
            "version": "1.0.0",
            "description": "Agent Tool Description Format with BMAD-METHOD integration"
        },
        "bmad": {
            "version": "1.0.0",
            "agents": ["atdf-specialist", "bmad-orchestrator"],
            "workflows": ["atdf-enhancement", "tool-integration"]
        }
    }

def generate_readme():
    """Generate comprehensive README documentation"""
    config = load_config()
    if not config:
        return False
    
    readme_content = f"""# {config['project']['name']}

## Overview
{config['project']['description']}

**Version:** {config['project']['version']}  
**BMAD Version:** {config['bmad']['version']}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Quick Start

### Installation
```bash
# Windows
install_bmad.bat

# Linux/Mac
chmod +x install_bmad.sh
./install_bmad.sh
```

### Available Commands
```bash
# Check BMAD status
npm run bmad:status

# Validate ATDF tools
npm run bmad:validate

# List available tools
npm run bmad:tools

# Start BMAD server
npm run bmad:start-server

# Generate documentation
npm run bmad:generate-docs

# List workflows
npm run bmad:workflow
```

## BMAD Agents
{chr(10).join(f"- {agent}" for agent in config['bmad']['agents'])}

## BMAD Workflows
{chr(10).join(f"- {workflow}" for workflow in config['bmad']['workflows'])}

## API Endpoints

### Health Check
```
GET /health
```

### List Tools
```
GET /tools
```

### Execute Tool
```
POST /tools/{{tool_name}}
```

## Documentation
- [ATDF Specification](schema/atdf_schema.json)
- [BMAD Agents](bmad/agents/)
- [BMAD Workflows](bmad/workflows/)
- [Examples](schema/examples/)

## Support
For issues and questions, please refer to the project documentation or create an issue.
"""
    
    with open("README_BMAD.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    return True

def generate_api_docs():
    """Generate API documentation"""
    api_docs = {
        "openapi": "3.0.0",
        "info": {
            "title": "ATDF Internal Ops API",
            "version": "1.0.0",
            "description": "Internal API used by the BMAD coordination tooling"
        },
        "servers": [
            {"url": "http://localhost:8000", "description": "Development server"}
        ],
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health check",
                    "responses": {
                        "200": {
                            "description": "Service is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "timestamp": {"type": "string"},
                                            "version": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/tools": {
                "get": {
                    "summary": "List available tools",
                    "responses": {
                        "200": {
                            "description": "List of ATDF tools",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "tools": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/ATDFTool"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "ATDFTool": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "description": {"type": "string"},
                        "when_to_use": {"type": "string"},
                        "inputSchema": {"type": "object"},
                        "metadata": {"type": "object"}
                    }
                }
            }
        }
    }
    
    with open("docs/api.json", "w", encoding="utf-8") as f:
        json.dump(api_docs, f, indent=2)
    
    return True

def main():
    """Main documentation generation function"""
    print("🔧 Generating BMAD internal documentation...")
    
    # Create docs directory
    os.makedirs("docs", exist_ok=True)
    
    # Generate README
    if generate_readme():
        print("✅ README_BMAD.md generated")
    else:
        print("❌ Failed to generate README")
        return 1
    
    # Generate API docs
    if generate_api_docs():
        print("✅ API documentation generated")
    else:
        print("❌ Failed to generate API documentation")
        return 1
    
    print("📚 Documentation generation completed!")
    print("\nGenerated files:")
    print("- README_BMAD.md")
    print("- docs/api.json")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())