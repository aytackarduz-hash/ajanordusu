"""
╔══════════════════════════════════════════════════════════════╗
║   NEXA DEEP INTELLIGENCE v6.0 — app.py (Single File)        ║
║   Yiğit Narin için Kişisel Stratejik İstihbarat Sistemi      ║
║   14 Ajan · Deep Research · Özel Komutlar · SQLite Hafıza    ║
╚══════════════════════════════════════════════════════════════╝

KOMUTLAR:
  /report    — Tam 14-ajan sabah raporu (~3-5 dk)
  /quick     — Stratejik Silah özeti (hızlı)
  /research  — Herhangi konuda derin araştırma
  /proptech  — PropTech + Türkiye piyasa analizi
  /longevity — Longevity + bilişsel optimizasyon protokolü
  /ai        — AI sistemleri + güvenlik araştırması
  /crypto    — Kripto/DeFi derin analiz
  /idea      — Fikir validasyonu + iş planı
  /osint     — OSINT + rakip profil analizi
  /status    — Sistem durumu
  /memory    — Hafıza özeti
  /vector    — Bugünün keşif vektörü
"""

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import asyncio
import json
import logging
import math
import re
import sys
from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

import aiosqlite
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
import os
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()


# ═════════════════════════════════════════════════════════════════════════════
# ① KULLANICI PROFİLİ
# ═════════════════════════════════════════════════════════════════════════════
USER = {
    "name": "Yiğit Narin",
    "age": 25,
    "role": "Nexa Digital Kurucusu · PropTech Girişimcisi · AI Sistemleri Mimarı · Adversarial AI Araştırmacısı",
    "location": "Ankara, Türkiye",

    "identity_pillars": [
        "PropTech × AI Security × Solopreneurship — Türkiye'de boş kategori, tek isim olma fırsatı",
        "14 yıl ulusal düzey rekabetçi yüzme (sprint/serbest stil) — baskı altında performans DNA'sı",
        "INTJ + 5w4 — Sistem mimarı + Vizyon adamı. Egemenlik motivasyonu, sıradanlığa tahammülsüzlük.",
        "Yazılım mühendisliği × gayrimenkul danışmanlığı × AI araştırması — birbirini besleyen 3 eksen",
    ],

    "strategic_goals": [
        "Türkiye PropTech ekosisteminin kaçınılmaz ismi olmak — Playwright OSINT + Gemini CRM + Adversarial AI",
        "Nexa CRM'i ilk ücretli SaaS kullanıcısına ulaştırmak (2026 Prio #1)",
        "İnsan bilişsel kapasitesini teknoloji ve biyokimya ile sistematik olarak maksimize etmek",
        "Radikal yaşam uzatma (longevity) ve nöro-enhancement araştırmaları için kişisel protokol geliştirmek",
        "Finansal bağımsızlık: Gayrimenkul komisyon + SaaS gelir + algoritmik trading bileşiği",
        "LLM güvenlik sertifikasyonu: MITRE ATLAS, OWASP LLM Top 10 — en az 1 sertifika/badge",
        "Kişisel marka pipeline: Haftalık 3+ Reels/Shorts/LinkedIn — AI video + hook içerik otomasyonu",
        "WA Grup Scraper canlıya alma: Günde 10+ otomatik lead yakalama",
        "İnsan-AI simbiyotik çalışma kültürü: Çok-ajanlı LLM mimarisini projelerine entegre etmek",
    ],

    "active_projects": [
        "Nexa CRM: Flask/Python + Firebase + Node.js (Baileys) + Vue.js — PropTech SaaS, ilk SaaS müşterisi hedefi",
        "Nexa OSINT Pipeline: PSI API + Playwright + BeautifulSoup — rakip emlakçı profil istihbaratı",
        "Nexa Movies: Veo 3.1 JSON, Non-Linear Sensory Editing, sinematik executive brand filmler",
        "Nexa Digital: Dijital ajans — teknik proje teslimi + sinematik brand filmler",
        "APEX TRADE: Algoritmik trading sistemi — 2 master-prompt mimari, kavramsal aşama",
        "WA Grup Scraper + İlan Eşleştirici: Otomatik lead yakalama — 2026 öncelik",
        "Emlak Portföyü: Gökdemir İmza (İncek/Mart 2029), Start Bravo Idea, Narçın Ronya City I",
        "LLM Güvenlik Araştırması: Dr. Nexus, OMNI-PROCESSOR, RED-OP persona mimarileri",
    ],

    "knowledge_domains": {
        "AI_Systems_Architecture": {
            "priority": 1,
            "topics": [
                "Agentic AI ve otonom ajan mimarileri — multi-step reasoning, tool use",
                "LLM güvenliği, adversarial prompting, Constitutional AI, RLHF mekanizmaları",
                "Multi-modal modeller, görme+dil+ses entegrasyonu",
                "RAG sistemleri, embedding optimizasyonu, long-context stratejileri",
                "AI güvenlik: MITRE ATLAS, OWASP LLM Top 10, jailbreak kataloğu",
                "Çok-ajanlı LLM mimarileri: orchestration, paralel reasoning, consensus",
                "Küçük-ama-güçlü modeller: distillation, quantization, edge deployment",
                "AI kod üretimi ve software engineering otomasyonu",
                "Reasoning modelleri: o3/o4 tarzı chain-of-thought mimarileri",
            ],
        },
        "Cognitive_Enhancement": {
            "priority": 2,
            "topics": [
                "Nootropics ve bilişsel performans optimizasyonu — mekanizma+protokol+kanıt kalitesi",
                "Nöropeptidler ve sinaptik plastisite güçlendirme",
                "BDNF, NGF, GDNF — nörotrofik faktör modülasyonu",
                "tDCS/tACS/TMS nörostimülasyon protokolleri",
                "Metabolik bilişsel optimizasyon: mitokondriyal fonksiyon, ATP üretimi",
                "Beyin-bilgisayar arayüzleri (BCI): Neuralink, Synchron, non-invasive",
                "Uyku optimizasyonu: REM/SWS arşivleme, sirkadiyen biyohacking",
                "Stres-performans eğrisi: optimal arousal, kortizol modülasyonu",
                "Hafıza konsolidasyonu ve öğrenme hızlandırma protokolleri",
            ],
        },
        "Longevity_Biotech": {
            "priority": 3,
            "topics": [
                "Senolitikler ve senostatikler — yaşlanma mekanizmalarını hedefleme",
                "CRISPR-Cas9/12/13 gen düzenleme: terapötik uygulamalar ve risk",
                "Mitokondriyal biyogenez ve enerji metabolizması optimizasyonu",
                "Epigenetik reprogramlama: Yamanaka faktörleri, kısmi reprogramlama",
                "Synthetic biology: hücre-dışı sentez, metabolik mühendislik",
                "Metabolomics ve proteomics: biyobelirteç tabanlı yaşlanma ölçümü",
                "Telomer biyolojisi ve telomeraz aktivasyonu",
                "mTOR/AMPK/Sirtuins: enerji hissi-sinyal yolları",
                "GLP-1 agonistleri ve metabolik yeniden yapılanma",
            ],
        },
        "Crypto_DeFi": {
            "priority": 4,
            "topics": [
                "DeFi protokol güvenliği ve smart contract denetim metodolojileri",
                "On-chain analitik: whale wallet takip, smart money akışı",
                "L2 scaling: Arbitrum, Optimism, Base, ZKsync mimarileri",
                "Zero-knowledge proofs: ZK-SNARKs, ZK-STARKs, zkEVM",
                "Tokenomics tasarımı: emisyon modelleri, likidite optimizasyonu",
                "MEV (Maximal Extractable Value) ve flashbot stratejileri",
                "RWA (Real World Assets) tokenizasyonu — PropTech kesişimi",
                "Kripto piyasa yapısı: funding rates, OI, CVD analizi",
                "AI × kripto entegrasyonu: ajan tabanlı trading mimarileri",
            ],
        },
        "PropTech_Business": {
            "priority": 5,
            "topics": [
                "PropTech Türkiye ekosistemi: boşluklar, fırsatlar, oyuncular",
                "SaaS iş modeli tasarımı: fiyatlandırma, churn azaltma, NRR",
                "Gayrimenkul CRM ve otomasyon teknolojileri",
                "Satış psikolojisi: FOMO mühendisliği, Velvet Rope Effect, Tier sistemi",
                "Gayrimenkul yatırım analitikleri: ROI, Cap Rate, IRR, DCF",
                "Dijital pazarlama: hook mimarisi, scroll-stop içerik, viral mekanikler",
                "Sahibinden.com / cb.com.tr veri yapısı ve scraping fırsatları",
                "WhatsApp pazarlama: broadcast stratejisi, engagement optimizasyonu",
                "Türkiye konut piyasası makrosu: faiz, enflasyon, döviz etkisi",
            ],
        },
        "Quantum_Advanced_Computing": {
            "priority": 6,
            "topics": [
                "Kuantum hata düzeltme: surface codes, logical qubit ilerleme",
                "Nöromorfik bilişim: Intel Loihi, IBM TrueNorth, enerji verimliliği",
                "Foton hesaplama: silikon fotonik, optical neural networks",
                "Post-kuantum kriptografi: NIST standartları, geçiş stratejisi",
                "Kuantum sensörler: atom interferometresi, manyetiği hassas ölçüm",
                "Analog bilişim ve in-memory computing rönesansı",
                "Nöral ağ donanım hızlandırıcıları: TPU/NPU/custom ASIC",
            ],
        },
        "Systems_Strategy_OSINT": {
            "priority": 7,
            "topics": [
                "OSINT metodolojileri: graph mapping, passive recon, açık kaynak istihbarat",
                "Anti-kırılganlık sistem tasarımı (Taleb): opsiyonellik, pozitif simetri",
                "First principles mühendisliği (Feynman): kısıtlamaları yeniden tanımlama",
                "Sun Tzu uygulamalı strateji: boşlukları hedefleme, beklenmedik hareket",
                "Ağ efektleri: Metcalfe yasası, tipping point mühendisliği",
                "Dikkat ekonomisi: meme teorisi, viral mekanikler, narrative hız",
                "Pazar yapısı analizi: Porter 5 Güç, Jobs-to-be-Done çerçevesi",
                "Competitive intelligence: rakip zayıflık haritası, blind spot analizi",
            ],
        },
    },

    "cognitive_profile": {
        "style": "Direkt, veri odaklı. Yüzeysel giriş ve kapanış yok. Laf kalabalığına sıfır tolerans.",
        "depth": "2. ve 3. derece çıkarımlar zorunlu. Domino zinciri — her etki bir sonraki etkiyi tetiklemeli.",
        "risk_appetite": "Yüksek. Kanıtlanmamış ama kaynaklı hipotezler kabul edilir. Erken benimseme önceliği.",
        "lens_stack": "Sun Tzu kurnazlığı + Taleb anti-kırılganlık + Feynman birinci prensipler",
        "analogy_resonance": "Spor/rekabet/performans analojileri güçlü etki yaratır. Sprint, er meydanı, antrenman.",
        "weaknesses_to_watch": [
            "Bitmemiş döngüler — yeni proje başlamadan eskiyi tamamlama disiplini",
            "Ultra-detailed fetişizm — analiz üretimin önüne geçebilir",
            "Deep work parçalanması — paralel kollar odak kırıntısı yaratır",
        ],
        "strengths_to_leverage": [
            "Fikri ürüne en kısa yoldan çeviren hız refleksi",
            "Tam stack teknik çok-dillilik (Python/JS/Vue/Node/Firebase)",
            "PropTech Türkiye boşluklarını erken görme kapasitesi",
            "Sistem mimarisi düşünme — her sorunu nasıl çalışır + kurar + geliştirir'e ayırma",
            "Meta-bilişsel kapasite — kendi düşünme kalıplarını analiz etme",
        ],
    },

    "aesthetic_dna": {
        "palette": "Teal-orange-dark — Nolan sinematografisi referans",
        "typography": "Space Mono font, minimal, teknik otorite",
        "lighting": "Chiaroscuro — tek spot ışık, tam siyah arka plan",
        "brand_anchor": "Sakal + koyu saç + yapılı omuz + takım elbise — fiziksel anchor değişmemeli",
        "video_philosophy": "Non-Linear Sensory Editing + Sound-Driven Editing + The Vacuum tekniği",
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# ② KONFİGÜRASYON
# ═════════════════════════════════════════════════════════════════════════════
class Config:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    MAX_RETRIES: int = 3
    RETRY_DELAY_S: float = 2.0
    QUALITY_THRESHOLD: float = 7.0
    MAX_MEMORY_ENTRIES: int = 120
    DIVERSITY_WINDOW_DAYS: int = 14
    REPORT_VERSION: str = "v6.0"

    # Sabah 10:00 Türkiye saati
    DAILY_HOUR: int = int(os.getenv("DAILY_HOUR", "10"))
    DAILY_MINUTE: int = int(os.getenv("DAILY_MINUTE", "0"))

    DB_PATH: str = os.getenv("DB_PATH", "nexa_memory.db")
    HTTP_TIMEOUT: float = 45.0
    AGENT_CONCURRENCY: int = 4

    TELEGRAM_MAX_CHARS: int = 4000
    TELEGRAM_PARSE_MODE: str = "HTML"

    LOG_FILE: str = "nexa_intel.log"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    AGENT_TEMPERATURES = {
        "temporal_arbitrage": 0.75,
        "contra_sentiment": 0.85,
        "weak_signal": 0.90,
        "cognitive_edge": 0.80,
        "systems_breakdown": 0.80,
        "narrative_velocity": 0.90,
        "deep_science": 0.70,
        "proptech_osint": 0.75,
        "strategic_weapon": 0.92,
        "quality_evaluator": 0.10,
        # Yeni ajanlar
        "deep_research": 0.80,
        "longevity_protocol": 0.75,
        "ai_security": 0.78,
        "crypto_alpha": 0.82,
        "idea_validator": 0.85,
        "osint_profiler": 0.78,
    }

    AGENT_MAX_TOKENS = {
        "temporal_arbitrage": 1800,
        "contra_sentiment": 1700,
        "weak_signal": 1800,
        "cognitive_edge": 2000,
        "systems_breakdown": 1700,
        "narrative_velocity": 1700,
        "deep_science": 2000,
        "proptech_osint": 1700,
        "strategic_weapon": 1200,
        "quality_evaluator": 600,
        # Yeni ajanlar
        "deep_research": 2500,
        "longevity_protocol": 2000,
        "ai_security": 2000,
        "crypto_alpha": 1800,
        "idea_validator": 2000,
        "osint_profiler": 1800,
    }


config = Config()


# ═════════════════════════════════════════════════════════════════════════════
# ③ HAFIZA MOTORU (SQLite)
# ═════════════════════════════════════════════════════════════════════════════
SCHEMA = """
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    date_str TEXT NOT NULL,
    quality REAL,
    vector_json TEXT,
    concepts_json TEXT,
    domain_focus TEXT,
    triggered_by TEXT DEFAULT 'schedule'
);
CREATE TABLE IF NOT EXISTS quality_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    score REAL NOT NULL,
    agent TEXT
);
CREATE TABLE IF NOT EXISTS covered_concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    concept TEXT NOT NULL,
    domain TEXT
);
CREATE TABLE IF NOT EXISTS agent_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    output_len INTEGER,
    success INTEGER DEFAULT 1,
    error_msg TEXT
);
CREATE TABLE IF NOT EXISTS kv_store (
    key TEXT PRIMARY KEY,
    value TEXT
);
CREATE INDEX IF NOT EXISTS idx_covered_ts ON covered_concepts(ts);
CREATE INDEX IF NOT EXISTS idx_reports_ts ON reports(ts);
CREATE INDEX IF NOT EXISTS idx_quality_ts ON quality_log(ts);
"""


class MemoryEngine:
    def __init__(self, db_path: str = config.DB_PATH):
        self.db_path = db_path

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(SCHEMA)
            await db.commit()

    async def save_report(self, ts, date_str, quality, vector, concepts, domain_focus, triggered_by="schedule"):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO reports (ts,date_str,quality,vector_json,concepts_json,domain_focus,triggered_by) VALUES (?,?,?,?,?,?,?)",
                (ts, date_str, quality, json.dumps(vector, ensure_ascii=False),
                 json.dumps(concepts, ensure_ascii=False), json.dumps(domain_focus, ensure_ascii=False), triggered_by),
            )
            now = datetime.utcnow().isoformat()
            for concept in concepts[:50]:
                await db.execute(
                    "INSERT INTO covered_concepts (ts,concept,domain) VALUES (?,?,?)",
                    (now, concept.lower(), ",".join(domain_focus)),
                )
            await db.commit()

    async def log_quality(self, score: float, agent: str = "overall"):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO quality_log (ts,score,agent) VALUES (?,?,?)",
                             (datetime.utcnow().isoformat(), score, agent))
            await db.commit()

    async def log_agent(self, agent_name, output_len, success=True, error_msg=None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO agent_history (ts,agent_name,output_len,success,error_msg) VALUES (?,?,?,?,?)",
                (datetime.utcnow().isoformat(), agent_name, output_len, 1 if success else 0, error_msg),
            )
            await db.commit()

    async def recent_concepts(self, days=None) -> list[str]:
        days = days or config.DIVERSITY_WINDOW_DAYS
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT DISTINCT concept FROM covered_concepts WHERE ts > ? LIMIT 300", (cutoff,))
            rows = await cursor.fetchall()
        return [r[0] for r in rows]

    async def recent_domain_focuses(self, n=7) -> list[str]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT domain_focus FROM reports ORDER BY ts DESC LIMIT ?", (n,))
            rows = await cursor.fetchall()
        focuses = []
        for (df,) in rows:
            try:
                focuses.extend(json.loads(df))
            except Exception:
                pass
        return list(set(focuses))

    async def avg_quality(self, n=10) -> str:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT AVG(score) FROM (SELECT score FROM quality_log WHERE agent='overall' ORDER BY ts DESC LIMIT ?)", (n,))
            row = await cursor.fetchone()
        val = row[0] if row and row[0] else None
        return f"{val:.1f}" if val else "?"

    async def report_count(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM reports")
            row = await cursor.fetchone()
        return row[0] if row else 0

    async def last_report_ts(self):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT ts,date_str,quality,triggered_by FROM reports ORDER BY ts DESC LIMIT 1")
            row = await cursor.fetchone()
        if not row:
            return None
        return {"ts": row[0], "date_str": row[1], "quality": row[2], "triggered_by": row[3]}

    async def quality_history(self, n=14) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT ts,score FROM quality_log WHERE agent='overall' ORDER BY ts DESC LIMIT ?", (n,))
            rows = await cursor.fetchall()
        return [{"ts": r[0], "score": r[1]} for r in rows]

    async def kv_set(self, key: str, value: Any):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO kv_store (key,value) VALUES (?,?)",
                             (key, json.dumps(value)))
            await db.commit()

    async def kv_get(self, key: str, default=None) -> Any:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT value FROM kv_store WHERE key=?", (key,))
            row = await cursor.fetchone()
        if not row:
            return default
        try:
            return json.loads(row[0])
        except Exception:
            return default

    async def cleanup_old_data(self, keep_days=90):
        cutoff = (datetime.utcnow() - timedelta(days=keep_days)).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM covered_concepts WHERE ts < ?", (cutoff,))
            await db.execute("DELETE FROM quality_log WHERE ts < ?", (cutoff,))
            await db.execute("DELETE FROM agent_history WHERE ts < ?", (cutoff,))
            await db.commit()

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


