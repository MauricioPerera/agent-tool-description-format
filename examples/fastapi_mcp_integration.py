"""FastAPI reference server fulfilling the ATDF Server Profile v1."""

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Literal

from fastapi import Body, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from jsonschema import ValidationError as JSONValidationError
from jsonschema import validators as jsonschema_validators
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from pydantic import BaseModel, EmailStr, Field, ValidationError
from uuid import uuid4

from improved_loader import detect_language, select_tool_by_goal
from tools.mcp_converter import mcp_to_atdf

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = PROJECT_ROOT / "schema"
BASIC_SCHEMA_PATH = SCHEMA_DIR / "atdf_schema.json"
ENHANCED_SCHEMA_PATH = SCHEMA_DIR / "enhanced_atdf_schema.json"


def _load_schema(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


BASIC_SCHEMA = _load_schema(BASIC_SCHEMA_PATH)
ENHANCED_SCHEMA = _load_schema(ENHANCED_SCHEMA_PATH)
ERROR_NAMESPACE = "https://atdf.example.com/errors"
SERVER_START_TIME = time.time()


def _build_tool_catalog() -> Dict[str, Dict[str, Any]]:
    timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    return {
        "hotel_reservation": {
            "tool_id": "hotel_reservation",
            "schema_version": "2.1.0",
            "description": "Create and manage hotel reservations with validation.",
            "when_to_use": "Use when travelers need to book or hold hotel rooms.",
            "metadata": {
                "version": "2.1.0",
                "author": "ATDF Example Team",
                "tags": ["travel", "hospitality", "booking"],
                "category": "travel",
                "created_at": timestamp,
                "updated_at": timestamp,
            },
            "localization": {
                "es": {
                    "description": "Gestiona reservas de hotel con validaciones basicas.",
                    "when_to_use": "Usar cuando clientes necesitan reservar una habitacion.",
                },
                "pt": {
                    "description": "Gerencia reservas de hotel com validacoes basicas.",
                    "when_to_use": "Use quando clientes precisam reservar um quarto.",
                },
            },
            "prerequisites": {
                "tools": ["payment_gateway"],
                "conditions": ["property_inventory_available"],
                "permissions": ["booking:create"],
            },
            "how_to_use": {
                "inputs": [
                    {
                        "name": "guest_name",
                        "type": "string",
                        "description": "Full name for the reservation.",
                        "required": True,
                    },
                    {
                        "name": "email",
                        "type": "string",
                        "description": "Contact email address.",
                        "required": True,
                    },
                    {
                        "name": "check_in",
                        "type": "string",
                        "description": "ISO 8601 check-in date.",
                        "required": True,
                    },
                    {
                        "name": "check_out",
                        "type": "string",
                        "description": "ISO 8601 check-out date.",
                        "required": True,
                    },
                    {
                        "name": "room_type",
                        "type": "string",
                        "description": "Room category to reserve.",
                        "required": True,
                        "schema": {"enum": ["single", "double", "suite"]},
                    },
                    {
                        "name": "guests",
                        "type": "integer",
                        "description": "Number of guests (1-4).",
                        "required": True,
                    },
                ],
                "outputs": {
                    "success": "Reservation confirmed with an identifier.",
                    "failure": [
                        {
                            "code": "invalid_dates",
                            "description": "Check-in must be before check-out and in the future.",
                        },
                        {
                            "code": "invalid_room_type",
                            "description": "Unsupported room type was provided.",
                        },
                        {
                            "code": "capacity_exceeded",
                            "description": "Guest count exceeds the supported capacity.",
                        },
                        {
                            "code": "internal_error",
                            "description": "Unexpected error while creating the reservation.",
                        },
                    ],
                },
            },
            "examples": [
                {
                    "goal": "Book a double room for a two night stay.",
                    "input_values": {
                        "guest_name": "Jamie Green",
                        "email": "jamie@example.com",
                        "check_in": "2025-05-18T15:00:00Z",
                        "check_out": "2025-05-20T11:00:00Z",
                        "room_type": "double",
                        "guests": 2,
                    },
                    "expected_result": "Reservation id with the provided details.",
                }
            ],
            "feedback": {
                "progress_indicators": [
                    "reservation_pending_review",
                    "inventory_checked",
                ],
                "completion_signals": ["reservation_confirmed"],
            },
        },
        "flight_booking": {
            "tool_id": "flight_booking",
            "schema_version": "2.1.0",
            "description": "Plan and confirm commercial flight itineraries.",
            "when_to_use": "Use when travelers need to purchase or hold flight tickets.",
            "metadata": {
                "version": "2.1.0",
                "author": "ATDF Example Team",
                "tags": ["travel", "aviation", "booking"],
                "category": "travel",
                "created_at": timestamp,
                "updated_at": timestamp,
            },
            "localization": {
                "es": {
                    "description": "Gestiona reservas de vuelos con validaciones basicas.",
                    "when_to_use": "Usar cuando clientes necesitan comprar boletos aereos.",
                },
                "pt": {
                    "description": "Gerencia reservas de voos com validacoes basicas.",
                    "when_to_use": "Use quando clientes precisam comprar passagens aereas.",
                },
            },
            "prerequisites": {
                "tools": ["payment_gateway"],
                "conditions": ["iata_airport_directory"],
                "permissions": ["booking:create"],
            },
            "how_to_use": {
                "inputs": [
                    {
                        "name": "passenger_name",
                        "type": "string",
                        "description": "Full name of the passenger.",
                        "required": True,
                    },
                    {
                        "name": "email",
                        "type": "string",
                        "description": "Passenger contact email.",
                        "required": True,
                    },
                    {
                        "name": "departure_city",
                        "type": "string",
                        "description": "Origin city or airport.",
                        "required": True,
                    },
                    {
                        "name": "arrival_city",
                        "type": "string",
                        "description": "Destination city or airport.",
                        "required": True,
                    },
                    {
                        "name": "departure_date",
                        "type": "string",
                        "description": "ISO 8601 departure date.",
                        "required": True,
                    },
                    {
                        "name": "return_date",
                        "type": "string",
                        "description": "ISO 8601 return date when round trip.",
                        "required": False,
                    },
                    {
                        "name": "seat_class",
                        "type": "string",
                        "description": "Cabin preference.",
                        "required": True,
                        "schema": {"enum": ["economy", "business", "first"]},
                    },
                ],
                "outputs": {
                    "success": "Flight booking confirmed with an identifier.",
                    "failure": [
                        {
                            "code": "invalid_dates",
                            "description": "Departure must be in the future and before return.",
                        },
                        {
                            "code": "invalid_route",
                            "description": "Arrival and departure cannot be the same city.",
                        },
                        {
                            "code": "internal_error",
                            "description": "Unexpected error while creating the booking.",
                        },
                    ],
                },
            },
            "examples": [
                {
                    "goal": "Book a round trip ticket from LAX to JFK.",
                    "input_values": {
                        "passenger_name": "Morgan Lee",
                        "email": "morgan@example.com",
                        "departure_city": "LAX",
                        "arrival_city": "JFK",
                        "departure_date": "2025-06-01T09:30:00Z",
                        "return_date": "2025-06-10T14:00:00Z",
                        "seat_class": "economy",
                    },
                    "expected_result": "Booking id with the confirmed itinerary.",
                }
            ],
            "feedback": {
                "progress_indicators": ["itinerary_pending_confirmation"],
                "completion_signals": ["ticket_issued"],
            },
        },
    }


TOOL_CATALOG = _build_tool_catalog()
TOOL_LIST = list(TOOL_CATALOG.values())
SEARCH_KEYWORDS = {
    "hotel_reservation": ["hotel", "stay", "room", "lodging", "suite"],
    "flight_booking": ["flight", "air", "plane", "ticket", "travel"],
}

app = FastAPI(title="ATDF FastAPI MCP Integration", version="2.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUEST_COUNT = Counter(
    "atdf_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status_code"],
)
REQUEST_DURATION = Histogram(
    "atdf_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
)
TOOL_EXECUTIONS = Counter(
    "atdf_tool_executions_total",
    "Total number of tool executions",
    ["tool_name", "status"],
)
TOOL_EXECUTION_DURATION = Histogram(
    "atdf_tool_execution_duration_seconds",
    "Tool execution duration in seconds",
    ["tool_name"],
)
ACTIVE_CONNECTIONS = Gauge(
    "atdf_active_connections",
    "Number of active connections",
)
ERROR_COUNT = Counter(
    "atdf_errors_total",
    "Total number of errors",
    ["error_type", "tool_name"],
)


