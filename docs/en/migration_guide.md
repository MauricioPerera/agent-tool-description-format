# Migration Guide: Upgrading to ATDF v2.0.0

## Overview

This guide helps you migrate from ATDF v1.x to v2.0.0, which introduces the **Enriched Response Standard** as the foundation of the format. The main changes focus on improving error handling and response consistency.

## 🚀 What's New in v2.0.0

### Core Changes
- **Enriched Response Standard**: Comprehensive error responses with detailed `expected` fields
- **Schema Version Compatibility**: New `schema_version` field for better compatibility
- **Enhanced Validation**: More robust validation with detailed feedback
- **Improved Documentation**: Better examples and implementation guides

## 📋 Migration Checklist

### 1. Update Schema Version
Add the `schema_version` field to all your tool descriptions:

**Before (v1.x):**
```json
{
  "tool_id": "my_tool",
  "description": "My tool description",
  "when_to_use": "When you need to...",
  "how_to_use": {
    "inputs": [...],
    "outputs": {...}
  }
}
```

**After (v2.0.0):**
```json
{
  "schema_version": "2.0.0",
  "tool_id": "my_tool",
  "description": "My tool description",
  "when_to_use": "When you need to...",
  "how_to_use": {
    "inputs": [...],
    "outputs": {...}
  }
}
```

### 2. Implement Enriched Responses

Replace simple error messages with comprehensive enriched responses:

**Before (v1.x):**
```json
{
  "status": "error",
  "message": "Invalid date range"
}
```

**After (v2.0.0):**
```json
{
  "status": "error",
  "data": {
    "code": "INVALID_DATE_RANGE",
    "message": "Date range validation failed",
    "details": {
      "field": "date_range",
      "received": {
        "start_date": "2023-12-01",
        "end_date": "2023-11-01"
      },
      "expected": {
        "conditions": [
          "start_date must be before end_date",
          "both dates must be after current date"
        ],
        "examples": {
          "valid_range": {
            "start_date": "2023-10-28",
            "end_date": "2023-11-15"
          }
        }
      },
      "solution": "Adjust dates so that start_date is before end_date and both are after current date"
    }
  },
  "meta": {
    "timestamp": "2023-10-27T10:35:00Z"
  }
}
```

### 3. Update Error Handling Code

**Before (v1.x):**
```python
def validate_date_range(start_date, end_date):
    if start_date >= end_date:
        return {
            "status": "error",
            "message": "Start date must be before end date"
        }
    return {"status": "success", "data": {...}}
```

**After (v2.0.0):**
```python
from examples.validation_patterns import ValidationPatterns

def validate_date_range(start_date, end_date):
    validator = ValidationPatterns()
    return validator.validate_date_range(start_date, end_date)
```

## 🔧 Step-by-Step Migration

### Step 1: Update Dependencies

```bash
# Update your requirements.txt or install new dependencies
pip install -r requirements.txt

# If using the SDK, ensure you have the latest version
pip install --upgrade atdf-sdk
```

### Step 2: Update Tool Descriptions

1. **Add schema_version field** to all your tool descriptions
2. **Review and update** error handling in your tools
3. **Test** your tools with the new validation patterns

### Step 3: Implement Enriched Responses

1. **Choose a validation pattern** from the examples
2. **Replace simple error handling** with enriched responses
3. **Test** error scenarios to ensure proper feedback

### Step 4: Update Client Code

1. **Update error handling** in your client applications
2. **Parse enriched responses** for better user experience
3. **Display solution guidance** to users

## 📚 Migration Examples

### Example 1: Email Validation Tool

**Before (v1.x):**
```python
def validate_email(email):
    if not email or '@' not in email:
        return {
            "status": "error",
            "message": "Invalid email format"
        }
    return {"status": "success", "data": {"email": email}}
```

**After (v2.0.0):**
```python
from examples.validation_patterns import ValidationPatterns

def validate_email(email):
    validator = ValidationPatterns()
    return validator.validate_email(email)
```

### Example 2: Password Strength Tool

**Before (v1.x):**
```python
def validate_password(password):
    if len(password) < 8:
        return {
            "status": "error",
            "message": "Password too short"
        }
    return {"status": "success", "data": {"password": "valid"}}
```

**After (v2.0.0):**
```python
from examples.validation_patterns import ValidationPatterns

def validate_password(password):
    validator = ValidationPatterns()
    return validator.validate_password_strength(password)
```

### Example 3: Date Range Tool

**Before (v1.x):**
```python
def validate_date_range(start_date, end_date):
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        if start >= end:
            return {
                "status": "error",
                "message": "Invalid date range"
            }
        return {"status": "success", "data": {"range": "valid"}}
    except ValueError:
        return {
            "status": "error",
            "message": "Invalid date format"
        }
```

**After (v2.0.0):**
```python
from examples.validation_patterns import ValidationPatterns

def validate_date_range(start_date, end_date):
    validator = ValidationPatterns()
    return validator.validate_date_range(start_date, end_date)
```

## 🛠️ Using Migration Helpers

