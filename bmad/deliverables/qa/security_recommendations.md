# Security Recommendations – ATDF Selector Stack

1. **TLS Termination**
   - Colocar reverse proxy (nginx/traefik) para entornos productivos.
   - Habilitar certificados automáticos (Let's Encrypt o managed cert).

2. **HTTP Security Headers**
   - Añadir middleware en `selector/api.py` con cabeceras `X-Content-Type-Options`, `Referrer-Policy`, `Content-Security-Policy` (según caso).

3. **Secrets Management**
   - Documentar variables sensibles (`ATDF_SELECTOR_DB`) y recomendar `.env` en despliegues remotos.

4. **Port Hardening**
   - Configurar firewall para restringir 8000/8001/8050 a loopback.
   - Para redes compartidas, usar SSH túneles o VPN.

5. **Dependency Monitoring**
   - Programar `pip-audit` semanal en CI.
   - Revisar actualizaciones `requests`, `uvicorn`, `fastapi` trimestralmente.
