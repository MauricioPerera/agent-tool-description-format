from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr, Field, validator, ValidationError
from datetime import datetime, timedelta
from uuid import uuid4
import json
import time
from typing import Dict, List, Optional, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title='ATDF FastAPI MCP Integration', version='2.0.0')

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'atdf_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'atdf_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

TOOL_EXECUTIONS = Counter(
    'atdf_tool_executions_total',
    'Total number of tool executions',
    ['tool_name', 'status']
)

TOOL_EXECUTION_DURATION = Histogram(
    'atdf_tool_execution_duration_seconds',
    'Tool execution duration in seconds',
    ['tool_name']
)

ACTIVE_CONNECTIONS = Gauge(
    'atdf_active_connections',
    'Number of active connections'
)

ERROR_COUNT = Counter(
    'atdf_errors_total',
    'Total number of errors',
    ['error_type', 'tool_name']
)

# Middleware for metrics collection
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Increment active connections
    ACTIVE_CONNECTIONS.inc()
    
    try:
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        endpoint = request.url.path
        method = request.method
        status_code = response.status_code
        
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        return response
    
    except Exception as e:
        # Record error metrics
        ERROR_COUNT.labels(
            error_type=type(e).__name__,
            tool_name="unknown"
        ).inc()
        raise
    
    finally:
        # Decrement active connections
        ACTIVE_CONNECTIONS.dec()

# ATDF Error Response Models
class ATDFErrorDetail(BaseModel):
    type: str
    title: str
    detail: str
    instance: str
    tool_name: Optional[str] = None
    parameter_name: Optional[str] = None
    suggested_value: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ATDFErrorResponse(BaseModel):
    errors: List[ATDFErrorDetail]

# Global exception handler for Pydantic validation errors
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Convert Pydantic validation errors to ATDF format"""
    errors = []
    for error in exc.errors():
        # Determine tool name based on request path
        tool_name = None
        if "/api/hotel/reserve" in str(request.url):
            tool_name = "hotel_reservation"
        elif "/api/flight/book" in str(request.url):
            tool_name = "flight_booking"
        
        error_detail = ATDFErrorDetail(
            type="https://api.example.com/errors/validation-error",
            title="Validation Error",
            detail=error["msg"],
            instance=f"/api/errors/{uuid4()}",
            tool_name=tool_name,
            parameter_name=error["loc"][-1] if error["loc"] else None,
            context={"field_path": error["loc"], "input_value": error.get("input")}
        )
        errors.append(error_detail)
    
    return JSONResponse(
        status_code=400,
        content=ATDFErrorResponse(errors=errors).dict()
    )

# Global exception handler for FastAPI RequestValidationError
@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert FastAPI request validation errors to ATDF format"""
    errors = []
    for error in exc.errors():
        # Determine tool name based on request path
        tool_name = None
        if "/api/hotel/reserve" in str(request.url):
            tool_name = "hotel_reservation"
        elif "/api/flight/book" in str(request.url):
            tool_name = "flight_booking"
        
        error_detail = ATDFErrorDetail(
            type="https://api.example.com/errors/validation-error",
            title="Validation Error",
            detail=error["msg"],
            instance=f"/api/errors/{uuid4()}",
            tool_name=tool_name,
            parameter_name=error["loc"][-1] if error["loc"] else None,
            context={"field_path": error["loc"], "input_value": error.get("input")}
        )
        errors.append(error_detail)
    
    return JSONResponse(
        status_code=400,
        content=ATDFErrorResponse(errors=errors).dict()
    )

# Pydantic Models for API
class HotelReservationRequest(BaseModel):
    guest_name: str = Field(..., description="Full name of the guest")
    email: EmailStr = Field(..., description="Guest email address")
    check_in: datetime = Field(..., description="Check-in date and time")
    check_out: datetime = Field(..., description="Check-out date and time")
    room_type: str = Field(..., description="Type of room (single, double, suite)")
    guests: int = Field(..., ge=1, le=4, description="Number of guests")
    
    @validator('check_out')
    def check_out_after_check_in(cls, v, values):
        if 'check_in' in values and v <= values['check_in']:
            raise ValueError('Check-out must be after check-in')
        return v

