#!/usr/bin/env python3
"""
Patrones de validación comunes para ATDF.

Este módulo proporciona patrones de validación reutilizables que pueden ser
utilizados en diferentes herramientas ATDF para mantener consistencia en las
respuestas enriquecidas.
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class ErrorCodes(Enum):
    """Códigos de error estandarizados para ATDF."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_DATE_RANGE = "INVALID_DATE_RANGE"
    INVALID_EMAIL_FORMAT = "INVALID_EMAIL_FORMAT"
    WEAK_PASSWORD = "WEAK_PASSWORD"
    EMPTY_FIELD = "EMPTY_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    INVALID_URL = "INVALID_URL"
    INVALID_PHONE = "INVALID_PHONE"
    INVALID_IP_ADDRESS = "INVALID_IP_ADDRESS"
    INVALID_JSON = "INVALID_JSON"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"


@dataclass
class ValidationResult:
    """Resultado de una validación individual."""

    condition: str
    passed: bool
    details: str = ""
    value: Any = None


class ValidationPatterns:
    """Patrones de validación comunes para ATDF."""

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
        """Crea una respuesta de error enriquecida estándar."""
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

    def validate_required_field(
        self, value: Any, field_name: str, field_type: str = "any"
    ) -> Optional[Dict[str, Any]]:
        """Valida que un campo requerido no esté vacío."""
        if value is None or (isinstance(value, str) and not value.strip()):
            return self.create_error_response(
                code=ErrorCodes.REQUIRED_FIELD_MISSING.value,
                message=f"{field_name} is required and cannot be empty",
                field=field_name,
                received={"value": value, "type": type(value).__name__},
                expected={
                    "conditions": [
                        f"{field_name} must not be null or empty",
                        f"{field_name} must be of type {field_type}",
                    ],
                    "format": f"Non-empty {field_type}",
                    "examples": {
                        "valid": self._get_valid_examples(field_type),
                        "invalid": [None, "", "   "],
                    },
                },
                solution=f"Provide a valid {field_type} value for {field_name}",
            )
        return None

    def validate_string_length(
        self, value: str, field_name: str, min_length: int = 0, max_length: int = None
    ) -> Optional[Dict[str, Any]]:
        """Valida la longitud de una cadena."""
        if not isinstance(value, str):
            return self.create_error_response(
                code=ErrorCodes.INVALID_FORMAT.value,
                message=f"{field_name} must be a string",
                field=field_name,
                received={
                    "value": value,
                    "type": type(value).__name__,
                    "length": len(str(value)),
                },
                expected={
                    "conditions": [f"{field_name} must be a string"],
                    "format": "string",
                    "examples": {
                        "valid": ["example string"],
                        "invalid": [123, True, None],
                    },
                },
                solution=f"Provide a string value for {field_name}",
            )

        length = len(value)
        validations = []

        if min_length > 0:
            validations.append(
                ValidationResult(
                    f"minimum {min_length} characters",
                    length >= min_length,
                    f"Current length: {length}",
                )
            )

        if max_length:
            validations.append(
                ValidationResult(
                    f"maximum {max_length} characters",
                    length <= max_length,
                    f"Current length: {length}",
                )
            )

        failed_validations = [v for v in validations if not v.passed]

        if failed_validations:
            failed_conditions = [v.condition for v in failed_validations]
            validation_results = {v.condition: v.passed for v in validations}

            return self.create_error_response(
                code=ErrorCodes.OUT_OF_RANGE.value,
                message=f"{field_name} length validation failed: {', '.join(failed_conditions)}",
                field=field_name,
                received={"value": value, "length": length},
                expected={
                    "conditions": [v.condition for v in validations],
                    "constraints": {"min_length": min_length, "max_length": max_length},
                    "examples": {
                        "valid": self._get_string_examples(min_length, max_length),
                        "invalid": [value],  # The actual invalid value
                    },
                },
                validation_results=validation_results,
                solution=f"Adjust {field_name} length to be between {min_length} and {max_length} characters",
            )

        return None

    def validate_email(self, email: str, field_name: str = "email") -> Dict[str, Any]:
        """Valida formato de email con respuestas enriquecidas."""
        # Validar campo requerido
        required_error = self.validate_required_field(email, field_name, "email")
        if required_error:
            return required_error

        # RFC 5322 compliant regex
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_pattern, email):
            return self.create_error_response(
                code=ErrorCodes.INVALID_EMAIL_FORMAT.value,
                message=f"{field_name} format is invalid",
                field=field_name,
                received={
                    "value": email,
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
                        ],
                    },
                },
                solution=f"Use a valid email format like user@example.com for {field_name}",
            )

        return self.create_success_response(
            {
                "message": f"{field_name} is valid",
                "email": email,
                "local_part": email.split("@")[0],
                "domain": email.split("@")[1],
                "validation_summary": {
                    "format_valid": True,
                    "length_valid": len(email) <= 254,
                },
            }
        )

    def validate_password_strength(
        self,
        password: str,
        field_name: str = "password",
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_numbers: bool = True,
        require_special: bool = True,
    ) -> Dict[str, Any]:
        """Valida la fortaleza de una contraseña."""
        # Validar campo requerido
        required_error = self.validate_required_field(password, field_name, "password")
        if required_error:
            return required_error

        # Validaciones de fortaleza
        validations = []

        if min_length > 0:
            validations.append(
                ValidationResult(
                    f"minimum {min_length} characters", len(password) >= min_length
                )
            )

        if require_uppercase:
            validations.append(
                ValidationResult(
                    "at least one uppercase letter (A-Z)",
                    bool(re.search(r"[A-Z]", password)),
                )
            )

        if require_lowercase:
            validations.append(
                ValidationResult(
                    "at least one lowercase letter (a-z)",
                    bool(re.search(r"[a-z]", password)),
                )
            )

        if require_numbers:
            validations.append(
                ValidationResult(
                    "at least one number (0-9)", bool(re.search(r"\d", password))
                )
            )

        if require_special:
            validations.append(
                ValidationResult(
                    'at least one special character (!@#$%^&*(),.?":{}|<>)',
                    bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
                )
            )

        passed_checks = sum(1 for v in validations if v.passed)
        total_checks = len(validations)

        # Determinar nivel de fortaleza
        if passed_checks == total_checks:
            strength = "strong"
        elif passed_checks >= total_checks * 0.8:
            strength = "medium"
        elif passed_checks >= total_checks * 0.6:
            strength = "weak"
        else:
            strength = "very_weak"

        if passed_checks == total_checks:
            return self.create_success_response(
                {
                    "message": f"{field_name} meets all strength requirements",
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
            code=ErrorCodes.WEAK_PASSWORD.value,
            message=f"{field_name} strength is {strength}",
            field=field_name,
            received={
                "password_length": len(password),
                "strength_level": strength,
                "score": passed_checks,
                "max_score": total_checks,
            },
            expected={
                "conditions": [v.condition for v in validations],
                "strength_levels": {
                    "very_weak": f"meets 0-{int(total_checks * 0.6)} conditions",
                    "weak": f"meets {int(total_checks * 0.6)}-{int(total_checks * 0.8)} conditions",
                    "medium": f"meets {int(total_checks * 0.8)}-{total_checks} conditions",
                    "strong": f"meets all {total_checks} conditions",
                },
                "examples": {
                    "strong": "MyP@ssw0rd!",
                    "medium": "MyPassword1",
                    "weak": "mypassword",
                    "very_weak": "123",
                },
            },
            validation_results=validation_results,
            solution=f"Add the missing requirements for {field_name}: {', '.join(failed_conditions)}",
        )

    def validate_date_range(
        self,
        start_date: str,
        end_date: str,
        field_name: str = "date_range",
        min_start_offset: int = 1,
        max_end_offset: int = 365,
    ) -> Dict[str, Any]:
        """Valida un rango de fechas con respuestas enriquecidas."""
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
                    f"start_date must be at least {min_start_offset} day(s) after current date",
                    start_dt > self.now + timedelta(days=min_start_offset - 1),
                ),
                ValidationResult(
                    f"end_date must be at most {max_end_offset} days after current date",
                    end_dt <= self.now + timedelta(days=max_end_offset),
                ),
            ]

            # Verificar si todas las validaciones pasan
            all_passed = all(v.passed for v in validations)

            if all_passed:
                return self.create_success_response(
                    {
                        "message": f"{field_name} is valid",
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
                code=ErrorCodes.INVALID_DATE_RANGE.value,
                message=f"{field_name} validation failed: {', '.join(failed_conditions)}",
                field=field_name,
                received={
                    "start_date": start_date,
                    "end_date": end_date,
                    "current_time": self.now.isoformat(),
                    "parsed_start": start_dt.isoformat(),
                    "parsed_end": end_dt.isoformat(),
                },
                expected={
                    "conditions": [v.condition for v in validations],
                    "format": "ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)",
                    "constraints": {
                        "min_start_date": f"now + {min_start_offset} day(s)",
                        "max_end_date": f"now + {max_end_offset} days",
                    },
                    "examples": {
                        "valid_range": {
                            "start_date": (
                                self.now + timedelta(days=min_start_offset)
                            ).isoformat(),
                            "end_date": (
                                self.now + timedelta(days=min_start_offset + 14)
                            ).isoformat(),
                        }
                    },
                },
                validation_results=validation_results,
                solution=f"Adjust your dates to meet these requirements: {', '.join(failed_conditions)}",
            )

        except ValueError as e:
            return self.create_error_response(
                code=ErrorCodes.INVALID_FORMAT.value,
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
                },
                solution="Use ISO 8601 format for dates: YYYY-MM-DDTHH:mm:ssZ",
            )

    def validate_url(self, url: str, field_name: str = "url") -> Dict[str, Any]:
        """Valida formato de URL."""
        # Validar campo requerido
        required_error = self.validate_required_field(url, field_name, "URL")
        if required_error:
            return required_error

        # Patrón de URL
        url_pattern = r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"

        if not re.match(url_pattern, url):
            return self.create_error_response(
                code=ErrorCodes.INVALID_URL.value,
                message=f"{field_name} format is invalid",
                field=field_name,
                received={
                    "value": url,
                    "length": len(url),
                    "starts_with_http": url.startswith(("http://", "https://")),
                },
                expected={
                    "conditions": [
                        "Must start with http:// or https://",
                        "Must have valid domain structure",
                        "Must have valid TLD",
                    ],
                    "format": "Valid HTTP/HTTPS URL",
                    "examples": {
                        "valid": [
                            "https://example.com",
                            "http://www.example.com/path",
                            "https://api.example.co.uk/v1/endpoint",
                        ],
                        "invalid": [
                            {"value": "not-a-url", "reason": "missing protocol"},
                            {
                                "value": "ftp://example.com",
                                "reason": "unsupported protocol",
                            },
                        ],
                    },
                },
                solution=f"Use a valid HTTP or HTTPS URL for {field_name}",
            )

        return self.create_success_response(
            {
                "message": f"{field_name} is valid",
                "url": url,
                "protocol": url.split("://")[0],
                "domain": url.split("://")[1].split("/")[0],
            }
        )

    def validate_json(
        self, json_string: str, field_name: str = "json"
    ) -> Dict[str, Any]:
        """Valida formato JSON."""
        # Validar campo requerido
        required_error = self.validate_required_field(
            json_string, field_name, "JSON string"
        )
        if required_error:
            return required_error

        try:
            parsed_json = json.loads(json_string)
            return self.create_success_response(
                {
                    "message": f"{field_name} is valid JSON",
                    "parsed_data": parsed_json,
                    "data_type": type(parsed_json).__name__,
                }
            )
        except json.JSONDecodeError as e:
            return self.create_error_response(
                code=ErrorCodes.INVALID_JSON.value,
                message=f"{field_name} is not valid JSON",
                field=field_name,
                received={
                    "value": json_string,
                    "parsing_error": str(e),
                    "error_position": e.pos,
                },
                expected={
                    "conditions": [
                        "Must be valid JSON format",
                        "Must have proper syntax",
                    ],
                    "format": "Valid JSON string",
                    "examples": {
                        "valid": [
                            '{"key": "value"}',
                            "[1, 2, 3]",
                            '{"nested": {"key": "value"}}',
                        ],
                        "invalid": [
                            {
                                "value": "{invalid json}",
                                "reason": "missing quotes around keys",
                            },
                            {
                                "value": '{"key": value}',
                                "reason": "missing quotes around string values",
                            },
                        ],
                    },
                },
                solution=f"Ensure {field_name} follows valid JSON syntax",
            )

    def _get_valid_examples(self, field_type: str) -> List[Any]:
        """Obtiene ejemplos válidos para un tipo de campo."""
        examples = {
            "string": ["example", "test value"],
            "number": [42, 3.14, -10],
            "boolean": [True, False],
            "email": ["user@example.com"],
            "url": ["https://example.com"],
            "date": ["2023-10-27T10:30:00Z"],
            "json": ['{"key": "value"}'],
            "any": ["example", 42, True],
        }
        return examples.get(field_type, ["example"])

    def _get_string_examples(self, min_length: int, max_length: int) -> List[str]:
        """Obtiene ejemplos de cadenas válidas para un rango de longitud."""
        if max_length and max_length < 10:
            return ["a" * min_length, "b" * max_length]
        else:
            return ["short", "medium length string", "a" * min_length]


