# Autonomia en procesos largos

Para evitar bloquear la terminal principal cuando se levantan servicios (API, Next.js, etc.), debemos lanzar cada comando en su propia sesion o proceso en segundo plano. Esto asegura que la ventana de trabajo siga libre y no parezca que el agente este "congelado".

## Ejemplo PowerShell

```powershell
# Levantar API en otra ventana
$cmd = "cd 'd:\\repos\\Nueva carpeta (12)\\agent-tool-description-format\\ardf-manager'; npm run dev --workspace @ardf/api"
Start-Process powershell -ArgumentList '-NoLogo', '-Command', $cmd
```

## Beneficios
- El proceso largo corre en su propia consola.
- Podemos seguir trabajando en la terminal principal (sembrar datos, correr migraciones, editar codigo, etc.).
- Se evita depender del usuario para reabrir o suspender la ejecucion.

## Seguimiento
- Verificar el servicio: `curl http://localhost:4000/health`.
- Detenerlo desde la ventana secundaria o usando `Stop-Process (Get-Process -Name node | Where-Object { $_.Path -like '*ardf-manager*' })`.

Usar siempre este patron para servicios de larga duracion.
