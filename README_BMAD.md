# ATDF-BMAD Integration

## Overview
Agent Tool Description Format with BMAD-METHOD integration

**Version:** 1.0.0  
**BMAD Version:** 1.0.0  
**Generated:** 2025-09-30 16:15:25

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
- atdf-specialist
- bmad-orchestrator

## BMAD Workflows
- atdf-enhancement
- tool-integration

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
POST /tools/{tool_name}
```

## Documentation
- [ATDF Specification](schema/atdf_schema.json)
- [BMAD Agents](bmad/agents/)
- [BMAD Workflows](bmad/workflows/)
- [Examples](schema/examples/)

## Support
For issues and questions, please refer to the project documentation or create an issue.
