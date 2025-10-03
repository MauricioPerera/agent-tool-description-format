#!/usr/bin/env python3
"""
BMAD-METHOD Integration for ATDF Project
========================================

This module provides integration between BMAD-METHOD framework and the
Agent Tool Description Format (ATDF) project, enabling AI agents to work
with ATDF schemas and tools in a structured, methodical way.

Features:
- BMAD-compatible tool descriptions using ATDF format
- Agent-specific tool generation for ATDF domain
- Integration with existing ATDF schemas and validation
- Support for BMAD workflows and agent collaboration

Author: ATDF Team
Version: 1.0.0
License: MIT
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BMadATDFIntegration:
    """
    Main integration class for BMAD-METHOD and ATDF

    This class provides methods to:
    1. Generate BMAD-compatible tool descriptions using ATDF format
    2. Create agent-specific tools for ATDF development
    3. Validate ATDF compliance in BMAD workflows
    4. Setup BMAD environment for ATDF project
    """

    def __init__(self, project_root: Optional[str] = None):
        """Initialize the integration with project paths"""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.schema_dir = self.project_root / "schema"
        self.tools_dir = self.project_root / "tools"
        self.bmad_dir = self.project_root / "bmad"
        self.examples_dir = self.project_root / "examples"

        # Ensure directories exist
        self.bmad_dir.mkdir(exist_ok=True)
        (self.bmad_dir / "tools").mkdir(exist_ok=True)
        (self.bmad_dir / "agents").mkdir(exist_ok=True)
        (self.bmad_dir / "workflows").mkdir(exist_ok=True)

        # Load ATDF schemas
        self.atdf_schema = self._load_atdf_schema()
        self.enhanced_schema = self._load_enhanced_schema()

        logger.info(
            f"BMad-ATDF Integration initialized for project: {self.project_root}"
        )

    def _load_atdf_schema(self) -> Optional[Dict[str, Any]]:
        """Load the main ATDF schema"""
        schema_path = self.schema_dir / "atdf_schema.json"
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as f:
                return json.load(f)
        logger.warning(f"ATDF schema not found at {schema_path}")
        return None

    def _load_enhanced_schema(self) -> Optional[Dict[str, Any]]:
        """Load the enhanced ATDF schema"""
        schema_path = self.schema_dir / "enhanced_atdf_schema.json"
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as f:
                return json.load(f)
        logger.warning(f"Enhanced ATDF schema not found at {schema_path}")
        return None

    def create_bmad_tool_description(
        self,
        tool_name: str,
        description: str,
        parameters: Dict[str, Any],
        agent_type: str = "general",
        examples: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Create a BMAD-compatible tool description using ATDF format

        Args:
            tool_name: Unique identifier for the tool
            description: Human-readable description
            parameters: JSON Schema parameters
            agent_type: Type of agent this tool is for (analyst, pm, architect, dev, qa)
            examples: Optional usage examples

        Returns:
            ATDF-compliant tool description for BMAD agents
        """
        tool_description = {
            "tools": [
                {
                    "name": tool_name,
                    "description": description,
                    "version": "1.0.0",
                    "tags": [
                        "bmad-generated",
                        "atdf-compliant",
                        f"agent-{agent_type}",
                        "ai-development",
                    ],
                    "inputSchema": {
                        "type": "object",
                        "properties": parameters,
                        "required": list(parameters.keys()),
                    },
                    "bmad_metadata": {
                        "agent_compatible": True,
                        "agent_type": agent_type,
                        "error_format": "atdf",
                        "framework": "bmad-method",
                        "domain": "atdf-development",
                        "created_at": datetime.now().isoformat(),
                        "integration_version": "1.0.0",
                    },
                }
            ]
        }

        # Add examples if provided
        if examples:
            tool_description["tools"][0]["examples"] = examples

        return tool_description

    def generate_analyst_tools(self) -> List[Dict[str, Any]]:
        """Generate ATDF tools for the Analyst agent"""
        tools = []

        # Schema Analysis Tool
        tools.append(
            self.create_bmad_tool_description(
                "analyze_atdf_schema",
                "Analyze ATDF schema for improvements, compliance, and optimization opportunities",
                {
                    "schema_file": {
                        "type": "string",
                        "description": "Path to ATDF schema file to analyze",
                        "default": "schema/atdf_schema.json",
                    },
                    "focus_areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific areas to analyze (validation, errors, interoperability, etc.)",
                        "default": ["validation", "error_handling", "interoperability"],
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["json", "markdown", "yaml"],
                        "description": "Format for analysis output",
                        "default": "markdown",
                    },
                },
                "analyst",
                [
                    {
                        "name": "Basic schema analysis",
                        "input": {
                            "schema_file": "schema/atdf_schema.json",
                            "focus_areas": ["validation", "error_handling"],
                            "output_format": "markdown",
                        },
                    }
                ],
            )
        )

        # Market Research Tool
        tools.append(
            self.create_bmad_tool_description(
                "research_tool_standards",
                "Research existing tool description standards and compare with ATDF",
                {
                    "standards_to_compare": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Standards to compare (OpenAPI, JSON Schema, MCP, etc.)",
                        "default": ["openapi", "json-schema", "mcp", "zapier"],
                    },
                    "comparison_criteria": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Criteria for comparison",
                        "default": [
                            "expressiveness",
                            "validation",
                            "error_handling",
                            "adoption",
                        ],
                    },
                },
                "analyst",
            )
        )

        return tools

    def generate_pm_tools(self) -> List[Dict[str, Any]]:
        """Generate ATDF tools for the Project Manager agent"""
        tools = []

        # Requirements Creation Tool
        tools.append(
            self.create_bmad_tool_description(
                "create_atdf_requirements",
                "Create detailed requirements document for ATDF enhancements",
                {
                    "current_version": {
                        "type": "string",
                        "description": "Current ATDF version",
                        "default": "2.0.0",
                    },
                    "target_features": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Features to implement in next version",
                    },
                    "stakeholders": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Key stakeholders to consider",
                        "default": ["developers", "ai_agents", "tool_creators"],
                    },
                    "priority_level": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Priority level for the requirements",
                        "default": "medium",
                    },
                },
                "pm",
            )
        )

        # Migration Planning Tool
        tools.append(
            self.create_bmad_tool_description(
                "plan_atdf_migration",
                "Plan migration strategy for existing tools to new ATDF version",
                {
                    "from_version": {
                        "type": "string",
                        "description": "Source ATDF version",
                    },
                    "to_version": {
                        "type": "string",
                        "description": "Target ATDF version",
                    },
                    "breaking_changes": {
                        "type": "boolean",
                        "description": "Whether migration includes breaking changes",
                        "default": False,
                    },
                    "timeline_weeks": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 52,
                        "description": "Timeline for migration in weeks",
                        "default": 4,
                    },
                },
                "pm",
            )
        )

        return tools

    def generate_architect_tools(self) -> List[Dict[str, Any]]:
        """Generate ATDF tools for the Architect agent"""
        tools = []

        # Schema Design Tool
        tools.append(
            self.create_bmad_tool_description(
                "design_atdf_schema",
                "Design new ATDF schema components with architectural best practices",
                {
                    "component_type": {
                        "type": "string",
                        "enum": [
                            "tool_description",
                            "error_response",
                            "metadata",
                            "validation",
                        ],
                        "description": "Type of schema component to design",
                    },
                    "requirements": {
                        "type": "object",
                        "description": "Functional and non-functional requirements",
                    },
                    "compatibility_targets": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Systems/frameworks to maintain compatibility with",
                        "default": ["mcp", "openapi", "json-schema"],
                    },
                    "performance_constraints": {
                        "type": "object",
                        "properties": {
                            "max_validation_time_ms": {
                                "type": "integer",
                                "default": 100,
                            },
                            "max_schema_size_kb": {"type": "integer", "default": 50},
                        },
                    },
                },
                "architect",
            )
        )

        # Integration Architecture Tool
        tools.append(
            self.create_bmad_tool_description(
                "design_integration_architecture",
                "Design architecture for integrating ATDF with external systems",
                {
                    "target_system": {
                        "type": "string",
                        "description": "System to integrate with (FastAPI, N8N, Zapier, etc.)",
                    },
                    "integration_pattern": {
                        "type": "string",
                        "enum": ["adapter", "bridge", "gateway", "proxy"],
                        "description": "Integration pattern to use",
                        "default": "adapter",
                    },
                    "data_flow_direction": {
                        "type": "string",
                        "enum": ["bidirectional", "inbound", "outbound"],
                        "description": "Direction of data flow",
                        "default": "bidirectional",
                    },
                },
                "architect",
            )
        )

        return tools

    def generate_dev_tools(self) -> List[Dict[str, Any]]:
        """Generate ATDF tools for the Developer agent"""
        tools = []

        # Code Generation Tool
        tools.append(
            self.create_bmad_tool_description(
                "generate_atdf_implementation",
                "Generate code implementation for ATDF schemas and validators",
                {
                    "target_language": {
                        "type": "string",
                        "enum": [
                            "python",
                            "javascript",
                            "typescript",
                            "java",
                            "csharp",
                        ],
                        "description": "Programming language for implementation",
                        "default": "python",
                    },
                    "component_type": {
                        "type": "string",
                        "enum": ["validator", "parser", "generator", "converter"],
                        "description": "Type of component to implement",
                    },
                    "framework": {
                        "type": "string",
                        "description": "Target framework (fastapi, express, spring, etc.)",
                        "default": "fastapi",
                    },
                    "include_tests": {
                        "type": "boolean",
                        "description": "Whether to generate unit tests",
                        "default": True,
                    },
                },
                "dev",
            )
        )

        # Testing Tool
        tools.append(
            self.create_bmad_tool_description(
                "create_atdf_tests",
                "Create comprehensive test suites for ATDF implementations",
                {
                    "test_type": {
                        "type": "string",
                        "enum": ["unit", "integration", "performance", "compatibility"],
                        "description": "Type of tests to create",
                    },
                    "coverage_target": {
                        "type": "integer",
                        "minimum": 70,
                        "maximum": 100,
                        "description": "Target code coverage percentage",
                        "default": 85,
                    },
                    "test_framework": {
                        "type": "string",
                        "description": "Testing framework to use",
                        "default": "pytest",
                    },
                },
                "dev",
            )
        )

        return tools

    def generate_qa_tools(self) -> List[Dict[str, Any]]:
        """Generate ATDF tools for the QA agent"""
        tools = []

        # Validation Testing Tool
        tools.append(
            self.create_bmad_tool_description(
                "test_atdf_validation",
                "Test ATDF schema validation across different scenarios",
                {
                    "test_scenarios": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Validation scenarios to test",
                        "default": [
                            "valid_input",
                            "invalid_input",
                            "edge_cases",
                            "malformed_data",
                        ],
                    },
                    "schema_version": {
                        "type": "string",
                        "description": "ATDF schema version to test against",
                        "default": "latest",
                    },
                    "generate_report": {
                        "type": "boolean",
                        "description": "Whether to generate detailed test report",
                        "default": True,
                    },
                },
                "qa",
            )
        )

        return tools

    def generate_all_agent_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate all ATDF tools for all BMAD agents"""
        return {
            "analyst": self.generate_analyst_tools(),
            "pm": self.generate_pm_tools(),
            "architect": self.generate_architect_tools(),
            "dev": self.generate_dev_tools(),
            "qa": self.generate_qa_tools(),
        }

    def save_agent_tools(
        self, tools_by_agent: Optional[Dict[str, List[Dict[str, Any]]]] = None
    ):
        """Save agent tools to BMAD directory structure"""
        if tools_by_agent is None:
            tools_by_agent = self.generate_all_agent_tools()

        for agent_type, tools in tools_by_agent.items():
            # Save individual agent tools
            agent_file = self.bmad_dir / "tools" / f"{agent_type}_atdf_tools.json"
            with open(agent_file, "w", encoding="utf-8") as f:
                json.dump({"tools": tools}, f, indent=2, ensure_ascii=False)

            logger.info(
                f"Saved {len(tools)} tools for {agent_type} agent: {agent_file}"
            )

        # Save combined tools file
        all_tools = []
        for tools in tools_by_agent.values():
            all_tools.extend(tools)

        combined_file = self.bmad_dir / "tools" / "atdf_all_tools.json"
        with open(combined_file, "w", encoding="utf-8") as f:
            json.dump({"tools": all_tools}, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(all_tools)} total tools: {combined_file}")

    def create_bmad_project_brief(self) -> str:
        """Create a BMAD project brief for ATDF development"""
        brief = f"""# ATDF Project Brief for BMAD-METHOD

