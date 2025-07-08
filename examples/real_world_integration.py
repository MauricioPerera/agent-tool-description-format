#!/usr/bin/env python3
"""
Ejemplo de Integración en el Mundo Real - ATDF v2.0.0

Este ejemplo demuestra cómo implementar respuestas enriquecidas en un escenario
real de API REST, mostrando la integración completa con un sistema de reservas
de hotel.
"""

import json
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from validation_patterns import ValidationPatterns, ErrorCodes


@dataclass
class HotelReservation:
    """Modelo de datos para una reserva de hotel."""
    guest_name: str
    guest_email: str
    check_in_date: str
    check_out_date: str
    room_type: str
    guests_count: int
    special_requests: Optional[str] = None


class HotelReservationAPI:
    """
    API de ejemplo para reservas de hotel que implementa respuestas enriquecidas.
    
    Este ejemplo muestra cómo usar ATDF v2.0.0 en un escenario real de negocio.
    """
    
    def __init__(self):
        self.validator = ValidationPatterns()
        self.reservations = []
        self.room_types = ["standard", "deluxe", "suite", "presidential"]
        self.max_guests_per_room = {
            "standard": 2,
            "deluxe": 3,
            "suite": 4,
            "presidential": 6
        }
    
    def create_reservation(self, reservation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea una nueva reserva de hotel con validación enriquecida.
        
        Args:
            reservation_data: Datos de la reserva
            
        Returns:
            Respuesta enriquecida con resultado o errores detallados
        """
        # Validar campos requeridos
        required_fields = ["guest_name", "guest_email", "check_in_date", "check_out_date", "room_type", "guests_count"]
        
        for field in required_fields:
            if field not in reservation_data:
                return self.validator.create_error_response(
                    code=ErrorCodes.REQUIRED_FIELD_MISSING.value,
                    message=f"Required field '{field}' is missing",
                    field=field,
                    received={"provided_fields": list(reservation_data.keys())},
                    expected={
                        "conditions": [f"Field '{field}' must be provided"],
                        "format": "All required fields must be present",
                        "examples": {
                            "valid": {
                                "guest_name": "John Doe",
                                "guest_email": "john@example.com",
                                "check_in_date": "2023-10-28T15:00:00Z",
                                "check_out_date": "2023-10-30T11:00:00Z",
                                "room_type": "standard",
                                "guests_count": 2
                            }
                        }
                    },
                    solution=f"Add the missing '{field}' field to your request"
                )
        
        # Validar nombre del huésped
        name_validation = self.validator.validate_string_length(
            reservation_data["guest_name"], 
            "guest_name", 
            min_length=2, 
            max_length=100
        )
        if name_validation:
            return name_validation
        
        # Validar email
        email_validation = self.validator.validate_email(reservation_data["guest_email"])
        if email_validation["status"] == "error":
            return email_validation
        
        # Validar rango de fechas
        date_validation = self.validator.validate_date_range(
            reservation_data["check_in_date"],
            reservation_data["check_out_date"],
            field_name="reservation_dates",
            min_start_offset=1,  # Mínimo 1 día en el futuro
            max_end_offset=365   # Máximo 1 año en el futuro
        )
        if date_validation["status"] == "error":
            return date_validation
        
        # Validar tipo de habitación
        room_type = reservation_data["room_type"].lower()
        if room_type not in self.room_types:
            return self.validator.create_error_response(
                code="INVALID_ROOM_TYPE",
                message=f"Invalid room type '{room_type}'",
                field="room_type",
                received={
                    "provided_room_type": room_type,
                    "available_room_types": self.room_types
                },
                expected={
                    "conditions": [
                        f"Room type must be one of: {', '.join(self.room_types)}",
                        "Room type is case-insensitive"
                    ],
                    "format": "Valid room type string",
                    "constraints": {
                        "available_types": self.room_types,
                        "case_sensitive": False
                    },
                    "examples": {
                        "valid": self.room_types,
                        "invalid": [
                            {
                                "value": "luxury",
                                "reason": "not in available room types"
                            },
                            {
                                "value": "STANDARD",
                                "reason": "valid type but wrong case (though accepted)"
                            }
                        ]
                    }
                },
                solution=f"Choose a room type from: {', '.join(self.room_types)}"
            )
        
        # Validar número de huéspedes
        guests_count = reservation_data["guests_count"]
        max_guests = self.max_guests_per_room[room_type]
        
        if not isinstance(guests_count, int) or guests_count < 1:
            return self.validator.create_error_response(
                code="INVALID_GUESTS_COUNT",
                message="Invalid guests count",
                field="guests_count",
                received={
                    "provided_count": guests_count,
                    "type": type(guests_count).__name__
                },
                expected={
                    "conditions": [
                        "Must be a positive integer",
                        f"Must not exceed {max_guests} for {room_type} room"
                    ],
                    "format": "Positive integer",
                    "constraints": {
                        "min_guests": 1,
                        "max_guests": max_guests,
                        "room_type_limit": f"{room_type}: {max_guests} guests"
                    },
                    "examples": {
                        "valid": list(range(1, max_guests + 1)),
                        "invalid": [
                            {
                                "value": 0,
                                "reason": "must be at least 1"
                            },
                            {
                                "value": max_guests + 1,
                                "reason": f"exceeds limit for {room_type} room"
                            },
                            {
                                "value": "2",
                                "reason": "must be integer, not string"
                            }
                        ]
                    }
                },
                solution=f"Provide a positive integer between 1 and {max_guests} for {room_type} room"
            )
        
        if guests_count > max_guests:
            return self.validator.create_error_response(
                code="TOO_MANY_GUESTS",
                message=f"Too many guests for {room_type} room",
                field="guests_count",
                received={
                    "provided_count": guests_count,
                    "room_type": room_type,
                    "max_allowed": max_guests
                },
                expected={
                    "conditions": [
                        f"Maximum {max_guests} guests allowed for {room_type} room"
                    ],
                    "constraints": {
                        "room_capacity": {
                            "standard": 2,
                            "deluxe": 3,
                            "suite": 4,
                            "presidential": 6
                        }
                    },
                    "examples": {
                        "valid_combinations": [
                            {"room_type": "standard", "guests": 1},
                            {"room_type": "standard", "guests": 2},
                            {"room_type": "deluxe", "guests": 3}
                        ],
                        "invalid_combinations": [
                            {
                                "room_type": "standard",
                                "guests": 3,
                                "reason": "exceeds standard room capacity"
                            }
                        ]
                    }
                },
                solution=f"Either reduce guests to {max_guests} or upgrade to a larger room type"
            )
        
        # Validar solicitudes especiales (opcional)
        if "special_requests" in reservation_data:
            special_requests = reservation_data["special_requests"]
            if special_requests and len(special_requests) > 500:
                return self.validator.create_error_response(
                    code="SPECIAL_REQUESTS_TOO_LONG",
                    message="Special requests too long",
                    field="special_requests",
                    received={
                        "length": len(special_requests),
                        "max_length": 500
                    },
                    expected={
                        "conditions": [
                            "Special requests must be 500 characters or less"
                        ],
                        "format": "Optional text string",
                        "constraints": {
                            "max_length": 500,
                            "optional": True
                        },
                        "examples": {
                            "valid": [
                                "Early check-in if possible",
                                "Room with ocean view",
                                None,
                                ""
                            ],
                            "invalid": [
                                {
                                    "value": "a" * 501,
                                    "reason": "exceeds 500 character limit"
                                }
                            ]
                        }
                    },
                    solution="Shorten your special requests to 500 characters or less"
                )
        
        # Si todas las validaciones pasan, crear la reserva
        try:
            reservation = HotelReservation(
                guest_name=reservation_data["guest_name"],
                guest_email=reservation_data["guest_email"],
                check_in_date=reservation_data["check_in_date"],
                check_out_date=reservation_data["check_out_date"],
                room_type=room_type,
                guests_count=guests_count,
                special_requests=reservation_data.get("special_requests")
            )
            
            # Simular guardado en base de datos
            reservation_id = f"RES-{len(self.reservations) + 1:06d}"
            self.reservations.append({
                "id": reservation_id,
                "reservation": reservation,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            
            return self.validator.create_success_response({
                "message": "Hotel reservation created successfully",
                "reservation_id": reservation_id,
                "reservation": {
                    "guest_name": reservation.guest_name,
                    "guest_email": reservation.guest_email,
                    "check_in_date": reservation.check_in_date,
                    "check_out_date": reservation.check_out_date,
                    "room_type": reservation.room_type,
                    "guests_count": reservation.guests_count,
                    "special_requests": reservation.special_requests
                },
                "summary": {
                    "total_nights": self._calculate_nights(reservation.check_in_date, reservation.check_out_date),
                    "room_capacity_used": f"{guests_count}/{max_guests}",
                    "estimated_price": self._estimate_price(room_type, reservation.check_in_date, reservation.check_out_date)
                }
            })
            
        except Exception as e:
            return self.validator.create_error_response(
                code="RESERVATION_CREATION_FAILED",
                message="Failed to create reservation due to system error",
                field="system",
                received={
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                expected={
                    "conditions": [
                        "System should be able to process valid reservation data"
                    ],
                    "format": "Valid reservation data"
                },
                solution="Please try again later or contact support if the problem persists"
            )
    
    def get_reservation(self, reservation_id: str) -> Dict[str, Any]:
        """
        Obtiene una reserva existente.
        
        Args:
            reservation_id: ID de la reserva
            
        Returns:
            Respuesta enriquecida con la reserva o error
        """
        # Validar formato del ID
        if not re.match(r'^RES-\d{6}$', reservation_id):
            return self.validator.create_error_response(
                code="INVALID_RESERVATION_ID",
                message="Invalid reservation ID format",
                field="reservation_id",
                received={
                    "provided_id": reservation_id
                },
                expected={
                    "conditions": [
                        "Must start with 'RES-'",
                        "Must be followed by 6 digits"
                    ],
                    "format": "RES-XXXXXX (where X are digits)",
                    "examples": {
                        "valid": ["RES-000001", "RES-123456"],
                        "invalid": [
                            {
                                "value": "123456",
                                "reason": "missing RES- prefix"
                            },
                            {
                                "value": "RES-123",
                                "reason": "not enough digits"
                            },
                            {
                                "value": "RES-ABC123",
                                "reason": "contains letters"
                            }
                        ]
                    }
                },
                solution="Use a valid reservation ID in format RES-XXXXXX"
            )
        
        # Buscar la reserva
        for reservation_data in self.reservations:
            if reservation_data["id"] == reservation_id:
                reservation = reservation_data["reservation"]
                return self.validator.create_success_response({
                    "message": "Reservation found",
                    "reservation": {
                        "id": reservation_id,
                        "guest_name": reservation.guest_name,
                        "guest_email": reservation.guest_email,
                        "check_in_date": reservation.check_in_date,
                        "check_out_date": reservation.check_out_date,
                        "room_type": reservation.room_type,
                        "guests_count": reservation.guests_count,
                        "special_requests": reservation.special_requests,
                        "created_at": reservation_data["created_at"]
                    }
                })
        
        return self.validator.create_error_response(
            code="RESERVATION_NOT_FOUND",
            message="Reservation not found",
            field="reservation_id",
            received={
                "provided_id": reservation_id,
                "total_reservations": len(self.reservations)
            },
            expected={
                "conditions": [
                    "Reservation ID must exist in the system"
                ],
                "format": "Valid existing reservation ID"
            },
            solution="Check the reservation ID or create a new reservation"
        )
    
    def _calculate_nights(self, check_in: str, check_out: str) -> int:
        """Calcula el número de noches entre check-in y check-out."""
        check_in_dt = datetime.fromisoformat(check_in.replace('Z', '+00:00'))
        check_out_dt = datetime.fromisoformat(check_out.replace('Z', '+00:00'))
        return (check_out_dt - check_in_dt).days
    
    def _estimate_price(self, room_type: str, check_in: str, check_out: str) -> str:
        """Estima el precio de la reserva."""
        base_prices = {
            "standard": 100,
            "deluxe": 150,
            "suite": 250,
            "presidential": 500
        }
        nights = self._calculate_nights(check_in, check_out)
        total = base_prices[room_type] * nights
        return f"${total} USD"


def main():
    """Ejemplo de uso de la API de reservas de hotel con respuestas enriquecidas."""
    print("=== API de Reservas de Hotel - ATDF v2.0.0 ===\n")
    
    api = HotelReservationAPI()
    
    # Ejemplo 1: Reserva válida
    print("1. Crear Reserva Válida")
    print("-" * 50)
    
    valid_reservation = {
        "guest_name": "María García",
        "guest_email": "maria@example.com",
        "check_in_date": "2023-10-28T15:00:00Z",
        "check_out_date": "2023-10-30T11:00:00Z",
        "room_type": "deluxe",
        "guests_count": 2,
        "special_requests": "Early check-in if possible"
    }
    
    result = api.create_reservation(valid_reservation)
    print("✅ Reserva creada exitosamente:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    # Ejemplo 2: Error - Campo faltante
    print("2. Error - Campo Faltante")
    print("-" * 50)
    
    invalid_reservation = {
        "guest_name": "Juan Pérez",
        "guest_email": "juan@example.com",
        "check_in_date": "2023-10-28T15:00:00Z",
        "check_out_date": "2023-10-30T11:00:00Z",
        "room_type": "standard"
        # Falta guests_count
    }
    
    result = api.create_reservation(invalid_reservation)
    print("❌ Error - Campo requerido faltante:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    # Ejemplo 3: Error - Tipo de habitación inválido
    print("3. Error - Tipo de Habitación Inválido")
    print("-" * 50)
    
    invalid_room_reservation = {
        "guest_name": "Ana López",
        "guest_email": "ana@example.com",
        "check_in_date": "2023-10-28T15:00:00Z",
        "check_out_date": "2023-10-30T11:00:00Z",
        "room_type": "luxury",  # Tipo inválido
        "guests_count": 2
    }
    
    result = api.create_reservation(invalid_room_reservation)
    print("❌ Error - Tipo de habitación inválido:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    # Ejemplo 4: Error - Demasiados huéspedes
    print("4. Error - Demasiados Huéspedes")
    print("-" * 50)
    
    too_many_guests_reservation = {
        "guest_name": "Carlos Rodríguez",
        "guest_email": "carlos@example.com",
        "check_in_date": "2023-10-28T15:00:00Z",
        "check_out_date": "2023-10-30T11:00:00Z",
        "room_type": "standard",
        "guests_count": 4  # Demasiados para habitación estándar
    }
    
    result = api.create_reservation(too_many_guests_reservation)
    print("❌ Error - Demasiados huéspedes:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    # Ejemplo 5: Obtener reserva existente
    print("5. Obtener Reserva Existente")
    print("-" * 50)
    
    result = api.get_reservation("RES-000001")
    print("✅ Reserva encontrada:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    # Ejemplo 6: Error - Reserva no encontrada
    print("6. Error - Reserva No Encontrada")
    print("-" * 50)
    
    result = api.get_reservation("RES-999999")
    print("❌ Error - Reserva no encontrada:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    print("=== Fin del Ejemplo ===")


if __name__ == "__main__":
    main() 