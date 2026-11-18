#!/usr/bin/env python3
"""Best-effort extractor for a public FilmAffinity list."""
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

LIST_URL = "https://m.filmaffinity.com/es/mylist.php?list_id=201"
OUT = Path("data/movies.json")
MAX_PAGES = 100
DELAY_SECONDS = 2.5
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PersonalListWidget/1.0)",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.7",
}

def get_year(text):
    match = re.search(r"\b(19\d{2}|20\d{2})\b", text or "")
    return int(match.group(1)) if match else None

def parse_page(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    found = {}
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        match = re.search(r"/film(\d+)\.html", urlparse(href).path)
        title = a.get("title") or a.get_text(" ", strip=True)
        if not match or not title:
            continue
        movie_id = match.group(1)
        title = re.sub(r"\s+", " ", title).strip()
        context = a.parent.get_text(" ", strip=True) if a.parent else title
        year = get_year(context) or get_year(a.get("title", ""))
        found[movie_id] = {
            "id": movie_id,
            "title": title,
            "year": year,
            "url": href,
        }

    next_urls = []
    for a in soup.find_all("a", href=True):
        label = (a.get_text(" ", strip=True) + " " + a.get("aria-label", "")).lower()
        href = urljoin(base_url, a["href"])
        if any(word in label for word in ("siguiente", "next", "»", "›")):
            if "mylist.php" in urlparse(href).path:
                next_urls.append(href)
    return found, next_urls

def sort_key(movie):
    # Años desconocidos al final; año descendente y título ascendente.
    year = movie.get("year")
    return (year is None, -(year or 0), movie.get("title", "").casefold(), movie.get("id", ""))

def main():
    session = requests.Session()
    session.headers.update(HEADERS)
    pending = [LIST_URL]
    visited = set()
    movies = {}

    while pending and len(visited) < MAX_PAGES:
        url = pending.pop(0)
        if url in visited:
            continue
        visited.add(url)
        response = session.get(url, timeout=30)
        response.raise_for_status()
        page_movies, next_urls = parse_page(response.text, response.url)
        movies.update(page_movies)
        for next_url in next_urls:
            if next_url not in visited and next_url not in pending:
                pending.append(next_url)
        if pending:
            time.sleep(DELAY_SECONDS)

    if len(movies) < 1:
        raise RuntimeError("No se encontraron películas. FilmAffinity puede haber cambiado el HTML o bloqueado la petición.")
    if len(movies) < 50:
        raise RuntimeError(f"Solo se encontraron {len(movies)} películas; se aborta para evitar publicar una lista incompleta.")

    ordered = sorted(movies.values(), key=sort_key)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "source": LIST_URL,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(ordered),
        "movies": ordered,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Guardadas {len(ordered)} películas en {OUT}")

if __name__ == "__main__":
    main()
