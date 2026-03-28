"""
NEXA DEEP INTELLIGENCE v5.0 — report_builder.py
Telegram için rapor formatlama. HTML modu.
4096 karakter limitine göre bölümlere ayırma.
"""

import re
from datetime import datetime

from config import config, USER
from diversity_engine import DiversityEngine


# ─────────────────────────────────────────────────────────────────────────────
# TELEGRAM HTML GÜVENLİ KAÇIŞ
# ─────────────────────────────────────────────────────────────────────────────
def tg_safe(text: str) -> str:
    """Telegram HTML için güvensiz karakterleri kaçır (sadece düz metin için)."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def clean_agent_output(text: str) -> str:
    """
    Ajan çıktısından gereksiz HTML'i temizle ve Telegram'a uyumlu hale getir.
    Telegram desteklediği: <b>, <i>, <u>, <s>, <code>, <pre>, <a>, <blockquote>
    """
    # Desteklenmeyen stil özelliklerini temizle
    text = re.sub(r'\s*style="[^"]*"', "", text)

    # <h2> ve <h3> → <b>
    text = re.sub(r"<h[23][^>]*>([\s\S]*?)</h[23]>", r"<b>\1</b>", text, flags=re.I)
    text = re.sub(r"<h[14][^>]*>([\s\S]*?)</h[14]>", r"<b>\1</b>", text, flags=re.I)

    # <span> → içerik (renk desteği yok)
    text = re.sub(r"<span[^>]*>([\s\S]*?)</span>", r"\1", text, flags=re.I)

    # <p> → satır başı
    text = re.sub(r"<p[^>]*>([\s\S]*?)</p>", r"\1\n", text, flags=re.I)

    # <ul>, <ol>, <li>
    text = re.sub(r"<[uo]l[^>]*>", "", text, flags=re.I)
    text = re.sub(r"</[uo]l>", "\n", text, flags=re.I)
    text = re.sub(r"<li[^>]*>([\s\S]*?)</li>", r"• \1\n", text, flags=re.I)

    # <table>, <tr>, <td> → düz metin
    text = re.sub(r"<table[^>]*>|</table>", "", text, flags=re.I)
    text = re.sub(r"<tr[^>]*>|</tr>", "\n", text, flags=re.I)
    text = re.sub(r"<t[dh][^>]*>([\s\S]*?)</t[dh]>", r"\1 | ", text, flags=re.I)

    # <hr> → çizgi
    text = re.sub(r"<hr[^>]*/?>", "\n" + "─" * 35 + "\n", text, flags=re.I)

    # Desteklenmeyen etiketleri sil ama içeriklerini koru
    text = re.sub(r"<(?!b|/b|i|/i|u|/u|s|/s|code|/code|pre|/pre|a |/a|blockquote|/blockquote)[^>]+>", "", text, flags=re.I)

    # Çoklu boş satırları azalt
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ─────────────────────────────────────────────────────────────────────────────
# TELEGRAM MESAJ BÖLÜCÜ
# ─────────────────────────────────────────────────────────────────────────────
def split_message(text: str, max_len: int = None) -> list[str]:
    """Uzun metni Telegram limit dahilinde böl."""
    max_len = max_len or config.TELEGRAM_MAX_CHARS
    if len(text) <= max_len:
        return [text]

    parts = []
    while text:
        if len(text) <= max_len:
            parts.append(text)
            break
        # Kelime sınırında böl
        cut = text[:max_len].rfind("\n")
        if cut < max_len // 2:
            cut = text[:max_len].rfind(" ")
        if cut <= 0:
            cut = max_len
        parts.append(text[:cut])
        text = text[cut:].lstrip()

    return parts


# ─────────────────────────────────────────────────────────────────────────────
# RAPOR BÖLÜMLERİ
# ─────────────────────────────────────────────────────────────────────────────
def build_header(date_str: str, time_str: str, quality: dict, vector: dict, avg_quality_10d: str) -> str:
    avg = float(quality.get("average", 7.5))
    q_label = "ELITE ⚡" if avg >= 8.5 else "SHARP" if avg >= 7.0 else "DILUTED"

    domain_str = " + ".join(vector.get("domain_focus", []))
    scores = quality.get("scores", {})
    scores_str = " | ".join(f"{k[:3].upper()}:{v:.1f}" for k, v in scores.items()) if scores else ""

    return f"""<b>⚡ NEXA DEEP INTELLIGENCE v5.0</b>