def extract_concepts(text: str, max_concepts: int = 80) -> list[str]:
    stop_words = {
        "için", "olan", "gibi", "daha", "veya", "ama", "ile", "bir", "bu",
        "çok", "var", "that", "with", "from", "this", "have", "been", "will",
        "they", "their", "which", "also", "into", "over", "what", "when",
        "where", "there", "than", "about", "these", "would", "could", "should",
        "very", "just", "some", "then", "each", "yani", "iken", "zaman",
        "kadar", "sonra", "önce", "bile", "biri", "her", "hiç", "nasıl",
        "neden", "ise", "değil",
    }
    words = re.findall(r"[a-zA-ZçğışöüÇĞİŞÖÜ]{4,}", text.lower())
    filtered = [w for w in words if w not in stop_words]
    freq = Counter(filtered)
    return [word for word, _ in freq.most_common(max_concepts)]


# Singleton
memory = MemoryEngine()


# ═════════════════════════════════════════════════════════════════════════════
# ④ ÇEŞİTLİLİK MOTORU
# ═════════════════════════════════════════════════════════════════════════════
class DailyVector(dict):
    pass


class DiversityEngine:
    TEMPORAL_LENSES = [
        "imminent_48h", "weekly_cycle", "monthly_shift", "quarter_trend",
        "year_horizon", "decade_shift", "contrarian_now",
    ]

    COGNITIVE_FRAMES = [
        "adversarial", "first_principles", "second_order", "inversion",
        "bayesian_update", "narrative_lens", "systems_lens", "optionality",
        "steelman", "arbitrage_lens", "velocity_lens", "decay_lens",
        "singularity_lens", "sunzi_lens",
    ]

    DOMAIN_ROTATIONS = [
        ["AI_Systems_Architecture", "Cognitive_Enhancement"],
        ["Longevity_Biotech", "Quantum_Advanced_Computing"],
        ["Crypto_DeFi", "PropTech_Business"],
        ["AI_Systems_Architecture", "Systems_Strategy_OSINT"],
        ["Cognitive_Enhancement", "Longevity_Biotech"],
        ["Quantum_Advanced_Computing", "Crypto_DeFi"],
        ["PropTech_Business", "AI_Systems_Architecture"],
        ["Systems_Strategy_OSINT", "Longevity_Biotech"],
        ["AI_Systems_Architecture", "Crypto_DeFi", "Cognitive_Enhancement"],
        ["Longevity_Biotech", "Quantum_Advanced_Computing", "Systems_Strategy_OSINT"],
        ["PropTech_Business", "AI_Systems_Architecture", "Crypto_DeFi"],
        ["Cognitive_Enhancement", "Systems_Strategy_OSINT"],
        ["AI_Systems_Architecture", "Longevity_Biotech", "PropTech_Business"],
        ["Quantum_Advanced_Computing", "Cognitive_Enhancement", "Crypto_DeFi"],
    ]

    SEARCH_MODES = [
        "bleeding_edge_papers", "smart_money_footprint", "developer_velocity",
        "niche_community_signal", "regulatory_shadow", "cross_domain_collision",
        "contrarian_data_point", "founder_intelligence", "patent_signal",
        "acquisition_radar", "talent_flow",
    ]

    WEEKDAY_CONTEXT = {
        "Pazartesi": "Haftalık strateji yenile. Sistemleri gözden geçir. Haftanın savaşını belirle.",
        "Salı":      "Derinlik günü. En karmaşık teknik konuya dal. First principles uygula.",
        "Çarşamba":  "Çapraz domain. Farklı alanların kesişimini ara. Cross-pollination.",
        "Perşembe":  "Piyasa günü. Fiyat aksiyonu, smart money, on-chain okuma.",
        "Cuma":      "Hafta özeti ve gelecek hafta pozisyon hazırlığı. Narrative velocity.",
        "Cumartesi": "Longevity ve bilişsel optimizasyon. Uzun vadeli beyin sermayesi.",
        "Pazar":     "Ufuk taraması. 10 yıllık paradigma kayması. Deep science.",
    }

    @classmethod
    def today_vector(cls) -> dict:
        now = datetime.now()
        day_idx = int(now.timestamp() / 86400)
        day_of_year = now.timetuple().tm_yday
        days_left_year = 365 - day_of_year
        weekdays = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        weekday = weekdays[now.weekday()]
        domain_combo = cls.DOMAIN_ROTATIONS[day_idx % len(cls.DOMAIN_ROTATIONS)]
        temporal = cls.TEMPORAL_LENSES[day_idx % len(cls.TEMPORAL_LENSES)]
        cognitive = cls.COGNITIVE_FRAMES[day_idx % len(cls.COGNITIVE_FRAMES)]
        search_mode = cls.SEARCH_MODES[day_idx % len(cls.SEARCH_MODES)]

        if weekday == "Cumartesi":
            if "Longevity_Biotech" not in domain_combo:
                domain_combo = ["Longevity_Biotech", "Cognitive_Enhancement"]
        elif weekday == "Pazar":
            if "Quantum_Advanced_Computing" not in domain_combo:
                domain_combo = ["Quantum_Advanced_Computing", "AI_Systems_Architecture"]
        elif weekday == "Perşembe":
            if "Crypto_DeFi" not in domain_combo:
                domain_combo = ["Crypto_DeFi"] + [d for d in domain_combo if d != "Crypto_DeFi"][:2]

        return {
            "temporal_lens": temporal,
            "cognitive_frame": cognitive,
            "domain_focus": domain_combo,
            "search_mode": search_mode,
            "weekday": weekday,
            "hour": now.hour,
            "day_of_year": day_of_year,
            "days_left_year": days_left_year,
            "week_number": now.isocalendar()[1],
            "primary_domain": domain_combo[0],
            "secondary_domain": domain_combo[1] if len(domain_combo) > 1 else domain_combo[0],
        }

    @classmethod
    def weekday_context(cls, weekday: str) -> str:
        return cls.WEEKDAY_CONTEXT.get(weekday, "Odaklan ve üret.")

    @classmethod
    def domain_topics(cls, domain_name: str) -> list[str]:
        domain_data = USER["knowledge_domains"].get(domain_name, {})
        return domain_data.get("topics", [])

    @classmethod
    def format_vector_info(cls, vector: dict) -> str:
        return (
            f"📅 {vector['weekday']} · Gün {vector['day_of_year']}/365 · Hafta {vector['week_number']}\n"
            f"🔭 Zaman: <code>{vector['temporal_lens']}</code>\n"
            f"🧠 Çerçeve: <code>{vector['cognitive_frame']}</code>\n"
            f"🎯 Domain: <code>{' | '.join(vector['domain_focus'])}</code>\n"
            f"🔍 Mod: <code>{vector['search_mode']}</code>\n"
            f"⏳ Yıla {vector['days_left_year']} gün kaldı"
        )


# ═════════════════════════════════════════════════════════════════════════════
# ⑤ VERİ TOPLAMA (DATA MESH)
# ═════════════════════════════════════════════════════════════════════════════
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
    intel: list = field(default_factory=list)
    dev_velocity: list = field(default_factory=list)
    hn_signal: list = field(default_factory=list)
    fetched_at: str = ""
    errors: list = field(default_factory=list)