## Project Overview
**Project Name**: Agent Tool Description Format (ATDF) Enhancement
**Version**: 2.0.0
**Domain**: AI Agent Tool Standardization
**Framework**: BMAD-METHOD Integration

## Current State
- ✅ ATDF specification v2.0 implemented
- ✅ FastAPI integration with MCP protocol
- ✅ Comprehensive error handling system
- ✅ Multi-language support (Python, JavaScript)
- ✅ Vector search capabilities
- ✅ Extensive test coverage (85%+)

## Enhancement Goals
1. **BMAD Integration**: Seamless integration with BMAD-METHOD framework
2. **Agent Collaboration**: Enable AI agents to work with ATDF tools
3. **Workflow Automation**: Automated ATDF development workflows
4. **Quality Assurance**: Enhanced testing and validation
5. **Documentation**: Comprehensive BMAD-ATDF documentation

## Key Stakeholders
- **Developers**: Using ATDF for tool descriptions
- **AI Agents**: Consuming ATDF-formatted tools
- **Framework Creators**: Integrating ATDF into their systems
- **BMAD Community**: Leveraging ATDF for agent development

## Success Criteria
- [ ] BMAD agents can generate ATDF-compliant tools
- [ ] Automated workflows for ATDF enhancement
- [ ] 90%+ test coverage maintained
- [ ] Documentation updated for BMAD integration
- [ ] Community adoption of BMAD-ATDF integration

