# CLAUDE.md - AI Assistant Guide for ATDF Repository

## Project Overview

**Agent Tool Description Format (ATDF)** is an open standard for describing AI agent tools and handling error responses in a standardized way. This repository provides:

- **Code-agnostic JSON templates** that work independently of programming language, framework, or tool
- **Standardized error handling templates** with enriched context and suggested corrections
- **Universal interoperability** across code-based (Python, JavaScript, Java) and no-code tools (n8n, Zapier)
- **MCP (Model Context Protocol) integration** for seamless AI agent interactions
- **Multilingual support** (English, Spanish, Portuguese)
- **Vector search capabilities** for semantic tool discovery

**Version**: 2.0.0
**License**: MIT
**Primary Language**: Python 3.9+
**Framework**: FastAPI

---

## Directory Structure

```
agent-tool-description-format/
├── sdk/                      # Core SDK and utilities
│   ├── core/                # Pydantic models and utilities
│   │   ├── schema.py       # ATDFTool, ATDFToolParameter models
│   │   └── utils.py        # Tool loading and validation
│   ├── atdf_sdk.py         # Main SDK with ATDFToolbox class
│   └── vector_search/      # LanceDB + Sentence Transformers
│       └── vector_store.py # Async vector storage for semantic search
│
├── selector/                # FastAPI tool selector service
│   ├── api.py              # Tool recommendation API (v0.2.0)
│   ├── catalog.py          # Multi-source tool catalog management
│   ├── ranker.py           # Heuristic-based tool ranking
│   └── storage.py          # SQLite persistence layer
│
├── tools/                   # Development and conversion tools
│   ├── validator.py        # Smart schema validation (auto-detects version)
│   ├── validate_enhanced.py # Enhanced schema validation
│   ├── converter.py        # Format conversion utilities
│   ├── mcp_converter.py    # MCP to ATDF conversion
│   ├── enhanced_loader.py  # Advanced tool loading with caching
│   ├── generate_docs.py    # Auto-documentation generation
│   └── demo/               # Agent examples and demonstrations
│
├── tests/                   # Comprehensive test suite
│   ├── run_all_tests.py    # Test orchestrator
│   ├── test_atdf_complete.py        # Core SDK tests
│   ├── test_enhanced_features.py    # Enhanced schema tests
│   ├── test_trilingual_agent.py     # Multilingual tests
│   ├── test_vector_search.py        # Vector search tests
│   ├── test_integration.py          # End-to-end integration tests
│   ├── test_validator.py            # Validation tests
│   └── test_ardf_mcp_server.py      # ARDF server tests
│
├── examples/                # Example implementations
│   ├── fastapi_mcp_integration.py   # Complete reference server with MCP
│   ├── mcp_atdf_bridge.py          # Bridge server for n8n integration
│   ├── enriched_responses_example.py # Rich error handling examples
│   ├── validation_patterns.py       # Validation best practices
│   ├── real_world_integration.py    # Production-ready patterns
│   ├── vector_search_example.py     # Semantic search setup
│   ├── demo_atdf_errors.py         # Error handling showcase
│   └── atdf-mcp-client/            # TypeScript MCP client
│
├── schema/                  # JSON Schema definitions
│   ├── atdf_schema.json    # Basic ATDF 1.x schema
│   ├── enhanced_atdf_schema.json    # Enhanced ATDF 2.x schema
│   ├── ardf.schema.json    # ARDF v1.0.0 schema (https://ardf.io/schema/v1)
│   ├── enriched_response_schema.json # Error response format
│   └── examples/           # Example tool descriptors
│
├── docs/                    # Multilingual documentation
│   ├── en/                 # English documentation
│   ├── es/                 # Spanish documentation
│   ├── pt/                 # Portuguese documentation
│   ├── aep/                # Architecture Enhancement Proposals
│   ├── ATDF_SPECIFICATION.md
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── BEST_PRACTICES.md
│   └── examples.md
│
├── n8n-nodes-ardf/         # n8n ARDF native nodes
│   └── nodes/              # ArdfExecutor, ArdfFilter, ArdfWorkflowRunner
│
├── n8n-nodes-atdf-mcp/     # n8n ATDF-MCP integration nodes
│   ├── nodes/              # AtdfMcpClient, AtdfMcpServer, AtdfToolSelector
│   ├── credentials/        # API credentials definitions
│   └── examples/           # Usage examples
│
├── n8n-workflows/          # Pre-built n8n workflows
│   ├── complete-travel-booking.json
│   ├── hotel-reservation-workflow.json
│   └── flight-booking-workflow.json
│
├── cli/                     # Command-line interface
├── scripts/                # Utility scripts
├── bmad/                   # Build, Measure, Analyze, Deliver tooling
│   ├── agents/            # Agent definitions
│   ├── tools/             # BMAD tools
│   ├── workflows/         # BMAD workflows
│   └── deliverables/      # Project deliverables
│
├── monitoring/             # Grafana dashboards and monitoring
├── ardf-manager/          # ARDF management application
└── server_ardf_mcp.py     # ARDF MCP server (FastAPI)
```