RSS_SOURCES = [
    {"tag": "arxiv_ai",      "url": "https://rss.arxiv.org/rss/cs.AI",        "limit": 8},
    {"tag": "arxiv_ml",      "url": "https://rss.arxiv.org/rss/cs.LG",        "limit": 8},
    {"tag": "arxiv_neuro",   "url": "https://rss.arxiv.org/rss/q-bio.NC",     "limit": 6},
    {"tag": "arxiv_quant",   "url": "https://rss.arxiv.org/rss/quant-ph",     "limit": 5},
    {"tag": "arxiv_bio",     "url": "https://rss.arxiv.org/rss/q-bio.GN",     "limit": 5},
    {"tag": "arxiv_cv",      "url": "https://rss.arxiv.org/rss/cs.CV",        "limit": 5},
    {"tag": "biorxiv",       "url": "https://www.biorxiv.org/rss/current",    "limit": 5},
    {"tag": "nature",        "url": "https://www.nature.com/subjects/biological-sciences.rss", "limit": 4},
    {"tag": "techcrunch_ai", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "limit": 6},
    {"tag": "arstechnica",   "url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "limit": 5},
    {"tag": "mit_tech",      "url": "https://www.technologyreview.com/feed/",  "limit": 5},
    {"tag": "wired_sci",     "url": "https://www.wired.com/feed/category/science/latest/rss", "limit": 4},
    {"tag": "verge",         "url": "https://www.theverge.com/rss/index.xml", "limit": 4},
    {"tag": "coindesk",      "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "limit": 6},
    {"tag": "theblock",      "url": "https://www.theblock.co/rss.xml",        "limit": 5},
    {"tag": "decrypt",       "url": "https://decrypt.co/feed",                "limit": 5},
    {"tag": "cointelegraph", "url": "https://cointelegraph.com/rss",          "limit": 5},
    {"tag": "singularity",   "url": "https://singularityhub.com/feed/",       "limit": 5},
    {"tag": "futurism",      "url": "https://futurism.com/feed",              "limit": 4},
    {"tag": "longevity",     "url": "https://www.longevity.technology/feed/", "limit": 5},
    {"tag": "hbr",           "url": "https://feeds.hbr.org/harvardbusiness",  "limit": 3},
    {"tag": "stratechery",   "url": "https://stratechery.com/feed/",          "limit": 3},
]


def strip_html(text: str) -> str:
    text = re.sub(r"<!\[CDATA\[([\s\S]*?)\]\]>", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _match_group(pattern, text, default="", flags=re.I):
    m = re.search(pattern, text, flags)
    return m.group(1) if m else default


def parse_rss(xml_content: str, tag: str, limit: int = 6) -> list:
    items = []
    for raw in re.findall(r"<item>([\s\S]*?)</item>", xml_content)[:limit]:
        title = strip_html(_match_group(r"<title>([\s\S]*?)</title>", raw))
        desc = strip_html(_match_group(r"<description>([\s\S]*?)</description>", raw))
        link = _match_group(r"<link>(.*?)</link>", raw).strip()
        if len(title) > 10:
            items.append(IntelItem(tag=tag, title=title[:200], desc=desc[:350], link=link[:300], source=tag))
    return items


def filter_intel_by_tags(items: list, tag_prefixes: list, limit: int = 10) -> list[str]:
    filtered = [
        f"{i.title} — {i.desc[:100]}"
        for i in items
        if any(i.tag.startswith(p) for p in tag_prefixes)
    ]
    return filtered[:limit]


class DataMesh:
    def __init__(self):
        self._client = None

    async def _get_client(self):
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=config.HTTP_TIMEOUT,
                headers={"User-Agent": "NexaIntelBot/6.0 (+https://nexa.digital)"},
                follow_redirects=True,
            )
        return self._client

    async def _fetch(self, url: str) -> str | None:
        try:
            client = await self._get_client()
            resp = await client.get(url)
            return resp.text if resp.status_code == 200 else None
        except Exception:
            return None

    async def fetch_all_rss(self) -> list:
        tasks = [self._fetch_rss(src) for src in RSS_SOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        items = []
        for r in results:
            if isinstance(r, list):
                items.extend(r)
        return items

    async def _fetch_rss(self, source: dict) -> list:
        xml = await self._fetch(source["url"])
        if not xml:
            return []
        return parse_rss(xml, source["tag"], source.get("limit", 5))

    async def fetch_market_pulse(self) -> dict:
        result = {}
        try:
            ids = (
                "bitcoin,ethereum,solana,sui,hyperliquid,chainlink,"
                "avalanche-2,the-open-network,arbitrum,optimism,"
                "injective-protocol,render-token,fetch-ai,bittensor,"
                "near,aptos,sei-network,celestia,starknet,eigenlayer"
            )
            data = await self._fetch(
                f"https://api.coingecko.com/api/v3/simple/price?ids={ids}"
                "&vs_currencies=usd&include_24hr_change=true&include_7d_change=true"
            )
            if data:
                result["prices"] = json.loads(data)
        except Exception:
            pass
        try:
            data = await self._fetch("https://api.coingecko.com/api/v3/search/trending")
            if data:
                td = json.loads(data)
                result["trending"] = [
                    {"name": c["item"]["name"], "symbol": c["item"]["symbol"],
                     "rank": c["item"].get("market_cap_rank", "?")}
                    for c in td.get("coins", [])[:8]
                ]
        except Exception:
            pass
        try:
            data = await self._fetch("https://api.alternative.me/fng/?limit=3")
            if data:
                result["fear_greed"] = json.loads(data).get("data", [])[:3]
        except Exception:
            pass
        try:
            data = await self._fetch("https://api.coingecko.com/api/v3/global")
            if data:
                d = json.loads(data).get("data", {})
                result["global_stats"] = {
                    "btc_dominance": round(d.get("market_cap_percentage", {}).get("btc", 0), 1),
                    "eth_dominance": round(d.get("market_cap_percentage", {}).get("eth", 0), 1),
                    "market_cap_change_24h": round(d.get("market_cap_change_percentage_24h_usd", 0), 2),
                }
        except Exception:
            pass
        return result

    async def fetch_dev_velocity(self) -> list:
        try:
            data = await self._fetch("https://github-trending-api.de/repositories?language=&since=daily")
            if data:
                repos = json.loads(data)
                return [{"name": r.get("name", ""), "author": r.get("author", ""),
                         "desc": (r.get("description") or "")[:180],
                         "stars": r.get("stars", 0), "stars_today": r.get("currentPeriodStars", "?"),
                         "language": r.get("language", ""), "url": r.get("url", "")}
                        for r in repos[:15]]
        except Exception:
            pass
        return []

    async def fetch_hn_signal(self) -> list:
        try:
            data = await self._fetch("https://hacker-news.firebaseio.com/v0/topstories.json")
            if not data:
                return []
            ids = json.loads(data)[:16]

            async def fetch_story(sid):
                d = await self._fetch(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
                if d:
                    s = json.loads(d)
                    if s.get("title"):
                        return {"title": s["title"], "score": s.get("score", 0),
                                "url": s.get("url", ""), "comments": s.get("descendants", 0)}
                return None

            results = await asyncio.gather(*[fetch_story(i) for i in ids], return_exceptions=True)
            return [r for r in results if isinstance(r, dict)]
        except Exception:
            return []

    async def fetch_all(self) -> DataBundle:
        intel, market, dev, hn = await asyncio.gather(
            self.fetch_all_rss(), self.fetch_market_pulse(),
            self.fetch_dev_velocity(), self.fetch_hn_signal(),
            return_exceptions=True,
        )
        bundle = DataBundle(fetched_at=datetime.utcnow().isoformat())
        bundle.intel = intel if isinstance(intel, list) else []
        bundle.market = market if isinstance(market, dict) else {}
        bundle.dev_velocity = dev if isinstance(dev, list) else []
        bundle.hn_signal = hn if isinstance(hn, list) else []
        return bundle

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()


def bundle_summary(bundle: DataBundle) -> str:
    lines = []
    fg = bundle.market.get("fear_greed", [{}])
    if fg:
        lines.append(f"[Piyasa] Fear&Greed: {fg[0].get('value_classification','?')} ({fg[0].get('value','?')})")
    gs = bundle.market.get("global_stats", {})
    if gs:
        lines.append(f"[Kripto] BTC Dom: {gs.get('btc_dominance','?')}% | 24h: {gs.get('market_cap_change_24h','?')}%")
    trending = bundle.market.get("trending", [])
    if trending:
        names = ", ".join(f"{t['name']}({t['symbol']})" for t in trending[:5])
        lines.append(f"[Trending] {names}")
    return "\n".join(lines)


# ═════════════════════════════════════════════════════════════════════════════
# ⑥ AJAN TABANLI ALTYAPI
# ═════════════════════════════════════════════════════════════════════════════
@dataclass
class AgentContext:
    bundle: DataBundle
    vector: dict
    avoid_concepts: list
    insights: dict
    date_str: str
    time_str: str


logger = logging.getLogger(__name__)


class AgentBase(ABC):
    def __init__(self, name: str, temperature: float = 0.85, max_tokens: int = 1800, use_search: bool = True):
        self.name = name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.use_search = use_search
        self._client = None

    async def _gemini_call(self, prompt: str) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{config.GEMINI_MODEL}:generateContent?key={config.GEMINI_API_KEY}"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self.temperature,
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": self.max_tokens,
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT",       "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ],
        }
        if self.use_search:
            payload["tools"] = [{"google_search": {}}]

        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=60.0)

        last_err = None
        for attempt in range(1, config.MAX_RETRIES + 1):
            try:
                resp = await self._client.post(url, json=payload)
                data = resp.json()
                if resp.status_code != 200:
                    raise RuntimeError(f"HTTP {resp.status_code}: {str(data.get('error',''))[:150]}")
                candidates = data.get("candidates", [])
                if not candidates:
                    raise RuntimeError("No candidates returned")
                candidate = candidates[0]
                if candidate.get("finishReason") == "SAFETY":
                    raise RuntimeError("SAFETY block")
                parts = candidate.get("content", {}).get("parts", [])
                text = "\n".join(p.get("text", "") for p in parts if p.get("text"))
                if not text.strip():
                    raise RuntimeError("Empty response")
                return text
            except Exception as e:
                last_err = e
                if attempt < config.MAX_RETRIES:
                    await asyncio.sleep(config.RETRY_DELAY_S * attempt)

        raise RuntimeError(f"[{self.name}] exhausted retries: {last_err}")

    @abstractmethod
    async def run(self, ctx: AgentContext) -> str:
        pass

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    @staticmethod
    def _avoid_str(concepts: list, n: int = 25) -> str:
        return ", ".join(concepts[:n]) if concepts else "yok"

    @staticmethod
    def _domain_topics_str(domain_names: list, max_per_domain: int = 5) -> str:
        result = []
        for dn in domain_names:
            topics = (USER["knowledge_domains"].get(dn, {}).get("topics", []))[:max_per_domain]
            if topics:
                result.append(f"[{dn.replace('_',' ')}]\n" + "\n".join(f"  • {t}" for t in topics))
        return "\n\n".join(result) or "—"

    @staticmethod
    def _goals_str() -> str:
        return "\n".join(f"• {g}" for g in USER["strategic_goals"])

    @staticmethod
    def _projects_str() -> str:
        return "\n".join(f"• {p}" for p in USER["active_projects"])


# ═════════════════════════════════════════════════════════════════════════════
# ⑦ GÜNLÜK RAPOR AJANLARI (9 Ajan)
# ═════════════════════════════════════════════════════════════════════════════

class TemporalArbitrageAgent(AgentBase):
    def __init__(self):
        super().__init__("TemporalArbitrageAgent",
                         config.AGENT_TEMPERATURES["temporal_arbitrage"],
                         config.AGENT_MAX_TOKENS["temporal_arbitrage"])

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        tech_signals = filter_intel_by_tags(ctx.bundle.intel, ["techcrunch", "arstechnica", "mit_tech", "wired", "verge"], 12)
        sci_signals = filter_intel_by_tags(ctx.bundle.intel, ["arxiv_ai", "arxiv_ml", "arxiv_neuro"], 8)
        domain_context = self._domain_topics_str(v["domain_focus"], 4)

        prompt = f"""
SEN: Zamansal Arbitraj Uzmanısın. 48 saatlik fırsat penceresini tespit edersin.
KULLANICI: {USER['name']}, {USER['age']}Y | {USER['role']}
TARİH: {ctx.date_str} {ctx.time_str} — Gün {v['day_of_year']}/365 — {v['weekday']}
ZAMANSAL MERCEKLİ: {v['temporal_lens']} | BİLİŞSEL ÇERÇEVE: {v['cognitive_frame']}
DOMAIN ODAĞI: {', '.join(v['domain_focus'])}
KAÇINILACAKLAR: {self._avoid_str(ctx.avoid_concepts)}

AKTİF PROJELER:
{self._projects_str()}

STRATEJİK HEDEFLER:
{self._goals_str()}

DOMAIN KONULARI:
{domain_context}

CANLI TEKNOLOJİ SİNYALLERİ:
{chr(10).join(tech_signals) or '[Google Search ile son 48 saati tara]'}

BİLİM SİNYALLERİ:
{chr(10).join(sci_signals) or '[arXiv son yayınları]'}

GÖREV: Son 48 saatte gerçekleşen, PENCERE DAR olan TEK olayı/gelişmeyi bul.
2. ve 3. derece domino zinciri ZORUNLU.

ÇIKTI FORMATI — Telegram HTML:
<b>⏱️ TEMPORAL ARBİTRAJ</b>
<b>📍 [BAŞLIK: Max 10 kelime, şok edici]</b>

<b>🕐 Arbitraj Penceresi:</b> [saat] | <b>Etki:</b> [X/10] | <b>Proje:</b> [hangi proje]

<b>Ne Oldu:</b>
[2-3 cümle, spesifik veri ile]

<b>Neden 48 Saat İçinde Değer Kaybeder:</b>
[mekanizma]

<b>2. Derece Domino:</b>
[ilk tetikleme → sonuç]

<b>3. Derece Domino:</b>
[derin sistemik etki]

<b>⚡ AKSİYON:</b>
[ne + ne zaman + ilk somut adım]
"""
        return await self._gemini_call(prompt)


class ContraSentimentAgent(AgentBase):
    def __init__(self):
        super().__init__("ContraSentimentAgent",
                         config.AGENT_TEMPERATURES["contra_sentiment"],
                         config.AGENT_MAX_TOKENS["contra_sentiment"])

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        fg = ctx.bundle.market.get("fear_greed", [])
        gs = ctx.bundle.market.get("global_stats", {})
        fg_str = " → ".join(f"{f.get('value_classification')}({f.get('value')})" for f in fg)
        gs_str = f"BTC Dom: {gs.get('btc_dominance')}% | 24h: {gs.get('market_cap_change_24h')}%" if gs else ""
        all_headlines = [i.title for i in ctx.bundle.intel[:30]]

        prompt = f"""
SEN: Kontrarian İstihbarat Analistinin. Konsensusun yanıldığı yerleri tespit edersin.
KULLANICI: {USER['name']} | Bilişsel lens stack: {USER['cognitive_profile']['lens_stack']}
ÇERÇEVE: {v['cognitive_frame']} | ARAMA MODU: {v['search_mode']}
KAÇINILACAKLAR: {self._avoid_str(ctx.avoid_concepts)}

PİYASA:
Fear&Greed: {fg_str or 'alınamadı'} | {gs_str}

MANŞETLER:
{chr(10).join(all_headlines[:25]) or '[Google Search]'}

HEDEFLER: {' | '.join(USER['strategic_goals'][:4])}

GÖREV: Herkesin kabul ettiği YANLIŞ bir inancı tespit et. Veri destekli kontrarian argüman sun.

ÇIKTI FORMATI — Telegram HTML:
<b>🔄 KONTRA-SENTİMENT İSTİHBARATI</b>
<b>📍 [Konsensus İnanç: Max 8 kelime]</b>

<b>Konsensus:</b>
[herkesin inandığı]

<b>Karşı Kanıt:</b>
[ters işaret eden spesifik veri]

<b>Neden Yanılıyorlar:</b>
[mekanizma]

<b>2. Derece Etki:</b>
[konsensus çöktüğünde ne olur]

<b>Risk Senaryosu:</b>
<i>[kontrarian yanılma koşulları]</i>

<b>Yiğit İçin:</b>
[hangi kararı veya pozisyonu etkiler]

<b>🎯 Conviction:</b> [Düşük/Orta/Yüksek] — [tek cümle neden]
"""
        return await self._gemini_call(prompt)


class WeakSignalAggregatorAgent(AgentBase):
    def __init__(self):
        super().__init__("WeakSignalAggregatorAgent",
                         config.AGENT_TEMPERATURES["weak_signal"],
                         config.AGENT_MAX_TOKENS["weak_signal"])

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        sci = filter_intel_by_tags(ctx.bundle.intel, ["arxiv", "biorxiv", "nature"], 8)
        tech = filter_intel_by_tags(ctx.bundle.intel, ["techcrunch", "arstechnica", "verge", "singularity", "futurism"], 8)
        fin = filter_intel_by_tags(ctx.bundle.intel, ["coindesk", "theblock", "decrypt", "cointelegraph"], 6)
        dev = [f"{d['name']}({d.get('stars_today','?')}★): {d['desc']}" for d in ctx.bundle.dev_velocity[:8]]
        hn = [f"[{h['score']}pts] {h['title']}" for h in ctx.bundle.hn_signal[:6]]
        domain_context = self._domain_topics_str(v["domain_focus"], 3)

        prompt = f"""
SEN: Zayıf Sinyal Uzmanısın. 3+ alandan aynı yönü gösteren sinyalleri birleştirirsin.
KULLANICI: {USER['name']} | ARAMA MODU: {v['search_mode']} | DOMAIN: {', '.join(v['domain_focus'])}
KAÇINILACAKLAR: {self._avoid_str(ctx.avoid_concepts)}

DOMAIN KONULARI:
{domain_context}

[Bilim]: {chr(10).join(sci) or '—'}
[Teknoloji]: {chr(10).join(tech) or '—'}
[Finans/Kripto]: {chr(10).join(fin) or '—'}
[GitHub]: {chr(10).join(dev) or '—'}
[HackerNews]: {chr(10).join(hn) or '—'}

GÖREV: 3+ FARKLI alandan gelen AYNI YÖNÜ işaret eden sinyalleri birleştir.
Sadece bugün niche'de olan, 6-18 ay içinde mainstream olacak örüntüyü bul.

ÇIKTI FORMATI — Telegram HTML:
<b>🔮 ZAYIF SİNYAL KONVERJANS</b>
<b>📍 [Örüntü adı: Max 10 kelime]</b>

<b>Güç:</b> [Zayıf/Orta/Güçlü] | <b>Ufuk:</b> [X ay/yıl] | <b>Güven:</b> [%X]

<b>Alan 1 — [isim]:</b> [sinyal]
<b>Alan 2 — [isim]:</b> [sinyal]
<b>Alan 3 — [isim]:</b> [sinyal]

<b>Konverjans Anlamı:</b>
[3 ayrı sinyalin aynı şeyi söylemesi ne anlama geliyor]

<b>Paradigma Kırılması:</b>
[mevcut durumdan nasıl sapıyor]

<b>Nexa Fırsatı:</b>
[Yiğit'in hangi projesine nasıl entegre edilir]

<b>Erken Pozisyon:</b>
[mainstream fark etmeden şimdi ne yapılmalı]
"""
        return await self._gemini_call(prompt)


class CognitiveEdgeAgent(AgentBase):
    def __init__(self):
        super().__init__("CognitiveEdgeAgent",
                         config.AGENT_TEMPERATURES["cognitive_edge"],
                         config.AGENT_MAX_TOKENS["cognitive_edge"])

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        bio_signals = filter_intel_by_tags(ctx.bundle.intel, ["arxiv_neuro", "arxiv_bio", "biorxiv", "nature", "longevity"], 8)
        cognitive_domain = USER["knowledge_domains"]["Cognitive_Enhancement"]["topics"]
        longevity_domain = USER["knowledge_domains"]["Longevity_Biotech"]["topics"]

        prompt = f"""
SEN: Nörobilim ve Bilişsel Optimizasyon Uzmanısın. Ampirik kanıta dayalı, mekanistik düşünürsün.
KULLANICI: {USER['name']}, {USER['age']}Y | Yüksek kognitif yük: kod, strateji, içerik üretimi
GÜN: {v['weekday']} | ÇERÇEVE: {v['cognitive_frame']}

BİLİŞSEL GELİŞTİRME ALANLARI:
{chr(10).join(f'• {t}' for t in cognitive_domain[:6])}

LONGEVİTY ALANLARI:
{chr(10).join(f'• {t}' for t in longevity_domain[:4])}

CANLI BİYO SİNYALLERİ:
{chr(10).join(bio_signals) or '[PubMed/bioRxiv son 7 gün: cognitive enhancement, neuroplasticity, longevity]'}

KAÇINILACAKLAR: {self._avoid_str(ctx.avoid_concepts)}

GÖREV: Son araştırmalara dayanan, AMAÇ ODAKLI bir bilişsel/longevity müdahalesi öner.
Spesifik mekanizmayı ve hedef nöral devreyi açıkla. KAYNAKLI olmalı.

ÇIKTI FORMATI — Telegram HTML:
<b>🧬 BİLİŞSEL KENAR PROTOKOLÜ</b>
<b>📍 [Protokol adı — spesifik, amaç odaklı]</b>

<b>Hedef Devre:</b> [nöral sistem] | <b>Etki Süresi:</b> [X] | <b>Kanıt:</b> [kalite]

<b>Mekanizma:</b>
[reseptör + sinyal yolu + biyolojik sonuç]

<b>Uygulama Protokolü:</b>
[yöntem, zamanlama, bağlam]

<b>Zirve Penceresi:</b>
<i>[başlangıç → zirve → bitiş]</i>

<b>Sinerjiler:</b>
[diğer müdahalelerle kombinasyon]

<b>Kontrendikasyonlar:</b>
[uyarılar]

<b>Yiğit'in Hedefine Bağlantı:</b>
[kod yazma / strateji / içerik üretimine katkı]

<b>Kaynak:</b> <code>[PMID / arXiv / DOI]</code>
"""
        return await self._gemini_call(prompt)


class SystemsBreakdownAgent(AgentBase):
    def __init__(self):
        super().__init__("SystemsBreakdownAgent",
                         config.AGENT_TEMPERATURES["systems_breakdown"],
                         config.AGENT_MAX_TOKENS["systems_breakdown"])

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        signals = [i.title for i in ctx.bundle.intel[:22]]
        dev = [f"{d['name']}({d.get('stars_today','?')}★): {d['desc']}" for d in ctx.bundle.dev_velocity[:10]]

        prompt = f"""
SEN: Sistem Dönüşümü Analistinin. Çözülen eski sistemleri ve yükselen yeni sistemleri görürsün.
KULLANICI: {USER['name']} | PROJELER: {' | '.join(USER['active_projects'][:4])}
ARAMA MODU: {v['search_mode']} | ALAN: {', '.join(v['domain_focus'])}
KAÇINILACAKLAR: {self._avoid_str(ctx.avoid_concepts)}

SİNYALLER:
{chr(10).join(signals) or '[Google Search]'}

GELİŞTİRİCİ VELOCİTY:
{chr(10).join(dev) or '—'}

GÖREV: Aktif çözülme sürecindeki BİR sistemi tespit et. First-mover fırsatı nerede?
PropTech × AI × kripto kesişimine öncelik ver.

ÇIKTI FORMATI — Telegram HTML:
<b>🌀 SİSTEM ÇÖZÜLME SİNYALİ</b>
<b>📍 [Dönüşen sistem: isim + sektör]</b>

<b>Eski Sistem (Çözülen):</b>
[neden çözülüyor]

<b>Yeni Sistem (Yükselen):</b>
[ne değiştiriyor]

<b>Dönüşüm Hızı:</b> [Yavaş/Orta/Hızlı] — [gösterge]

<b>Açılan Boşluk:</b>
[şu an kim dolduruyor, kim doldurabilir]

<b>Nexa Fırsatı:</b>
[Yiğit'e spesifik öneri]

<b>Tehlike Radari:</b>
[mevcut Nexa projelerini tehdit ediyor mu]

<b>First-Mover Penceresi:</b>
[ne kadar vakti var]
"""
        return await self._gemini_call(prompt)


class NarrativeVelocityAgent(AgentBase):
    def __init__(self):
        super().__init__("NarrativeVelocityAgent",
                         config.AGENT_TEMPERATURES["narrative_velocity"],
                         config.AGENT_MAX_TOKENS["narrative_velocity"])

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        hn = [f"[{h['score']}pts, {h['comments']} yorum] {h['title']}" for h in ctx.bundle.hn_signal[:8]]
        dev = [f"{d['name']}({d.get('stars_today','?')}★ bugün): {d['desc']}" for d in ctx.bundle.dev_velocity[:8]]
        frontier = filter_intel_by_tags(ctx.bundle.intel, ["singularity", "futurism", "longevity", "biorxiv"], 8)

        prompt = f"""
SEN: Niche-to-Mainstream Analistinin. Niche'de ivme kazanan ama henüz büyük kitleye ulaşmamış fikirleri yakalarsın.
KULLANICI: {USER['name']} | ARAMA MODU: {v['search_mode']} | ÇERÇEVE: {v['cognitive_frame']}
KAÇINILACAKLAR: {self._avoid_str(ctx.avoid_concepts)}

HackerNews: {chr(10).join(hn) or '—'}
GitHub Dev Velocity: {chr(10).join(dev) or '—'}
Frontier Sinyalleri: {chr(10).join(frontier) or '—'}

AKTİF PROJELER: {' | '.join(USER['active_projects'][:4])}

GÖREV: Sadece niche'de tartışılan, 6-18 ay içinde mainstream'e ulaşacak TEK fikir/teknoloji bul.

ÇIKTI FORMATI — Telegram HTML:
<b>🚀 NARATİF VELOCİTY TARAMASI</b>
<b>📍 [Fikir/Teknoloji adı]</b>

<b>Kategori:</b> [AI/Biotech/Kripto/Diğer] | <b>Olgunluk:</b> [aşama] | <b>Mainstream'e:</b> ~[X ay]

<b>Bu Nedir:</b>
[özlü teknik açıklama]

<b>Neden Şimdi Hızlanıyor:</b>
[spesifik göstergeler]

<b>Katalizör:</b>
[ne ile patlar]

<b>Nexa Entegrasyonu:</b>
[hangi projeye nasıl giriyor]

<b>İlk Adım:</b>
[öğren / dene / pozisyon al]

<b>Kaynaklar:</b>
<code>[GitHub / arXiv / topluluk linki]</code>
"""
        return await self._gemini_call(prompt)


class DeepScienceAgent(AgentBase):
    def __init__(self):
        super().__init__("DeepScienceAgent",
                         config.AGENT_TEMPERATURES["deep_science"],
                         config.AGENT_MAX_TOKENS["deep_science"])

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        sci_papers = [
            f"[{i.tag.replace('arxiv_','').replace('biorxiv','bio')}] {i.title} — {i.desc[:120]}"
            for i in ctx.bundle.intel
            if i.tag.startswith("arxiv") or i.tag in ("biorxiv", "nature", "longevity")
        ]
        domain_context = self._domain_topics_str(
            ["Longevity_Biotech", "Cognitive_Enhancement", "AI_Systems_Architecture", "Quantum_Advanced_Computing"], 3)

        prompt = f"""
SEN: Derin Bilim İstihbarat Analistinin. Henüz mainstream radara girmemiş bilimsel atılımları tespit edersin.
KULLANICI: {USER['name']} | Öncelik: longevity > nörobilim > CRISPR > AI mimari > kuantum
ÇERÇEVE: {v['cognitive_frame']} | UFUK: {v['temporal_lens']}
KAÇINILACAKLAR: {self._avoid_str(ctx.avoid_concepts)}

BİLİM ALAN KONULARI:
{domain_context}

PREPRINT/PAPER SİNYALLERİ:
{chr(10).join(sci_papers[:20]) or '[Google Scholar: son 7 gün longevity neuroscience AI breakthrough CRISPR]'}

GÖREV: Mevcut paradigmayı kıracak TEK bilimsel gelişmeyi seç. Şüphe payını dürüstçe değerlendir.

ÇIKTI FORMATI — Telegram HTML:
<b>🔬 DERİN BİLİM ATILIMI</b>
<b>📍 [Keşfin başlığı]</b>

<b>Alan:</b> [disiplin] | <b>Olgunluk:</b> [Preprint/Published/Replicated] | <b>Etki Ufku:</b> [X yıl]

<b>Ne Bulundu:</b>
[özet — mekanizma dahil]

<b>Eski Paradigma:</b>
[bugüne kadar ne biliniyordu]

<b>Paradigma Kırılması:</b>
[neyi değiştiriyor]

<b>Pratik Uygulama:</b>
[ne zaman gerçek hayata geçer]

<b>Yiğit'in Hedeflerine Bağlantı:</b>
[longevity / bilişsel / AI / PropTech ile kesişim]

<b>Şüphe Payı:</b>
<i>[yanıltıcı olabilecek faktörler]</i>

<b>Kaynak:</b> <code>[arXiv / DOI / PMID]</code>
"""
        return await self._gemini_call(prompt)


class PropTechOSINTAgent(AgentBase):
    def __init__(self):
        super().__init__("PropTechOSINTAgent",
                         config.AGENT_TEMPERATURES["proptech_osint"],
                         config.AGENT_MAX_TOKENS["proptech_osint"])

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        fin_signals = filter_intel_by_tags(ctx.bundle.intel, ["coindesk", "theblock", "decrypt", "cointelegraph", "hbr"], 8)
        tech_signals = filter_intel_by_tags(ctx.bundle.intel, ["techcrunch", "arstechnica", "verge"], 6)
        dev = [f"{d['name']}({d.get('stars_today','?')}★): {d['desc']}" for d in ctx.bundle.dev_velocity[:6]]
        proptech_topics = USER["knowledge_domains"]["PropTech_Business"]["topics"]
        crypto_topics = USER["knowledge_domains"]["Crypto_DeFi"]["topics"][:4]

        prompt = f"""
SEN: PropTech × AI × Kripto İstihbarat Uzmanısın.
KULLANICI: {USER['name']} | Türkiye PropTech'de tek kategori: PropTech × AI Security × Solopreneurship
ÇERÇEVE: {v['cognitive_frame']} | ARAMA MODU: {v['search_mode']}
KAÇINILACAKLAR: {self._avoid_str(ctx.avoid_concepts)}

PROPTECH ALANLARI:
{chr(10).join(f'• {t}' for t in proptech_topics[:5])}

KRİPTO/RWA ALANLARI:
{chr(10).join(f'• {t}' for t in crypto_topics)}

FİNANS SİNYALLERİ:
{chr(10).join(fin_signals) or '[Google Search: PropTech AI CRM SaaS 2025-2026]'}

TEKNOLOJİ SİNYALLERİ:
{chr(10).join(tech_signals) or '—'}

AKTİF PROJELER: {' | '.join(USER['active_projects'][:5])}
HEDEF: İlk SaaS müşteri — CB Dikmen danışmanı | 2026 Prio 1

GÖREV: PropTech pozisyonunu güçlendirecek ÖZEL bir sinyal bul.
Rakiplerin görmediği ama Playwright+AI stack'iyle exploit edebilecek boşluk.

ÇIKTI FORMATI — Telegram HTML:
<b>🏢 PROPTECH OSINT İSTİHBARATI</b>
<b>📍 [Fırsat/Sinyal başlığı]</b>

<b>Kategori:</b> [CRM/Pazarlama/RWA/AI-Emlak/Diğer] | <b>Pazar:</b> [Türkiye/Global] | <b>Aciliyet:</b> [X/10]

<b>Sinyal:</b>
[ne oldu/değişti/çıktı]

<b>Türkiye Bağlantısı:</b>
[Türkiye gayrimenkul piyasasına etkisi]

<b>Rakip Kör Noktası:</b>
[standart danışmanların göremediği]

<b>Nexa Stack Avantajı:</b>
[Playwright OSINT + Gemini CRM + WA bot nasıl exploit eder]

<b>CB VIP / SaaS Önceliği:</b>
[Nexa CRM'e somut nasıl eklenir]

<b>Aksiyon:</b>
[ilk somut adım]
"""
        return await self._gemini_call(prompt)


class StrategicWeaponAgent(AgentBase):
    def __init__(self):
        super().__init__("StrategicWeaponAgent",
                         config.AGENT_TEMPERATURES["strategic_weapon"],
                         config.AGENT_MAX_TOKENS["strategic_weapon"],
                         use_search=False)

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        insight_summary = "\n\n".join(
            f"[{k.upper()}]:\n{re.sub(r'<[^>]+>', ' ', v_str).strip()[:250]}"
            for k, v_str in ctx.insights.items()
            if v_str and len(v_str) > 50
        )

        prompt = f"""
SEN: Stratejik Silah. Bugünün TÜM istihbaratını sentezler, en yüksek kaldıraçlı hareketi belirlersin.
KULLANICI: {USER['name']}, {USER['age']}Y
ROL: {USER['role']}
BİLİŞSEL ÇERÇEVE: {USER['cognitive_profile']['lens_stack']}
KİMLİK SÜTUNLARI: {' | '.join(USER['identity_pillars'])}

BUGÜN: {ctx.date_str} {ctx.time_str} — {v['weekday']} — Gün {v['day_of_year']}/365 ({v['days_left_year']} gün kaldı)
ÇERÇEVE: {v['cognitive_frame']} | LENS: {v['temporal_lens']}

STRATEJİK HEDEFLER:
{self._goals_str()}

AKTİF PROJELER:
{self._projects_str()}

AJANLARDAN BUGÜNÜN BULGULARI:
{insight_summary or '[henüz yok]'}

MUTLAK YASAKLAR:
- "İyi sabahlar" / "Başarılar" / "Güzel günler" gibi klişe cümleler
- Jenerik motivasyon konuşması
- Yüzeysel öneriler
Son cümle MUTLAKA emir kipi olacak.

GÖREV: Bugünün tüm istihbaratını sentezle. EN YÜKSEK kaldıraçlı TEK eylemi belirle.
14 yıllık rekabetçi yüzücünün disiplini + INTJ sistem mimarisini çağır.
Sun Tzu: Rakip körken konuşlan. Taleb: Pozitif asimetri kur. Feynman: Varsayımı kır.

ÇIKTI FORMATI — Telegram HTML:
<b>🗡️ STRATEJİK SİLAH</b>

<blockquote>[3-4 satır manifesto — Sun Tzu/Taleb/Feynman ruhunda, bugünün bulgularına özgü]</blockquote>

<b>Bugünün Savaşı:</b>
[ölçülebilir tek hedef]

<b>İçsel Düşman:</b>
[bugün yenilecek psikolojik/operasyonel engel]

<b>Kaldıraç Noktası:</b>
[bugün yapılabilecek en yüksek asimetrik kaldıraçlı tek eylem]

<b>Sinerjik Hareket:</b>
[bu eylem aynı anda hangi 2 hedefi birden ilerletiyor]

<b>23:59 Zafer Kriteri:</b>
<b>[bu gerçekleştiyse günü kazandın: net ve ölçülebilir çıktı]</b>

<b>▶ [SON KOMUT — emir kipi, tek cümle, sadece Yiğit için]</b>
"""
        return await self._gemini_call(prompt)


class QualityEvaluator(AgentBase):
    def __init__(self):
        super().__init__("QualityEvaluator",
                         config.AGENT_TEMPERATURES["quality_evaluator"],
                         config.AGENT_MAX_TOKENS["quality_evaluator"],
                         use_search=False)

    async def run(self, ctx: AgentContext) -> str:
        return ""

    async def evaluate(self, report_text: str) -> dict:
        clean = re.sub(r"<[^>]+>", " ", report_text)
        clean = re.sub(r"\s+", " ", clean)[:5000]

        prompt = f"""
Kullanıcı: {USER['name']}, {USER['age']}Y
Hedefler: {' | '.join(USER['strategic_goals'][:4])}

Raporu 6 kriterde puanla (1.0-10.0):
- novelty: Yeni bilgi mi?
- specificity: Veri destekli ve spesifik mi?
- actionability: Somut aksiyon var mı?
- depth: 2. ve 3. derece çıkarım var mı?
- diversity: Farklı domain'ler kapsandı mı?
- personalization: Yiğit'e özgü mü?

RAPOR:
{clean}

SADECE geçerli JSON döndür:
{{"scores":{{"novelty":X.X,"specificity":X.X,"actionability":X.X,"depth":X.X,"diversity":X.X,"personalization":X.X}},"average":X.X,"weakest":"alan","strongest":"alan","should_send":true}}
"""
        try:
            raw = await self._gemini_call(prompt)
            raw = re.sub(r"```json|```", "", raw).strip()
            return json.loads(raw)
        except Exception:
            return {"average": 7.5, "should_send": True, "weakest": "unknown", "strongest": "unknown", "scores": {}}


AGENT_DEFINITIONS = [
    {"key": "temporal",     "class": TemporalArbitrageAgent,   "label": "⏱️  Temporal Arbitraj"},
    {"key": "contra",       "class": ContraSentimentAgent,     "label": "🔄  Kontra-Sentiment"},
    {"key": "weak_signal",  "class": WeakSignalAggregatorAgent,"label": "🔮  Zayıf Sinyal"},
    {"key": "cognitive",    "class": CognitiveEdgeAgent,       "label": "🧬  Bilişsel Kenar"},
    {"key": "systems",      "class": SystemsBreakdownAgent,    "label": "🌀  Sistem Çözülme"},
    {"key": "narrative",    "class": NarrativeVelocityAgent,   "label": "🚀  Narratif Velocity"},
    {"key": "deep_science", "class": DeepScienceAgent,         "label": "🔬  Derin Bilim"},
    {"key": "proptech",     "class": PropTechOSINTAgent,       "label": "🏢  PropTech OSINT"},
]


# ═════════════════════════════════════════════════════════════════════════════
# ⑧ MANUEL KOMUT AJANLARI (6 Yeni Ajan)
# ═════════════════════════════════════════════════════════════════════════════

class DeepResearchAgent(AgentBase):
    """
    /research <konu> komutu için.
    Herhangi bir konuyu Yiğit'in context'iyle ilişkilendirerek derin araştırır.
    """
    def __init__(self):
        super().__init__("DeepResearchAgent",
                         config.AGENT_TEMPERATURES["deep_research"],
                         config.AGENT_MAX_TOKENS["deep_research"],
                         use_search=True)

    async def research(self, topic: str, ctx: AgentContext) -> str:
        all_domains = list(USER["knowledge_domains"].keys())
        all_topics_str = self._domain_topics_str(all_domains, 3)

        prompt = f"""
SEN: Yiğit Narin'in kişisel deep research ajanısın. Verilen konuyu onun lens stack'iyle derinlemesine araştırırsın.
KULLANICI: {USER['name']}, {USER['age']}Y | {USER['role']}
LENS STACK: {USER['cognitive_profile']['lens_stack']}
TARİH: {ctx.date_str} {ctx.time_str}

ARAŞTIRILACAK KONU: "{topic}"

KULLANICININ TÜM ALANLARI:
{all_topics_str}

AKTİF PROJELER:
{self._projects_str()}

STRATEJİK HEDEFLER:
{self._goals_str()}

ARAŞTIRMA KURALLARI:
1. Google Search ile en güncel, en güvenilir kaynakları tara.
2. Konuyu Yiğit'in 7 domain'inden hangisiyle kesiştiğini belirle.
3. Mevcut projelerine nasıl kaldıraç yarattığını göster.
4. 2. ve 3. derece çıkarımlar ZORUNLU.
5. Kaynak kalitesini değerlendir (preprint vs peer-reviewed vs blog).
6. Jenerik bilgi değil, Yiğit'in özel pozisyonuna özgü içgörü üret.
7. Sun Tzu/Taleb/Feynman çerçevesini uygula.

ÇIKTI FORMATI — Telegram HTML:
<b>🔍 DEEP RESEARCH: {topic.upper()}</b>

<b>📌 Domain Kesişimi:</b> [hangi Yiğit domain'leri ile örtüşüyor]
<b>⚡ Önem Skoru:</b> [X/10] | <b>Aciliyet:</b> [Yüksek/Orta/Düşük]

━━━━━━━━━━━━━━━━━━━━

<b>🧠 Nedir / Ne Durumda:</b>
[Konunun güncel durumu — en son gelişmeler, spesifik verilerle]

<b>🔬 Derinlik Katmanı 1 — Mekanizma:</b>
[Nasıl çalışıyor? Teknik/bilimsel temel]

<b>📈 Derinlik Katmanı 2 — Piyasa/Ekosistem:</b>
[Kimler oynuyor, para nereye akıyor, hangi boşluk var]

<b>🌐 Derinlik Katmanı 3 — Türkiye Lens:</b>
[Türkiye özelinde durum, fırsat, risk]

━━━━━━━━━━━━━━━━━━━━

<b>🔮 2. Derece Etki:</b>
[Bu konu 6-18 ayda neleri değiştirecek]

<b>💥 3. Derece Etki:</b>
[Sistemik domino — 2-5 yıl çerçevesi]

<b>🎯 Yiğit İçin Asimetrik Fırsat:</b>
[Playwright + Gemini + AI stack'iyle nasıl exploit edilir]

<b>🚧 Karşı Argüman (Steelman):</b>
<i>[Bu konunun neden hayal kırıklığı yaratabilecek en güçlü argümanı]</i>

<b>⚡ İlk 3 Aksiyon:</b>
1. [bugün yapılabilecek]
2. [bu hafta]
3. [bu ay]

<b>📚 Kaynaklar:</b>
<code>[En değerli 3 kaynak: başlık + link]</code>
"""
        return await self._gemini_call(prompt)

    async def run(self, ctx: AgentContext) -> str:
        return await self.research("genel araştırma", ctx)


class LongevityProtocolAgent(AgentBase):
    """
    /longevity komutu için.
    Güncel longevity + bilişsel optimizasyon protokolü üretir.
    """
    def __init__(self):
        super().__init__("LongevityProtocolAgent",
                         config.AGENT_TEMPERATURES["longevity_protocol"],
                         config.AGENT_MAX_TOKENS["longevity_protocol"],
                         use_search=True)

    async def run(self, ctx: AgentContext) -> str:
        longevity_topics = USER["knowledge_domains"]["Longevity_Biotech"]["topics"]
        cognitive_topics = USER["knowledge_domains"]["Cognitive_Enhancement"]["topics"]

        prompt = f"""
SEN: Yiğit Narin'in kişisel Longevity + Bilişsel Optimizasyon araştırma ajanısın.
KULLANICI: {USER['name']}, {USER['age']}Y | Yüksek kognitif yük: kod + strateji + içerik
HEDEF: Maximum bilişsel output + uzun vadeli beyin sağlığı + yaşam uzatma

LONGEVİTY İLGİ ALANLARI:
{chr(10).join(f'• {t}' for t in longevity_topics)}

BİLİŞSEL OPTİMİZASYON ALANLARI:
{chr(10).join(f'• {t}' for t in cognitive_topics)}

TARİH: {ctx.date_str} | GÜN: {ctx.vector['weekday']}

GÖREV: Google Search ile son 30 günün en önemli longevity/bilişsel optimizasyon bulgusunu bul.
25 yaşında, yüksek performanslı, teknoloji girişimcisi için özelleştirilmiş protokol üret.
KANIT BAZLI ol. Her önerinin mekanizmasını açıkla.

ÇIKTI FORMATI — Telegram HTML:
<b>🧬 LONGEVİTY + BİLİŞSEL OPTİMİZASYON PROTOKOLÜ</b>
<b>📅 {ctx.date_str}</b>

━━━━━━━━━━━━━━━━━━━━

<b>🔬 BU HAFTANİN EN ÖNEMLİ BULGUSU:</b>
<b>Başlık:</b> [spesifik çalışma/keşif başlığı]
<b>Kaynak:</b> <code>[PMID/DOI/arXiv]</code>
<b>Özet:</b> [ne bulundu, mekanizma dahil]

━━━━━━━━━━━━━━━━━━━━

<b>💊 AKTİF STACK ANALİZİ (Yiğit için):</b>

<b>1. Bilişsel Hız + Odak:</b>
[Mekanizma + Etki Penceresi + Kanıt Kalitesi]

<b>2. Nöroplastisite + Öğrenme:</b>
[Mekanizma + Zamanlama + Sinerji]

<b>3. Mitokondriyal Enerji:</b>
[Mekanizma + Performans Bağlantısı]

<b>4. Uyku Kalitesi + REM Optimizasyonu:</b>
[Protokol + Zamanlama]

━━━━━━━━━━━━━━━━━━━━

<b>⚠️ KONTRENDİKASYONLAR:</b>
<i>[Kombinasyon riskleri, bireysel varyasyon faktörleri]</i>

<b>📊 PROTOKOL TAKVİMİ:</b>
[Sabah / Öğle / Akşam / Uyku öncesi — zaman çizelgesi]

<b>🎯 YİĞİT'İN PROFİLİNE ÖZEL:</b>
[25Y + yüksek kognitif yük + sprint mentalitesi → optimize edilmiş kombinasyon]

<b>🔮 SONRAKİ 30 GÜNDE TAKİP EDİLECEKLER:</b>
[Yaklaşan klinik deneyler / preprint'ler / konferanslar]
"""
        return await self._gemini_call(prompt)


class AISecurityAgent(AgentBase):
    """
    /ai komutu için.
    AI sistemleri + güvenlik araştırması derinleştirir.
    """
    def __init__(self):
        super().__init__("AISecurityAgent",
                         config.AGENT_TEMPERATURES["ai_security"],
                         config.AGENT_MAX_TOKENS["ai_security"],
                         use_search=True)

    async def run(self, ctx: AgentContext) -> str:
        ai_topics = USER["knowledge_domains"]["AI_Systems_Architecture"]["topics"]
        sci_signals = filter_intel_by_tags(ctx.bundle.intel, ["arxiv_ai", "arxiv_ml", "arxiv_cv"], 10)
        dev = [f"{d['name']}({d.get('stars_today','?')}★): {d['desc']}" for d in ctx.bundle.dev_velocity[:8]]

        prompt = f"""
SEN: Yiğit Narin'in AI Sistemleri + Güvenlik araştırma ajanısın.
KULLANICI: {USER['name']} | Adversarial AI Araştırmacısı + LLM Güvenlik odağı
HEDEF: MITRE ATLAS + OWASP LLM Top 10 sertifikasyon hazırlığı + Nexa AI entegrasyonu

AI SİSTEMLERİ İLGİ ALANLARI:
{chr(10).join(f'• {t}' for t in ai_topics)}

CANLI arXiv SİNYALLERİ:
{chr(10).join(sci_signals) or '[Google Scholar: AI security LLM jailbreak agentic AI 2025]'}

GELİŞTİRİCİ VELOCİTY:
{chr(10).join(dev) or '—'}

TARİH: {ctx.date_str}

GÖREV: Google Search ile son 7 günün en önemli AI güvenlik + LLM mimari bulgusunu bul.
Adversarial prompting, agentic AI güvenliği, Constitutional AI, yeni saldırı vektörleri öncelikli.
Yiğit'in Dr. Nexus / RED-OP / OMNI-PROCESSOR araştırma çerçevesiyle ilişkilendir.

ÇIKTI FORMATI — Telegram HTML:
<b>🤖 AI SİSTEMLERİ + GÜVENLİK İSTİHBARATI</b>
<b>📅 {ctx.date_str}</b>

━━━━━━━━━━━━━━━━━━━━

<b>🚨 HAFTA'NIN KRİTİK GELİŞMESİ:</b>
[başlık + kaynak + özet]

━━━━━━━━━━━━━━━━━━━━

<b>🔴 YENİ SALDIRI VEKTÖRLERİ / GÜVENLIK AÇIKLARI:</b>
[Son tespit edilen LLM güvenlik açıkları — spesifik, teknik]

<b>🛡️ SAVUNMA MİMARİSİ GELİŞMELERİ:</b>
[Constitutional AI / RLHF / guardrail güncellemeleri]

<b>⚙️ AJAN MİMARİSİ GELİŞMELERİ:</b>
[Multi-agent, tool use, reasoning modeli güncellemeleri]

━━━━━━━━━━━━━━━━━━━━

<b>🎯 OWASP LLM Top 10 GÜNCEL DURUM:</b>
[Bu haftaki gelişme hangi riski aktive ediyor/güncelliyor]

<b>🗡️ ADVERSARİAL ARAŞTIRMA NOTU:</b>
[Yiğit'in Dr. Nexus / RED-OP çerçevesine uygun savunma perspektifi]

<b>🔧 NEXA CRM / OSINT STACK ETKİSİ:</b>
[Bu güvenlik gelişmesi Yiğit'in Gemini/LLM entegrasyonunu nasıl etkiliyor]

<b>📚 SERTİFİKASYON RADAR:</b>
[MITRE ATLAS / OWASP ilerleme notları]

<b>⚡ Bu Hafta Yapılacak:</b>
1. [teknik aksiyon]
2. [araştırma]
3. [entegrasyon]
"""
        return await self._gemini_call(prompt)


class CryptoAlphaAgent(AgentBase):
    """
    /crypto komutu için.
    Kripto/DeFi derin analiz + on-chain alpha üretir.
    """
    def __init__(self):
        super().__init__("CryptoAlphaAgent",
                         config.AGENT_TEMPERATURES["crypto_alpha"],
                         config.AGENT_MAX_TOKENS["crypto_alpha"],
                         use_search=True)

    async def run(self, ctx: AgentContext) -> str:
        crypto_topics = USER["knowledge_domains"]["Crypto_DeFi"]["topics"]
        fin_signals = filter_intel_by_tags(ctx.bundle.intel, ["coindesk", "theblock", "decrypt", "cointelegraph"], 10)
        fg = ctx.bundle.market.get("fear_greed", [{}])
        gs = ctx.bundle.market.get("global_stats", {})
        prices = ctx.bundle.market.get("prices", {})
        trending = ctx.bundle.market.get("trending", [])

        fg_str = f"{fg[0].get('value_classification','?')} ({fg[0].get('value','?')})" if fg else "?"
        gs_str = f"BTC Dom: {gs.get('btc_dominance','?')}% | 24h: {gs.get('market_cap_change_24h','?')}%" if gs else ""
        trend_str = ", ".join(f"{t['name']}({t['symbol']})" for t in trending[:5])

        # Fiyat özeti
        price_lines = []
        for coin, data in list(prices.items())[:8]:
            p = data.get("usd", 0)
            c24 = data.get("usd_24h_change", 0) or 0
            c7 = data.get("usd_7d_change", 0) or 0
            sym = coin.split("-")[0].upper()
            p_str = f"${p:,.0f}" if p > 100 else f"${p:.4f}"
            price_lines.append(f"{sym}: {p_str} ({c24:+.1f}% 24h, {c7:+.1f}% 7d)")

        prompt = f"""
SEN: Yiğit Narin'in Kripto/DeFi Alpha araştırma ajanısın.
KULLANICI: {USER['name']} | APEX TRADE projesi + RWA × PropTech kesişim araştırması
HEDEF: On-chain alpha + Asimetrik fırsat + APEX TRADE için veri

KRİPTO/DeFi İLGİ ALANLARI:
{chr(10).join(f'• {t}' for t in crypto_topics)}

CANLI PİYASA:
Fear&Greed: {fg_str}
{gs_str}
Trending: {trend_str}

FİYATLAR:
{chr(10).join(price_lines) or '—'}

HABERLER:
{chr(10).join(fin_signals) or '[Google Search: crypto DeFi on-chain alpha 2025]'}

TARİH: {ctx.date_str}

GÖREV: Google Search ile bugünün en önemli kripto alpha fırsatını bul.
Smart money hareketleri, on-chain anomaliler, regulatory sinyaller, RWA PropTech kesişim.
APEX TRADE için stratejik veri üret.

ÇIKTI FORMATI — Telegram HTML:
<b>₿ KRİPTO/DeFi ALPHA İSTİHBARATI</b>
<b>📅 {ctx.date_str}</b>

━━━━━━━━━━━━━━━━━━━━

<b>📊 PİYASA NABI:</b>
F&G: <b>{fg_str}</b> | {gs_str}

━━━━━━━━━━━━━━━━━━━━

<b>🔥 BUGÜNÜN EN YÜKSEK CONVICTION FIRKATI:</b>
[Neden şimdi, hangi varlık/protokol, hangi katalizör]

<b>🐋 SMART MONEY SİNYALİ:</b>
[Whale hareketleri, büyük cüzdan girişleri, VC pozisyonlama]

<b>⛓️ ON-CHAIN ANOMALİ:</b>
[Olağandışı işlem paterni, DEX hacmi, open interest]

━━━━━━━━━━━━━━━━━━━━

<b>🏢 RWA × PropTech RADAR:</b>
[Gayrimenkul tokenizasyonu gelişmeleri — Yiğit'in kesişim noktası]

<b>⚖️ REGÜLATİF SİNYAL:</b>
[Yaklaşan düzenleme/ban/onay — piyasaya etkisi]

<b>🚨 APEX TRADE İÇİN:</b>
[Bu hafta izlenecek setup — net entry/exit mantığı]

<b>⚠️ Risk Senaryosu:</b>
<i>[Bu analizin yanlış çıkabileceği koşullar]</i>
"""
        return await self._gemini_call(prompt)


class IdeaValidatorAgent(AgentBase):
    """
    /idea <fikir> komutu için.
    Bir iş fikrini Yiğit'in tüm lens stack'iyle doğrular.
    """
    def __init__(self):
        super().__init__("IdeaValidatorAgent",
                         config.AGENT_TEMPERATURES["idea_validator"],
                         config.AGENT_MAX_TOKENS["idea_validator"],
                         use_search=True)

    async def validate(self, idea: str, ctx: AgentContext) -> str:
        prompt = f"""
SEN: Yiğit Narin'in kişisel İş Fikri Validasyon ajanısın.
KULLANICI: {USER['name']}, {USER['age']}Y | {USER['role']}
LENS STACK: {USER['cognitive_profile']['lens_stack']}
KİMLİK SÜTUNLARI: {' | '.join(USER['identity_pillars'])}

DOĞRULANACAK FİKİR: "{idea}"

AKTİF PROJELER:
{self._projects_str()}

STRATEJİK HEDEFLER:
{self._goals_str()}

NEXA STACK: Flask/Python + Firebase + Node.js (Baileys) + Vue.js + Playwright + Gemini API

GÖREVE: Google Search ile bu fikrin piyasa validasyonunu yap.
Yiğit'in mevcut stack'iyle build edilebilirliği, PropTech × AI Security × Solopreneurship üçgenine uyumu,
ve Türkiye piyasasındaki boşluk analizini çıkar.
INVERSION ZORUNLU: Neden başarısız olur?

ÇIKTI FORMATI — Telegram HTML:
<b>💡 FİKİR VALIDASYONU: {idea[:60]}</b>

━━━━━━━━━━━━━━━━━━━━

<b>📊 HIZLI KARAR SKORU:</b>
Piyasa Boşluğu: [X/10]
Build Edilebilirlik: [X/10]
Yiğit Uyumu: [X/10]
Türkiye Potansiyeli: [X/10]
<b>TOPLAM: [X/40] — [YAP/BEKLE/HAYIR]</b>

━━━━━━━━━━━━━━━━━━━━

<b>✅ STERLİNG ARGÜMANlar (Fikirle hemfikir olan en güçlü noktalar):</b>
1. [piyasa boşluğu kanıtı]
2. [Yiğit'in stack avantajı]
3. [timing faktörü]

<b>🔴 STEELman (En güçlü karşı argüman — dürüst):</b>
1. [neden başarısız olabilir — inversion]
2. [mevcut rakipler / alternatifler]
3. [Yiğit'in zayıf yanları bu fikir için]

━━━━━━━━━━━━━━━━━━━━

<b>💰 İŞ MODELİ ANALİZİ:</b>
Gelir Modeli: [nasıl para kazanılır]
İlk 3 Ay Hedef: [ölçülebilir]
Break-even: [ne zaman]
Büyüme Kaldıracı: [network effect / otomasyon / SaaS]

<b>🔧 NEXA STACK İLE BUILD:</b>
[Mevcut teknoloji stack'iyle MVP'yi nasıl inşa eder — spesifik]
MVP Süresi: [X hafta]

<b>🎯 TÜRK PROPTECH EKOSİSTEMİNE GİRİŞ:</b>
[Türkiye'deki ilk 3 potansiyel müşteri segmenti]

<b>⚡ SONUÇ — KARAR:</b>
[Evet ise: ilk 3 somut adım | Hayır ise: neden ve alternatif]
"""
        return await self._gemini_call(prompt)

    async def run(self, ctx: AgentContext) -> str:
        return await self.validate("genel fikir", ctx)


class OSINTProfilerAgent(AgentBase):
    """
    /osint <hedef> komutu için.
    Rekabet istihbaratı ve OSINT analizi üretir.
    """
    def __init__(self):
        super().__init__("OSINTProfilerAgent",
                         config.AGENT_TEMPERATURES["osint_profiler"],
                         config.AGENT_MAX_TOKENS["osint_profiler"],
                         use_search=True)

    async def profile(self, target: str, ctx: AgentContext) -> str:
        osint_topics = USER["knowledge_domains"]["Systems_Strategy_OSINT"]["topics"]
        proptech_topics = USER["knowledge_domains"]["PropTech_Business"]["topics"][:4]

        prompt = f"""
SEN: Yiğit Narin'in OSINT + Rekabet İstihbaratı ajanısın.
KULLANICI: {USER['name']} | Playwright OSINT pipeline mimarı | PropTech × AI Security araştırmacısı
LENS: Sun Tzu — Rakibin kör noktasına konuşlan.

OSINT ARAŞTIRMA HEDEFİ: "{target}"

OSINT METODOLOJİLERİ:
{chr(10).join(f'• {t}' for t in osint_topics[:5])}

PROPTECH BAĞLAM:
{chr(10).join(f'• {t}' for t in proptech_topics)}

AKTİF NEXA STACK:
• Playwright headless scraping
• PSI API + BeautifulSoup
• Gemini API analiz
• Telegram bot bildirim

TARİH: {ctx.date_str}

GÖREV: Google Search ile "{target}" konusunda OSINT araştırması yap.
Rakip analizi, piyasa konumlandırması, kör noktalar, Nexa'nın exploit edebileceği boşluklar.
SADECE açık kaynak, etik ve yasal yöntemler kullan.

ÇIKTI FORMATI — Telegram HTML:
<b>🕵️ OSINT İSTİHBARATI: {target[:50]}</b>
<b>📅 {ctx.date_str} | Sınıflandırma: NEXA GİZLİ</b>

━━━━━━━━━━━━━━━━━━━━

<b>📍 HEDEF PROFİLİ:</b>
[Temel bilgiler — açık kaynak]

<b>💪 GÜÇLÜ YANLARI:</b>
[Nerede güçlüler]

<b>🔍 KÖR NOKTALAR:</b>
[Nerede göremeiyorlar / eksik oldukları]

<b>📊 DİJİTAL AYAK İZİ:</b>
[Online presence, içerik stratejisi, teknik stack ipuçları]

━━━━━━━━━━━━━━━━━━━━

<b>⚔️ YİĞİT İÇİN STRATEJİK KONUM:</b>
[Sun Tzu: Rakip körken nereye konuşlan?]

<b>🎯 EXPLOIT EDİLEBİLECEK BOŞLUK:</b>
[Playwright + Gemini + AI stack ile nasıl avantaj alınır]

<b>⚡ AKSİYON PLANI:</b>
1. [Veri toplama — Playwright/PSI API]
2. [Analiz — Gemini API]
3. [Strateji — ne yapılacak]

<b>🚨 ETİK SINIR NOTU:</b>
<i>Tüm veriler açık kaynak. Kişisel veri ihlali yok.</i>
"""
        return await self._gemini_call(prompt)

    async def run(self, ctx: AgentContext) -> str:
        return await self.profile("Türkiye PropTech rakipleri", ctx)


# ═════════════════════════════════════════════════════════════════════════════
# ⑨ RAPOR MOTORU (Orchestrator)
# ═════════════════════════════════════════════════════════════════════════════
class IntelligenceEngine:
    def __init__(self, mem: MemoryEngine):
        self.memory = mem
        self.data_mesh = DataMesh()

    async def run(self, triggered_by: str = "schedule",
                  progress_callback: Callable | None = None) -> dict:
        now = datetime.now()
        date_str = now.strftime("%d %B %Y %A")
        time_str = now.strftime("%H:%M")

        def notify(msg: str):
            logger.info(msg)
            if progress_callback:
                progress_callback(msg)

        notify("🚀 Nexa Deep Intelligence v6.0 başlatıldı")

        vector = DiversityEngine.today_vector()
        avoid_concepts = await self.memory.recent_concepts()

        notify(f"📍 Vektör: {vector['cognitive_frame']} | {vector['search_mode']} | {'+'.join(vector['domain_focus'])}")

        notify("🌐 Veri toplama başlıyor...")
        bundle = await self.data_mesh.fetch_all()
        market_summary = bundle_summary(bundle)
        notify(f"📊 Veri hazır: {len(bundle.intel)} haber | {len(bundle.dev_velocity)} repo | {len(bundle.hn_signal)} HN")

        ctx = AgentContext(
            bundle=bundle,
            vector=vector,
            avoid_concepts=avoid_concepts,
            insights={},
            date_str=date_str,
            time_str=time_str,
        )

        semaphore = asyncio.Semaphore(config.AGENT_CONCURRENCY)
        sections = {}

        async def run_agent(defn: dict) -> tuple[str, str]:
            key = defn["key"]
            label = defn["label"]
            async with semaphore:
                notify(f"  ▶ {label} çalışıyor...")
                try:
                    agent = defn["class"]()
                    result = await agent.run(ctx)
                    await agent.close()
                    await self.memory.log_agent(key, len(result), success=True)
                    notify(f"  ✓ {label} — {len(result)} karakter")
                    return key, result
                except Exception as e:
                    err_msg = str(e)[:200]
                    await self.memory.log_agent(key, 0, success=False, error_msg=err_msg)
                    logger.error(f"  ✗ {label} FAILED: {err_msg}")
                    return key, f"<b>{label}</b>\n<i>Ajan geçici olarak kullanılamıyor.</i>"

        notify("🤖 8 ajan eş zamanlı başlatılıyor...")
        results = await asyncio.gather(*[run_agent(defn) for defn in AGENT_DEFINITIONS])

        for key, output in results:
            sections[key] = output
            ctx.insights[key] = output

        notify("  ▶ 🗡️ Stratejik Silah — sentez başlıyor...")
        try:
            strategic_agent = StrategicWeaponAgent()
            sections["strategy"] = await strategic_agent.run(ctx)
            await strategic_agent.close()
            await self.memory.log_agent("strategy", len(sections["strategy"]), success=True)
            notify(f"  ✓ Stratejik Silah — {len(sections['strategy'])} karakter")
        except Exception as e:
            logger.error(f"  ✗ Strategic Weapon FAILED: {e}")
            sections["strategy"] = "<b>🗡️ STRATEJİK SİLAH</b>\n<i>Geçici hata.</i>"

        notify("🔍 Kalite değerlendiriliyor...")
        all_text = "\n".join(sections.values())
        evaluator = QualityEvaluator()
        quality = await evaluator.evaluate(all_text)
        await evaluator.close()

        avg_q = float(quality.get("average", 7.5))
        await self.memory.log_quality(avg_q, agent="overall")
        notify(f"📈 Kalite: {avg_q:.1f}/10 | En zayıf: {quality.get('weakest','?')}")

        concepts = extract_concepts(all_text)
        ts = datetime.utcnow().isoformat()
        await self.memory.save_report(
            ts=ts, date_str=date_str, quality=avg_q, vector=dict(vector),
            concepts=concepts, domain_focus=vector["domain_focus"], triggered_by=triggered_by,
        )
        await self.memory.cleanup_old_data(keep_days=90)

        return {
            "sections": sections, "quality": quality, "vector": dict(vector),
            "market": bundle.market, "market_summary": market_summary,
            "date_str": date_str, "time_str": time_str, "ts": ts,
        }

    async def close(self):
        await self.data_mesh.close()


# ═════════════════════════════════════════════════════════════════════════════
# ⑩ RAPOR BUILDER (Telegram HTML Format)
# ═════════════════════════════════════════════════════════════════════════════
def tg_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def clean_agent_output(text: str) -> str:
    text = re.sub(r'\s*style="[^"]*"', "", text)
    text = re.sub(r"<h[23][^>]*>([\s\S]*?)</h[23]>", r"<b>\1</b>", text, flags=re.I)
    text = re.sub(r"<h[14][^>]*>([\s\S]*?)</h[14]>", r"<b>\1</b>", text, flags=re.I)
    text = re.sub(r"<span[^>]*>([\s\S]*?)</span>", r"\1", text, flags=re.I)
    text = re.sub(r"<p[^>]*>([\s\S]*?)</p>", r"\1\n", text, flags=re.I)
    text = re.sub(r"<[uo]l[^>]*>", "", text, flags=re.I)
    text = re.sub(r"</[uo]l>", "\n", text, flags=re.I)
    text = re.sub(r"<li[^>]*>([\s\S]*?)</li>", r"• \1\n", text, flags=re.I)
    text = re.sub(r"<table[^>]*>|</table>", "", text, flags=re.I)
    text = re.sub(r"<tr[^>]*>|</tr>", "\n", text, flags=re.I)
    text = re.sub(r"<t[dh][^>]*>([\s\S]*?)</t[dh]>", r"\1 | ", text, flags=re.I)
    text = re.sub(r"<hr[^>]*/?>", "\n" + "─" * 35 + "\n", text, flags=re.I)
    text = re.sub(r"<(?!b|/b|i|/i|u|/u|s|/s|code|/code|pre|/pre|a |/a|blockquote|/blockquote)[^>]+>", "", text, flags=re.I)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_message(text: str, max_len: int = None) -> list[str]:
    max_len = max_len or config.TELEGRAM_MAX_CHARS
    if len(text) <= max_len:
        return [text]
    parts = []
    while text:
        if len(text) <= max_len:
            parts.append(text)
            break
        cut = text[:max_len].rfind("\n")
        if cut < max_len // 2:
            cut = text[:max_len].rfind(" ")
        if cut <= 0:
            cut = max_len
        parts.append(text[:cut])
        text = text[cut:].lstrip()
    return parts


def build_header(date_str, time_str, quality, vector, avg_quality_10d) -> str:
    avg = float(quality.get("average", 7.5))
    q_label = "ELITE ⚡" if avg >= 8.5 else "SHARP" if avg >= 7.0 else "DILUTED"
    domain_str = " + ".join(vector.get("domain_focus", []))
    scores = quality.get("scores", {})
    scores_str = " | ".join(f"{k[:3].upper()}:{v:.1f}" for k, v in scores.items()) if scores else ""

    return f"""<b>⚡ NEXA DEEP INTELLIGENCE v6.0</b>
<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>

📅 {date_str}
🕐 {time_str} | 9 Ajan | Google Grounding

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
        lines.append(f"\nF&G: <b>{fg[0].get('value_classification','?')}</b> ({fg[0].get('value','?')})")
    if gs:
        lines.append(f"BTC Dom: {gs.get('btc_dominance','?')}% | 24h: {gs.get('market_cap_change_24h','?')}%")
    trending = market.get("trending", [])
    if trending:
        trend_names = ' · '.join(t['name'] for t in trending[:5])
        lines.append(f"Trending: {trend_names}")
    return "\n".join(lines)


def build_footer(vector: dict, ts: str) -> str:
    weekday_ctx = DiversityEngine.weekday_context(vector.get("weekday", ""))
    return f"""<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>
<i>{weekday_ctx}</i>

<code>NEXA HQ · v6.0 · {ts[:16]}Z</code>
<code>9-Ajan Pipeline · Google Grounding · SQLite Memory</code>"""


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
    messages = []
    messages.append(build_header(
        date_str=result["date_str"], time_str=result["time_str"],
        quality=result["quality"], vector=result["vector"],
        avg_quality_10d=avg_quality_10d,
    ))
    market_msg = build_market_ticker(result.get("market", {}))
    if market_msg:
        messages.append(market_msg)
    sections = result.get("sections", {})
    for key, label in SECTION_ORDER:
        content = sections.get(key, "")
        if not content or len(content) < 30:
            continue
        cleaned = clean_agent_output(content)
        if not cleaned.startswith("<b>"):
            cleaned = f"<b>{label}</b>\n\n{cleaned}"
        for part in split_message(cleaned):
            messages.append(part)
    messages.append(build_footer(
        vector=result["vector"],
        ts=result.get("ts", datetime.utcnow().isoformat()),
    ))
    return messages


def build_status_message(memory_summary: dict, vector: dict) -> str:
    last = memory_summary.get("last_report") or {}
    return f"""<b>⚡ NEXA SİSTEM DURUMU v6.0</b>

<b>📊 İstatistikler:</b>
Toplam Rapor: <code>{memory_summary.get('total_reports',0)}</code>
10 Günlük Ort. Kalite: <code>{memory_summary.get('avg_quality_10d','?')}/10</code>
Son 7 Günde Kavram: <code>{memory_summary.get('concepts_last_7d',0)}</code>

<b>📅 Son Rapor:</b>
Tarih: <code>{last.get('date_str','Hiç çalışmadı')}</code>
Kalite: <code>{last.get('quality','?')}</code>
Tetikleyen: <code>{last.get('triggered_by','?')}</code>

<b>🔭 Bugünün Vektörü:</b>
Domain: <code>{' + '.join(vector.get('domain_focus',[]))}</code>
Çerçeve: <code>{vector.get('cognitive_frame','?')}</code>

<b>⏰ Otomatik Çalışma:</b>
Her gün <code>{config.DAILY_HOUR:02d}:{config.DAILY_MINUTE:02d}</code> Türkiye saati (sabah 10:00)

<b>🤖 Komutlar:</b>
/report /quick /research /proptech /longevity /ai /crypto /idea /osint /status /memory /vector"""


def build_help_message() -> str:
    return f"""<b>⚡ NEXA DEEP INTELLIGENCE v6.0</b>
<b>Yiğit Narin için Kişisel İstihbarat Sistemi</b>

<b>📋 GÜNLÜK RAPOR:</b>
/report — Tam 9-ajan raporu (~3-5 dk)
/quick — Stratejik Silah özeti (hızlı)

<b>🔍 DEEP RESEARCH:</b>
/research &lt;konu&gt; — Herhangi konuda derin araştırma
/proptech — PropTech × Türkiye piyasa analizi
/longevity — Longevity + bilişsel optimizasyon
/ai — AI sistemleri + güvenlik araştırması
/crypto — Kripto/DeFi alpha analizi
/idea &lt;fikir&gt; — İş fikri validasyonu
/osint &lt;hedef&gt; — OSINT + rekabet analizi

<b>📊 SİSTEM:</b>
/status — Sistem durumu
/memory — Hafıza özeti
/vector — Bugünün vektörü
/help — Bu mesaj

<b>⏰ Otomatik:</b>
Her sabah <code>{config.DAILY_HOUR:02d}:{config.DAILY_MINUTE:02d}</code>'da tam rapor.

<b>9 Günlük Ajan + 6 Araştırma Ajanı</b>
PropTech · AI Security · Longevity · Kripto · OSINT"""


# ═════════════════════════════════════════════════════════════════════════════
# ⑪ TELEGRAM BOT
# ═════════════════════════════════════════════════════════════════════════════
def is_authorized(update: Update) -> bool:
    if not config.TELEGRAM_CHAT_ID:
        return True
    return str(update.effective_chat.id) == config.TELEGRAM_CHAT_ID


async def send_messages(update: Update, context: ContextTypes.DEFAULT_TYPE,
                        messages: list[str], parse_mode: str = ParseMode.HTML):
    chat_id = update.effective_chat.id
    for i, msg in enumerate(messages):
        if not msg.strip():
            continue
        try:
            await context.bot.send_message(
                chat_id=chat_id, text=msg, parse_mode=parse_mode,
                disable_web_page_preview=True,
            )
            if i < len(messages) - 1:
                await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Mesaj gönderme hatası: {e}")
            try:
                plain = re.sub(r"<[^>]+>", "", msg)
                await context.bot.send_message(chat_id=chat_id, text=plain[:4000],
                                               disable_web_page_preview=True)
            except Exception as e2:
                logger.error(f"Plain text de başarısız: {e2}")


async def send_typing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")


# ─── KOMUT HANDLERLARı ───────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Yetkisiz erişim.")
        return
    await send_messages(update, context, [build_help_message()])


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await send_messages(update, context, [build_help_message()])


async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Yetkisiz erişim.")
        return
    await send_typing(update, context)
    start_msg = await update.message.reply_text(
        "🚀 <b>Nexa Deep Intelligence v6.0 başlatıldı...</b>\n9 ajan eş zamanlı çalışacak. ~3-5 dakika sürebilir.",
        parse_mode=ParseMode.HTML,
    )
    mem = context.bot_data.get("memory")
    engine = IntelligenceEngine(mem)
    try:
        result = await engine.run(triggered_by="telegram_command")
        await engine.close()
        avg_q = await mem.avg_quality(10)
        messages = build_telegram_messages(result, avg_quality_10d=avg_q)
        try:
            await start_msg.delete()
        except Exception:
            pass
        await send_messages(update, context, messages)
    except Exception as e:
        logger.error(f"Rapor hatası: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ <b>Rapor hatası:</b>\n<code>{str(e)[:300]}</code>",
            parse_mode=ParseMode.HTML,
        )


async def cmd_quick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await send_typing(update, context)
    await update.message.reply_text("⚡ <b>Hızlı Stratejik Özet hazırlanıyor...</b>", parse_mode=ParseMode.HTML)
    vector = DiversityEngine.today_vector()
    now = datetime.now()
    ctx = AgentContext(
        bundle=DataBundle(), vector=vector, avoid_concepts=[], insights={},
        date_str=now.strftime("%d %B %Y %A"), time_str=now.strftime("%H:%M"),
    )
    try:
        agent = StrategicWeaponAgent()
        result = await agent.run(ctx)
        await agent.close()
        for part in split_message(clean_agent_output(result)):
            await send_messages(update, context, [part])
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)[:200]}", parse_mode=ParseMode.HTML)


async def cmd_research(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /research <konu> — Herhangi konuda derin araştırma
    """
    if not is_authorized(update):
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "❓ Kullanım: <code>/research &lt;araştırmak istediğin konu&gt;</code>\n"
            "Örnek: <code>/research agentic AI 2025 trends</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    topic = " ".join(args)
    await send_typing(update, context)
    await update.message.reply_text(
        f"🔍 <b>Deep Research başlatıldı:</b> <code>{topic}</code>\n~1-2 dakika sürebilir...",
        parse_mode=ParseMode.HTML,
    )

    vector = DiversityEngine.today_vector()
    now = datetime.now()
    ctx = AgentContext(
        bundle=DataBundle(), vector=vector, avoid_concepts=[], insights={},
        date_str=now.strftime("%d %B %Y %A"), time_str=now.strftime("%H:%M"),
    )
    try:
        agent = DeepResearchAgent()
        result = await agent.research(topic, ctx)
        await agent.close()
        mem = context.bot_data.get("memory")
        if mem:
            await mem.log_agent("deep_research", len(result), success=True)
        for part in split_message(clean_agent_output(result)):
            await send_messages(update, context, [part])
    except Exception as e:
        logger.error(f"Research hatası: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Hata: {str(e)[:200]}", parse_mode=ParseMode.HTML)


async def cmd_proptech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /proptech — PropTech + Türkiye piyasa odaklı araştırma
    """
    if not is_authorized(update):
        return
    await send_typing(update, context)
    await update.message.reply_text(
        "🏢 <b>PropTech OSINT analizi başlatıldı...</b>", parse_mode=ParseMode.HTML)

    mem = context.bot_data.get("memory")
    dm = DataMesh()
    try:
        bundle = await dm.fetch_all()
        vector = DiversityEngine.today_vector()
        now = datetime.now()
        ctx = AgentContext(
            bundle=bundle, vector=vector, avoid_concepts=[], insights={},
            date_str=now.strftime("%d %B %Y %A"), time_str=now.strftime("%H:%M"),
        )
        agent = PropTechOSINTAgent()
        result = await agent.run(ctx)
        await agent.close()
        if mem:
            await mem.log_agent("proptech_manual", len(result), success=True)
        for part in split_message(clean_agent_output(result)):
            await send_messages(update, context, [part])
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)[:200]}", parse_mode=ParseMode.HTML)
    finally:
        await dm.close()


async def cmd_longevity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /longevity — Longevity + bilişsel optimizasyon protokolü
    """
    if not is_authorized(update):
        return
    await send_typing(update, context)
    await update.message.reply_text(
        "🧬 <b>Longevity + Bilişsel Optimizasyon araştırması başlatıldı...</b>",
        parse_mode=ParseMode.HTML,
    )
    vector = DiversityEngine.today_vector()
    now = datetime.now()
    ctx = AgentContext(
        bundle=DataBundle(), vector=vector, avoid_concepts=[], insights={},
        date_str=now.strftime("%d %B %Y %A"), time_str=now.strftime("%H:%M"),
    )
    try:
        agent = LongevityProtocolAgent()
        result = await agent.run(ctx)
        await agent.close()
        mem = context.bot_data.get("memory")
        if mem:
            await mem.log_agent("longevity_manual", len(result), success=True)
        for part in split_message(clean_agent_output(result)):
            await send_messages(update, context, [part])
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)[:200]}", parse_mode=ParseMode.HTML)


