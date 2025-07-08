# Best Practices for Enriched Responses in ATDF

## Overview

This guide provides best practices for implementing the Enriched Response Standard in ATDF tools. Following these practices ensures consistent, helpful, and maintainable error handling across all your tools.

## 🎯 Core Principles

### 1. Be Comprehensive
Always provide complete context about what went wrong and how to fix it.

### 2. Be Actionable
Give users specific steps they can take to resolve the issue.

### 3. Be Consistent
Use the same structure and patterns across all your tools.

### 4. Be User-Friendly
Write error messages that humans can understand and act upon.

## 📋 Response Structure Best Practices

### Standard Response Format

```json
{
  "status": "success|error",
  "data": {
    // Success: actual result data
    // Error: comprehensive error details
  },
  "meta": {
    "timestamp": "ISO 8601 timestamp"
  }
}
```

### Error Response Structure

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
        // Detailed expectations
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

## 🔧 Implementation Best Practices

### 1. Error Code Naming

**✅ Good:**
```json
{
  "code": "INVALID_DATE_RANGE",
  "code": "WEAK_PASSWORD",
  "code": "EMPTY_EMAIL"
}
```

**❌ Bad:**
```json
{
  "code": "error1",
  "code": "invalid_input",
  "code": "bad_data"
}
```

**Guidelines:**
- Use UPPERCASE with underscores
- Be descriptive and specific
- Include the context (e.g., `INVALID_DATE_RANGE` not just `INVALID_RANGE`)
- Make codes unique across your entire system

### 2. Expected Field Structure

**✅ Comprehensive Example:**
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
      "valid": {
        "start_date": "2023-10-28T00:00:00Z",
        "end_date": "2023-11-15T23:59:59Z"
      },
      "invalid": [
        {
          "value": {
            "start_date": "2023-11-01T00:00:00Z",
            "end_date": "2023-10-01T00:00:00Z"
          },
          "reason": "start_date after end_date"
        }
      ]
    }
  }
}
```

### 3. Solution Field Guidelines

**✅ Good Solutions:**
```json
{
  "solution": "Adjust dates so that: 1) start_date is before end_date, 2) both dates are after current date"
}
```

**❌ Bad Solutions:**
```json
{
  "solution": "Fix the dates",
  "solution": "Invalid input",
  "solution": "Check your data"
}
```

**Guidelines:**
- Be specific and actionable
- Provide step-by-step instructions
- Reference the failed conditions
- Include examples when helpful

## 🛠️ Implementation Patterns

### 1. Validation Helper Class

```python
class EnrichedResponseValidator:
    def __init__(self):
        self.now = datetime.now(timezone.utc)
    
    def create_error_response(
        self, 
        code: str, 
        message: str, 
        field: str,
        received: Dict[str, Any],
        expected: Dict[str, Any],
        validation_results: Dict[str, bool] = None,
        solution: str = None
    ) -> Dict[str, Any]:
        """Create a standardized enriched error response."""
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
                    "solution": solution or "Review the expected conditions and adjust your input accordingly."
                }
            },
            "meta": {
                "timestamp": self.now.isoformat()
            }
        }
```

### 2. Validation Result Tracking

```python
@dataclass
class ValidationResult:
    """Track individual validation results."""
    condition: str
    passed: bool
    details: str = ""

# Usage
validations = [
    ValidationResult("start_date must be before end_date", start_dt < end_dt),
    ValidationResult("start_date must be after current date", start_dt > self.now),
    ValidationResult("end_date must be after current date", end_dt > self.now)
]