class ATDFErrorDetail(BaseModel):
    type: str
    title: str
    detail: str
    instance: str
    tool_name: str = Field(default="server")
    parameter_name: Optional[str] = None
    suggested_value: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    code: Optional[str] = None


class ATDFErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    errors: List[ATDFErrorDetail]
    meta: Optional[Dict[str, Any]] = None

    class Config:
        extra = "forbid"


def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def isoformat_utc(dt: datetime) -> str:
    return to_utc(dt).replace(tzinfo=None, microsecond=0).isoformat() + "Z"


def clone_descriptor(descriptor: Dict[str, Any]) -> Dict[str, Any]:
    return json.loads(json.dumps(descriptor))


def infer_tool_name(request: Request) -> str:
    path = request.url.path
    if path.startswith("/api/hotel"):
        return "hotel_reservation"
    if path.startswith("/api/flight"):
        return "flight_booking"
    return "server"


def build_error_detail(
    request: Request,
    *,
    error_type: str,
    title: str,
    detail: str,
    tool_name: str = "server",
    parameter_name: Optional[str] = None,
    suggested_value: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    code: Optional[str] = None,
) -> ATDFErrorDetail:
    return ATDFErrorDetail(
        type=error_type,
        title=title,
        detail=detail,
        instance=f"{request.url.path}#{uuid4()}",
        tool_name=tool_name,
        parameter_name=parameter_name,
        suggested_value=suggested_value,
        context=context,
        code=code,
    )