async def cmd_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /ai — AI sistemleri + güvenlik araştırması
    """
    if not is_authorized(update):
        return
    await send_typing(update, context)
    await update.message.reply_text(
        "🤖 <b>AI Sistemleri + Güvenlik araştırması başlatıldı...</b>",
        parse_mode=ParseMode.HTML,
    )
    dm = DataMesh()
    try:
        bundle = await dm.fetch_all()
        vector = DiversityEngine.today_vector()
        now = datetime.now()
        ctx = AgentContext(
            bundle=bundle, vector=vector, avoid_concepts=[], insights={},
            date_str=now.strftime("%d %B %Y %A"), time_str=now.strftime("%H:%M"),
        )
        agent = AISecurityAgent()
        result = await agent.run(ctx)
        await agent.close()
        mem = context.bot_data.get("memory")
        if mem:
            await mem.log_agent("ai_manual", len(result), success=True)
        for part in split_message(clean_agent_output(result)):
            await send_messages(update, context, [part])
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)[:200]}", parse_mode=ParseMode.HTML)
    finally:
        await dm.close()


async def cmd_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /crypto — Kripto/DeFi alpha analizi
    """
    if not is_authorized(update):
        return
    await send_typing(update, context)
    await update.message.reply_text(
        "₿ <b>Kripto/DeFi Alpha analizi başlatıldı...</b>", parse_mode=ParseMode.HTML)

    dm = DataMesh()
    try:
        bundle = await dm.fetch_all()
        vector = DiversityEngine.today_vector()
        now = datetime.now()
        ctx = AgentContext(
            bundle=bundle, vector=vector, avoid_concepts=[], insights={},
            date_str=now.strftime("%d %B %Y %A"), time_str=now.strftime("%H:%M"),
        )
        agent = CryptoAlphaAgent()
        result = await agent.run(ctx)
        await agent.close()
        mem = context.bot_data.get("memory")
        if mem:
            await mem.log_agent("crypto_manual", len(result), success=True)
        for part in split_message(clean_agent_output(result)):
            await send_messages(update, context, [part])
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)[:200]}", parse_mode=ParseMode.HTML)
    finally:
        await dm.close()


