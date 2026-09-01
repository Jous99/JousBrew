# Rastreador de noticias de Nintendo Switch 2

Un repositorio que **se actualiza solo**: una vez al día busca noticias sobre
emulación y homebrew de la Switch 2 y, si encuentra algo nuevo, lo apunta en
[`NOTICIAS.md`](NOTICIAS.md) con un commit automático. No necesitas tener nada
encendido: todo el trabajo lo hace GitHub gratis (GitHub Actions).

## Cómo funciona (en 4 piezas)

1. **`feeds.txt`** — la lista de fuentes RSS que se vigilan (Reddit, Wololo,
   Nintendo Life, GBAtemp...). Puedes añadir o quitar las que quieras.
2. **`rastrear.py`** — el programa: lee los feeds, se queda con lo que menciona
   "Switch 2", evita repetir noticias (las recuerda en `data/visto.json`) y
   escribe las nuevas arriba del todo de `NOTICIAS.md`.
3. **`.github/workflows/rastrear.yml`** — el "reloj": le dice a GitHub que
   ejecute el programa cada día y haga commit de los cambios.
4. **`NOTICIAS.md`** — el resultado, que se va llenando solo.

## Puesta en marcha (paso a paso)

1. Crea una cuenta en [github.com](https://github.com) si no la tienes.
2. Crea un repositorio nuevo (por ejemplo `switch2-tracker`). Puede ser público
   o privado, da igual.
3. Sube estos archivos al repositorio. Dos formas:
   - **Fácil (web):** botón *Add file → Upload files*, y arrastra todo. Ojo: la
     carpeta `.github` a veces no se sube arrastrando porque empieza por punto;
     si te pasa, créala a mano con *Add file → Create new file* y escribe la ruta
     `.github/workflows/rastrear.yml`.
   - **Con git (terminal):**
     ```bash
     git init
     git add .
     git commit -m "Primer commit"
     git branch -M main
     git remote add origin https://github.com/TU_USUARIO/switch2-tracker.git
     git push -u origin main
     ```
4. En el repositorio, ve a la pestaña **Settings → Actions → General**, baja a
   *Workflow permissions* y marca **"Read and write permissions"**. Esto es lo
   que permite al robot hacer commits. (Guarda con *Save*.)
5. Ve a la pestaña **Actions**, elige *"Rastrear noticias Switch 2"* y pulsa
   **"Run workflow"** para probarlo ahora mismo sin esperar a mañana.

¡Listo! A partir de ahí se ejecuta solo cada día a las 08:00 UTC (10:00 en
España en verano). Puedes cambiar esa hora editando la línea `cron` del archivo
`.github/workflows/rastrear.yml`.

## Probarlo en tu ordenador (opcional)

```bash
pip install -r requirements.txt
python rastrear.py
```

## Ajustes que puedes tocar

- **Fuentes:** edita `feeds.txt`. Una URL por línea. Las líneas con `#` son
  comentarios. Puedes añadir `all` después de una URL para guardar **todos** los
  posts de ese feed (útil en webs pequeñas y temáticas como wayayeo); sin `all`,
  solo guarda los que mencionen las palabras clave.
  Truco: casi cualquier web hecha con WordPress tiene su feed en `/feed/` (por
  ejemplo `https://wayayeo.org/feed/`). Es más fiable que raspar el HTML.
- **Qué se considera relevante:** en `rastrear.py`, la lista `PALABRAS_CLAVE`.
  Si añades por ejemplo `"atmosphere"` o `"eden"`, también las cazará.
- **Cada cuánto se ejecuta:** la línea `cron` del workflow. Formato:
  `minuto hora día mes día-semana`. Por ejemplo `0 */6 * * *` = cada 6 horas.

## Notas

- Si un feed deja de funcionar, el script simplemente lo salta; no rompe nada.
- La primera ejecución puede recoger varias noticias de golpe (las recientes de
  cada feed). A partir de ahí solo verás lo nuevo.
