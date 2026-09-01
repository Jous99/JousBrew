#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rastrear.py
-----------
Lee una lista de feeds RSS (en feeds.txt), busca noticias que hablen de la
Nintendo Switch 2, y escribe las nuevas al principio de NOTICIAS.md.

Guarda en data/visto.json los enlaces que ya ha registrado, para no repetir
la misma noticia dos veces.

Está pensado para ejecutarse solo (con un GitHub Action programado), pero
también puedes ejecutarlo a mano:  python rastrear.py
"""

import json
import os
import datetime
import html

import feedparser  # librería que sabe leer RSS/Atom. Se instala con: pip install feedparser


# --- Configuración -----------------------------------------------------------

# Palabras que tienen que aparecer en el título o el resumen para que la
# noticia nos interese. Si una noticia contiene CUALQUIERA de estas, la
# guardamos. Todo en minúsculas (la comparación no distingue mayúsculas).
PALABRAS_CLAVE = [
    "switch 2",
    "switch2",
]

# Archivos que usa el script (rutas relativas a este archivo).
AQUI = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_FEEDS = os.path.join(AQUI, "feeds.txt")
ARCHIVO_VISTO = os.path.join(AQUI, "data", "visto.json")
ARCHIVO_NOTICIAS = os.path.join(AQUI, "NOTICIAS.md")


# --- Funciones auxiliares ----------------------------------------------------

def leer_feeds():
    """Devuelve la lista de URLs de feeds.txt, ignorando comentarios y líneas vacías."""
    urls = []
    with open(ARCHIVO_FEEDS, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea and not linea.startswith("#"):
                urls.append(linea)
    return urls


def cargar_visto():
    """Carga el conjunto de enlaces ya registrados. Si no existe, empieza vacío."""
    if os.path.exists(ARCHIVO_VISTO):
        with open(ARCHIVO_VISTO, encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def guardar_visto(visto):
    """Guarda el conjunto de enlaces vistos en disco (como lista ordenada)."""
    os.makedirs(os.path.dirname(ARCHIVO_VISTO), exist_ok=True)
    with open(ARCHIVO_VISTO, "w", encoding="utf-8") as f:
        json.dump(sorted(visto), f, ensure_ascii=False, indent=2)


def es_relevante(entrada):
    """True si el título o el resumen de la noticia menciona alguna palabra clave."""
    titulo = entrada.get("title", "")
    resumen = entrada.get("summary", "")
    texto = (titulo + " " + resumen).lower()
    return any(palabra in texto for palabra in PALABRAS_CLAVE)


# --- Programa principal ------------------------------------------------------

def main():
    visto = cargar_visto()
    nuevas = []  # lista de noticias nuevas encontradas en esta ejecución

    for url in leer_feeds():
        print(f"Leyendo feed: {url}")
        # feedparser nunca lanza excepción: si el feed falla, devuelve algo vacío.
        feed = feedparser.parse(url)
        fuente = feed.feed.get("title", url)  # nombre legible de la fuente

        for entrada in feed.entries:
            enlace = entrada.get("link")
            if not enlace or enlace in visto:
                continue  # sin enlace, o ya la teníamos: la saltamos
            if not es_relevante(entrada):
                continue  # no habla de la Switch 2

            titulo = html.unescape(entrada.get("title", "(sin título)")).strip()
            nuevas.append({"titulo": titulo, "enlace": enlace, "fuente": fuente})
            visto.add(enlace)  # la marcamos como vista para no repetirla

    if not nuevas:
        print("No hay noticias nuevas.")
        return

    print(f"¡{len(nuevas)} noticia(s) nueva(s)!")

    # Construimos el bloque de texto que añadiremos ARRIBA del archivo.
    hoy = datetime.date.today().isoformat()
    lineas = [f"## {hoy}", ""]
    for n in nuevas:
        lineas.append(f"- [{n['titulo']}]({n['enlace']}) — _{n['fuente']}_")
    lineas.append("")  # línea en blanco de separación
    bloque_nuevo = "\n".join(lineas)

    # Leemos lo que ya había (o creamos la cabecera si el archivo no existe).
    if os.path.exists(ARCHIVO_NOTICIAS):
        with open(ARCHIVO_NOTICIAS, encoding="utf-8") as f:
            contenido_previo = f.read()
    else:
        contenido_previo = ""

    cabecera = "# Noticias de Nintendo Switch 2 (emulación y homebrew)\n\n"
    cuerpo_previo = contenido_previo
    if cuerpo_previo.startswith(cabecera):
        cuerpo_previo = cuerpo_previo[len(cabecera):]

    # Escribimos: cabecera + noticias nuevas + lo que ya había.
    with open(ARCHIVO_NOTICIAS, "w", encoding="utf-8") as f:
        f.write(cabecera + bloque_nuevo + "\n" + cuerpo_previo)

    guardar_visto(visto)
    print("NOTICIAS.md actualizado.")


if __name__ == "__main__":
    main()
