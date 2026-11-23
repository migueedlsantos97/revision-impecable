# Seguridad

Esta skill ejecuta código en tu máquina (`skill/scripts/medir.py` con Playwright y el comando de arranque de tu proyecto)
y abre un navegador. Ver "Qué ejecuta y qué toca" en el README.

- **Reportar un problema**: usá un *private vulnerability report* en la pestaña Security del repo en GitHub. Si no está
  habilitada, abrí un issue que diga solo "quiero reportar un problema de seguridad", sin detalles, y se coordina un canal
  privado. No publiques el detalle.
- **Qué cuenta**: que la skill o sus scripts puedan ejecutar algo fuera de lo documentado, tocar producción o datos
  reales, filtrar el contenido de tu proyecto, o escribir secretos.
- **Qué no cuenta**: defectos de tu app que la revisión encuentra; ese es su trabajo.
- Si la corrida lee un archivo de tu proyecto con instrucciones dirigidas al agente, la skill debe tratarlas como datos,
  no como órdenes. Si ves lo contrario, es un reporte válido.