def create_error_response(
    request: Request,
    *,
    status_code: int,
    errors: List[ATDFErrorDetail],
    meta: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    body = ATDFErrorResponse(errors=errors, meta=meta)
    return JSONResponse(
        status_code=status_code, content=body.model_dump(exclude_none=True)
    )


def create_atdf_error_response(
    error_type: str,
    title: str,
    detail: str,
    tool_name: Optional[str] = None,
    parameter_name: Optional[str] = None,
    suggested_value: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    code: Optional[str] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> JSONResponse:
    detail_payload = ATDFErrorDetail(
        type=error_type,
        title=title,
        detail=detail,
        instance="/errors/" + str(uuid4()),
        tool_name=tool_name or "server",
        parameter_name=parameter_name,
        suggested_value=suggested_value,
        context=context,
        code=code,
    )
    body = ATDFErrorResponse(errors=[detail_payload])
    return JSONResponse(
        status_code=status_code, content=body.model_dump(exclude_none=True)
    )


def resolve_schema(descriptor: Dict[str, Any]) -> Tuple[Dict[str, Any], str, bool]:
    schema_version = str(descriptor.get("schema_version", "")).strip()
    enhanced_keys = {
        "metadata",
        "localization",
        "examples",
        "prerequisites",
        "feedback",
    }
    if schema_version.startswith("2."):
        return ENHANCED_SCHEMA, schema_version, False
    if enhanced_keys.intersection(descriptor.keys()):
        return ENHANCED_SCHEMA, schema_version or "2.x", False
    return BASIC_SCHEMA, schema_version or "1.x", True


def validate_against_schema(
    descriptor: Dict[str, Any],
    schema: Dict[str, Any],
    *,
    ignore_additional: bool,
) -> List[JSONValidationError]:
    base_class = jsonschema_validators.validator_for(schema)
    if ignore_additional:
        validator_class = jsonschema_validators.extend(
            base_class,
            {"additionalProperties": lambda validator, value, instance, schema: None},
        )
    else:
        validator_class = base_class
    validator = validator_class(schema)
    return list(validator.iter_errors(descriptor))


def score_tool_for_query(tool: Dict[str, Any], query: str, language: str) -> float:
    query_lower = query.lower()
    tool_id = tool.get("tool_id", "").lower()
    description = tool.get("description", "").lower()
    tags = [tag.lower() for tag in tool.get("metadata", {}).get("tags", [])]
    score = 0.1
    if tool_id and tool_id in query_lower:
        score += 0.4
    if any(tag in query_lower for tag in tags):
        score += 0.2
    if any(word in query_lower for word in SEARCH_KEYWORDS.get(tool_id, [])):
        score += 0.3
    if language in {"es", "pt"} and tool.get("localization", {}).get(language):
        score += 0.1
    if description and any(word in description for word in query_lower.split()):
        score += 0.1
    return min(score, 1.0)


class HotelReservationRequest(BaseModel):
    guest_name: str = Field(..., min_length=1)
    email: EmailStr
    check_in: datetime
    check_out: datetime
    room_type: Literal["single", "double", "suite"]
    guests: int = Field(..., ge=1, le=4)


class FlightBookingRequest(BaseModel):
    passenger_name: str = Field(..., min_length=1)
    email: EmailStr
    departure_city: str = Field(..., min_length=1)
    arrival_city: str = Field(..., min_length=1)
    departure_date: datetime
    return_date: Optional[datetime] = None
    seat_class: Literal["economy", "business", "first"]


class MCPConvertRequest(BaseModel):
    mcp: Any = Field(..., description="MCP tool descriptor or list of descriptors.")
    enhanced: bool = False
    author: Optional[str] = None

    class Config:
        extra = "forbid"


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    language: Optional[str] = None
    limit: int = Field(default=5, ge=1, le=20)
    filters: Optional[Dict[str, Any]] = None

    class Config:
        extra = "forbid"


hotel_reservations: Dict[str, Dict[str, Any]] = {}
flight_bookings: Dict[str, Dict[str, Any]] = {}


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    ACTIVE_CONNECTIONS.inc()
    start = time.perf_counter()
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception as exc:
        ERROR_COUNT.labels(error_type=type(exc).__name__, tool_name="server").inc()
        raise
    finally:
        duration = time.perf_counter() - start
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=str(status_code),
        ).inc()
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path,
        ).observe(duration)
        ACTIVE_CONNECTIONS.dec()