---

## Key Technologies

### Core Stack
- **Python 3.9+**: Primary development language
- **FastAPI**: High-performance async web framework
- **Pydantic 2.x**: Data validation and schema enforcement
- **Uvicorn**: ASGI server for production deployment

### Validation & Standards
- **jsonschema 4.0+**: JSON Schema validation (draft-07/2020-12)
- **JSON Schema**: Validation against ATDF/ARDF schemas
- **PyYAML**: YAML descriptor support

### Optional Features
- **LanceDB**: Vector database for semantic search
- **Sentence-Transformers**: Embedding generation (all-MiniLM-L6-v2)
- **NumPy & Pandas**: Data manipulation

### Testing & Quality
- **pytest**: Testing framework with coverage tracking
- **pytest-asyncio**: Async test support
- **black**: Code formatting (line length: 88)
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security scanning
- **safety**: Dependency vulnerability scanning

### Integration Technologies
- **n8n**: Workflow automation platform
- **MCP (Model Context Protocol)**: AI agent communication
- **Docker**: Containerization
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards

---

## Schema Versions and Formats

### 1. ATDF Schema 1.x (Basic)
**File**: `schema/atdf_schema.json`

**Structure**:
```json
{
  "schema_version": "1.0.0",
  "tool_id": "unique_tool_identifier",
  "description": "Clear, concise tool description",
  "when_to_use": "Scenarios when this tool should be invoked",
  "how_to_use": {
    "inputs": [
      {
        "name": "parameter_name",
        "type": "string|integer|boolean|object|array",
        "description": "Parameter description",
        "required": true
      }
    ],
    "outputs": {
      "success": "Success message template",
      "failure": [
        {
          "code": "ERROR_CODE",
          "description": "Error description"
        }
      ]
    }
  }
}
```

**Use When**: Building simple tools without complex metadata requirements.

### 2. ATDF Schema 2.x (Enhanced)
**File**: `schema/enhanced_atdf_schema.json`

**Additional Fields**:
- `metadata`: version, author, tags, category, created_at, updated_at
- `localization`: Multi-language support (e.g., "en", "es-MX", "pt-BR")
- `prerequisites`: tools, conditions, permissions required
- `feedback`: progress_indicator, completion_signal
- `examples`: Array of goal/input/expected_result examples

**Use When**: Building production tools requiring localization, metadata tracking, or complex prerequisites.

### 3. ARDF Schema v1.0.0
**File**: `schema/ardf.schema.json`
**Canonical ID**: `https://ardf.io/schema/v1`

**Resource Types**: tool, prompt, document, workflow, policy, model, dataset, connector, custom

**Key Features**:
- Content types with structured data
- Maturity levels (experimental, beta, stable, deprecated)
- Resources: `dataset` requires `content.type = "dataset/spec"`
- Resources: `connector` requires `content.type = "connector/spec"` with endpoints

**Use When**: Working with diverse AI resources beyond tools (prompts, workflows, datasets).

### 4. Enriched Response Schema
**File**: `schema/enriched_response_schema.json`

**Structure**:
```json
{
  "status": "error",
  "data": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "problematic_field",
      "received": { /* actual value */ },
      "expected": { /* expected format/value */ },
      "solution": "Suggested fix"
    }
  },
  "meta": {
    "timestamp": "ISO 8601 timestamp"
  }
}
```

