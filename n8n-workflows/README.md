# 📋 N8N Workflows Documentation - ATDF + MCP Integration

## 🎯 Overview

This directory contains n8n workflows that demonstrate the integration between ATDF (Agent Tool Description Format), MCP (Model Context Protocol), and n8n automation platform.

## 🏗️ Architecture

```
ATDF Server (Port 8000) → MCP Bridge (Port 8001) → n8n (Port 5678)
```

- **ATDF Server**: Provides tool definitions and execution capabilities
- **MCP Bridge**: Translates between ATDF and MCP protocols
- **n8n**: Workflow automation platform that consumes MCP tools

## 📁 Available Workflows

### 1. Hotel Reservation Test (`hotel-reservation-test.json`)

**Purpose**: Test the hotel reservation tool through the ATDF-MCP integration.

**Key Features**:
- Validates MCP bridge connectivity
- Checks tool availability
- Executes hotel reservation with sample data
- Handles success/error scenarios
- Sends Slack notifications

**Test Parameters**:
```json
{
  "destination": "Madrid",
  "checkin_date": "2024-02-15",
  "checkout_date": "2024-02-18",
  "guests": 2,
  "room_type": "deluxe"
}
```

**Expected Flow**:
1. Manual trigger → 2. Get tools → 3. Validate → 4. Book hotel → 5. Process response → 6. Notify

### 2. Flight Booking Test (`flight-booking-test.json`)

**Purpose**: Test the flight booking tool through the ATDF-MCP integration.

**Key Features**:
- Validates MCP bridge connectivity
- Checks flight booking tool availability
- Executes flight booking with sample data
- Handles booking confirmation
- Sends notifications via Slack and email

**Test Parameters**:
```json
{
  "origin": "Madrid",
  "destination": "Barcelona",
  "departure_date": "2024-02-15",
  "return_date": "2024-02-18",
  "passengers": 2,
  "class": "economy"
}
```

**Expected Flow**:
1. Manual trigger → 2. Get tools → 3. Validate → 4. Book flight → 5. Process response → 6. Notify

### 3. Complete Travel Booking (`complete-travel-booking.json`)

**Purpose**: Demonstrate end-to-end travel booking combining both hotel and flight reservations.

**Key Features**:
- Sequential booking workflow
- Data sharing between hotel and flight bookings
- Comprehensive error handling
- Final confirmation email
- Complete travel itinerary generation

**Workflow Steps**:
1. Initialize travel data
2. Verify ATDF tools availability
3. Book hotel reservation
4. Process hotel booking response
5. Book flight (if hotel successful)
6. Process flight booking response
7. Send final confirmation email

## 🔧 Configuration Requirements

### Prerequisites

1. **ATDF Server Running**: `http://localhost:8000`
2. **MCP Bridge Running**: `http://localhost:8001`
3. **n8n Running**: `http://localhost:5678`

### Environment Variables

Configure these in your n8n environment:

```bash
# Slack Integration (Optional)
SLACK_WEBHOOK_URL=your_slack_webhook_url

# Email Integration (Optional)
SMTP_HOST=your_smtp_host
SMTP_PORT=587
SMTP_USER=your_email@domain.com
SMTP_PASS=your_email_password
```

### MCP Bridge Endpoints

The workflows use these MCP bridge endpoints:

- **Get Tools**: `GET http://localhost:8001/tools`
- **Execute Tool**: `POST http://localhost:8001/execute`

## 🚀 Quick Start

### 1. Import Workflows

1. Open n8n at `http://localhost:5678`
2. Go to **Workflows** → **Import from File**
3. Select the desired workflow JSON file
4. Click **Import**

### 2. Configure Credentials

1. **Slack Webhook** (if using notifications):
   - Go to **Credentials** → **Add Credential**
   - Select **Slack Webhook**
   - Enter your webhook URL

2. **SMTP** (if using email notifications):
   - Go to **Credentials** → **Add Credential**
   - Select **SMTP**
   - Configure your email settings

### 3. Test Workflows

1. **Individual Tool Tests**:
   - Start with `hotel-reservation-test.json`
   - Then test `flight-booking-test.json`

2. **Complete Integration**:
   - Use `complete-travel-booking.json` for end-to-end testing

## 🔍 Troubleshooting

### Common Issues

1. **MCP Bridge Not Responding**:
   ```bash
   # Check if bridge is running
   curl http://localhost:8001/tools
   ```

2. **ATDF Server Not Available**:
   ```bash
   # Check if ATDF server is running
   curl http://localhost:8000/tools
   ```

3. **Tool Not Found**:
   - Verify tool names in MCP bridge response
   - Check tool availability: `GET /tools`

### Debug Steps

1. **Check Service Status**:
   ```bash
   # ATDF Server
   curl -s http://localhost:8000/health

   # MCP Bridge
   curl -s http://localhost:8001/tools

   # n8n
   curl -s http://localhost:5678
   ```

2. **Validate Tool Execution**:
   ```bash
   # Test tool execution directly
   curl -X POST http://localhost:8001/execute \
     -H "Content-Type: application/json" \
     -d '{"tool_name": "hotel_reservation", "parameters": {...}}'
   ```

## 📊 Monitoring

### Workflow Execution Logs

Monitor workflow execution in n8n:
1. Go to **Executions** tab
2. Check execution status and logs
3. Review error messages for debugging

### Service Health Checks

Regular health checks for all services:
- ATDF Server: `http://localhost:8000/health`
- MCP Bridge: `http://localhost:8001/tools`
- n8n: `http://localhost:5678`

## 🔄 Workflow Customization

### Adding New Tools

1. **Define Tool in ATDF**: Add new tool definition to ATDF server
2. **Restart Services**: Restart ATDF server and MCP bridge
3. **Update Workflows**: Modify n8n workflows to use new tools

### Modifying Parameters

Edit workflow nodes to change:
- Tool parameters
- Notification settings
- Error handling logic
- Data processing steps

## 📝 Best Practices

1. **Error Handling**: Always include error handling nodes
2. **Logging**: Use debug nodes for troubleshooting
3. **Validation**: Validate tool availability before execution
4. **Notifications**: Implement proper success/failure notifications
5. **Testing**: Test workflows individually before combining

## 🔗 Related Documentation

- [ATDF Specification](../docs/ATDF_SPECIFICATION.md)
- [MCP Integration Guide](../GUIA_INTEGRACION_N8N.md)
- [Integration Status](../estado_final_integracion.md)