# Convert to response format
validation_results = {v.condition: v.passed for v in validations}
failed_conditions = [v.condition for v in validations if not v.passed]
```

### 3. Consistent Error Codes

```python
class ErrorCodes:
    """Centralized error code definitions."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_DATE_RANGE = "INVALID_DATE_RANGE"
    INVALID_EMAIL_FORMAT = "INVALID_EMAIL_FORMAT"
    WEAK_PASSWORD = "WEAK_PASSWORD"
    EMPTY_FIELD = "EMPTY_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
```

## 📝 Common Patterns

### 1. Date Validation

```python
def validate_date_range(self, start_date: str, end_date: str) -> Dict[str, Any]:
    """Validate date range with enriched responses."""
    try:
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        validations = [
            ValidationResult("start_date must be before end_date", start_dt < end_dt),
            ValidationResult("start_date must be after current date", start_dt > self.now),
            ValidationResult("end_date must be after current date", end_dt > self.now)
        ]
        
        if all(v.passed for v in validations):
            return self.create_success_response({
                "message": "Date range is valid",
                "start_date": start_date,
                "end_date": end_date,
                "duration_days": (end_dt - start_dt).days
            })
        
        failed_conditions = [v.condition for v in validations if not v.passed]
        validation_results = {v.condition: v.passed for v in validations}
        
        return self.create_error_response(
            code=ErrorCodes.INVALID_DATE_RANGE,
            message=f"Date range validation failed: {', '.join(failed_conditions)}",
            field="date_range",
            received={
                "start_date": start_date,
                "end_date": end_date,
                "current_time": self.now.isoformat()
            },
            expected={
                "conditions": [v.condition for v in validations],
                "format": "ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)",
                "constraints": {
                    "min_start_date": "now + 1 day",
                    "max_end_date": "now + 365 days"
                },
                "examples": {
                    "valid_range": {
                        "start_date": (self.now + timedelta(days=1)).isoformat(),
                        "end_date": (self.now + timedelta(days=15)).isoformat()
                    }
                }
            },
            validation_results=validation_results,
            solution=f"Adjust your dates to meet these requirements: {', '.join(failed_conditions)}"
        )
        
    except ValueError as e:
        return self.create_error_response(
            code=ErrorCodes.INVALID_FORMAT,
            message="Invalid date format provided",
            field="date_format",
            received={
                "start_date": start_date,
                "end_date": end_date,
                "parsing_error": str(e)
            },
            expected={
                "format": "ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)",
                "examples": [
                    "2023-10-27T10:30:00Z",
                    "2023-10-27T10:30:00+00:00"
                ]
            },
            solution="Use ISO 8601 format for dates: YYYY-MM-DDTHH:mm:ssZ"
        )
```

### 2. Email Validation

```python
def validate_email(self, email: str) -> Dict[str, Any]:
    """Validate email with enriched responses."""
    if not email:
        return self.create_error_response(
            code=ErrorCodes.EMPTY_FIELD,
            message="Email address cannot be empty",
            field="email",
            received={"email": email},
            expected={
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
            solution="Provide a valid email address"
        )
    
    # RFC 5322 compliant regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return self.create_error_response(
            code=ErrorCodes.INVALID_EMAIL_FORMAT,
            message="Email format is invalid",
            field="email",
            received={
                "email": email,
                "length": len(email),
                "contains_at": "@" in email,
                "at_count": email.count("@")
            },
            expected={
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
                        }
                    ]
                }
            },
            solution="Use a valid email format like user@example.com"
        )
    
    return self.create_success_response({
        "message": "Email is valid",
        "email": email,
        "local_part": email.split('@')[0],
        "domain": email.split('@')[1]
    })
```

## 🔍 Testing Best Practices

### 1. Test All Error Scenarios

```python
def test_date_validation_errors():
    validator = EnrichedResponseValidator()
    
    # Test invalid date range
    result = validator.validate_date_range("2023-12-01", "2023-11-01")
    assert result["status"] == "error"
    assert result["data"]["code"] == "INVALID_DATE_RANGE"
    assert "start_date must be before end_date" in result["data"]["details"]["expected"]["conditions"]
    
    # Test invalid format
    result = validator.validate_date_range("invalid-date", "2023-11-01")
    assert result["status"] == "error"
    assert result["data"]["code"] == "INVALID_FORMAT"
    assert "ISO 8601" in result["data"]["details"]["expected"]["format"]
```

### 2. Validate Response Schema

```python
import jsonschema

def test_response_schema():
    validator = EnrichedResponseValidator()
    result = validator.validate_date_range("2023-12-01", "2023-11-01")
    
    # Load the enriched response schema
    with open("schema/enriched_response_schema.json") as f:
        schema = json.load(f)
    
    # Validate the response
    jsonschema.validate(result, schema)
```

## 📊 Monitoring and Analytics

### 1. Track Error Patterns

```python
def log_error_analytics(error_response: Dict[str, Any]):
    """Log error analytics for monitoring."""
    analytics = {
        "error_code": error_response["data"]["code"],
        "field": error_response["data"]["details"]["field"],
        "timestamp": error_response["meta"]["timestamp"],
        "failed_conditions": list(error_response["data"]["details"]["validation_results"].keys())
    }
    
    # Send to your analytics system
    logger.info(f"Error Analytics: {analytics}")
```

### 2. Error Rate Monitoring

```python
class ErrorRateMonitor:
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.total_requests = 0
    
    def record_response(self, response: Dict[str, Any]):
        self.total_requests += 1
        if response["status"] == "error":
            self.error_counts[response["data"]["code"]] += 1
    
    def get_error_rate(self) -> Dict[str, float]:
        return {
            code: count / self.total_requests 
            for code, count in self.error_counts.items()
        }
```

## 🚀 Performance Considerations

### 1. Lazy Evaluation

```python
def create_expected_field(self, conditions: List[str], examples: Dict = None) -> Dict[str, Any]:
    """Create expected field with lazy evaluation for expensive operations."""
    expected = {
        "conditions": conditions,
        "format": self.get_format_description()
    }
    
    # Only add examples if they're not too expensive to generate
    if examples and len(examples) < 10:
        expected["examples"] = examples
    
    return expected
```

### 2. Caching Common Responses

```python
class ResponseCache:
    def __init__(self):
        self.cache = {}
    
    def get_cached_response(self, error_code: str, field: str) -> Optional[Dict[str, Any]]:
        key = f"{error_code}:{field}"
        return self.cache.get(key)
    
    def cache_response(self, error_code: str, field: str, response: Dict[str, Any]):
        key = f"{error_code}:{field}"
        self.cache[key] = response
```

## 📚 Documentation Standards

### 1. Document All Error Codes

```python
class ErrorCodeDocumentation:
    """Documentation for all error codes."""
    
    ERROR_CODES = {
        "INVALID_DATE_RANGE": {
            "description": "Date range validation failed",
            "common_causes": [
                "Start date is after end date",
                "Dates are in the past",
                "Date range is too long"
            ],
            "solution": "Ensure start_date is before end_date and both dates are in the future"
        },
        "WEAK_PASSWORD": {
            "description": "Password does not meet strength requirements",
            "common_causes": [
                "Password is too short",
                "Missing required character types",
                "Common password patterns"
            ],
            "solution": "Use a password with at least 8 characters including uppercase, lowercase, number, and special character"
        }
    }
```

### 2. API Documentation

```python
def document_error_responses():
    """Generate API documentation for error responses."""
    docs = []
    
    for code, info in ErrorCodeDocumentation.ERROR_CODES.items():
        docs.append(f"""
## {code}

**Description**: {info['description']}

**Common Causes**:
{chr(10).join(f"- {cause}" for cause in info['common_causes'])}

**Solution**: {info['solution']}

**Example Response**:
```json
{json.dumps(create_example_response(code), indent=2)}
```
""")
    
    return "\n".join(docs)
```

## 🎯 Summary

Following these best practices ensures that your ATDF tools provide:

1. **Comprehensive Error Context**: Users understand exactly what went wrong
2. **Actionable Solutions**: Clear steps to fix the problem
3. **Consistent Experience**: Same patterns across all tools
4. **Maintainable Code**: Easy to update and extend
5. **Good Performance**: Efficient error handling
6. **Proper Monitoring**: Track and improve error handling over time

Remember: The goal is to make errors helpful, not just informative. Every error response should guide the user toward a solution. 