---

## Development Workflows

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/MauricioPerera/agent-tool-description-format.git
cd agent-tool-description-format

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg

# Optional: Install vector search dependencies
pip install -r requirements-vector.txt
```

### Running the Server

```bash
# Development mode with auto-reload (use with caution on Windows)
uvicorn examples.fastapi_mcp_integration:app --reload --port 8000

# Production mode without auto-reload (recommended)
uvicorn examples.fastapi_mcp_integration:app --no-reload --port 8000

# Using npm scripts
npm run dev        # Development with reload
npm run dev:safe   # Development without reload

# Using Makefile
make dev-up        # Start development environment with Docker
```

**Important Windows Note**: The `--reload` flag can cause infinite reload loops on Windows/MINGW64 due to WatchFiles bugs. Always prefer `--no-reload` or limit `--reload-dir` to source code only.

### Running Tests

```bash
# Run all tests with coverage
pytest tests/ -v --cov=sdk --cov=tools --cov=examples --cov-report=xml

# Run specific test suites
pytest tests/test_atdf_complete.py -v
pytest tests/test_enhanced_features.py -v
pytest tests/test_vector_search.py -v

# Run all tests using the orchestrator
python tests/run_all_tests.py

# Run integration tests
python examples/test_fastapi_mcp.py

# Using npm
npm test

# Using Makefile
make test
make test-coverage
make test-integration
```

### Code Quality Checks

```bash
# Format code
black .
isort .

# Check formatting
black --check .
isort --check-only .

# Lint code
flake8 .

# Type checking
mypy sdk/ tools/ examples/ --ignore-missing-imports

# Security scanning
safety check
bandit -r sdk/ tools/ examples/

# Using Makefile
make format        # Auto-format code
make format-check  # Check formatting only
make lint          # Run all linting
make security-scan # Run security checks
```

### Validation

```bash
# Validate ATDF descriptor (auto-detects schema version)
python tools/validator.py path/to/tool.json

# Validate with specific schema
python tools/validator.py path/to/tool.json --schema schema/atdf_schema.json

# Smart validation (enhanced features)
python tools/validate_enhanced.py path/to/tool.json

# Using CLI
atdf validate path/to/tool.json --smart
```

### Conversion

```bash
# Convert MCP tool to ATDF
python tools/mcp_converter.py input.json output.json

# Convert to enhanced format
python tools/converter.py --input basic.json --output enhanced.json --enhanced
```

---

## Key Conventions and Patterns

### 1. Code Style
- **Line Length**: 88 characters (Black default)
- **Import Order**: stdlib → third-party → first-party (isort with Black profile)
- **Type Hints**: Required for all public functions
- **Docstrings**: Google-style docstrings for all public APIs

### 2. Async/Await
- Use `async def` for all I/O operations
- FastAPI endpoints should be async when calling async functions
- Vector search operations are fully async

```python
# Good
async def search_tools(query: str) -> List[ATDFTool]:
    vector_store = await VectorStore.create()
    results = await vector_store.search(query, top_k=5)
    return results

# Bad (synchronous when should be async)
def search_tools(query: str) -> List[ATDFTool]:
    vector_store = VectorStore()  # Blocking!
    return vector_store.search(query)
```

### 3. Error Handling

**Always use ATDF enriched error format**:

```python
from fastapi import HTTPException
from pydantic import BaseModel

class ATDFErrorDetail(BaseModel):
    type: str
    title: str
    detail: str
    instance: str
    tool_name: str
    parameter_name: str
    suggested_value: Optional[str] = None
    context: Dict[str, Any]

# Raise errors with context
raise HTTPException(
    status_code=400,
    detail={
        "errors": [
            {
                "type": "https://api.example.com/errors/validation-error",
                "title": "Invalid Date",
                "detail": "Check-in date cannot be in the past",
                "instance": f"/api/errors/{uuid.uuid4()}",
                "tool_name": "hotel_reservation",
                "parameter_name": "check_in",
                "suggested_value": datetime.now().isoformat(),
                "context": {
                    "current_time": datetime.now().isoformat(),
                    "provided_date": check_in
                }
            }
        ]
    }
)
```

### 4. Validation Flow

```python
# 1. Schema validation (automatic with Pydantic)
class HotelReservation(BaseModel):
    guest_name: str
    email: EmailStr
    check_in: datetime
    check_out: datetime
    room_type: Literal["single", "double", "suite"]
    guests: int = Field(ge=1, le=4)