async def cmd_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /idea <fikir> — İş fikri validasyonu
    """
    if not is_authorized(update):
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "❓ Kullanım: <code>/idea &lt;iş fikrin&gt;</code>\n"
            "Örnek: <code>/idea WhatsApp'tan otomatik lead yakalayan AI CRM</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    idea = " ".join(args)
    await send_typing(update, context)
    await update.message.reply_text(
        f"💡 <b>Fikir validasyonu başlatıldı:</b>\n<i>{idea}</i>\n\n~1-2 dakika...",
        parse_mode=ParseMode.HTML,
    )

    vector = DiversityEngine.today_vector()
    now = datetime.now()
    ctx = AgentContext(
        bundle=DataBundle(), vector=vector, avoid_concepts=[], insights={},
        date_str=now.strftime("%d %B %Y %A"), time_str=now.strftime("%H:%M"),
    )
    try:
        agent = IdeaValidatorAgent()
        result = await agent.validate(idea, ctx)
        await agent.close()
        mem = context.bot_data.get("memory")
        if mem:
            await mem.log_agent("idea_validator", len(result), success=True)
        for part in split_message(clean_agent_output(result)):
            await send_messages(update, context, [part])
    except Exception as e:
        logger.error(f"Idea validation hatası: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Hata: {str(e)[:200]}", parse_mode=ParseMode.HTML)


async def cmd_osint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /osint <hedef> — OSINT + rakip profil analizi
    """
    if not is_authorized(update):
        return

    args = context.args
    target = " ".join(args) if args else "Türkiye PropTech rakipleri ve liderler"

    await send_typing(update, context)
    await update.message.reply_text(
        f"🕵️ <b>OSINT analizi başlatıldı:</b>\n<code>{target}</code>\n\n~1-2 dakika...",
        parse_mode=ParseMode.HTML,
    )

    vector = DiversityEngine.today_vector()
    now = datetime.now()
    ctx = AgentContext(
        bundle=DataBundle(), vector=vector, avoid_concepts=[], insights={},
        date_str=now.strftime("%d %B %Y %A"), time_str=now.strftime("%H:%M"),
    )
    try:
        agent = OSINTProfilerAgent()
        result = await agent.profile(target, ctx)
        await agent.close()
        mem = context.bot_data.get("memory")
        if mem:
            await mem.log_agent("osint_manual", len(result), success=True)
        for part in split_message(clean_agent_output(result)):
            await send_messages(update, context, [part])
    except Exception as e:
        logger.error(f"OSINT hatası: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Hata: {str(e)[:200]}", parse_mode=ParseMode.HTML)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    mem: MemoryEngine = context.bot_data.get("memory")
    summary = await mem.summary()
    vector = DiversityEngine.today_vector()
    await send_messages(update, context, [build_status_message(summary, dict(vector))])


