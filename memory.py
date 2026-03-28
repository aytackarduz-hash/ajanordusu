"""
NEXA DEEP INTELLIGENCE v5.0 — memory.py
Kalıcı hafıza motoru. SQLite tabanlı, async destekli.
Konsept çeşitliliği, kalite geçmişi, kaynak takibi.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import aiosqlite

from config import config

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# VERİTABANI ŞEMASI
# ─────────────────────────────────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS reports (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT NOT NULL,
    date_str    TEXT NOT NULL,
    quality     REAL,
    vector_json TEXT,
    concepts_json TEXT,
    domain_focus TEXT,
    triggered_by TEXT DEFAULT 'schedule'
);

CREATE TABLE IF NOT EXISTS quality_log (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    ts      TEXT NOT NULL,
    score   REAL NOT NULL,
    agent   TEXT
);

CREATE TABLE IF NOT EXISTS covered_concepts (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    ts      TEXT NOT NULL,
    concept TEXT NOT NULL,
    domain  TEXT
);

CREATE TABLE IF NOT EXISTS agent_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT NOT NULL,
    agent_name  TEXT NOT NULL,
    output_len  INTEGER,
    success     INTEGER DEFAULT 1,
    error_msg   TEXT
);

CREATE TABLE IF NOT EXISTS kv_store (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_covered_ts ON covered_concepts(ts);
CREATE INDEX IF NOT EXISTS idx_reports_ts ON reports(ts);
CREATE INDEX IF NOT EXISTS idx_quality_ts ON quality_log(ts);
"""


