# ATDF Server Profile v1

The ATDF Server Profile defines the minimum HTTP surface area that an ATDF-compatible server must expose so agents, bridges, and external tooling can interact with tool catalogs in a consistent way.

## Required Endpoints

### `GET /health`
Returns service health information.

```json
{
  "status": "healthy",
  "uptime_seconds": 1234,
  "version": "2.1.0"
}
```

### `GET /metrics`
Prometheus-compatible metrics exporting the counters and histograms described below.

### `GET /tools`
Returns the catalog of available tools in ATDF format.

```json
{
  "tools": [
    { /* ATDF descriptor */ }
  ]
}
```

### `GET /tools/{tool_id}`
Returns a specific tool descriptor by `tool_id`.

### `POST /tools/validate`
Validates an ATDF descriptor sent in the request body. Responds with:

```json
{
  "valid": true
}
```

or with a 400 response using the ATDF error schema when invalid.

### `POST /convert/mcp`
Accepts an MCP catalog payload and returns the ATDF converted version. Supports an optional `enhanced` flag.

### `POST /search`
Accepts a query and optional filters, returning tool recommendations.

```json
{
  "query": "Book a flight",
  "language": "en",
  "limit": 5,
  "filters": {
    "tags": ["travel"],
    "requires": ["authentication"]
  }
}
```

Responses must include a ranked list of matching tools:

```json
{
  "results": [
    {
      "tool_id": "flight_booking",
      "score": 0.92,
      "metadata": {"tags": ["travel"]}
    }
  ]
}
```

## Error Handling
All error responses must comply with [`schema/error_atdf.json`](schema/error_atdf.json). When multiple errors are returned, the `errors` array should contain each violation in the order detected.

## Metrics (Prometheus)

Required series:

- `atdf_requests_total{method,endpoint,status_code}`
- `atdf_request_duration_seconds{method,endpoint}` (histogram)
- `atdf_tool_executions_total{tool_name,status}`
- `atdf_tool_execution_duration_seconds{tool_name}` (histogram)
- `atdf_errors_total{error_type,tool_name}`
- `atdf_active_connections`

## OpenAPI
Servers SHOULD publish their OpenAPI description under `GET /openapi.json` and enable Swagger UI at `/docs`.

## Authentication
If authentication is required, servers must return standard HTTP statuses (401/403) and provide instructions in the error detail. For local/testing scenarios, unauthenticated access SHOULD be allowed.

## Conformance Checklist

1. `GET /health` returns HTTP 200 with `status` field.
2. `GET /metrics` exposes all required Prometheus series.
3. `GET /tools` returns an array of ATDF descriptors.
4. `GET /tools/{tool_id}` returns 404 with ATDF error schema when not found.
5. `POST /tools/validate` validates descriptors and returns ATDF error schema on failure.
6. `POST /convert/mcp` accepts valid MCP payloads and returns ATDF output.
7. `POST /search` supports `language`, `limit`, and optional filters.
8. All error responses conform to `schema/error_atdf.json`.
9. OpenAPI spec is available at `/openapi.json`.
10. Integration tests covering these endpoints pass in the TCK suite.