# 2. Business rule validation
def validate_dates(check_in: datetime, check_out: datetime) -> None:
    if check_in < datetime.now():
        raise ValidationError("Check-in date cannot be in the past")
    if check_out <= check_in:
        raise ValidationError("Check-out must be after check-in")

# 3. ATDF error conversion
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return convert_to_atdf_error(exc)
```

### 5. Tool Loading Patterns

```python
from sdk.atdf_sdk import ATDFToolbox
from sdk.core.utils import load_tool

# Pattern 1: Load single tool
tool = load_tool("schema/examples/hole_maker.json")

# Pattern 2: Load multiple tools with toolbox
toolbox = ATDFToolbox()
await toolbox.load_tools_from_directory("schema/examples/")

# Pattern 3: Smart loading with enhanced loader
from tools.enhanced_loader import EnhancedLoader

loader = EnhancedLoader()
tools = loader.load_all_tools(
    directory="schema/examples/",
    languages=["en", "es", "pt"],
    cache=True
)
```

### 6. Vector Search Integration

```python
from sdk.vector_search.vector_store import VectorStore

# Initialize (async)
vector_store = await VectorStore.create(
    db_path="./lancedb",
    embedding_model="all-MiniLM-L6-v2"
)

# Add tools
await vector_store.add_tool(tool)

# Search semantically
results = await vector_store.search(
    query="I need to book a hotel",
    top_k=5,
    language="en"
)
```

### 7. MCP Integration Pattern

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/tools")
async def list_tools():
    """List all tools in MCP-compatible format."""
    return {
        "tools": [
            {
                "name": tool.tool_id,
                "description": tool.description,
                "inputSchema": convert_to_json_schema(tool.how_to_use.inputs)
            }
            for tool in toolbox.get_all_tools()
        ]
    }

@app.post("/tools/{tool_id}/call")
async def execute_tool(tool_id: str, params: dict):
    """Execute tool with ATDF error handling."""
    tool = toolbox.get_tool(tool_id)
    try:
        result = await tool.execute(params)
        return {"status": "success", "data": result}
    except Exception as e:
        return convert_to_atdf_error(e)
```

### 8. n8n Integration Pattern

**Using MCP Bridge**:
```bash
# 1. Start ATDF server
uvicorn examples.fastapi_mcp_integration:app --port 8000

# 2. Start MCP bridge
python examples/mcp_atdf_bridge.py --port 8001 --atdf-server http://localhost:8000

# 3. Configure n8n to use http://localhost:8001
```

**Direct ATDF API Calls**:
```javascript
// In n8n HTTP Request node
{
  "method": "POST",
  "url": "http://localhost:8000/api/hotel/reserve",
  "body": {
    "guest_name": "{{$json.guest_name}}",
    "email": "{{$json.email}}",
    "check_in": "{{$json.check_in}}",
    "check_out": "{{$json.check_out}}",
    "room_type": "{{$json.room_type}}",
    "guests": "{{$json.guests}}"
  }
}
```

### 9. Multilingual Tool Creation

```json
{
  "schema_version": "2.0.0",
  "tool_id": "text_translator",
  "description": "Translate text between languages",
  "localization": {
    "en": {
      "description": "Translate text between languages",
      "when_to_use": "When you need to translate text"
    },
    "es": {
      "description": "Traduce texto entre idiomas",
      "when_to_use": "Cuando necesites traducir texto"
    },
    "pt": {
      "description": "Traduzir texto entre idiomas",
      "when_to_use": "Quando você precisar traduzir texto"
    }
  }
}
```

