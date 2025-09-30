# ATDF Monitoring and Metrics

This document describes the monitoring and metrics system for the Agent Tool Description Format (ATDF) application.

## Overview

The ATDF application includes comprehensive monitoring using:
- **Prometheus** for metrics collection
- **Grafana** for visualization and dashboards
- **Custom metrics** for application-specific monitoring
- **Health checks** for service availability
- **Alerting** for proactive issue detection

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ATDF API      │───▶│   Prometheus    │───▶│    Grafana      │
│                 │    │                 │    │                 │
│ /metrics        │    │ Scrapes metrics │    │ Visualizations  │
│ /health         │    │ Stores data     │    │ Dashboards      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Alert Rules   │    │   Notifications │
│   Redis         │    │                 │    │                 │
│   System        │    │ Thresholds      │    │ Email/Slack     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Metrics Collected

### HTTP Request Metrics

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `atdf_requests_total` | Counter | Total HTTP requests | `method`, `endpoint`, `status` |
| `atdf_request_duration_seconds` | Histogram | Request duration | `method`, `endpoint` |
| `atdf_active_connections` | Gauge | Active connections | - |
| `atdf_errors_total` | Counter | Total errors | `error_type`, `endpoint` |

### Tool Execution Metrics

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `atdf_tool_executions_total` | Counter | Tool executions | `tool_name`, `status` |
| `atdf_tool_execution_duration_seconds` | Histogram | Tool execution time | `tool_name` |

### System Metrics

- CPU usage
- Memory usage
- Disk usage
- Network I/O
- Database connections
- Redis memory usage

## Quick Start

### 1. Setup Monitoring

```bash
# Automated setup
make setup-monitoring

# Manual setup
docker-compose up -d prometheus grafana postgres redis
```

### 2. Start Application

```bash
# Start ATDF API
docker-compose up -d atdf-api

# Check status
make monitoring-status
```

### 3. Access Dashboards

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Application Metrics**: http://localhost:8000/metrics
- **Health Check**: http://localhost:8000/health

### 4. Test Metrics

```bash
# Run metrics test
make test-metrics

# Check metrics manually
make metrics
```

## Configuration

### Prometheus Configuration

The Prometheus configuration is defined in `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'atdf-api'
    static_configs:
      - targets: ['atdf-api:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Grafana Dashboards

Pre-configured dashboards include:

1. **ATDF Overview Dashboard**
   - Request rate and latency
   - Error rates
   - Tool execution metrics
   - System resources

2. **Infrastructure Dashboard**
   - Database metrics
   - Redis metrics
   - System metrics

### Alert Rules

Key alerts configured:

- API service down
- High error rate (>5%)
- High response time (>2s)
- Database connection issues
- High memory usage (>80%)
- Disk space low (<10%)

## Custom Metrics

### Adding New Metrics

1. **Define the metric** in `fastapi_mcp_integration.py`:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metric
CUSTOM_METRIC = Counter(
    'atdf_custom_operations_total',
    'Total custom operations',
    ['operation_type', 'status']
)
```

2. **Instrument your code**:

```python
def custom_operation():
    start_time = time.time()
    try:
        # Your operation logic
        result = perform_operation()
        
        # Record success
        CUSTOM_METRIC.labels(
            operation_type='data_processing',
            status='success'
        ).inc()
        
        return result
    except Exception as e:
        # Record error
        CUSTOM_METRIC.labels(
            operation_type='data_processing',
            status='error'
        ).inc()
        raise
```

3. **Update Grafana dashboard** to visualize the new metric.

### Metric Types

- **Counter**: Monotonically increasing values (requests, errors)
- **Gauge**: Values that can go up and down (connections, memory)
- **Histogram**: Distribution of values (response times, sizes)
- **Summary**: Similar to histogram with quantiles

## Health Checks

### Application Health

The `/health` endpoint provides:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy"
  },
  "metrics": {
    "total_reservations": 150,
    "total_bookings": 89,
    "uptime_seconds": 3600
  }
}
```

### Service Dependencies

Health checks verify:
- Database connectivity
- Redis connectivity
- External API availability
- Disk space
- Memory usage

## Alerting

### Alert Configuration

Alerts are defined in `alert_rules.yml`:

```yaml
groups:
  - name: atdf_alerts
    rules:
      - alert: ATDFServiceDown
        expr: up{job="atdf-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "ATDF API service is down"
```

### Notification Channels

Configure notifications in Grafana:
1. Go to Alerting → Notification channels
2. Add channels (email, Slack, webhook)
3. Test notifications

## Troubleshooting

### Common Issues

1. **Metrics not appearing**
   - Check Prometheus targets: http://localhost:9090/targets
   - Verify application is exposing `/metrics`
   - Check network connectivity

2. **Grafana dashboard empty**
   - Verify Prometheus datasource configuration
   - Check time range in dashboard
   - Ensure metrics are being scraped

3. **High memory usage**
   - Check metric cardinality
   - Review label usage
   - Consider metric retention policies

### Debug Commands

```bash
# Check service status
make monitoring-status

# View logs
docker-compose logs -f atdf-api
docker-compose logs -f prometheus
docker-compose logs -f grafana

# Test metrics endpoint
curl http://localhost:8000/metrics

# Query Prometheus
curl 'http://localhost:9090/api/v1/query?query=up'
```

## Performance Considerations

### Metric Collection

- **Scrape interval**: Balance between granularity and performance
- **Retention**: Configure appropriate data retention
- **Cardinality**: Avoid high-cardinality labels

### Resource Usage

- Prometheus: ~100MB RAM + storage
- Grafana: ~50MB RAM
- Application overhead: <5% CPU, <10MB RAM

### Optimization Tips

1. Use appropriate metric types
2. Limit label cardinality
3. Set reasonable scrape intervals
4. Configure data retention policies
5. Use recording rules for complex queries

## Security

### Access Control

- Grafana authentication enabled
- Prometheus access restricted
- Metrics endpoint public (no sensitive data)

### Data Privacy

- No sensitive data in metrics
- Sanitized error messages
- Anonymized user identifiers

## Maintenance

### Regular Tasks

1. **Monitor disk usage** for Prometheus data
2. **Review alert rules** and thresholds
3. **Update dashboards** as application evolves
4. **Backup Grafana** configuration
5. **Test alerting** channels

### Upgrades

1. Update Docker images
2. Migrate configuration files
3. Test monitoring functionality
4. Update documentation

## API Reference

### Metrics Endpoint

**GET /metrics**

Returns Prometheus-formatted metrics:

```
# HELP atdf_requests_total Total HTTP requests
# TYPE atdf_requests_total counter
atdf_requests_total{method="GET",endpoint="/health",status="200"} 42
```

### Health Endpoint

**GET /health**

Returns application health status:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {...},
  "metrics": {...}
}
```

## Examples

### Query Examples

```promql
# Request rate
rate(atdf_requests_total[5m])

# Error rate
rate(atdf_requests_total{status=~"4..|5.."}[5m]) / rate(atdf_requests_total[5m])

# 95th percentile response time
histogram_quantile(0.95, rate(atdf_request_duration_seconds_bucket[5m]))

# Tool success rate
rate(atdf_tool_executions_total{status="success"}[5m]) / rate(atdf_tool_executions_total[5m])
```

### Dashboard Panels

See `grafana/dashboards/atdf-dashboard.json` for complete dashboard configuration.

## Support

For monitoring-related issues:

1. Check this documentation
2. Review logs and metrics
3. Test with provided scripts
4. Consult Prometheus/Grafana documentation

---

*Last updated: January 2024*