@app.exception_handler(ValidationError)
async def handle_validation_error(request: Request, exc: ValidationError):
    tool_name = infer_tool_name(request)
    errors = []
    for error in exc.errors():
        parameter_name = ".".join(str(part) for part in error.get("loc", [])) or None
        errors.append(
            build_error_detail(
                request,
                error_type=f"{ERROR_NAMESPACE}/model-validation",
                title="Validation failed",
                detail=error.get("msg", "Invalid value."),
                tool_name=tool_name,
                parameter_name=parameter_name,
                context={
                    "loc": error.get("loc"),
                    "type": error.get("type"),
                    "ctx": error.get("ctx"),
                },
                code="validation_error",
            )
        )
    return create_error_response(
        request, status_code=status.HTTP_400_BAD_REQUEST, errors=errors
    )


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(
    request: Request, exc: RequestValidationError
):
    tool_name = infer_tool_name(request)
    errors = []
    for error in exc.errors():
        parameter_name = ".".join(str(part) for part in error.get("loc", [])) or None
        errors.append(
            build_error_detail(
                request,
                error_type=f"{ERROR_NAMESPACE}/request-validation",
                title="Request payload validation failed",
                detail=error.get("msg", "Invalid request payload."),
                tool_name=tool_name,
                parameter_name=parameter_name,
                context={
                    "loc": error.get("loc"),
                    "type": error.get("type"),
                    "ctx": error.get("ctx"),
                },
                code="validation_error",
            )
        )
    return create_error_response(
        request, status_code=status.HTTP_400_BAD_REQUEST, errors=errors
    )


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    uptime_seconds = int(time.time() - SERVER_START_TIME)
    return {
        "status": "healthy",
        "uptime_seconds": uptime_seconds,
        "version": app.version,
        "timestamp": isoformat_utc(datetime.utcnow()),
        "metrics": {
            "total_hotel_reservations": len(hotel_reservations),
            "total_flight_bookings": len(flight_bookings),
        },
    }


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "message": "ATDF FastAPI MCP Integration",
        "version": app.version,
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "tools": "/tools",
            "tool_detail": "/tools/{tool_id}",
            "validate": "/tools/validate",
            "convert_mcp": "/convert/mcp",
            "search": "/search",
            "hotel_reservation": "/api/hotel/reserve",
            "flight_booking": "/api/flight/book",
        },
    }


@app.get("/tools")
async def list_tools() -> Dict[str, Any]:
    return {"tools": [clone_descriptor(tool) for tool in TOOL_LIST]}


@app.get("/tools/{tool_id}")
async def get_tool(tool_id: str, request: Request) -> Any:
    descriptor = TOOL_CATALOG.get(tool_id)
    if descriptor:
        return clone_descriptor(descriptor)
    error = build_error_detail(
        request,
        error_type=f"{ERROR_NAMESPACE}/tool-not-found",
        title="Tool not found",
        detail=f"Tool '{tool_id}' is not registered in this catalog.",
        tool_name="server",
        code="tool_not_found",
    )
    return create_error_response(
        request, status_code=status.HTTP_404_NOT_FOUND, errors=[error]
    )


