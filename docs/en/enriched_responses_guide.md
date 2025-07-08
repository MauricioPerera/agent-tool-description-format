# Enriched Responses and Detailed Expected Field Guide

## Overview

This guide establishes the **Enriched Response Standard** as the foundation of ATDF (Agent Tool Description Format). The key innovation is the detailed `expected` field that provides comprehensive context about what was expected, what was received, and how to fix issues.

## Core Principles

### 1. Standard Response Structure

All ATDF tools must return responses in this consistent format:

```json
{
  "status": "success|error",
  "data": {
    // Success: actual result data
    // Error: error details with enriched context
  },
  "meta": {
    "timestamp": "ISO 8601 timestamp"
  }
}
```

### 2. Enriched Error Responses

Error responses must include detailed context in the `expected` field:

```json
{
  "status": "error",
  "data": {
    "code": "UNIQUE_ERROR_CODE",
    "message": "Human-readable error description",
    "details": {
      "field": "field_name_with_error",
      "received": {
        // What was actually received
      },
      "expected": {
        // Detailed expectations with conditions, examples, and constraints
      },
      "validation_results": {
        // Specific validation failures
      },
      "solution": "Step-by-step solution guide"
    }
  },
  "meta": {
    "timestamp": "2023-10-27T10:35:00Z"
  }
}
```

## Detailed Expected Field Structure

### Basic Structure

```json
{
  "expected": {
    "conditions": [
      "Condition 1 description",
      "Condition 2 description",
      "Condition 3 description"
    ],
    "format": "Expected format specification",
    "constraints": {
      "min_value": "minimum allowed value",
      "max_value": "maximum allowed value",
      "pattern": "regex pattern if applicable"
    },
    "examples": {
      "valid": ["example1", "example2"],
      "invalid": [
        {
          "value": "invalid_example",
          "reason": "why it's invalid"
        }
      ]
    }
  }
}
```

### Advanced Structure with Validation Results

```json
{
  "expected": {
    "conditions": [
      "start_date must be before end_date",
      "start_date must be after current date",
      "end_date must be after current date"
    ],
    "format": "ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)",
    "constraints": {
      "min_start_date": "now + 1 day",
      "max_end_date": "now + 365 days",
      "min_duration": "1 day",
      "max_duration": "30 days"
    },
    "examples": {
      "valid_range": {
        "start_date": "2023-10-28T00:00:00Z",
        "end_date": "2023-11-15T23:59:59Z"
      },
      "invalid_ranges": [
        {
          "start_date": "2023-11-01T00:00:00Z",
          "end_date": "2023-10-01T00:00:00Z",
          "reason": "start_date after end_date"
        }
      ]
    }
  },
  "validation_results": {
    "start_before_end": false,
    "start_after_now": true,
    "end_after_now": false
  }
}
```

## Implementation Examples

### 1. Date Range Validation

