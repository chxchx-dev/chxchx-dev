# CHXCHX-DEV — perfil público

## Estado verificado
- [x] Banner con la máscara original y efecto glitch
- [x] PNG de skills y tecnologías, separado de la terminal animada
- [x] Terminal animada de Fedora
- [x] Panel propio `CHXCHX / SIGNAL` con datos reales de GitHub
- [x] Generación diaria automática mediante `CHXCHX Activity Signal`
- [x] Gráfico 3D genérico retirado del README y su workflow desactivado
- [ ] Verificar el resultado visual en pantalla móvil y escritorio

## Activity Signal

La imagen `assets/activity-signal.png` se crea desde `scripts/generate_activity.py`. Se consulta el calendario de contribuciones visibles de GitHub mediante GraphQL en ventanas de 90 días para reducir problemas de límites de consulta. La representación incluye la máscara original del encabezado como marca de agua. La imagen no contiene estadísticas inventadas y se actualiza diariamente mediante GitHub Actions.

El SVG generado `assets/activity-signal.svg` se conserva como salida vectorial; el README usa el PNG para asegurar compatibilidad con el renderizador de GitHub.

> Los datos corresponden a contribuciones visibles para el token del workflow. No necesariamente incluyen la actividad privada ni coinciden con todas las métricas del perfil de usuario.

## Mantenimiento

1. Cambia la visualización en `scripts/generate_activity.py`.
2. Ejecuta el workflow **CHXCHX Activity Signal** manualmente o espera a la siguiente ejecución programada.
3. Revisa `assets/activity-signal.png` y el README después del commit automático.
4. Conserva los permisos mínimos de GitHub Actions; no introduzcas un PAT personal ni secretos en el repositorio.

La carpeta `profile-3d-contrib/` permanece en Git como historial de la etapa anterior, pero no se utiliza en el README.