async def cmd_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    mem: MemoryEngine = context.bot_data.get("memory")
    concepts = await mem.recent_concepts(config.DIVERSITY_WINDOW_DAYS)
    domain_focuses = await mem.recent_domain_focuses(7)
    concept_str = ", ".join(concepts[:30]) if concepts else "Henüz kavram yok"
    focus_str = ", ".join(set(domain_focuses[:10])) if domain_focuses else "Henüz yok"
    msg = f"""<b>🧠 HAFIZA ÖZETİ</b>

<b>Son {config.DIVERSITY_WINDOW_DAYS} Günde Kapsanan Kavramlar:</b>
<i>{concept_str}</i>

<b>Son 7 Günde Aktif Domainler:</b>
<code>{focus_str}</code>

<i>Bu kavramlar tekrar edilmeyecek. Sistem çeşitlilik için bunlardan kaçınır.</i>"""
    await send_messages(update, context, [msg])


async def cmd_vector(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    vector = DiversityEngine.today_vector()
    msg = f"<b>🔭 BUGÜNÜN KEŞİF VEKTÖRü</b>\n\n{DiversityEngine.format_vector_info(vector)}"
    await send_messages(update, context, [msg])


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text(
        "❓ Bilinmeyen komut. /help ile komutları görün.",
        parse_mode=ParseMode.HTML,
    )


# ─── BOT SINIFI ──────────────────────────────────────────────────────────────
class NexaBot:
    def __init__(self, mem: MemoryEngine):
        self.memory = mem
        self.app: Application | None = None

    def build(self) -> Application:
        self.app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        self.app.bot_data["memory"] = self.memory

        # Tüm komutları kaydet
        handlers = [
            ("start",    cmd_start),
            ("help",     cmd_help),
            ("report",   cmd_report),
            ("quick",    cmd_quick),
            ("research", cmd_research),
            ("proptech", cmd_proptech),
            ("longevity",cmd_longevity),
            ("ai",       cmd_ai),
            ("crypto",   cmd_crypto),
            ("idea",     cmd_idea),
            ("osint",    cmd_osint),
            ("status",   cmd_status),
            ("memory",   cmd_memory),
            ("vector",   cmd_vector),
        ]
        for cmd, handler in handlers:
            self.app.add_handler(CommandHandler(cmd, handler))
        self.app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

        logger.info("Nexa Bot oluşturuldu — 14 komut hazır.")
        return self.app

    async def send_scheduled_report(self, result: dict, avg_quality_10d: str = "?"):
        if not config.TELEGRAM_CHAT_ID:
            logger.warning("TELEGRAM_CHAT_ID ayarlanmamış.")
            return
        messages = build_telegram_messages(result, avg_quality_10d=avg_quality_10d)
        for i, msg in enumerate(messages):
            if not msg.strip():
                continue
            try:
                await self.app.bot.send_message(
                    chat_id=config.TELEGRAM_CHAT_ID, text=msg,
                    parse_mode=ParseMode.HTML, disable_web_page_preview=True,
                )
                if i < len(messages) - 1:
                    await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Zamanlı rapor mesaj {i+1} hatası: {e}")
        logger.info(f"Zamanlı rapor gönderildi: {len(messages)} mesaj")


# ═════════════════════════════════════════════════════════════════════════════
# ⑫ ANA DÖNGÜ
# ═════════════════════════════════════════════════════════════════════════════
def setup_logging():
    fmt = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
    ]
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
        format=fmt, datefmt="%Y-%m-%d %H:%M:%S", handlers=handlers,
    )
    for quiet in ["httpx", "httpcore", "telegram", "apscheduler"]:
        logging.getLogger(quiet).setLevel(logging.WARNING)
    return logging.getLogger(__name__)