@app.post("/tools/validate")
async def validate_tools(request: Request, payload: Any = Body(...)) -> Any:
    descriptors = payload if isinstance(payload, list) else [payload]
    errors: List[ATDFErrorDetail] = []
    results: List[Dict[str, Any]] = []
    for index, descriptor in enumerate(descriptors):
        if not isinstance(descriptor, dict):
            errors.append(
                build_error_detail(
                    request,
                    error_type=f"{ERROR_NAMESPACE}/validation-error",
                    title="Descriptor type is invalid",
                    detail="Each descriptor must be a JSON object.",
                    tool_name="server",
                    parameter_name=f"[{index}]",
                    code="invalid_descriptor",
                )
            )
            continue
        schema, schema_version, ignore_additional = resolve_schema(descriptor)
        schema_errors = validate_against_schema(
            descriptor, schema, ignore_additional=ignore_additional
        )
        if schema_errors:
            for schema_error in schema_errors:
                pointer = ".".join(str(part) for part in schema_error.path) or None
                errors.append(
                    build_error_detail(
                        request,
                        error_type=f"{ERROR_NAMESPACE}/validation-error",
                        title="ATDF descriptor failed validation",
                        detail=schema_error.message,
                        tool_name=descriptor.get("tool_id")
                        or descriptor.get("id")
                        or "server",
                        parameter_name=pointer,
                        context={
                            "json_path": list(schema_error.path),
                            "schema_path": list(schema_error.schema_path),
                        },
                        code="validation_error",
                    )
                )
        else:
            resolved_version = schema_version or (
                "2.x" if schema is ENHANCED_SCHEMA else "1.x"
            )
            results.append(
                {
                    "tool_id": descriptor.get("tool_id") or descriptor.get("id"),
                    "schema_version": resolved_version,
                }
            )
    if errors:
        return create_error_response(
            request, status_code=status.HTTP_400_BAD_REQUEST, errors=errors
        )
    return {"valid": True, "results": results}


@app.post("/convert/mcp")
async def convert_mcp(request: Request, payload: MCPConvertRequest) -> Any:
    try:
        author = payload.author or "MCP Converter"
        if isinstance(payload.mcp, list):
            converted = [
                mcp_to_atdf(tool, enhanced=payload.enhanced, author=author)
                for tool in payload.mcp
            ]
        else:
            converted = mcp_to_atdf(
                payload.mcp, enhanced=payload.enhanced, author=author
            )
        tools = converted if isinstance(converted, list) else [converted]
        return {
            "enhanced": payload.enhanced,
            "tools": tools,
        }
    except ValueError as exc:
        error = build_error_detail(
            request,
            error_type=f"{ERROR_NAMESPACE}/conversion-error",
            title="MCP conversion failed",
            detail=str(exc),
            tool_name="server",
            code="conversion_error",
        )
        return create_error_response(
            request, status_code=status.HTTP_400_BAD_REQUEST, errors=[error]
        )
    except Exception as exc:  # pragma: no cover - unexpected branch
        error = build_error_detail(
            request,
            error_type=f"{ERROR_NAMESPACE}/internal-error",
            title="Unexpected conversion error",
            detail=str(exc),
            tool_name="server",
            code="internal_error",
        )
        return create_error_response(
            request, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, errors=[error]
        )