### Validation Patterns

Use the provided validation patterns to quickly implement enriched responses:

```python
from examples.validation_patterns import ValidationPatterns

# Create validator instance
validator = ValidationPatterns()

# Use pre-built validations
email_result = validator.validate_email("user@example.com")
password_result = validator.validate_password_strength("MyP@ssw0rd!")
date_result = validator.validate_date_range("2023-10-28", "2023-11-15")
url_result = validator.validate_url("https://example.com")
json_result = validator.validate_json('{"key": "value"}')
```

### Custom Validations

Extend the patterns for your specific needs:

```python
class CustomValidator(ValidationPatterns):
    def validate_custom_field(self, value, field_name):
        # Your custom validation logic
        if not self._custom_validation(value):
            return self.create_error_response(
                code="CUSTOM_VALIDATION_ERROR",
                message=f"{field_name} failed custom validation",
                field=field_name,
                received={"value": value},
                expected={
                    "conditions": ["Must pass custom validation"],
                    "examples": {"valid": ["valid_value"]}
                },
                solution="Ensure the value meets custom requirements"
            )
        return self.create_success_response({"message": "Custom validation passed"})
```

## 🔍 Testing Your Migration

### 1. Validate Tool Descriptions

```bash
# Use the smart validator to check your tools
python tools/validator.py --smart path/to/your/tools/

# Or use the SDK
from sdk import ATDFSDK
sdk = ATDFSDK()
sdk.validate_all_tools()
```

### 2. Test Error Scenarios

```python
# Test your enriched responses
def test_enriched_responses():
    validator = ValidationPatterns()
    
    # Test invalid email
    result = validator.validate_email("invalid-email")
    assert result["status"] == "error"
    assert result["data"]["code"] == "INVALID_EMAIL_FORMAT"
    assert "expected" in result["data"]["details"]
    assert "solution" in result["data"]["details"]
    
    # Test valid email
    result = validator.validate_email("user@example.com")
    assert result["status"] == "success"
```

### 3. Validate Response Schema

```python
import jsonschema

def validate_response_schema(response):
    with open("schema/enriched_response_schema.json") as f:
        schema = json.load(f)
    jsonschema.validate(response, schema)
```

## 📊 Migration Benefits

### Before Migration
- ❌ Simple error messages
- ❌ No context about what went wrong
- ❌ No guidance on how to fix issues
- ❌ Inconsistent error formats
- ❌ Difficult debugging

### After Migration
- ✅ Comprehensive error context
- ✅ Detailed expectations and constraints
- ✅ Step-by-step solution guidance
- ✅ Consistent response format
- ✅ Easy debugging and monitoring
- ✅ Better user experience
- ✅ AI-ready error handling

## 🚨 Breaking Changes

### 1. Response Structure
- Error responses now use `data` field instead of direct `message`
- New required fields: `code`, `details`, `meta`

### 2. Schema Version
- New required field: `schema_version`
- Tools without this field may not validate correctly

### 3. Error Codes
- Error codes are now required and must follow naming conventions
- Use UPPERCASE with underscores (e.g., `INVALID_DATE_RANGE`)

## 🔄 Rollback Plan

If you need to rollback to v1.x:

1. **Remove schema_version** from tool descriptions
2. **Revert to simple error responses**
3. **Update client code** to handle old format
4. **Test thoroughly** before deploying

## 📞 Getting Help

### Documentation
- [Enriched Responses Guide](enriched_responses_guide.md)
- [Best Practices](best_practices_enriched_responses.md)
- [Validation Patterns](../examples/validation_patterns.py)

### Examples
- [Complete Implementation Example](../examples/enriched_responses_example.py)
- [Validation Patterns](../examples/validation_patterns.py)

### Support
- Check the [GitHub Issues](https://github.com/MauricioPerera/agent-tool-description-format/issues)
- Review the [FAQ](faq.md)
- Join the [Discussions](https://github.com/MauricioPerera/agent-tool-description-format/discussions)

## 🎯 Migration Timeline

### Phase 1: Preparation (1-2 days)
- [ ] Review new features and changes
- [ ] Update dependencies
- [ ] Plan migration strategy

### Phase 2: Implementation (3-5 days)
- [ ] Update tool descriptions with schema_version
- [ ] Implement enriched responses
- [ ] Test error scenarios

### Phase 3: Testing (2-3 days)
- [ ] Validate all tools
- [ ] Test client applications
- [ ] Performance testing

### Phase 4: Deployment (1 day)
- [ ] Deploy updated tools
- [ ] Monitor for issues
- [ ] Update documentation

## 📈 Success Metrics

After migration, you should see:

- **Improved User Experience**: Better error messages and guidance
- **Reduced Support Tickets**: Users can self-solve issues
- **Faster Debugging**: Clear error context and validation results
- **Better Monitoring**: Detailed error analytics and patterns
- **AI Integration**: Better tool selection and error handling by AI agents

---

**Ready to migrate?** Start with Step 1 and follow the checklist above. The enriched response standard will significantly improve your tool's usability and maintainability. 