def validate_config() -> list[str]:
    errors = []
    if not config.GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY ayarlanmamış!")
    if not config.TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN ayarlanmamış!")
    if not config.TELEGRAM_CHAT_ID:
        print("⚠️  UYARI: TELEGRAM_CHAT_ID ayarlanmamış.")
    return errors


async def scheduled_report_job(bot: NexaBot, mem: MemoryEngine):
    logger_sched = logging.getLogger("scheduler")
    logger_sched.info(f"⏰ Zamanlanmış rapor: {datetime.now().strftime('%H:%M')}")
    engine = IntelligenceEngine(mem)
    try:
        result = await engine.run(triggered_by="schedule")
        avg_q = await mem.avg_quality(10)
        await bot.send_scheduled_report(result, avg_quality_10d=avg_q)
        logger_sched.info("✅ Zamanlanmış rapor gönderildi.")
    except Exception as e:
        logger_sched.error(f"❌ Zamanlanmış rapor hatası: {e}", exc_info=True)
        if config.TELEGRAM_CHAT_ID and bot.app:
            try:
                await bot.app.bot.send_message(
                    chat_id=config.TELEGRAM_CHAT_ID,
                    text=f"❌ <b>Zamanlanmış Rapor Hatası</b>\n<code>{str(e)[:300]}</code>",
                    parse_mode="HTML",
                )
            except Exception:
                pass
    finally:
        await engine.close()