```python
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

def validate_date_range(start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Validates a date range with enriched error responses.
    """
    now = datetime.now(timezone.utc)
    
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Validations
        start_before_end = start_dt < end_dt
        start_after_now = start_dt > now
        end_after_now = end_dt > now
        
        # Success case
        if start_before_end and start_after_now and end_after_now:
            return {
                "status": "success",
                "data": {
                    "message": "Date range is valid",
                    "start_date": start_date,
                    "end_date": end_date,
                    "duration_days": (end_dt - start_dt).days
                },
                "meta": {
                    "timestamp": now.isoformat()
                }
            }
        
        # Error case with enriched details
        validation_results = {
            "start_before_end": start_before_end,
            "start_after_now": start_after_now,
            "end_after_now": end_after_now
        }
        
        failed_conditions = []
        if not start_before_end:
            failed_conditions.append("start_date must be before end_date")
        if not start_after_now:
            failed_conditions.append("start_date must be after current date")
        if not end_after_now:
            failed_conditions.append("end_date must be after current date")
        
        return {
            "status": "error",
            "data": {
                "code": "INVALID_DATE_RANGE",
                "message": f"Date range validation failed: {', '.join(failed_conditions)}",
                "details": {
                    "field": "date_range",
                    "received": {
                        "start_date": start_date,
                        "end_date": end_date,
                        "current_time": now.isoformat()
                    },
                    "expected": {
                        "conditions": [
                            "start_date must be before end_date",
                            "start_date must be after current date (now)",
                            "end_date must be after current date (now)"
                        ],
                        "format": "ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)",
                        "constraints": {
                            "min_start_date": "now + 1 day",
                            "max_end_date": "now + 365 days"
                        },
                        "examples": {
                            "valid_range": {
                                "start_date": (now + timedelta(days=1)).isoformat(),
                                "end_date": (now + timedelta(days=15)).isoformat()
                            }
                        }
                    },
                    "validation_results": validation_results,
                    "solution": "Adjust dates so that: 1) start_date is before end_date, 2) both dates are after current date"
                }
            },
            "meta": {
                "timestamp": now.isoformat()
            }
        }
        
    except ValueError as e:
        return {
            "status": "error",
            "data": {
                "code": "INVALID_DATE_FORMAT",
                "message": "Invalid date format provided",
                "details": {
                    "field": "date_format",
                    "received": {
                        "start_date": start_date,
                        "end_date": end_date
                    },
                    "expected": {
                        "format": "ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)",
                        "examples": [
                            "2023-10-27T10:30:00Z",
                            "2023-10-27T10:30:00+00:00"
                        ]
                    },
                    "parsing_error": str(e),
                    "solution": "Use ISO 8601 format for dates"
                }
            },
            "meta": {
                "timestamp": now.isoformat()
            }
        }
```

### 2. Email Validation

```python
import re
from typing import Dict, Any

def validate_email(email: str) -> Dict[str, Any]:
    """
    Validates email with enriched error responses.
    """
    if not email:
        return {
            "status": "error",
            "data": {
                "code": "EMPTY_EMAIL",
                "message": "Email address cannot be empty",
                "details": {
                    "field": "email",
                    "received": {
                        "email": email
                    },
                    "expected": {
                        "conditions": [
                            "Email must not be empty",
                            "Email must contain @ symbol",
                            "Email must have valid domain"
                        ],
                        "format": "RFC 5322 email format",
                        "examples": {
                            "valid": ["user@example.com", "test.email+tag@domain.co.uk"],
                            "invalid": ["invalid-email", "@domain.com", "user@"]
                        }
                    },
                    "solution": "Provide a valid email address"
                }
            },
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    
    # RFC 5322 compliant regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return {
            "status": "error",
            "data": {
                "code": "INVALID_EMAIL_FORMAT",
                "message": "Email format is invalid",
                "details": {
                    "field": "email",
                    "received": {
                        "email": email
                    },
                    "expected": {
                        "conditions": [
                            "Must contain exactly one @ symbol",
                            "Local part before @ must be valid",
                            "Domain after @ must be valid",
                            "Must have valid TLD (2+ characters)"
                        ],
                        "format": "RFC 5322 email format",
                        "constraints": {
                            "max_length": "254 characters total",
                            "local_part_max": "64 characters",
                            "domain_max": "253 characters"
                        },
                        "examples": {
                            "valid": ["user@example.com", "test.email+tag@domain.co.uk"],
                            "invalid": [
                                {
                                    "value": "invalid-email",
                                    "reason": "missing @ symbol"
                                },
                                {
                                    "value": "@domain.com",
                                    "reason": "empty local part"
                                },
                                {
                                    "value": "user@",
                                    "reason": "empty domain"
                                }
                            ]
                        }
                    },
                    "solution": "Use a valid email format like user@example.com"
                }
            },
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    
    return {
        "status": "success",
        "data": {
            "message": "Email is valid",
            "email": email,
            "local_part": email.split('@')[0],
            "domain": email.split('@')[1]
        },
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
```

### 3. Password Strength Validation

