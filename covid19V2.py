# mapa_covid_noticias_global.py
# Mapa global com pontos de notícias (Google News RSS) e popup ao clicar.
# Esta versão é resiliente: User-Agent, timeout, retries, e fallback por área.

from datetime import datetime, timedelta
from urllib.parse import quote_plus
from dateutil import parser as dtparser
import time
import sys

import requests
import feedparser
import folium
from folium.plugins import MarkerCluster

# ======= CONFIG =======
DAYS_BACK = 15        # Janela de notícias (últimos N dias)
USE_CLUSTER = True    # Agrupar marcadores
MAX_PER_AREA = 12     # Limite de notícias por área

# Networking
HTTP_TIMEOUT = 15     # segundos por requisição
HTTP_RETRIES = 2      # tentativas por URL
HTTP_BACKOFF = 2      # segundos entre tentativas

# Cabeçalhos (alguns endpoints bloqueiam clientes sem User-Agent)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0 Safari/537.36"
}

# ======= ALVOS GLOBAIS =======
TARGETS = {
    # --- América do Sul ---
    "Brasil":         {"q": "COVID OR covid-19 OR coronavírus Brasil variante",           "coords": (-14.2350, -51.9253), "hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-419"},
    "Argentina":      {"q": "COVID OR coronavirus Argentina variante",                    "coords": (-38.4161, -63.6167), "hl": "es-419", "gl": "AR", "ceid": "AR:es-419"},
    "Chile":          {"q": "COVID OR coronavirus Chile variante",                        "coords": (-35.6751, -71.5430), "hl": "es-419", "gl": "CL", "ceid": "CL:es-419"},
    "Colômbia":       {"q": "COVID OR coronavirus Colombia variante",                     "coords": (4.5709, -74.2973),  "hl": "es-419", "gl": "CO", "ceid": "CO:es-419"},
    "Peru":           {"q": "COVID OR coronavirus Peru variante",                         "coords": (-9.1900, -75.0152), "hl": "es-419", "gl": "PE", "ceid": "PE:es-419"},
    # --- América do Norte ---
    "Estados Unidos": {"q": "COVID OR coronavirus variant outbreak United States",        "coords": (37.0902, -95.7129), "hl": "en-US", "gl": "US", "ceid": "US:en"},
    "Canadá":         {"q": "COVID OR coronavirus variant Canada",                        "coords": (56.1304, -106.3468),"hl": "en-CA", "gl": "CA", "ceid": "CA:en"},
    "México":         {"q": "COVID OR coronavirus Mexico variante",                       "coords": (23.6345, -102.5528),"hl": "es-419","gl": "MX", "ceid": "MX:es-419"},
    # --- Europa ---
    "Reino Unido":    {"q": "COVID OR coronavirus variant UK",                            "coords": (55.3781, -3.4360),  "hl": "en-GB", "gl": "GB", "ceid": "GB:en"},
    "França":         {"q": "COVID OR coronavirus France variant",                        "coords": (46.2276, 2.2137),   "hl": "fr-FR", "gl": "FR", "ceid": "FR:fr"},
    "Alemanha":       {"q": "COVID OR coronavirus Germany variant",                       "coords": (51.1657, 10.4515),  "hl": "de-DE", "gl": "DE", "ceid": "DE:de"},
    "Espanha":        {"q": "COVID OR coronavirus España variante",                       "coords": (40.4637, -3.7492),  "hl": "es-419","gl": "ES", "ceid": "ES:es-419"},
    "Itália":         {"q": "COVID OR coronavirus Italia variante",                       "coords": (41.8719, 12.5674),  "hl": "it-IT", "gl": "IT", "ceid": "IT:it"},
    "Portugal":       {"q": "COVID OR coronavírus Portugal variante",                     "coords": (39.3999, -8.2245),  "hl": "pt-PT","gl": "PT", "ceid": "PT:pt-150"},
    # --- África ---
    "África do Sul":  {"q": "COVID OR coronavirus South Africa variant",                  "coords": (-30.5595, 22.9375), "hl": "en-ZA", "gl": "ZA", "ceid": "ZA:en"},
    "Nigéria":        {"q": "COVID OR coronavirus Nigeria",                               "coords": (9.0820, 8.6753),    "hl": "en-US", "gl": "NG", "ceid": "NG:en"},
    "Egito":          {"q": "COVID OR coronavirus Egypt",                                 "coords": (26.8206, 30.8025),  "hl": "en-US", "gl": "EG", "ceid": "EG:en"},
    # --- Ásia ---
    "Índia":          {"q": "COVID OR coronavirus India variant",                         "coords": (20.5937, 78.9629),  "hl": "en-IN", "gl": "IN", "ceid": "IN:en"},
    "China":          {"q": "COVID OR coronavirus China",                                 "coords": (35.8617, 104.1954), "hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans"},
    "Japão":          {"q": "COVID OR coronavirus Japan variant",                         "coords": (36.2048, 138.2529), "hl": "ja-JP", "gl": "JP", "ceid": "JP:ja"},
    "Coreia do Sul":  {"q": "COVID OR coronavirus South Korea variant",                   "coords": (35.9078, 127.7669), "hl": "ko-KR", "gl": "KR", "ceid": "KR:ko"},
    # --- Oriente Médio ---
    "Israel":         {"q": "COVID OR coronavirus Israel variant",                        "coords": (31.0461, 34.8516),  "hl": "en-US", "gl": "IL", "ceid": "IL:en"},
    "Arábia Saudita": {"q": "COVID OR coronavirus Saudi Arabia",                          "coords": (23.8859, 45.0792),  "hl": "en-US", "gl": "SA", "ceid": "SA:en"},
    "EAU":            {"q": "COVID OR coronavirus United Arab Emirates UAE",              "coords": (23.4241, 53.8478),  "hl": "en-US", "gl": "AE", "ceid": "AE:en"},
    # --- Oceania ---
    "Austrália":      {"q": "COVID OR coronavirus Australia variant",                     "coords": (-25.2744, 133.7751),"hl": "en-AU", "gl": "AU", "ceid": "AU:en"},
    "Nova Zelândia":  {"q": "COVID OR coronavirus New Zealand variant",                   "coords": (-40.9006, 174.8860),"hl": "en-GB", "gl": "NZ", "ceid": "NZ:en"},
    # --- Local extra ---
    "Manaus (AM)":    {"q": "COVID OR covid-19 OR coronavírus Manaus Amazonas",          "coords": (-3.1190, -60.0217), "hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-419"},
}

