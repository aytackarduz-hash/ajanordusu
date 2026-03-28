"""
NEXA DEEP INTELLIGENCE v5.0 — data_mesh.py
Tüm harici veri kaynaklarından async veri toplama.
RSS, API, haber akışları, kripto verileri, GitHub trendi.
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import httpx

from config import config

logger = logging.getLogger(__name__)


@dataclass
class IntelItem:
    tag: str
    title: str
    desc: str = ""
    link: str = ""
    source: str = ""


@dataclass
class DataBundle:
    market: dict = field(default_factory=dict)
    intel: list[IntelItem] = field(default_factory=list)
    dev_velocity: list[dict] = field(default_factory=list)
    hn_signal: list[dict] = field(default_factory=list)
    fetched_at: str = ""
    errors: list[str] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# RSS KAYNAKLARI
# ─────────────────────────────────────────────────────────────────────────────
RSS_SOURCES = [
    # Bilim / Akademi
    {"tag": "arxiv_ai",      "url": "https://rss.arxiv.org/rss/cs.AI",        "limit": 8},
    {"tag": "arxiv_ml",      "url": "https://rss.arxiv.org/rss/cs.LG",        "limit": 8},
    {"tag": "arxiv_neuro",   "url": "https://rss.arxiv.org/rss/q-bio.NC",     "limit": 6},
    {"tag": "arxiv_quant",   "url": "https://rss.arxiv.org/rss/quant-ph",     "limit": 5},
    {"tag": "arxiv_bio",     "url": "https://rss.arxiv.org/rss/q-bio.GN",     "limit": 5},
    {"tag": "arxiv_cv",      "url": "https://rss.arxiv.org/rss/cs.CV",        "limit": 5},
    {"tag": "biorxiv",       "url": "https://www.biorxiv.org/rss/current",    "limit": 5},
    {"tag": "nature",        "url": "https://www.nature.com/subjects/biological-sciences.rss", "limit": 4},

    # Teknoloji Haberleri
    {"tag": "techcrunch_ai", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "limit": 6},
    {"tag": "arstechnica",   "url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "limit": 5},
    {"tag": "mit_tech",      "url": "https://www.technologyreview.com/feed/", "limit": 5},
    {"tag": "wired_sci",     "url": "https://www.wired.com/feed/category/science/latest/rss", "limit": 4},
    {"tag": "verge",         "url": "https://www.theverge.com/rss/index.xml", "limit": 4},

    # Kripto / DeFi
    {"tag": "coindesk",      "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "limit": 6},
    {"tag": "theblock",      "url": "https://www.theblock.co/rss.xml",        "limit": 5},
    {"tag": "decrypt",       "url": "https://decrypt.co/feed",                "limit": 5},
    {"tag": "cointelegraph", "url": "https://cointelegraph.com/rss",          "limit": 5},

    # Frontier / Longevity / Biotech
    {"tag": "singularity",   "url": "https://singularityhub.com/feed/",       "limit": 5},
    {"tag": "futurism",      "url": "https://futurism.com/feed",              "limit": 4},
    {"tag": "longevity",     "url": "https://www.longevity.technology/feed/", "limit": 5},

    # Girişimcilik / Strateji
    {"tag": "hbr",           "url": "https://feeds.hbr.org/harvardbusiness",  "limit": 3},
    {"tag": "stratechery",   "url": "https://stratechery.com/feed/",          "limit": 3},
]

# ─────────────────────────────────────────────────────────────────────────────
# YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────────────────────────────────────
def strip_html(text: str) -> str:
    text = re.sub(r"<!\[CDATA\[([\s\S]*?)\]\]>", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _match_group(pattern, text, default="", flags=re.I):
    m = re.search(pattern, text, flags)
    return m.group(1) if m else default


def parse_rss_items_safe(xml_content: str, tag: str, limit: int = 6) -> list[IntelItem]:
    items = []
    raw_items = re.findall(r"<item>([\s\S]*?)</item>", xml_content)
    for raw in raw_items[:limit]:
        title = strip_html(_match_group(r"<title>([\s\S]*?)</title>", raw))
        desc = strip_html(_match_group(r"<description>([\s\S]*?)</description>", raw))
        link = _match_group(r"<link>(.*?)</link>", raw).strip()

        if len(title) > 10:
            items.append(IntelItem(
                tag=tag,
                title=title[:200].strip(),
                desc=desc[:350].strip(),
                link=link[:300],
                source=tag,
            ))
    return items


# ─────────────────────────────────────────────────────────────────────────────
# DATA MESH
# ─────────────────────────────────────────────────────────────────────────────
class DataMesh:
    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=config.HTTP_TIMEOUT,
                headers={
                    "User-Agent": "NexaIntelBot/5.0 (+https://nexa.digital)",
                    "Accept": "application/rss+xml, application/xml, text/xml, */*",
                },
                follow_redirects=True,
            )
        return self._client

    async def _fetch_url(self, url: str) -> str | None:
        try:
            client = await self._get_client()
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.text
            logger.debug(f"HTTP {resp.status_code} for {url}")
            return None
        except Exception as e:
            logger.debug(f"Fetch error {url}: {e}")
            return None

    # ─── RSS AKIŞLARI ─────────────────────────────────────────────────────────
    async def fetch_single_rss(self, source: dict) -> list[IntelItem]:
        xml = await self._fetch_url(source["url"])
        if not xml:
            return []
        return parse_rss_items_safe(xml, source["tag"], source.get("limit", 5))

    async def fetch_all_rss(self) -> list[IntelItem]:
        tasks = [self.fetch_single_rss(src) for src in RSS_SOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        items = []
        for r in results:
            if isinstance(r, list):
                items.extend(r)
        logger.info(f"RSS: {len(items)} items from {len(RSS_SOURCES)} sources")
        return items

    # ─── KRİPTO PİYASA VERİSİ ─────────────────────────────────────────────────
    async def fetch_market_pulse(self) -> dict:
        result = {}

        # Fiyatlar
        try:
            ids = (
                "bitcoin,ethereum,solana,sui,hyperliquid,chainlink,"
                "avalanche-2,the-open-network,arbitrum,optimism,"
                "injective-protocol,render-token,fetch-ai,bittensor,"
                "near,aptos,sei-network,celestia,starknet,eigenlayer"
            )
            url = (
                f"https://api.coingecko.com/api/v3/simple/price"
                f"?ids={ids}&vs_currencies=usd"
                f"&include_24hr_change=true&include_7d_change=true&include_market_cap=true"
            )
            data = await self._fetch_url(url)
            if data:
                import json
                result["prices"] = json.loads(data)
        except Exception as e:
            logger.debug(f"Prices error: {e}")

        # Trend coinler
        try:
            data = await self._fetch_url("https://api.coingecko.com/api/v3/search/trending")
            if data:
                import json
                trending_data = json.loads(data)
                result["trending"] = [
                    {
                        "name": c["item"]["name"],
                        "symbol": c["item"]["symbol"],
                        "rank": c["item"].get("market_cap_rank", "?"),
                    }
                    for c in trending_data.get("coins", [])[:8]
                ]
        except Exception as e:
            logger.debug(f"Trending error: {e}")

        # Fear & Greed
        try:
            data = await self._fetch_url("https://api.alternative.me/fng/?limit=3")
            if data:
                import json
                result["fear_greed"] = json.loads(data).get("data", [])[:3]
        except Exception as e:
            logger.debug(f"Fear&Greed error: {e}")

        # Global stats
        try:
            data = await self._fetch_url("https://api.coingecko.com/api/v3/global")
            if data:
                import json
                d = json.loads(data).get("data", {})
                result["global_stats"] = {
                    "total_market_cap_usd": d.get("total_market_cap", {}).get("usd"),
                    "btc_dominance": round(d.get("market_cap_percentage", {}).get("btc", 0), 1),
                    "eth_dominance": round(d.get("market_cap_percentage", {}).get("eth", 0), 1),
                    "market_cap_change_24h": round(d.get("market_cap_change_percentage_24h_usd", 0), 2),
                    "active_cryptos": d.get("active_cryptocurrencies"),
                }
        except Exception as e:
            logger.debug(f"Global stats error: {e}")

        logger.info(f"Market: prices={bool(result.get('prices'))}, fg={result.get('fear_greed', [{}])[0].get('value_classification', '?')}")
        return result

    # ─── GITHUB TREND ─────────────────────────────────────────────────────────
    async def fetch_dev_velocity(self) -> list[dict]:
        # Önce trending API dene
        try:
            data = await self._fetch_url(
                "https://github-trending-api.de/repositories?language=&since=daily"
            )
            if data:
                import json
                repos = json.loads(data)
                return [
                    {
                        "name": r.get("name", ""),
                        "author": r.get("author", ""),
                        "desc": (r.get("description") or "")[:180],
                        "stars": r.get("stars", 0),
                        "stars_today": r.get("currentPeriodStars", "?"),
                        "language": r.get("language", ""),
                        "url": r.get("url", ""),
                    }
                    for r in repos[:15]
                ]
        except Exception:
            pass

        # Fallback: GitHub Search API
        try:
            from datetime import datetime, timedelta
            yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
            data = await self._fetch_url(
                f"https://api.github.com/search/repositories"
                f"?q=created:>{yesterday}&sort=stars&order=desc&per_page=12"
            )
            if data:
                import json
                items = json.loads(data).get("items", [])
                return [
                    {
                        "name": r.get("name", ""),
                        "author": r.get("owner", {}).get("login", ""),
                        "desc": (r.get("description") or "")[:180],
                        "stars": r.get("stargazers_count", 0),
                        "stars_today": "?",
                        "language": r.get("language", ""),
                        "url": r.get("html_url", ""),
                    }
                    for r in items[:12]
                ]
        except Exception as e:
            logger.debug(f"Dev velocity error: {e}")

        return []

    # ─── HACKER NEWS ─────────────────────────────────────────────────────────
    async def fetch_hn_signal(self) -> list[dict]:
        try:
            data = await self._fetch_url(
                "https://hacker-news.firebaseio.com/v0/topstories.json"
            )
            if not data:
                return []
            import json
            ids = json.loads(data)[:20]

            async def fetch_story(story_id: int) -> dict | None:
                d = await self._fetch_url(
                    f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                )
                if d:
                    s = json.loads(d)
                    if s.get("title"):
                        return {
                            "title": s["title"],
                            "score": s.get("score", 0),
                            "url": s.get("url", ""),
                            "comments": s.get("descendants", 0),
                        }
                return None

            tasks = [fetch_story(i) for i in ids[:12]]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            stories = [r for r in results if isinstance(r, dict)]
            logger.info(f"HN: {len(stories)} stories")
            return stories
        except Exception as e:
            logger.debug(f"HN error: {e}")
            return []

    # ─── HEPSINI TOPLA ────────────────────────────────────────────────────────
    async def fetch_all(self) -> DataBundle:
        logger.info("DataMesh.fetch_all() başlıyor...")
        now = datetime.utcnow().isoformat()

        # Paralel fetch
        rss_task = self.fetch_all_rss()
        market_task = self.fetch_market_pulse()
        dev_task = self.fetch_dev_velocity()
        hn_task = self.fetch_hn_signal()

        intel, market, dev, hn = await asyncio.gather(
            rss_task, market_task, dev_task, hn_task,
            return_exceptions=True,
        )

        bundle = DataBundle(fetched_at=now)
        bundle.intel = intel if isinstance(intel, list) else []
        bundle.market = market if isinstance(market, dict) else {}
        bundle.dev_velocity = dev if isinstance(dev, list) else []
        bundle.hn_signal = hn if isinstance(hn, list) else []

        logger.info(
            f"DataMesh tamamlandı: "
            f"intel={len(bundle.intel)}, "
            f"dev={len(bundle.dev_velocity)}, "
            f"hn={len(bundle.hn_signal)}, "
            f"market_ok={bool(bundle.market.get('prices'))}"
        )
        return bundle

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# ─────────────────────────────────────────────────────────────────────────────
# YARDIMCI: BUNDLE ÖZETLEME
# ─────────────────────────────────────────────────────────────────────────────
def bundle_summary(bundle: DataBundle) -> str:
    """DataBundle'ı ajan promptları için özet stringe çevir."""
    lines = []

    # Piyasa özeti
    fg = bundle.market.get("fear_greed", [{}])
    if fg:
        lines.append(f"[Piyasa] Fear&Greed: {fg[0].get('value_classification', '?')} ({fg[0].get('value', '?')})")
    gs = bundle.market.get("global_stats", {})
    if gs:
        lines.append(
            f"[Kripto] BTC Dom: {gs.get('btc_dominance', '?')}% | "
            f"24h: {gs.get('market_cap_change_24h', '?')}%"
        )

    # Trending coinler
    trending = bundle.market.get("trending", [])
    if trending:
        names = ", ".join(f"{t['name']}({t['symbol']})" for t in trending[:5])
        lines.append(f"[Trending] {names}")

    return "\n".join(lines)


def filter_intel_by_tags(items: list[IntelItem], tag_prefixes: list[str], limit: int = 10) -> list[str]:
    """İstihbarat öğelerini tag ile filtrele."""
    filtered = [
        f"{i.title} — {i.desc[:100]}"
        for i in items
        if any(i.tag.startswith(p) for p in tag_prefixes)
    ]
    return filtered[:limit]
