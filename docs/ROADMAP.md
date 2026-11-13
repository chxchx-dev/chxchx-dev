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

El panel `assets/activity-signal.svg` se crea desde `scripts/generate_activity.py` y el README lo muestra como vector SVG. Se consulta el calendario de contribuciones visibles de GitHub mediante GraphQL en ventanas de 90 días para reducir problemas de límites de consulta. La representación conserva la estética del panel y la máscara original del encabezado como marca de agua. Muestra contribuciones visibles, días activos y racha actual; los datos se actualizan diariamente mediante GitHub Actions.

El SVG es la única salida del panel. El README enlaza el archivo SVG para que GitHub lo renderice sin rasterizarlo en PNG.

> Los datos corresponden a contribuciones visibles para el token del workflow. No necesariamente incluyen la actividad privada ni coinciden con todas las métricas del perfil de usuario.

## Mantenimiento

1. Cambia la visualización en `scripts/generate_activity.py`; el resultado editable se guarda como SVG.
2. Ejecuta el workflow **CHXCHX Activity Signal** manualmente o espera a la siguiente ejecución programada.
3. Revisa `assets/activity-signal.svg` y el README después del commit automático.
4. Conserva los permisos mínimos de GitHub Actions; no introduzcas un PAT personal ni secretos en el repositorio.

La carpeta `profile-3d-contrib/` permanece en Git como historial de la etapa anterior, pero no se utiliza en el README.