### 10. Testing Patterns

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_hotel_reservation_success():
    """Test successful hotel reservation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/hotel/reserve",
            json={
                "guest_name": "John Doe",
                "email": "john@example.com",
                "check_in": "2025-12-01T14:00:00Z",
                "check_out": "2025-12-05T12:00:00Z",
                "room_type": "double",
                "guests": 2
            }
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "confirmed"

@pytest.mark.asyncio
async def test_hotel_reservation_validation_error():
    """Test validation error handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/hotel/reserve",
            json={
                "guest_name": "John Doe",
                "email": "invalid-email",  # Invalid email
                "check_in": "2025-12-01T14:00:00Z",
                "check_out": "2025-12-05T12:00:00Z",
                "room_type": "double",
                "guests": 2
            }
        )
    assert response.status_code == 400
    data = response.json()
    assert "errors" in data
    assert data["errors"][0]["type"].endswith("/validation-error")
```

---

## Common Tasks for AI Assistants

### Task 1: Create a New ATDF Tool

1. **Choose schema version**: 1.x (basic) or 2.x (enhanced)
2. **Create descriptor file** in `schema/examples/`
3. **Validate the descriptor**:
   ```bash
   python tools/validator.py schema/examples/my_tool.json
   ```
4. **Test loading**:
   ```python
   from sdk.core.utils import load_tool
   tool = load_tool("schema/examples/my_tool.json")
   ```

### Task 2: Add a New API Endpoint

1. **Define Pydantic models** for request/response
2. **Create endpoint** in `examples/fastapi_mcp_integration.py`
3. **Add ATDF error handling**
4. **Update `/tools` endpoint** to include new tool
5. **Write tests** in `examples/test_fastapi_mcp.py`
6. **Run tests**: `pytest examples/test_fastapi_mcp.py -v`

### Task 3: Convert MCP Tool to ATDF

```bash
python tools/mcp_converter.py mcp_tool.json atdf_tool.json
python tools/validator.py atdf_tool.json
```

### Task 4: Add Multilingual Support

1. **Update tool descriptor** with `localization` field
2. **Add translations** for description, when_to_use, etc.
3. **Test with trilingual agent**:
   ```bash
   pytest tests/test_trilingual_agent.py -v
   ```

### Task 5: Create n8n Integration

1. **Start ATDF server**: `uvicorn examples.fastapi_mcp_integration:app --port 8000`
2. **Start MCP bridge**: `python examples/mcp_atdf_bridge.py --port 8001`
3. **Import workflow** from `n8n-workflows/`
4. **Configure credentials** in n8n

### Task 6: Add Vector Search to Tool

1. **Ensure dependencies**: `pip install -r requirements-vector.txt`
2. **Initialize vector store**:
   ```python
   from sdk.vector_search.vector_store import VectorStore
   vector_store = await VectorStore.create()
   ```
3. **Index tools**: `await vector_store.add_tool(tool)`
4. **Search**: `results = await vector_store.search("query")`

### Task 7: Debug Validation Errors

1. **Check schema version** in descriptor
2. **Run smart validator**: `python tools/validator.py tool.json --smart`
3. **Review error messages** for field paths
4. **Common issues**:
   - Missing required fields (`tool_id`, `description`, `when_to_use`, `how_to_use`)
   - Invalid `schema_version` (should be "1.0.0" or "2.0.0")
   - Incorrect parameter types
   - Additional properties in 1.x schema (set `additionalProperties: false`)

### Task 8: Run Full Test Suite

```bash
# Run all tests
python tests/run_all_tests.py

# Run with coverage
pytest tests/ -v --cov=sdk --cov=tools --cov=examples --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Task 9: Deploy with Docker

```bash
# Build image
docker build -t atdf:latest .

# Run development
docker-compose -f docker-compose.dev.yml up

# Run production
docker-compose up

# Using Makefile
make build
make dev-up
make prod-up
```

### Task 10: Monitor Application

```bash
# Check health
curl http://localhost:8000/health

# View metrics
curl http://localhost:8000/metrics

# Access Grafana
# http://localhost:3000 (default: admin/admin)

# Access Prometheus
# http://localhost:9090

# Using Makefile
make health
make metrics
make monitoring-status
```

---

## Important Notes for AI Assistants

### Do's ✅

1. **Always validate ATDF descriptors** before committing
2. **Use async/await** for all I/O operations
3. **Include ATDF error context** in all error responses
4. **Write tests** for new features and endpoints
5. **Follow Black formatting** (88 character line length)
6. **Add type hints** to all function signatures
7. **Use Pydantic models** for data validation
8. **Check existing examples** before creating new patterns
9. **Update documentation** when adding new features
10. **Run the full test suite** before submitting changes