# ======= FUNÇÕES =======
def google_news_rss_url(q, hl="pt-BR", gl="BR", ceid="BR:pt-419"):
    return f"https://news.google.com/rss/search?q={quote_plus(q)}&hl={hl}&gl={gl}&ceid={ceid}"

def is_recent(pub_dt, days_back=DAYS_BACK):
    return pub_dt and pub_dt >= (datetime.utcnow() - timedelta(days=days_back))

def parse_date(entry):
    if getattr(entry, "published_parsed", None):
        return datetime(*entry.published_parsed[:6])
    for k in ("published", "updated", "date"):
        v = entry.get(k)
        if v:
            try:
                return dtparser.parse(v)
            except Exception:
                pass
    return None

def http_get_bytes(url):
    """Baixa bytes do URL com retries/backoff e User-Agent."""
    last_err = None
    for attempt in range(1, HTTP_RETRIES + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=HTTP_TIMEOUT, allow_redirects=True)
            resp.raise_for_status()
            return resp.content
        except Exception as e:
            last_err = e
            print(f"[WARN] Falha ao baixar ({attempt}/{HTTP_RETRIES}): {url}\n       {e}")
            if attempt < HTTP_RETRIES:
                time.sleep(HTTP_BACKOFF)
    raise last_err

def fetch_points():
    """Retorna lista [(lat, lon, titulo, data_iso, link, area_label)] com deduplicação por título."""
    points = []
    for area_label, cfg in TARGETS.items():
        try:
            url = google_news_rss_url(cfg["q"], cfg["hl"], cfg["gl"], cfg["ceid"])
            raw = http_get_bytes(url)
            feed = feedparser.parse(raw)
        except Exception as e:
            print(f"[ERRO] Não consegui ler RSS para {area_label}: {e} — pulando.")
            continue

        seen_titles = set()
        added = 0
        for e in feed.entries:
            if added >= MAX_PER_AREA:
                break
            pub = parse_date(e)
            if not is_recent(pub):
                continue

            title = (e.get("title") or "Notícia").strip()
            if title in seen_titles:
                continue
            seen_titles.add(title)

            lat, lon = cfg["coords"]
            link = e.get("link") or "#"
            data_iso = pub.strftime("%Y-%m-%d") if pub else "?"
            points.append((lat, lon, title, data_iso, link, area_label))
            added += 1

        # pausa curta entre áreas (educado com o feed)
        time.sleep(0.2)

    return points

# ======= MAPA =======
def build_map(points):
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB dark_matter")

    if USE_CLUSTER:
        layer = MarkerCluster(name=f"Notícias (últimos {DAYS_BACK} dias)").add_to(m)
    else:
        layer = folium.FeatureGroup(name=f"Notícias (últimos {DAYS_BACK} dias)").add_to(m)

    for lat, lon, title, data_iso, link, area in points:
        html = (
            f"<b>{area}</b><br>"
            f"{title}<br>"
            f"<small>Data: {data_iso}</small><br>"
            f"<a href='{link}' target='_blank' rel='noopener'>Abrir notícia</a>"
        )
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(html, max_width=320),
            icon=folium.Icon(color="red", icon="info-sign"),
        ).add_to(layer)

    folium.LayerControl(collapsed=True).add_to(m)
    return m

def main():
    print("Buscando notícias globais (RSS)…")
    pts = fetch_points()
    print(f"Total de itens no mapa: {len(pts)}")
    m = build_map(pts)
    out = "mapa_covid_noticias_global.html"
    m.save(out)
    print(f"OK! Abra: {out}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Execução interrompida pelo usuário.")
        sys.exit(1)