def main():
    """Ejemplo de uso de los patrones de validación."""
    print("=== Patrones de Validación ATDF ===\n")

    validator = ValidationPatterns()

    # Ejemplo 1: Validación de email
    print("1. Validación de Email")
    print("-" * 40)

    result = validator.validate_email("invalid-email")
    print("❌ Email inválido:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    result = validator.validate_email("user@example.com")
    print("✅ Email válido:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    # Ejemplo 2: Validación de contraseña
    print("2. Validación de Contraseña")
    print("-" * 40)

    result = validator.validate_password_strength("weak", min_length=6)
    print("❌ Contraseña débil:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    result = validator.validate_password_strength("MyP@ssw0rd!")
    print("✅ Contraseña fuerte:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    # Ejemplo 3: Validación de URL
    print("3. Validación de URL")
    print("-" * 40)

    result = validator.validate_url("not-a-url")
    print("❌ URL inválida:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    result = validator.validate_url("https://example.com")
    print("✅ URL válida:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    # Ejemplo 4: Validación de JSON
    print("4. Validación de JSON")
    print("-" * 40)

    result = validator.validate_json("{invalid json}")
    print("❌ JSON inválido:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    result = validator.validate_json('{"key": "value"}')
    print("✅ JSON válido:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    print("=== Fin del Ejemplo ===")


if __name__ == "__main__":
    main()