<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>

📅 {date_str}
🕐 {time_str} | 8 Ajan | Google Grounding

<b>📊 KALİTE:</b> <code>{avg:.1f}/10 · {q_label}</code>
Zayıf: <i>{quality.get('weakest','?')}</i> | Güçlü: <i>{quality.get('strongest','?')}</i>
10-gün ort: <code>{avg_quality_10d}</code>
{f'Detay: <code>{scores_str}</code>' if scores_str else ''}

<b>🔭 BUGÜNÜN VEKTÖRü:</b>
Çerçeve: <code>{vector.get('cognitive_frame','?')}</code>
Domain: <code>{domain_str}</code>
Mod: <code>{vector.get('search_mode','?')}</code>
Lens: <code>{vector.get('temporal_lens','?')}</code>

FOR {USER['name'].upper()} ONLY · CLASSIFIED"""


def build_market_ticker(market: dict) -> str | None:
    prices = market.get("prices", {})
    if not prices:
        return None

    lines = ["<b>📈 PİYASA NABZI</b>"]
    for coin, data in list(prices.items())[:10]:
        price = data.get("usd", 0)
        change_24h = data.get("usd_24h_change", 0) or 0
        change_7d = data.get("usd_7d_change", 0) or 0
        arrow = "▲" if change_24h >= 0 else "▼"
        sign = "+" if change_24h >= 0 else ""
        symbol = coin.split("-")[0].upper()
        price_str = f"${price:,.0f}" if price > 100 else f"${price:.4f}"
        lines.append(f"<code>{symbol:8}</code> {price_str:>12}  {arrow}{sign}{change_24h:.1f}%  (7d: {change_7d:+.1f}%)")

    fg = market.get("fear_greed", [{}])
    gs = market.get("global_stats", {})
    if fg and fg[0]:
        fg_val = fg[0].get("value_classification", "?")
        lines.append(f"\nF&G: <b>{fg_val}</b> ({fg[0].get('value','?')})")
    if gs:
        lines.append(f"BTC Dom: {gs.get('btc_dominance','?')}% | 24h: {gs.get('market_cap_change_24h','?')}%")

    trending = market.get("trending", [])
    if trending:
        trend_str = " · ".join(f"{t['name']}" for t in trending[:5])
        lines.append(f"Trending: {trend_str}")

    return "\n".join(lines)


def build_footer(vector: dict, ts: str) -> str:
    weekday_ctx = DiversityEngine.weekday_context(vector.get("weekday", ""))
    return f"""<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>
<i>{weekday_ctx}</i>

<code>NEXA HQ · v5.0 · {ts[:16]}Z</code>
<code>9-Ajan Pipeline · Google Grounding · SQLite Memory</code>"""


# ─────────────────────────────────────────────────────────────────────────────
# TAM RAPORU TELEGRAM MESAJLARINA ÇEVİR
# ─────────────────────────────────────────────────────────────────────────────
SECTION_ORDER = [
    ("temporal",    "⏱️ TEMPORAL ARBİTRAJ"),
    ("contra",      "🔄 KONTRA-SENTİMENT"),
    ("weak_signal", "🔮 ZAYIF SİNYAL"),
    ("cognitive",   "🧬 BİLİŞSEL KENAR"),
    ("systems",     "🌀 SİSTEM ÇÖZÜLME"),
    ("narrative",   "🚀 NARATİF VELOCİTY"),
    ("deep_science","🔬 DERİN BİLİM"),
    ("proptech",    "🏢 PROPTECH OSINT"),
    ("strategy",    "🗡️ STRATEJİK SİLAH"),
]


def build_telegram_messages(result: dict, avg_quality_10d: str = "?") -> list[str]:
    """
    Tam sonuç dict'ini Telegram mesajları listesine çevir.
    Her mesaj 4000 karakter limitini aşmaz.
    """
    messages = []

    # 1. Header
    header = build_header(
        date_str=result["date_str"],
        time_str=result["time_str"],
        quality=result["quality"],
        vector=result["vector"],
        avg_quality_10d=avg_quality_10d,
    )
    messages.append(header)

    # 2. Piyasa ticker (opsiyonel)
    market_msg = build_market_ticker(result.get("market", {}))
    if market_msg:
        messages.append(market_msg)

    # 3. Her ajan bölümü ayrı mesaj(lar)
    sections = result.get("sections", {})
    for key, label in SECTION_ORDER:
        content = sections.get(key, "")
        if not content or len(content) < 30:
            continue

        cleaned = clean_agent_output(content)
        # Bölüm başlığını ekle (eğer ajan kendi koymamışsa)
        if not cleaned.startswith("<b>"):
            cleaned = f"<b>{label}</b>\n\n{cleaned}"

        # Çok uzunsa böl
        for part in split_message(cleaned):
            messages.append(part)

    # 4. Footer
    footer = build_footer(
        vector=result["vector"],
        ts=result.get("ts", datetime.utcnow().isoformat()),
    )
    messages.append(footer)

    return messages


# ─────────────────────────────────────────────────────────────────────────────
# DURUM MESAJI
# ─────────────────────────────────────────────────────────────────────────────
def build_status_message(memory_summary: dict, vector: dict) -> str:
    last = memory_summary.get("last_report") or {}
    return f"""<b>⚡ NEXA SİSTEM DURUMU</b>