@app.post("/search")
async def search_tools(request: Request, payload: SearchRequest) -> Dict[str, Any]:
    language = (payload.language or detect_language(payload.query)).lower()
    filters = payload.filters or {}
    requested_tags = {
        str(tag).lower()
        for tag in filters.get("tags", [])
        if isinstance(filters.get("tags"), list)
    }
    requires = {
        str(req).lower()
        for req in filters.get("requires", [])
        if isinstance(filters.get("requires"), list)
    }

    scored_tools: List[Tuple[Dict[str, Any], float]] = []
    for descriptor in TOOL_LIST:
        tags = {tag.lower() for tag in descriptor.get("metadata", {}).get("tags", [])}
        if requested_tags and not requested_tags.intersection(tags):
            continue
        prereq = descriptor.get("prerequisites", {})
        available_requirements = set()
        for bucket in ("permissions", "tools", "conditions"):
            for value in prereq.get(bucket, []):
                available_requirements.add(str(value).lower())
        if requires and not requires.issubset(available_requirements):
            continue
        score = score_tool_for_query(descriptor, payload.query, language)
        scored_tools.append((descriptor, score))

    if not scored_tools:
        primary_tool = select_tool_by_goal(TOOL_LIST, payload.query, language)
        if primary_tool:
            scored_tools.append(
                (
                    primary_tool,
                    score_tool_for_query(primary_tool, payload.query, language),
                )
            )

    scored_tools.sort(key=lambda item: item[1], reverse=True)
    limited = scored_tools[: payload.limit]
    results = [
        {
            "tool_id": descriptor.get("tool_id"),
            "score": round(score, 4),
            "metadata": descriptor.get("metadata", {}),
        }
        for descriptor, score in limited
    ]

    return {
        "query": payload.query,
        "language": language,
        "results": results,
    }


@app.post("/api/hotel/reserve")
async def reserve_hotel(request: Request, payload: HotelReservationRequest) -> Any:
    tool_name = "hotel_reservation"
    start = time.perf_counter()
    try:
        now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
        check_in = to_utc(payload.check_in)
        check_out = to_utc(payload.check_out)
        if check_in < now_utc:
            ERROR_COUNT.labels(error_type="invalid_dates", tool_name=tool_name).inc()
            TOOL_EXECUTIONS.labels(tool_name=tool_name, status="error").inc()
            error = build_error_detail(
                request,
                error_type=f"{ERROR_NAMESPACE}/invalid-date",
                title="Invalid check-in date",
                detail="Check-in must be in the future.",
                tool_name=tool_name,
                parameter_name="check_in",
                suggested_value=isoformat_utc(datetime.utcnow() + timedelta(hours=1)),
                context={"provided": isoformat_utc(check_in)},
                code="invalid_dates",
            )
            return create_error_response(
                request, status_code=status.HTTP_400_BAD_REQUEST, errors=[error]
            )
        if check_out <= check_in:
            ERROR_COUNT.labels(error_type="invalid_dates", tool_name=tool_name).inc()
            TOOL_EXECUTIONS.labels(tool_name=tool_name, status="error").inc()
            error = build_error_detail(
                request,
                error_type=f"{ERROR_NAMESPACE}/invalid-date",
                title="Invalid stay duration",
                detail="Check-out must occur after check-in.",
                tool_name=tool_name,
                parameter_name="check_out",
                suggested_value=isoformat_utc(check_in + timedelta(days=1)),
                context={
                    "check_in": isoformat_utc(check_in),
                    "check_out": isoformat_utc(check_out),
                },
                code="invalid_dates",
            )
            return create_error_response(
                request, status_code=status.HTTP_400_BAD_REQUEST, errors=[error]
            )
        reservation_id = str(uuid4())
        reservation = {
            "reservation_id": reservation_id,
            "guest_name": payload.guest_name,
            "email": payload.email,
            "check_in": isoformat_utc(check_in),
            "check_out": isoformat_utc(check_out),
            "room_type": payload.room_type,
            "guests": payload.guests,
            "status": "confirmed",
            "created_at": isoformat_utc(datetime.utcnow()),
        }
        hotel_reservations[reservation_id] = reservation
        TOOL_EXECUTIONS.labels(tool_name=tool_name, status="success").inc()
        return {
            "reservation_id": reservation_id,
            "status": "confirmed",
            "details": reservation,
        }
    except Exception as exc:
        ERROR_COUNT.labels(error_type="internal_error", tool_name=tool_name).inc()
        TOOL_EXECUTIONS.labels(tool_name=tool_name, status="error").inc()
        error = build_error_detail(
            request,
            error_type=f"{ERROR_NAMESPACE}/internal-error",
            title="Internal server error",
            detail=str(exc),
            tool_name=tool_name,
            code="internal_error",
        )
        return create_error_response(
            request, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, errors=[error]
        )
    finally:
        TOOL_EXECUTION_DURATION.labels(tool_name=tool_name).observe(
            time.perf_counter() - start
        )