## Technical Constraints
- Must maintain backwards compatibility with ATDF v1.x
- Must support existing FastAPI/MCP integration
- Must work across Python 3.8+ and Node.js 20+
- Must maintain current performance benchmarks

## Timeline
- **Phase 1**: BMAD setup and basic integration (Week 1)
- **Phase 2**: Agent tools and workflows (Week 2-3)
- **Phase 3**: Testing and documentation (Week 4)
- **Phase 4**: Community rollout (Week 5-6)

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return brief

    def setup_bmad_environment(self):
        """Setup complete BMAD environment for ATDF project"""
        logger.info("Setting up BMAD environment for ATDF project...")

        # Generate and save all agent tools
        self.save_agent_tools()

        # Create project brief
        brief_file = self.bmad_dir / "project_brief.md"
        with open(brief_file, "w", encoding="utf-8") as f:
            f.write(self.create_bmad_project_brief())
        logger.info(f"Created project brief: {brief_file}")

        # Create BMAD status file
        status = {
            "bmad_integration": {
                "status": "active",
                "version": "1.0.0",
                "setup_date": datetime.now().isoformat(),
                "project_type": "api-framework",
                "primary_language": "python",
                "agents_configured": ["analyst", "pm", "architect", "dev", "qa"],
                "tools_generated": sum(
                    len(tools) for tools in self.generate_all_agent_tools().values()
                ),
                "workflows_available": [
                    "schema_enhancement",
                    "tool_integration",
                    "error_handling_improvement",
                ],
            }
        }

        status_file = self.bmad_dir / "bmad_status.json"
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
        logger.info(f"Created BMAD status file: {status_file}")

        logger.info("✅ BMAD-ATDF integration setup complete!")
        return True


def main():
    """Main function to setup BMAD-ATDF integration"""
    print("🚀 Setting up BMAD-METHOD integration for ATDF project...")
    print("=" * 60)

    try:
        # Initialize integration
        integration = BMadATDFIntegration()

        # Setup BMAD environment
        integration.setup_bmad_environment()

        print("\n✅ BMAD-ATDF Integration Setup Complete!")
        print("\n📋 Next Steps:")
        print("1. Install BMAD-METHOD: npm run install:bmad")
        print("2. Visit https://gemini.google.com or https://chat.openai.com")
        print("3. Upload bmad-orchestrator.md file")
        print("4. Start with: *help or *analyst")
        print("\n📚 Documentation:")
        print("- BMAD Tools: ./bmad/tools/")
        print("- Project Brief: ./bmad/project_brief.md")
        print("- ATDF Specification: ./docs/ATDF_SPECIFICATION.md")

    except Exception as e:
        logger.error(f"Error setting up BMAD integration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