```python
import re
from typing import Dict, Any

def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validates password strength with detailed feedback.
    """
    if not password:
        return {
            "status": "error",
            "data": {
                "code": "EMPTY_PASSWORD",
                "message": "Password cannot be empty",
                "details": {
                    "field": "password",
                    "received": {
                        "password": ""
                    },
                    "expected": {
                        "conditions": [
                            "Password must not be empty",
                            "Minimum 8 characters",
                            "At least one uppercase letter",
                            "At least one lowercase letter",
                            "At least one number",
                            "At least one special character"
                        ],
                        "constraints": {
                            "min_length": 8,
                            "max_length": 128
                        }
                    },
                    "solution": "Provide a non-empty password"
                }
            },
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    
    # Validation checks
    checks = {
        "min_length": len(password) >= 8,
        "max_length": len(password) <= 128,
        "has_uppercase": bool(re.search(r'[A-Z]', password)),
        "has_lowercase": bool(re.search(r'[a-z]', password)),
        "has_number": bool(re.search(r'\d', password)),
        "has_special": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    }
    
    passed_checks = sum(checks.values())
    
    if passed_checks == len(checks):
        return {
            "status": "success",
            "data": {
                "message": "Password meets all strength requirements",
                "strength": "strong",
                "score": passed_checks,
                "max_score": len(checks)
            },
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    
    # Determine strength level
    if passed_checks >= 5:
        strength = "medium"
    elif passed_checks >= 3:
        strength = "weak"
    else:
        strength = "very_weak"
    
    failed_conditions = []
    if not checks["min_length"]:
        failed_conditions.append("minimum 8 characters")
    if not checks["max_length"]:
        failed_conditions.append("maximum 128 characters")
    if not checks["has_uppercase"]:
        failed_conditions.append("at least one uppercase letter")
    if not checks["has_lowercase"]:
        failed_conditions.append("at least one lowercase letter")
    if not checks["has_number"]:
        failed_conditions.append("at least one number")
    if not checks["has_special"]:
        failed_conditions.append("at least one special character")
    
    return {
        "status": "error",
        "data": {
            "code": "WEAK_PASSWORD",
            "message": f"Password strength is {strength}",
            "details": {
                "field": "password",
                "received": {
                    "password_length": len(password),
                    "strength_level": strength
                },
                "expected": {
                    "conditions": [
                        "Minimum 8 characters",
                        "Maximum 128 characters", 
                        "At least one uppercase letter (A-Z)",
                        "At least one lowercase letter (a-z)",
                        "At least one number (0-9)",
                        "At least one special character (!@#$%^&*(),.?\":{}|<>)"
                    ],
                    "strength_levels": {
                        "very_weak": "meets 0-2 conditions",
                        "weak": "meets 3-4 conditions",
                        "medium": "meets 5-6 conditions",
                        "strong": "meets all 6 conditions"
                    },
                    "examples": {
                        "strong": "MyP@ssw0rd!",
                        "medium": "MyPassword1",
                        "weak": "mypassword",
                        "very_weak": "123"
                    }
                },
                "validation_results": checks,
                "failed_conditions": failed_conditions,
                "solution": f"Add the missing requirements: {', '.join(failed_conditions)}"
            }
        },
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
```

## Best Practices

### 1. Error Code Naming

- Use UPPERCASE with underscores
- Be descriptive and specific
- Examples: `INVALID_DATE_RANGE`, `WEAK_PASSWORD`, `EMPTY_EMAIL`

### 2. Expected Field Content

- **Conditions**: List all validation rules clearly
- **Format**: Specify exact format requirements
- **Constraints**: Include min/max values, patterns, etc.
- **Examples**: Provide both valid and invalid examples
- **Validation Results**: Show which specific checks failed

### 3. Solution Field

- Be actionable and specific
- Provide step-by-step guidance
- Include code examples when helpful
- Reference the failed conditions

### 4. Consistency

- Use the same structure across all tools
- Maintain consistent field names
- Follow the same error code patterns
- Use consistent timestamp format (ISO 8601)

## Integration with ATDF Schema

This enriched response format should be integrated into the ATDF schema to ensure all tools follow this standard. The schema should include:

1. Required error response structure
2. Detailed expected field format
3. Validation result structure
4. Solution field requirements

## Benefits

1. **Better Debugging**: Clear understanding of what went wrong
2. **Self-Documenting**: Responses serve as documentation
3. **User-Friendly**: Actionable error messages
4. **Consistent**: Standardized across all tools
5. **Extensible**: Easy to add new validation types

This enriched response format establishes ATDF as a comprehensive standard for tool communication, making it easier for AI agents and developers to understand and fix issues. 