@app.post("/api/flight/book")
async def book_flight(request: Request, payload: FlightBookingRequest) -> Any:
    tool_name = "flight_booking"
    start = time.perf_counter()
    try:
        now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
        departure = to_utc(payload.departure_date)
        if departure < now_utc:
            ERROR_COUNT.labels(error_type="invalid_dates", tool_name=tool_name).inc()
            TOOL_EXECUTIONS.labels(tool_name=tool_name, status="error").inc()
            error = build_error_detail(
                request,
                error_type=f"{ERROR_NAMESPACE}/invalid-date",
                title="Invalid departure date",
                detail="Departure must be in the future.",
                tool_name=tool_name,
                parameter_name="departure_date",
                suggested_value=isoformat_utc(datetime.utcnow() + timedelta(hours=2)),
                context={"provided": isoformat_utc(departure)},
                code="invalid_dates",
            )
            return create_error_response(
                request, status_code=status.HTTP_400_BAD_REQUEST, errors=[error]
            )
        if (
            payload.arrival_city.strip().lower()
            == payload.departure_city.strip().lower()
        ):
            ERROR_COUNT.labels(error_type="invalid_route", tool_name=tool_name).inc()
            TOOL_EXECUTIONS.labels(tool_name=tool_name, status="error").inc()
            error = build_error_detail(
                request,
                error_type=f"{ERROR_NAMESPACE}/invalid-route",
                title="Arrival city must differ from departure city",
                detail="Please choose a different arrival city.",
                tool_name=tool_name,
                parameter_name="arrival_city",
                suggested_value=None,
                context={
                    "departure_city": payload.departure_city,
                    "arrival_city": payload.arrival_city,
                },
                code="invalid_route",
            )
            return create_error_response(
                request, status_code=status.HTTP_400_BAD_REQUEST, errors=[error]
            )
        if payload.return_date is not None:
            return_dt = to_utc(payload.return_date)
            if return_dt <= departure:
                ERROR_COUNT.labels(
                    error_type="invalid_dates", tool_name=tool_name
                ).inc()
                TOOL_EXECUTIONS.labels(tool_name=tool_name, status="error").inc()
                error = build_error_detail(
                    request,
                    error_type=f"{ERROR_NAMESPACE}/invalid-date",
                    title="Invalid return date",
                    detail="Return must be scheduled after departure.",
                    tool_name=tool_name,
                    parameter_name="return_date",
                    suggested_value=isoformat_utc(departure + timedelta(days=1)),
                    context={
                        "departure_date": isoformat_utc(departure),
                        "return_date": isoformat_utc(return_dt),
                    },
                    code="invalid_dates",
                )
                return create_error_response(
                    request, status_code=status.HTTP_400_BAD_REQUEST, errors=[error]
                )
        booking_id = str(uuid4())
        booking = {
            "booking_id": booking_id,
            "passenger_name": payload.passenger_name,
            "email": payload.email,
            "departure_city": payload.departure_city,
            "arrival_city": payload.arrival_city,
            "departure_date": isoformat_utc(departure),
            "return_date": (
                isoformat_utc(to_utc(payload.return_date))
                if payload.return_date
                else None
            ),
            "seat_class": payload.seat_class,
            "status": "confirmed",
            "created_at": isoformat_utc(datetime.utcnow()),
        }
        flight_bookings[booking_id] = booking
        TOOL_EXECUTIONS.labels(tool_name=tool_name, status="success").inc()
        return {
            "booking_id": booking_id,
            "status": "confirmed",
            "details": booking,
        }
    except Exception as exc:
        ERROR_COUNT.labels(error_type="internal_error", tool_name=tool_name).inc()
        TOOL_EXECUTIONS.labels(tool_name=tool_name, status="error").inc()
        error = build_error_detail(
            request,
            error_type=f"{ERROR_NAMESPACE}/internal-error",
            title="Internal server error",
            detail=str(exc),
            tool_name=tool_name,
            code="internal_error",
        )
        return create_error_response(
            request, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, errors=[error]
        )
    finally:
        TOOL_EXECUTION_DURATION.labels(tool_name=tool_name).observe(
            time.perf_counter() - start
        )


@app.get("/api/hotel/reservations")
async def list_hotel_reservations() -> Dict[str, Any]:
    return {"reservations": list(hotel_reservations.values())}


@app.get("/api/flight/bookings")
async def list_flight_bookings() -> Dict[str, Any]:
    return {"bookings": list(flight_bookings.values())}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
