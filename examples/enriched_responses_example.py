#!/usr/bin/env python3
"""
Ejemplo práctico de respuestas enriquecidas con campo expected detallado.

Este script demuestra la implementación del estándar de respuestas enriquecidas
como base fundamental de ATDF, con ejemplos de validación de fechas, emails
y contraseñas.
"""

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List


@dataclass
class ValidationResult:
    """Resultado de una validación individual."""

    condition: str
    passed: bool
    details: str = ""


class EnrichedResponseValidator:
    """
    Validador que implementa el estándar de respuestas enriquecidas de ATDF.
    """

    def __init__(self):
        self.now = datetime.now(timezone.utc)

    def create_success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una respuesta de éxito estándar."""
        return {
            "status": "success",
            "data": data,
            "meta": {"timestamp": self.now.isoformat()},
        }

    def create_error_response(
        self,
        code: str,
        message: str,
        field: str,
        received: Dict[str, Any],
        expected: Dict[str, Any],
        validation_results: Dict[str, bool] = None,
        solution: str = None,
    ) -> Dict[str, Any]:
        """Crea una respuesta de error enriquecida."""
        return {
            "status": "error",
            "data": {
                "code": code,
                "message": message,
                "details": {
                    "field": field,
                    "received": received,
                    "expected": expected,
                    "validation_results": validation_results or {},
                    "solution": solution
                    or "Review the expected conditions and adjust your input accordingly.",
                },
            },
            "meta": {"timestamp": self.now.isoformat()},
        }

    def validate_date_range(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Valida un rango de fechas con respuestas enriquecidas.

        Ejemplo de uso:
        validator = EnrichedResponseValidator()
        result = validator.validate_date_range("2023-12-01T10:00:00Z", "2023-11-01T15:30:00Z")
        """
        try:
            # Parsear fechas
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

            # Validaciones
            validations = [
                ValidationResult(
                    "start_date must be before end_date", start_dt < end_dt
                ),
                ValidationResult(
                    "start_date must be after current date", start_dt > self.now
                ),
                ValidationResult(
                    "end_date must be after current date", end_dt > self.now
                ),
            ]

            # Verificar si todas las validaciones pasan
            all_passed = all(v.passed for v in validations)

            if all_passed:
                return self.create_success_response(
                    {
                        "message": "Date range is valid",
                        "start_date": start_date,
                        "end_date": end_date,
                        "duration_days": (end_dt - start_dt).days,
                        "validation_summary": {
                            "total_checks": len(validations),
                            "passed_checks": len(validations),
                            "failed_checks": 0,
                        },
                    }
                )

            # Construir respuesta de error enriquecida
            failed_conditions = [v.condition for v in validations if not v.passed]
            validation_results = {v.condition: v.passed for v in validations}

            return self.create_error_response(
                code="INVALID_DATE_RANGE",
                message=f"Date range validation failed: {', '.join(failed_conditions)}",
                field="date_range",
                received={
                    "start_date": start_date,
                    "end_date": end_date,
                    "current_time": self.now.isoformat(),
                    "parsed_start": start_dt.isoformat(),
                    "parsed_end": end_dt.isoformat(),
                },
                expected={
                    "conditions": [
                        "start_date must be before end_date",
                        "start_date must be after current date (now)",
                        "end_date must be after current date (now)",
                    ],
                    "format": "ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)",
                    "constraints": {
                        "min_start_date": "now + 1 day",
                        "max_end_date": "now + 365 days",
                        "min_duration": "1 day",
                        "max_duration": "30 days",
                    },
                    "examples": {
                        "valid_range": {
                            "start_date": (self.now + timedelta(days=1)).isoformat(),
                            "end_date": (self.now + timedelta(days=15)).isoformat(),
                        },
                        "invalid_ranges": [
                            {
                                "start_date": "2023-11-01T00:00:00Z",
                                "end_date": "2023-10-01T00:00:00Z",
                                "reason": "start_date after end_date",
                            },
                            {
                                "start_date": "2023-10-20T00:00:00Z",
                                "end_date": "2023-10-25T00:00:00Z",
                                "reason": "start_date before current date",
                            },
                        ],
                    },
                },
                validation_results=validation_results,
                solution=f"Adjust your dates to meet these requirements: {', '.join(failed_conditions)}",
            )

        except ValueError as e:
            return self.create_error_response(
                code="INVALID_DATE_FORMAT",
                message="Invalid date format provided",
                field="date_format",
                received={
                    "start_date": start_date,
                    "end_date": end_date,
                    "parsing_error": str(e),
                },
                expected={
                    "format": "ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)",
                    "examples": ["2023-10-27T10:30:00Z", "2023-10-27T10:30:00+00:00"],
                    "common_mistakes": [
                        "Missing timezone indicator (Z or +00:00)",
                        "Wrong date separator (use T between date and time)",
                        "Invalid month/day values",
                    ],
                },
                solution="Use ISO 8601 format for dates: YYYY-MM-DDTHH:mm:ssZ",
            )

    def validate_email(self, email: str) -> Dict[str, Any]:
        """
        Valida un email con respuestas enriquecidas.

        Ejemplo de uso:
        validator = EnrichedResponseValidator()
        result = validator.validate_email("invalid-email")
        """
        if not email:
            return self.create_error_response(
                code="EMPTY_EMAIL",
                message="Email address cannot be empty",
                field="email",
                received={"email": email},
                expected={
                    "conditions": [
                        "Email must not be empty",
                        "Email must contain @ symbol",
                        "Email must have valid domain",
                    ],
                    "format": "RFC 5322 email format",
                    "examples": {
                        "valid": ["user@example.com", "test.email+tag@domain.co.uk"],
                        "invalid": ["invalid-email", "@domain.com", "user@"],
                    },
                },
                solution="Provide a valid email address",
            )

        # RFC 5322 compliant regex
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_pattern, email):
            return self.create_error_response(
                code="INVALID_EMAIL_FORMAT",
                message="Email format is invalid",
                field="email",
                received={
                    "email": email,
                    "length": len(email),
                    "contains_at": "@" in email,
                    "at_count": email.count("@"),
                },
                expected={
                    "conditions": [
                        "Must contain exactly one @ symbol",
                        "Local part before @ must be valid",
                        "Domain after @ must be valid",
                        "Must have valid TLD (2+ characters)",
                    ],
                    "format": "RFC 5322 email format",
                    "constraints": {
                        "max_length": "254 characters total",
                        "local_part_max": "64 characters",
                        "domain_max": "253 characters",
                        "tld_min": "2 characters",
                    },
                    "examples": {
                        "valid": ["user@example.com", "test.email+tag@domain.co.uk"],
                        "invalid": [
                            {"value": "invalid-email", "reason": "missing @ symbol"},
                            {"value": "@domain.com", "reason": "empty local part"},
                            {"value": "user@", "reason": "empty domain"},
                            {
                                "value": "user@@domain.com",
                                "reason": "multiple @ symbols",
                            },
                        ],
                    },
                },
                solution="Use a valid email format like user@example.com",
            )

        return self.create_success_response(
            {
                "message": "Email is valid",
                "email": email,
                "local_part": email.split("@")[0],
                "domain": email.split("@")[1],
                "validation_summary": {
                    "format_valid": True,
                    "length_valid": len(email) <= 254,
                },
            }
        )

    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Valida la fortaleza de una contraseña con respuestas enriquecidas.

        Ejemplo de uso:
        validator = EnrichedResponseValidator()
        result = validator.validate_password_strength("weak")
        """
        if not password:
            return self.create_error_response(
                code="EMPTY_PASSWORD",
                message="Password cannot be empty",
                field="password",
                received={"password": ""},
                expected={
                    "conditions": [
                        "Password must not be empty",
                        "Minimum 8 characters",
                        "At least one uppercase letter",
                        "At least one lowercase letter",
                        "At least one number",
                        "At least one special character",
                    ],
                    "constraints": {"min_length": 8, "max_length": 128},
                },
                solution="Provide a non-empty password",
            )

        # Validaciones de fortaleza
        validations = [
            ValidationResult("Minimum 8 characters", len(password) >= 8),
            ValidationResult("Maximum 128 characters", len(password) <= 128),
            ValidationResult(
                "At least one uppercase letter (A-Z)",
                bool(re.search(r"[A-Z]", password)),
            ),
            ValidationResult(
                "At least one lowercase letter (a-z)",
                bool(re.search(r"[a-z]", password)),
            ),
            ValidationResult(
                "At least one number (0-9)", bool(re.search(r"\d", password))
            ),
            ValidationResult(
                'At least one special character (!@#$%^&*(),.?":{}|<>)',
                bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
            ),
        ]

        passed_checks = sum(1 for v in validations if v.passed)
        total_checks = len(validations)

        # Determinar nivel de fortaleza
        if passed_checks == total_checks:
            strength = "strong"
        elif passed_checks >= 5:
            strength = "medium"
        elif passed_checks >= 3:
            strength = "weak"
        else:
            strength = "very_weak"

        if passed_checks == total_checks:
            return self.create_success_response(
                {
                    "message": "Password meets all strength requirements",
                    "strength": strength,
                    "score": passed_checks,
                    "max_score": total_checks,
                    "validation_summary": {
                        "total_checks": total_checks,
                        "passed_checks": passed_checks,
                        "failed_checks": total_checks - passed_checks,
                    },
                }
            )

        # Respuesta de error con detalles enriquecidos
        failed_conditions = [v.condition for v in validations if not v.passed]
        validation_results = {v.condition: v.passed for v in validations}

        return self.create_error_response(
            code="WEAK_PASSWORD",
            message=f"Password strength is {strength}",
            field="password",
            received={
                "password_length": len(password),
                "strength_level": strength,
                "score": passed_checks,
                "max_score": total_checks,
            },
            expected={
                "conditions": [
                    "Minimum 8 characters",
                    "Maximum 128 characters",
                    "At least one uppercase letter (A-Z)",
                    "At least one lowercase letter (a-z)",
                    "At least one number (0-9)",
                    'At least one special character (!@#$%^&*(),.?":{}|<>)',
                ],
                "strength_levels": {
                    "very_weak": "meets 0-2 conditions",
                    "weak": "meets 3-4 conditions",
                    "medium": "meets 5-6 conditions",
                    "strong": "meets all 6 conditions",
                },
                "examples": {
                    "strong": "MyP@ssw0rd!",
                    "medium": "MyPassword1",
                    "weak": "mypassword",
                    "very_weak": "123",
                },
            },
            validation_results=validation_results,
            solution=f"Add the missing requirements: {', '.join(failed_conditions)}",
        )


def main():
    """Ejemplo de uso del validador con respuestas enriquecidas."""
    print("=== Ejemplo de Respuestas Enriquecidas ATDF ===\n")

    validator = EnrichedResponseValidator()

    # Ejemplo 1: Validación de rango de fechas
    print("1. Validación de Rango de Fechas")
    print("-" * 40)

    # Caso de error
    result = validator.validate_date_range(
        "2023-12-01T10:00:00Z", "2023-11-01T15:30:00Z"
    )
    print("❌ Error en rango de fechas:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    # Caso de éxito
    future_start = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    future_end = (datetime.now(timezone.utc) + timedelta(days=15)).isoformat()
    result = validator.validate_date_range(future_start, future_end)
    print("✅ Rango de fechas válido:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    # Ejemplo 2: Validación de email
    print("2. Validación de Email")
    print("-" * 40)

    # Caso de error
    result = validator.validate_email("invalid-email")
    print("❌ Email inválido:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    # Caso de éxito
    result = validator.validate_email("user@example.com")
    print("✅ Email válido:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    # Ejemplo 3: Validación de contraseña
    print("3. Validación de Contraseña")
    print("-" * 40)

    # Caso de error
    result = validator.validate_password_strength("weak")
    print("❌ Contraseña débil:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    # Caso de éxito
    result = validator.validate_password_strength("MyP@ssw0rd!")
    print("✅ Contraseña fuerte:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    print("=== Fin del Ejemplo ===")


if __name__ == "__main__":
    main()
