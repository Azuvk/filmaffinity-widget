# Widget FilmAffinity para Kadr (Android 15)

Widget grande en formato lista para mostrar la lista pública de FilmAffinity.

## Orden
La lista se ordena por **año de estreno, del más reciente al más antiguo**. Dentro de cada año, los títulos van en orden alfabético. Los títulos cuyo año no se pueda detectar aparecen al final. El año se muestra junto al título cuando está disponible.

## Configuración
1. Crea un repositorio público en GitHub y sube estos archivos.
2. En `widget.html`, sustituye `DATA_URL` por la URL RAW de `data/movies.json` de tu repositorio.
3. En GitHub, activa Actions y ejecuta manualmente el flujo **Actualizar lista FilmAffinity** una primera vez.
4. Instala Kadr en Android y crea un widget HTML grande apuntando a `widget.html` (o pega el contenido HTML, según la versión de Kadr).
5. El flujo está programado para actualizar el JSON diariamente. También puedes ejecutarlo manualmente desde Actions.

## Notas
- El extractor intenta leer la lista pública sin iniciar sesión. No incluyas cookies, contraseñas ni datos privados.
- FilmAffinity puede cambiar su HTML, limitar peticiones o paginar de forma distinta. Si el extractor no encuentra títulos, revisa el log de GitHub Actions; no significa que la lista se haya sincronizado.
- La vista del widget muestra una selección de títulos del JSON, no una lista interactiva completa desplazable.