async def main():
    log = setup_logging()
    log.info("=" * 60)
    log.info("  NEXA DEEP INTELLIGENCE v6.0 BAŞLATIYOR")
    log.info(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"  9 Ajan · 6 Research Ajanı · Sabah {config.DAILY_HOUR:02d}:{config.DAILY_MINUTE:02d}")
    log.info("=" * 60)

    errors = validate_config()
    if errors:
        for err in errors:
            log.critical(f"KONFİGÜRASYON HATASI: {err}")
        sys.exit(1)

    await memory.init()
    log.info("✅ Hafıza motoru başlatıldı.")

    bot = NexaBot(memory)
    app = bot.build()

    scheduler = AsyncIOScheduler(timezone="Europe/Istanbul")
    scheduler.add_job(
        scheduled_report_job,
        CronTrigger(hour=config.DAILY_HOUR, minute=config.DAILY_MINUTE, timezone="Europe/Istanbul"),
        id="daily_report",
        name=f"Günlük Rapor ({config.DAILY_HOUR:02d}:{config.DAILY_MINUTE:02d})",
        args=[bot, memory],
        max_instances=1,
        misfire_grace_time=300,
    )
    scheduler.start()
    log.info(f"✅ Zamanlayıcı: her gün {config.DAILY_HOUR:02d}:{config.DAILY_MINUTE:02d} Türkiye saati")

    job = scheduler.get_job("daily_report")
    if job and job.next_run_time:
        log.info(f"📅 Sonraki çalışma: {job.next_run_time.strftime('%Y-%m-%d %H:%M %Z')}")

    log.info("🤖 Telegram bot başlatılıyor...")
    log.info("Komutlar: /report /research /proptech /longevity /ai /crypto /idea /osint")

    # ── WEBHOOK vs POLLING otomatik seçimi ──────────────────────────────────
    # Render ve cloud platformlar PORT env variable set eder.
    # Local geliştirmede PORT yoktur → polling.
    PORT = int(os.getenv("PORT", 0))
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "") or os.getenv("RENDER_EXTERNAL_URL", "")
    USE_WEBHOOK = bool(PORT and WEBHOOK_URL)

    async with app:
        await app.initialize()
        await app.start()

        if USE_WEBHOOK:
            # ── WEBHOOK MODU (Render / Production) ──────────────────────────
            webhook_path = f"/{config.TELEGRAM_BOT_TOKEN}"
            full_webhook_url = f"{WEBHOOK_URL.rstrip('/')}{webhook_path}"

            await app.bot.set_webhook(
                url=full_webhook_url,
                allowed_updates=["message", "callback_query"],
                drop_pending_updates=True,
            )
            log.info(f"WEBHOOK MODU — Port: {PORT} | URL: {full_webhook_url[:60]}...")

            await app.updater.start_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=config.TELEGRAM_BOT_TOKEN,
                webhook_url=full_webhook_url,
                drop_pending_updates=True,
            )
            log.info("Bot webhook aktif. Tek instance garantili.")
        else:
            # ── POLLING MODU (Local geliştirme) ─────────────────────────────
            await app.bot.delete_webhook(drop_pending_updates=True)
            log.info("POLLING MODU (local) — Webhook temizlendi.")
            # Conflict varsa bekle ve tekrar dene (eski instance'ın ölmesini bekle)
            for attempt in range(1, 6):
                try:
                    await app.bot.delete_webhook(drop_pending_updates=True)
                    await app.updater.start_polling(
                        drop_pending_updates=True,
                        allowed_updates=["message", "callback_query"],
                        error_callback=lambda exc: log.warning(f"Polling hatası (geçici): {exc}"),
                    )
                    log.info(f"Bot polling aktif (deneme {attempt}).")
                    break
                except Exception as poll_err:
                    if "Conflict" in str(poll_err) and attempt < 5:
                        log.warning(f"Conflict — eski instance ölüyor, {30*attempt}s bekleniyor... (deneme {attempt}/5)")
                        await asyncio.sleep(30 * attempt)
                    else:
                        raise

        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            log.info("Kapatiliyor...")
        finally:
            scheduler.shutdown(wait=False)
            await app.updater.stop()
            await app.stop()


# ─── DRY RUN ─────────────────────────────────────────────────────────────────
async def dry_run():
    log = setup_logging()
    log.info("🔧 DRY RUN modu (Telegram yok)")
    await memory.init()
    dm = DataMesh()
    bundle = await dm.fetch_all()
    await dm.close()
    print(f"\n📊 Veri: intel={len(bundle.intel)}, dev={len(bundle.dev_velocity)}, hn={len(bundle.hn_signal)}")
    vector = DiversityEngine.today_vector()
    print(f"🔭 Vektör: {vector['cognitive_frame']} | {vector['domain_focus']} | {vector['weekday']}")
    print("✅ Dry run tamamlandı.")


# ═════════════════════════════════════════════════════════════════════════════
# GİRİŞ NOKTASI
# ═════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Nexa Deep Intelligence v6.0")
    parser.add_argument("--mode", choices=["run", "dry-run"], default="run")
    args = parser.parse_args()

    if args.mode == "run":
        asyncio.run(main())
    elif args.mode == "dry-run":
        asyncio.run(dry_run())