# ─────────────────────────────────────────────────────────────────────────────
# HAFIZA MOTORU
# ─────────────────────────────────────────────────────────────────────────────
class MemoryEngine:
    def __init__(self, db_path: str = config.DB_PATH):
        self.db_path = db_path

    async def init(self):
        """Veritabanını başlat ve şemayı oluştur."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(SCHEMA)
            await db.commit()
        logger.info(f"Memory engine initialized: {self.db_path}")

    # ─── RAPOR KAYDI ────────────────────────────────────────────────────────
    async def save_report(
        self,
        ts: str,
        date_str: str,
        quality: float,
        vector: dict,
        concepts: list[str],
        domain_focus: list[str],
        triggered_by: str = "schedule",
    ):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO reports
                   (ts, date_str, quality, vector_json, concepts_json, domain_focus, triggered_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    ts,
                    date_str,
                    quality,
                    json.dumps(vector, ensure_ascii=False),
                    json.dumps(concepts, ensure_ascii=False),
                    json.dumps(domain_focus, ensure_ascii=False),
                    triggered_by,
                ),
            )
            # Konseptleri ayrı tabloya kaydet
            now = datetime.utcnow().isoformat()
            for concept in concepts[:50]:
                await db.execute(
                    "INSERT INTO covered_concepts (ts, concept, domain) VALUES (?, ?, ?)",
                    (now, concept.lower(), ",".join(domain_focus)),
                )
            await db.commit()

    # ─── KALİTE KAYDI ───────────────────────────────────────────────────────
    async def log_quality(self, score: float, agent: str = "overall"):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO quality_log (ts, score, agent) VALUES (?, ?, ?)",
                (datetime.utcnow().isoformat(), score, agent),
            )
            await db.commit()

    # ─── AJAN GEÇMİŞİ ────────────────────────────────────────────────────────
    async def log_agent(
        self,
        agent_name: str,
        output_len: int,
        success: bool = True,
        error_msg: str = None,
    ):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO agent_history
                   (ts, agent_name, output_len, success, error_msg)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    datetime.utcnow().isoformat(),
                    agent_name,
                    output_len,
                    1 if success else 0,
                    error_msg,
                ),
            )
            await db.commit()

    # ─── SON N GÜNÜN KONSEPTLERINI AL ────────────────────────────────────────
    async def recent_concepts(self, days: int = None) -> list[str]:
        days = days or config.DIVERSITY_WINDOW_DAYS
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT DISTINCT concept FROM covered_concepts WHERE ts > ? LIMIT 300",
                (cutoff,),
            )
            rows = await cursor.fetchall()
        return [r[0] for r in rows]

    # ─── SON N RAPORDAKI DOMAIN ODAKLARINI AL ────────────────────────────────
    async def recent_domain_focuses(self, n: int = 7) -> list[str]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT domain_focus FROM reports ORDER BY ts DESC LIMIT ?",
                (n,),
            )
            rows = await cursor.fetchall()
        focuses = []
        for (df,) in rows:
            try:
                focuses.extend(json.loads(df))
            except Exception:
                pass
        return list(set(focuses))

    # ─── ORTALAMA KALİTE ─────────────────────────────────────────────────────
    async def avg_quality(self, n: int = 10) -> str:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT AVG(score) FROM (SELECT score FROM quality_log WHERE agent='overall' ORDER BY ts DESC LIMIT ?)",
                (n,),
            )
            row = await cursor.fetchone()
        val = row[0] if row and row[0] else None
        return f"{val:.1f}" if val else "?"

    # ─── RAPOR SAYISI ─────────────────────────────────────────────────────────
    async def report_count(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM reports")
            row = await cursor.fetchone()
        return row[0] if row else 0

    # ─── SON RAPORUN TARİHİ ───────────────────────────────────────────────────
    async def last_report_ts(self) -> str | None:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT ts, date_str, quality, triggered_by FROM reports ORDER BY ts DESC LIMIT 1"
            )
            row = await cursor.fetchone()
        if not row:
            return None
        return {"ts": row[0], "date_str": row[1], "quality": row[2], "triggered_by": row[3]}

    # ─── KALİTE GEÇMİŞİ ──────────────────────────────────────────────────────
    async def quality_history(self, n: int = 14) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT ts, score FROM quality_log WHERE agent='overall' ORDER BY ts DESC LIMIT ?",
                (n,),
            )
            rows = await cursor.fetchall()
        return [{"ts": r[0], "score": r[1]} for r in rows]

    # ─── AJAN BAŞARI ORANI ────────────────────────────────────────────────────
    async def agent_success_rate(self, agent_name: str, n: int = 20) -> str:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """SELECT AVG(success) FROM
                   (SELECT success FROM agent_history WHERE agent_name=? ORDER BY ts DESC LIMIT ?)""",
                (agent_name, n),
            )
            row = await cursor.fetchone()
        val = row[0] if row and row[0] is not None else None
        return f"{val*100:.0f}%" if val is not None else "?"

    # ─── KV STORE ─────────────────────────────────────────────────────────────
    async def kv_set(self, key: str, value: Any):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)",
                (key, json.dumps(value)),
            )
            await db.commit()

    async def kv_get(self, key: str, default=None) -> Any:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT value FROM kv_store WHERE key = ?", (key,)
            )
            row = await cursor.fetchone()
        if not row:
            return default
        try:
            return json.loads(row[0])
        except Exception:
            return default

    # ─── ESKİ VERİYİ TEMİZLE ─────────────────────────────────────────────────
    async def cleanup_old_data(self, keep_days: int = 90):
        cutoff = (datetime.utcnow() - timedelta(days=keep_days)).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM covered_concepts WHERE ts < ?", (cutoff,))
            await db.execute("DELETE FROM quality_log WHERE ts < ?", (cutoff,))
            await db.execute("DELETE FROM agent_history WHERE ts < ?", (cutoff,))
            await db.commit()
        logger.info(f"Cleaned up data older than {keep_days} days")

    # ─── HAFIZA ÖZETİ ─────────────────────────────────────────────────────────
    async def summary(self) -> dict:
        count = await self.report_count()
        avg_q = await self.avg_quality()
        last = await self.last_report_ts()
        concepts = await self.recent_concepts(7)
        return {
            "total_reports": count,
            "avg_quality_10d": avg_q,
            "last_report": last,
            "concepts_last_7d": len(concepts),
        }


# Singleton
memory = MemoryEngine()


# ─────────────────────────────────────────────────────────────────────────────
# YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────────────────────────────────────
def extract_concepts(text: str, max_concepts: int = 80) -> list[str]:
    """Metinden anahtar kavramları çıkar."""
    import re
    stop_words = {
        "için", "olan", "gibi", "daha", "veya", "ama", "ile", "bir", "bu",
        "çok", "var", "that", "with", "from", "this", "have", "been", "will",
        "they", "their", "which", "also", "into", "over", "what", "when",
        "where", "there", "than", "about", "these", "would", "could", "should",
        "very", "just", "some", "when", "then", "into", "than", "each",
        "yani", "olan", "iken", "zaman", "kadar", "sonra", "önce", "bile",
        "biri", "her", "hiç", "nasıl", "neden", "ise", "değil",
    }
    # 4+ karakterli anlamlı kelimeleri al
    words = re.findall(r"[a-zA-ZçğışöüÇĞİŞÖÜ]{4,}", text.lower())
    filtered = [w for w in words if w not in stop_words]
    # Frekans sıralaması
    from collections import Counter
    freq = Counter(filtered)
    top = [word for word, _ in freq.most_common(max_concepts)]
    return top
