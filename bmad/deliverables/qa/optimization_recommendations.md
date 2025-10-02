# Optimization Recommendations – Selector Performance

1. **Warmup Request**
   - Ejecutar una llamada preliminar al selector antes de medir latencia (reduce el primer acceso ~15 ms).

2. **Connection Pooling**
   - Configurar `requests.Session` en performance_test_suite.py para reutilizar sockets.

3. **Uvicorn Workers**
   - Evaluar `--workers 2` cuando `tool_count` > 20 (latencia estable <110 ms).

4. **Async n8n Node**
   - Para cargas superiores, utilizar nodos HTTP asincrónicos o batching en n8n.

5. **Monitoring**
   - Agregar métrica de latencia p95 al pipeline CI para detectar regresiones tempranas.
