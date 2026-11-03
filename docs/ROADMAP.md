# CHXCHX-DEV — mantenimiento del perfil

## Estado
- [x] Una sola sección `~/whoami` reúne identidad, especialidades, stack y principios.
- [x] Sin sección de proyectos destacados.
- [x] Terminal animada de Fedora y contribuciones 3D.
- [x] Script local para animar únicamente la máscara del banner original.
- [x] GitHub Actions prepara la generación y publicación automática del GIF.
- [ ] Subir `assets/header-original.png` desde el archivo original.
- [ ] Confirmar que GitHub Actions genera `assets/header-glitch.gif` y actualiza el README.
- [ ] Revisar calidad visual en móvil y escritorio.

## Activar el banner solicitado
1. En GitHub, abrir el repositorio `chxchx-dev/chxchx-dev` en la carpeta `assets/`.
2. Elegir **Add file → Upload files**, cargar el PNG original y guardarlo con el nombre **header-original.png**.
3. Confirmar la subida en la rama `main`.
4. El workflow `Render CHXCHX animated header` genera el GIF y sustituye la referencia del banner SVG en el README.
5. La animación se reproduce en bucle; en dispositivos con preferencia de movimiento reducido se muestra la imagen original estática.

## Diseño
- Conservar la composición: título, cielo, ciudad, personaje sentado y elementos de escritorio.
- Aplicar desaparición y glitches solamente a la máscara del fondo.
- Evitar animaciones invasivas o texto repetido debajo del banner.
- Mantener accesibilidad y enlaces verificables, sin repositorios privados ni información sensible.
- Si cambia la imagen de origen, revisar las coordenadas de la máscara en `scripts/generate_header_glitch.py` antes de publicarla.
