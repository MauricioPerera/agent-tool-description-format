from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr, Field, validator, ValidationError
from datetime import datetime, timedelta
from uuid import uuid4
import json
from typing import Dict, List, Optional, Any

app = FastAPI(title='ATDF FastAPI MCP Integration', version='2.0.0')

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """MCP tools endpoint returning tool descriptions"""
    tools = [
        {
            "name": "hotel_reservation",
            "description": "Make a hotel reservation with validation and ATDF error handling",
            "inputSchema": {
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
            }
        },
        {
            "name": "flight_booking",
            "description": "Book a flight with validation and ATDF error handling",
            "inputSchema": {
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
            }
        }
    ]
    return {"tools": tools}

@app.post('/api/hotel/reserve')
async def reserve_hotel(request: HotelReservationRequest):
    """Make a hotel reservation with ATDF error handling"""
    try:
        # Validate business rules
        if request.check_in < datetime.now():
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
        
        return {
            "reservation_id": reservation_id,
            "status": "confirmed",
            "message": "Hotel reservation created successfully",
            "details": hotel_reservations[reservation_id]
        }
        
    except Exception as e:
        return create_atdf_error_response(
            error_type="https://api.example.com/errors/internal-error",
            title="Internal Server Error",
            detail=str(e),
            tool_name="hotel_reservation"
        )

@app.post('/api/flight/book')
async def book_flight(request: FlightBookingRequest):
    """Book a flight with ATDF error handling"""
    try:
        # Validate business rules
        if request.departure_date < datetime.now():
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
        
        return {
            "booking_id": booking_id,
            "status": "confirmed",
            "message": "Flight booking created successfully",
            "details": flight_bookings[booking_id]
        }
        
    except Exception as e:
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