<b>📊 İstatistikler:</b>
Toplam Rapor: <code>{memory_summary.get('total_reports', 0)}</code>
10 Günlük Ort. Kalite: <code>{memory_summary.get('avg_quality_10d', '?')}/10</code>
Son 7 Günde Kavram: <code>{memory_summary.get('concepts_last_7d', 0)}</code>

<b>📅 Son Rapor:</b>
Tarih: <code>{last.get('date_str', 'Hiç çalışmadı')}</code>
Kalite: <code>{last.get('quality', '?')}</code>
Tetikleyen: <code>{last.get('triggered_by', '?')}</code>

<b>🔭 Bugünün Vektörü:</b>
Domain: <code>{' + '.join(vector.get('domain_focus', []))}</code>
Çerçeve: <code>{vector.get('cognitive_frame', '?')}</code>
Mod: <code>{vector.get('search_mode', '?')}</code>

<b>⏰ Otomatik Çalışma:</b>
Her gün <code>{config.DAILY_HOUR:02d}:{config.DAILY_MINUTE:02d}</code> yerel saat

<i>Komutlar: /report /quick /status /memory /help</i>"""


def build_memory_message(concepts: list[str], domain_focuses: list[str]) -> str:
    concept_str = ", ".join(concepts[:30]) if concepts else "Henüz kavram yok"
    focus_str = ", ".join(set(domain_focuses[:10])) if domain_focuses else "Henüz yok"
    return f"""<b>🧠 HAFIZA ÖZETI</b>

<b>Son {config.DIVERSITY_WINDOW_DAYS} Günde Kapsanan Kavramlar:</b>
<i>{concept_str}</i>

<b>Son 7 Günde Aktif Domainler:</b>
<code>{focus_str}</code>

<i>Bu kavramlar tekrar edilmeyecek. Sistem çeşitlilik için bunlardan kaçınır.</i>"""


def build_help_message() -> str:
    return f"""<b>⚡ NEXA DEEP INTELLIGENCE v5.0</b>
<b>Yiğit Narin için Kişisel İstihbarat Sistemi</b>

<b>Komutlar:</b>
/report — Tam 9-ajan raporu oluştur ve gönder
/quick — Sadece Stratejik Silah (hızlı özet)
/status — Sistem durumu ve son çalışma
/memory — Hafıza özeti (kapsanan kavramlar)
/help — Bu mesaj

<b>Otomatik:</b>
Her sabah <code>{config.DAILY_HOUR:02d}:{config.DAILY_MINUTE:02d}</code>'da çalışır.

<b>8+1 Ajan:</b>
⏱️ Temporal Arbitraj
🔄 Kontra-Sentiment
🔮 Zayıf Sinyal Konverjans
🧬 Bilişsel Kenar Protokolü
🌀 Sistem Çözülme
🚀 Narratif Velocity
🔬 Derin Bilim Atılımı
🏢 PropTech OSINT
🗡️ Stratejik Silah (Sentez)

<i>Domains: AI · Longevity · Kripto · PropTech · Biyohacking · Kuantum · OSINT</i>"""