### Don'ts ❌

1. **Don't use `--reload` on Windows** without `--reload-dir` restriction
2. **Don't skip validation** when creating ATDF descriptors
3. **Don't mix sync and async** code patterns
4. **Don't hardcode values** - use configuration or environment variables
5. **Don't ignore type checking warnings** from mypy
6. **Don't modify schema files** without updating validators
7. **Don't create tools without test coverage**
8. **Don't bypass error handling** - always use ATDF format
9. **Don't commit without running** `black` and `isort`
10. **Don't merge PRs** without CI/CD pipeline passing

### When in Doubt

1. **Check existing examples** in `examples/` directory
2. **Review tests** in `tests/` for usage patterns
3. **Consult documentation** in `docs/`
4. **Run validators** to ensure correctness
5. **Ask for clarification** rather than making assumptions

---

## CI/CD Pipeline

### Workflow Jobs

1. **Code Quality & Linting**:
   - Black formatting check
   - isort import sorting check
   - flake8 linting
   - mypy type checking

2. **Python Tests** (Python 3.9, 3.10, 3.11, 3.12):
   - Full test suite with coverage
   - Coverage upload to Codecov

3. **JavaScript Tests**:
   - npm linting
   - Jest test suite
   - Coverage upload to Codecov

4. **Integration Tests**:
   - Start FastAPI server
   - Run integration test suite
   - Test API endpoints

5. **Security Scan**:
   - safety check (dependencies)
   - bandit (security linting)

6. **Docker Build & Test**:
   - Build Docker image
   - Test containerized application

7. **Deploy** (main branch only):
   - Automated deployment to staging

8. **Release** (tags only):
   - Create GitHub release

### ARDF CI Pipeline

**Triggers**: Push to main/develop, PRs affecting ARDF files

**Steps**:
1. Validate ARDF samples with Python jsonschema
2. Validate ARDF samples with Node.js AJV
3. Start MCP server and health check
4. Verify served schema matches canonical file
5. Run negative validation checks (dataset/connector rules)
6. Run pytest suite
7. Optional n8n smoke test

---

## Useful Commands Quick Reference

```bash
# Development
npm run dev                      # Start dev server with reload
npm run dev:safe                 # Start dev server without reload
make dev-up                      # Docker dev environment

# Testing
pytest tests/ -v                 # Run all tests
python tests/run_all_tests.py   # Test orchestrator
npm test                         # Run JS tests

# Code Quality
black .                          # Format code
isort .                          # Sort imports
flake8 .                         # Lint code
mypy sdk/ tools/ examples/       # Type check

# Validation
atdf validate tool.json --smart  # Smart validation
python tools/validator.py tool.json  # Basic validation

# Conversion
python tools/mcp_converter.py input.json output.json

# Monitoring
make health                      # Check API health
make metrics                     # View Prometheus metrics
make monitoring-status           # Check all services

# Docker
make build                       # Build images
make prod-up                     # Start production
make clean                       # Clean Docker resources

# Database
make db-init                     # Initialize database
make db-backup                   # Backup database
make db-shell                    # Connect to DB shell
```

---

## Resources

- **Main Documentation**: `/docs/`
- **Specification**: `/docs/ATDF_SPECIFICATION.md`
- **Implementation Guide**: `/docs/IMPLEMENTATION_GUIDE.md`
- **Best Practices**: `/docs/BEST_PRACTICES.md`
- **Examples**: `/docs/examples.md`
- **Version Compatibility**: `/docs/en/version_compatibility.md`
- **Integration Flow**: `/docs/atdf_mcp_n8n_integration_flow.md`

---

## Version History

- **v2.0.0**: Enhanced ATDF schema with metadata, localization, prerequisites
- **v1.0.0**: Basic ATDF schema with core functionality
- **ARDF v1.0.0**: Resource-oriented format with canonical schema

---

This guide is maintained for AI assistants working with the ATDF codebase. When making changes, always prioritize code quality, comprehensive testing, and clear documentation.