class FlightBookingRequest(BaseModel):
    passenger_name: str = Field(..., description="Full name of the passenger")
    email: EmailStr = Field(..., description="Passenger email address")
    departure_city: str = Field(..., description="Departure city")
    arrival_city: str = Field(..., description="Arrival city")
    departure_date: datetime = Field(..., description="Departure date and time")
    return_date: Optional[datetime] = Field(None, description="Return date and time (for round trip)")
    seat_class: str = Field(..., description="Seat class (economy, business, first)")
    
    @validator('return_date')
    def return_after_departure(cls, v, values):
        if v and 'departure_date' in values and v <= values['departure_date']:
            raise ValueError('Return date must be after departure date')
        return v

# In-memory storage
hotel_reservations = {}
flight_bookings = {}

def create_atdf_error_response(
    error_type: str,
    title: str,
    detail: str,
    tool_name: Optional[str] = None,
    parameter_name: Optional[str] = None,
    suggested_value: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create an ATDF-compliant error response"""
    error_detail = ATDFErrorDetail(
        type=error_type,
        title=title,
        detail=detail,
        instance=f"/api/errors/{uuid4()}",
        tool_name=tool_name,
        parameter_name=parameter_name,
        suggested_value=suggested_value,
        context=context
    )
    
    return JSONResponse(
        status_code=400,
        content=ATDFErrorResponse(errors=[error_detail]).dict()
    )

@app.get('/metrics')
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get('/health')
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "metrics": {
            "total_hotel_reservations": len(hotel_reservations),
            "total_flight_bookings": len(flight_bookings)
        }
    }

@app.get('/')
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ATDF FastAPI MCP Integration",
        "version": "2.0.0",
        "endpoints": {
            "hotel_reservation": "/api/hotel/reserve",
            "flight_booking": "/api/flight/book",
            "tools": "/tools"
        }
    }

@app.get('/tools')
async def get_tools():
    """MCP tools endpoint returning enhanced ATDF tool descriptions with metadata"""
    current_time = datetime.now()
    
    # Hotel reservation tool with enhanced metadata
    hotel_tool = ATDFToolDescriptor(
        tool_id="hotel_reservation",
        description="Make a hotel reservation with validation and ATDF error handling",
        when_to_use="When a user wants to book accommodation at a hotel",
        inputSchema={
            "type": "object",
            "properties": {
                "guest_name": {"type": "string", "description": "Full name of the guest"},
                "email": {"type": "string", "format": "email", "description": "Guest email address"},
                "check_in": {"type": "string", "format": "date-time", "description": "Check-in date and time"},
                "check_out": {"type": "string", "format": "date-time", "description": "Check-out date and time"},
                "room_type": {"type": "string", "enum": ["single", "double", "suite"], "description": "Type of room"},
                "guests": {"type": "integer", "minimum": 1, "maximum": 4, "description": "Number of guests"}
            },
            "required": ["guest_name", "email", "check_in", "check_out", "room_type", "guests"]
        },
        metadata=ATDFMetadata(
            version="2.0.0",
            author="ATDF Development Team",
            tags=["hotel", "reservation", "booking", "accommodation"],
            category="travel",
            created_at=current_time,
            updated_at=current_time
        ),
        localization={
            "es": ATDFLocalization(
                description="Realizar una reserva de hotel con validación y manejo de errores ATDF",
                when_to_use="Cuando un usuario quiere reservar alojamiento en un hotel"
            ),
            "en": ATDFLocalization(
                description="Make a hotel reservation with validation and ATDF error handling",
                when_to_use="When a user wants to book accommodation at a hotel"
            )
        },
        examples=[
            ATDFExample(
                goal="Book a single room for one night",
                input_values={
                    "guest_name": "John Doe",
                    "email": "john.doe@example.com",
                    "check_in": "2024-12-25T15:00:00Z",
                    "check_out": "2024-12-26T11:00:00Z",
                    "room_type": "single",
                    "guests": 1
                },
                expected_result="Hotel reservation created successfully with confirmation ID"
            )
        ],
        prerequisites=ATDFPrerequisite(
            tools=[],
            permissions=["booking:create"],
            environment={"timezone": "UTC"}
        )
    )
    
    # Flight booking tool with enhanced metadata
    flight_tool = ATDFToolDescriptor(
        tool_id="flight_booking",
        description="Book a flight with validation and ATDF error handling",
        when_to_use="When a user wants to book air travel between cities",
        inputSchema={
            "type": "object",
            "properties": {
                "passenger_name": {"type": "string", "description": "Full name of the passenger"},
                "email": {"type": "string", "format": "email", "description": "Passenger email address"},
                "departure_city": {"type": "string", "description": "Departure city"},
                "arrival_city": {"type": "string", "description": "Arrival city"},
                "departure_date": {"type": "string", "format": "date-time", "description": "Departure date and time"},
                "return_date": {"type": "string", "format": "date-time", "description": "Return date and time (optional)"},
                "seat_class": {"type": "string", "enum": ["economy", "business", "first"], "description": "Seat class"}
            },
            "required": ["passenger_name", "email", "departure_city", "arrival_city", "departure_date", "seat_class"]
        },
        metadata=ATDFMetadata(
            version="2.0.0",
            author="ATDF Development Team",
            tags=["flight", "booking", "travel", "aviation"],
            category="travel",
            created_at=current_time,
            updated_at=current_time
        ),
        localization={
            "es": ATDFLocalization(
                description="Reservar un vuelo con validación y manejo de errores ATDF",
                when_to_use="Cuando un usuario quiere reservar viajes aéreos entre ciudades"
            ),
            "en": ATDFLocalization(
                description="Book a flight with validation and ATDF error handling",
                when_to_use="When a user wants to book air travel between cities"
            )
        },
        examples=[
            ATDFExample(
                goal="Book a round-trip economy flight",
                input_values={
                    "passenger_name": "Jane Smith",
                    "email": "jane.smith@example.com",
                    "departure_city": "New York",
                    "arrival_city": "Los Angeles",
                    "departure_date": "2024-12-20T08:00:00Z",
                    "return_date": "2024-12-27T18:00:00Z",
                    "seat_class": "economy"
                },
                expected_result="Flight booking created successfully with confirmation number"
            )
        ],
        prerequisites=ATDFPrerequisite(
            tools=[],
            permissions=["booking:create"],
            environment={"timezone": "UTC"}
        )
    )
    
    return {
        "tools": [
            hotel_tool.dict(),
            flight_tool.dict()
        ]
    }

@app.post('/api/hotel/reserve')
async def reserve_hotel(request: HotelReservationRequest):
    """Make a hotel reservation with ATDF error handling"""
    start_time = time.time()
    tool_name = "hotel_reservation"
    
    try:
        # Validate business rules
        if request.check_in < datetime.now():
            TOOL_EXECUTIONS.labels(tool_name=tool_name, status="error").inc()
            ERROR_COUNT.labels(error_type="invalid_date", tool_name=tool_name).inc()
            return create_atdf_error_response(
                error_type="https://api.example.com/errors/invalid-date",
                title="Invalid Check-in Date",
                detail="Check-in date cannot be in the past",
                tool_name="hotel_reservation",
                parameter_name="check_in",
                suggested_value=datetime.now().isoformat(),
                context={"current_time": datetime.now().isoformat()}
            )
        
        if request.check_out - request.check_in < timedelta(hours=1):
            TOOL_EXECUTIONS.labels(tool_name=tool_name, status="error").inc()
            ERROR_COUNT.labels(error_type="invalid_duration", tool_name=tool_name).inc()
            return create_atdf_error_response(
                error_type="https://api.example.com/errors/invalid-duration",
                title="Invalid Stay Duration",
                detail="Minimum stay duration is 1 hour",
                tool_name="hotel_reservation",
                parameter_name="check_out",
                context={"minimum_duration": "1 hour"}
            )
        
        # Create reservation
        reservation_id = str(uuid4())
        hotel_reservations[reservation_id] = {
            "id": reservation_id,
            "guest_name": request.guest_name,
            "email": request.email,
            "check_in": request.check_in.isoformat(),
            "check_out": request.check_out.isoformat(),
            "room_type": request.room_type,
            "guests": request.guests,
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        # Record successful execution metrics
        TOOL_EXECUTIONS.labels(tool_name=tool_name, status="success").inc()
        TOOL_EXECUTION_DURATION.labels(tool_name=tool_name).observe(time.time() - start_time)
        
        return {
            "reservation_id": reservation_id,
            "status": "confirmed",
            "message": "Hotel reservation created successfully",
            "details": hotel_reservations[reservation_id]
        }
        
    except Exception as e:
        TOOL_EXECUTIONS.labels(tool_name=tool_name, status="error").inc()
        ERROR_COUNT.labels(error_type="internal_error", tool_name=tool_name).inc()
        TOOL_EXECUTION_DURATION.labels(tool_name=tool_name).observe(time.time() - start_time)
        return create_atdf_error_response(
            error_type="https://api.example.com/errors/internal-error",
            title="Internal Server Error",
            detail=str(e),
            tool_name="hotel_reservation"
        )

@app.post('/api/flight/book')
async def book_flight(request: FlightBookingRequest):
    """Book a flight with ATDF error handling"""
    start_time = time.time()
    tool_name = "flight_booking"
    
    try:
        # Validate business rules
        if request.departure_date < datetime.now():
            TOOL_EXECUTIONS.labels(tool_name=tool_name, status="error").inc()
            ERROR_COUNT.labels(error_type="invalid_date", tool_name=tool_name).inc()
            return create_atdf_error_response(
                error_type="https://api.example.com/errors/invalid-date",
                title="Invalid Departure Date",
                detail="Departure date cannot be in the past",
                tool_name="flight_booking",
                parameter_name="departure_date",
                suggested_value=datetime.now().isoformat(),
                context={"current_time": datetime.now().isoformat()}
            )
        
        if request.departure_city.lower() == request.arrival_city.lower():
            TOOL_EXECUTIONS.labels(tool_name=tool_name, status="error").inc()
            ERROR_COUNT.labels(error_type="invalid_route", tool_name=tool_name).inc()
            return create_atdf_error_response(
                error_type="https://api.example.com/errors/invalid-route",
                title="Invalid Route",
                detail="Departure and arrival cities cannot be the same",
                tool_name="flight_booking",
                parameter_name="arrival_city",
                context={"departure_city": request.departure_city}
            )
        
        # Create booking
        booking_id = str(uuid4())
        flight_bookings[booking_id] = {
            "id": booking_id,
            "passenger_name": request.passenger_name,
            "email": request.email,
            "departure_city": request.departure_city,
            "arrival_city": request.arrival_city,
            "departure_date": request.departure_date.isoformat(),
            "return_date": request.return_date.isoformat() if request.return_date else None,
            "seat_class": request.seat_class,
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        # Record successful execution metrics
        TOOL_EXECUTIONS.labels(tool_name=tool_name, status="success").inc()
        TOOL_EXECUTION_DURATION.labels(tool_name=tool_name).observe(time.time() - start_time)
        
        return {
            "booking_id": booking_id,
            "status": "confirmed",
            "message": "Flight booking created successfully",
            "details": flight_bookings[booking_id]
        }
        
    except Exception as e:
        TOOL_EXECUTIONS.labels(tool_name=tool_name, status="error").inc()
        ERROR_COUNT.labels(error_type="internal_error", tool_name=tool_name).inc()
        TOOL_EXECUTION_DURATION.labels(tool_name=tool_name).observe(time.time() - start_time)
        return create_atdf_error_response(
            error_type="https://api.example.com/errors/internal-error",
            title="Internal Server Error",
            detail=str(e),
            tool_name="flight_booking"
        )

@app.get('/api/hotel/reservations')
async def get_hotel_reservations():
    """Get all hotel reservations"""
    return {"reservations": list(hotel_reservations.values())}

@app.get('/api/flight/bookings')
async def get_flight_bookings():
    """Get all flight bookings"""
    return {"bookings": list(flight_bookings.values())}

# Metadata Models for Enhanced ATDF
class ATDFMetadata(BaseModel):
    version: str = Field(..., description="Tool version")
    author: str = Field(..., description="Tool author")
    tags: List[str] = Field(default_factory=list, description="Tool tags for categorization")
    category: str = Field(..., description="Tool category")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

class ATDFLocalization(BaseModel):
    description: str = Field(..., description="Localized description")
    when_to_use: str = Field(..., description="Localized when to use")

class ATDFExample(BaseModel):
    goal: str = Field(..., description="What the example demonstrates")
    input_values: Dict[str, Any] = Field(..., description="Example input values")
    expected_result: str = Field(..., description="Expected result description")

class ATDFPrerequisite(BaseModel):
    tools: List[str] = Field(default_factory=list, description="Required tools")
    permissions: List[str] = Field(default_factory=list, description="Required permissions")
    environment: Dict[str, str] = Field(default_factory=dict, description="Environment requirements")

class ATDFToolDescriptor(BaseModel):
    tool_id: str = Field(..., description="Unique tool identifier")
    description: str = Field(..., description="Tool description")
    when_to_use: str = Field(..., description="When to use this tool")
    inputSchema: Dict[str, Any] = Field(..., description="JSON Schema for input validation")
    metadata: Optional[ATDFMetadata] = Field(None, description="Tool metadata")
    localization: Optional[Dict[str, ATDFLocalization]] = Field(None, description="Localized content")
    examples: Optional[List[ATDFExample]] = Field(None, description="Usage examples")
    prerequisites: Optional[ATDFPrerequisite] = Field(None, description="Tool prerequisites")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
