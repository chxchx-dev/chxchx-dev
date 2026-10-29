# CHXCHX-DEV — roadmap

## Objetivo
Construir una identidad de GitHub centrada en evidencia técnica, ética profesional y software abierto. El personaje de máscara azul es la firma visual; el valor del perfil debe venir de los proyectos verificables.

## Estado (2026-10-29)
- [x] Repositorio de perfil público con el mismo nombre de usuario
- [x] README con identidad, stack, principios y proyectos públicos
- [x] Banner SVG vectorial propio, sin servicios externos
- [x] Terminal SVG accesible y con cursor animado
- [x] Semilla de generador GIF en Python
- [x] Workflows para actualizar GIF y contribuciones 3D
- [ ] Ejecutar manualmente ambos workflows por primera vez
- [ ] Confirmar que se generen los archivos binarios/SVG y que el commit automático funcione
- [ ] Incorporar al README el calendario 3D generado cuando exista
- [ ] Revisar el banner en pantalla móvil y escritorio
- [ ] Añadir enlaces verificables de demos/casos de uso, solo si se pueden mostrar públicamente

## Fase 1 — Identidad y legibilidad (primer día)
Revisar HTML renderizado en GitHub, formato móvil, enlaces, contraste y texto alternativo. El banner funciona sin fuentes personalizadas.

**Criterio de salida:** README visible en https://github.com/chxchx-dev y cinco proyectos públicos accesibles.

## Fase 2 — Automatizaciones (días 2–3)
En **Actions** ejecutar `Update CHXCHX terminal GIF` y `CHXCHX 3D contributions`. Los workflows usan `GITHUB_TOKEN` efímero, ninguna clave personal, versiones fijas y escritura limitada a contenidos.

**Criterio de salida:** `assets/terminal.gif` y `profile-3d-contrib/profile-chxchx.svg` aparecen en `main` y los logs no tienen secretos expuestos.

Tras la primera ejecución, sustituir en `README.md` el elemento `assets/terminal.svg` por `assets/terminal.gif` e insertar el calendario:
```html
<img alt="Calendario de contribuciones 3D" width="94%" src="./profile-3d-contrib/profile-chxchx.svg" />
```

## Fase 3 — Evidencia y mantenimiento (semana 1)
Escribir una nota de arquitectura, screenshot, pruebas y límites por cada proyecto destacado. No incluir repos privados, secretos, datos de clientes ni capturas de infraestructura.

**Criterio de salida:** cada proyecto enlazado demuestra una decisión de ingeniería y un resultado verificable.

## Fase 4 — Evolución (semana 2)
Agregar un laboratorio de seguridad defensiva reproducible con alcance y autorización, y un caso de IA aplicada con RAG y evaluación medible. Evitar porcentajes de éxito no medidos y títulos inflados.

## Operación y seguridad
- Repositorio público **sin** tokens, .env, contraseñas, inventarios privados ni credenciales.
- Los workflows usan checkout por SHA. Revisar dependencias y actualizar SHA conscientemente.
- El workflow de contribuciones corre diariamente; no necesita un PAT.
- Si el repositorio tiene restricciones para GitHub Actions, verificar **Settings → Actions → General** y **Workflow permissions**; no conceder más permisos que los necesarios.
- Las estadísticas de servicios externos pueden fallar o tener cuotas; el README debe seguir funcionando sin ellas.
