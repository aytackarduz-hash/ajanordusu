"""
NEXA DEEP INTELLIGENCE v5.0 — agents.py
8 Uzman Ajan + Kalite Değerlendirici.
Her ajan: Yiğit'in domain'lerine, projelerine ve bilişsel stiline özel.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

import httpx

from config import config, USER
from data_mesh import DataBundle, filter_intel_by_tags
from diversity_engine import DailyVector, DiversityEngine

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# TEMEL AJAN
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class AgentContext:
    bundle: DataBundle
    vector: DailyVector
    avoid_concepts: list[str]
    insights: dict[str, str]
    date_str: str
    time_str: str


class AgentBase(ABC):
    def __init__(self, name: str, temperature: float = 0.85, max_tokens: int = 1800, use_search: bool = True):
        self.name = name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.use_search = use_search
        self._client: httpx.AsyncClient | None = None

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
                logger.debug(f"  [{self.name}] attempt {attempt}")
                resp = await self._client.post(url, json=payload)
                data = resp.json()
                if resp.status_code != 200:
                    raise RuntimeError(f"HTTP {resp.status_code}: {str(data.get('error', ''))[:150]}")
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
                logger.info(f"  [{self.name}] ✓ {len(text)} chars")
                return text
            except Exception as e:
                last_err = e
                logger.warning(f"  [{self.name}] attempt {attempt} failed: {e}")
                if attempt < config.MAX_RETRIES:
                    await asyncio.sleep(config.RETRY_DELAY_S * attempt)

        raise RuntimeError(f"[{self.name}] exhausted retries: {last_err}")

    @abstractmethod
    async def run(self, ctx: AgentContext) -> str:
        pass

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # ─── YARDIMCI: KAÇINILACAK KONULARI FORMATLA ───────────────────────────
    @staticmethod
    def _avoid_str(concepts: list[str], n: int = 25) -> str:
        if not concepts:
            return "yok"
        return ", ".join(concepts[:n])

    # ─── YARDIMCI: DOMAIN KONULARINI FORMATLA ──────────────────────────────
    @staticmethod
    def _domain_topics_str(domain_names: list[str], max_per_domain: int = 5) -> str:
        result = []
        for dn in domain_names:
            topics = DiversityEngine.domain_topics(dn)[:max_per_domain]
            if topics:
                result.append(f"[{dn.replace('_', ' ')}]\n" + "\n".join(f"  • {t}" for t in topics))
        return "\n\n".join(result) or "—"

    # ─── YARDIMCI: HEDEFLER ────────────────────────────────────────────────
    @staticmethod
    def _goals_str() -> str:
        return "\n".join(f"• {g}" for g in USER["strategic_goals"])

    # ─── YARDIMCI: PROJELEr ───────────────────────────────────────────────
    @staticmethod
    def _projects_str() -> str:
        return "\n".join(f"• {p}" for p in USER["active_projects"])


# ─────────────────────────────────────────────────────────────────────────────
# AJAN 1: TEMPORAL ARBİTRAJ
# ─────────────────────────────────────────────────────────────────────────────
class TemporalArbitrageAgent(AgentBase):
    def __init__(self):
        t = config.AGENT_TEMPERATURES["temporal_arbitrage"]
        m = config.AGENT_MAX_TOKENS["temporal_arbitrage"]
        super().__init__("TemporalArbitrageAgent", temperature=t, max_tokens=m, use_search=True)

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
KAÇINILACAKLAR (son {config.DIVERSITY_WINDOW_DAYS} gün): {self._avoid_str(ctx.avoid_concepts)}

AKTİF PROJELER:
{self._projects_str()}

STRATEJİK HEDEFLER:
{self._goals_str()}

DOMAIN KONULARI (bugünün odak alanları):
{domain_context}

CANLI TEKNOLOJİ SİNYALLERİ:
{chr(10).join(tech_signals) or '[Google Search ile son 48 saati tara]'}

BİLİM SİNYALLERİ:
{chr(10).join(sci_signals) or '[arXiv son yayınları]'}

GÖREV: Son 48 saatte gerçekleşen, PENCERE DAR olan TEK olayı/gelişmeyi bul.
Bu gelişme Yiğit'in domain'leriyle (AI, longevity, kripto, PropTech, bilişsel geliştirme) kesişmeli.
2. ve 3. derece domino zinciri ZORUNLU. Neden şimdi harekete geçmek kritik?

ÇIKTI FORMATI — Telegram HTML:
<b>⏱️ TEMPORAL ARBİTRAJ</b>
<b>📍 [BAŞLIK: Max 10 kelime, şok edici]</b>

<b>🕐 Arbitraj Penceresi:</b> [saat] | <b>Etki:</b> [X/10] | <b>Proje:</b> [hangi proje]

<b>Ne Oldu:</b>
[2-3 cümle, spesifik veri ile]

<b>Neden 48 Saat İçinde Değer Kaybeder:</b>
[mekanizma açıkla]

<b>2. Derece Domino:</b>
[ilk tetikleme → sonuç]

<b>3. Derece Domino:</b>
[derin sistemik etki]

<b>⚡ AKSİYON:</b>
[ne + ne zaman + ilk somut adım]
"""
        return await self._gemini_call(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# AJAN 2: KONTRA-SENTIMENT
# ─────────────────────────────────────────────────────────────────────────────
class ContraSentimentAgent(AgentBase):
    def __init__(self):
        t = config.AGENT_TEMPERATURES["contra_sentiment"]
        m = config.AGENT_MAX_TOKENS["contra_sentiment"]
        super().__init__("ContraSentimentAgent", temperature=t, max_tokens=m, use_search=True)

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        fg = ctx.bundle.market.get("fear_greed", [])
        gs = ctx.bundle.market.get("global_stats", {})
        fg_str = " → ".join(f"{f.get('value_classification')}({f.get('value')})" for f in fg)
        gs_str = (f"BTC Dom: {gs.get('btc_dominance')}% | 24h: {gs.get('market_cap_change_24h')}%") if gs else ""

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

GÖREV: Herkesin kabul ettiği YANLIş bir inancı tespit et. Veri destekli kontrarian argüman sun.
Domain: AI, kripto, longevity, PropTech, biyohacking alanlarından birinde odaklan.
Risk: Kontrarian pozisyon ne zaman yanlış çıkar? Dürüst ol.

ÇIKTI FORMATI — Telegram HTML:
<b>🔄 KONTRA-SENTİMENT İSTİHBARATI</b>
<b>📍 [Konsensus İnanç: Max 8 kelime]</b>

<b>Konsensus:</b>
[herkesin inandığı/söylediği]

<b>Karşı Kanıt:</b>
[ters işaret eden spesifik veri/gözlem]

<b>Neden Yanılıyorlar:</b>
[mekanizma — psikolojik önyargı veya eksik bilgi]

<b>2. Derece Etki:</b>
[konsensus çöktüğünde ne olur]

<b>Risk Senaryosu:</b>
<i>[kontrarian yanılma koşulları — dürüst değerlendirme]</i>

<b>Yiğit İçin:</b>
[hangi kararı veya pozisyonu etkiler]

<b>🎯 Conviction:</b> [Düşük/Orta/Yüksek] — [tek cümle neden]
"""
        return await self._gemini_call(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# AJAN 3: ZAYIF SİNYAL TOPLAYICI
# ─────────────────────────────────────────────────────────────────────────────
class WeakSignalAggregatorAgent(AgentBase):
    def __init__(self):
        t = config.AGENT_TEMPERATURES["weak_signal"]
        m = config.AGENT_MAX_TOKENS["weak_signal"]
        super().__init__("WeakSignalAggregatorAgent", temperature=t, max_tokens=m, use_search=True)

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        sci = filter_intel_by_tags(ctx.bundle.intel, ["arxiv", "biorxiv", "nature"], 8)
        tech = filter_intel_by_tags(ctx.bundle.intel, ["techcrunch", "arstechnica", "verge", "singularity", "futurism"], 8)
        fin = filter_intel_by_tags(ctx.bundle.intel, ["coindesk", "theblock", "decrypt", "cointelegraph"], 6)
        dev = [f"{d['name']}({d.get('stars_today', '?')}★ bugün): {d['desc']}" for d in ctx.bundle.dev_velocity[:8]]
        hn = [f"[{h['score']}pts] {h['title']}" for h in ctx.bundle.hn_signal[:6]]

        domain_context = self._domain_topics_str(v["domain_focus"], 3)

        prompt = f"""
SEN: Zayıf Sinyal Uzmanısın. Birbirinden bağımsız görünen sinyallerin aynı yönü işaret ettiğini görürsün.
KULLANICI: {USER['name']} | ARAMA MODU: {v['search_mode']} | DOMAIN: {', '.join(v['domain_focus'])}
KAÇINILACAKLAR: {self._avoid_str(ctx.avoid_concepts)}

DOMAIN KONULARI:
{domain_context}

[Bilim/Akademi Sinyalleri]:
{chr(10).join(sci) or '—'}

[Teknoloji Sinyalleri]:
{chr(10).join(tech) or '—'}

[Finans/Kripto Sinyalleri]:
{chr(10).join(fin) or '—'}

[Geliştirici Hızı - GitHub]:
{chr(10).join(dev) or '—'}

[HackerNews]:
{chr(10).join(hn) or '—'}

GÖREV: 3+ FARKLI alandan gelen ve AYNI YÖNÜ işaret eden sinyalleri birleştir.
Bu konverjans hangi paradigma kaymasını öngörüyor?
Sadece bugün niche'de olan, 6-18 ay içinde mainstream olacak örüntüyü bul.

ÇIKTI FORMATI — Telegram HTML:
<b>🔮 ZAYIF SİNYAL KONVERJANS</b>
<b>📍 [Örüntü adı: Max 10 kelime]</b>

<b>Güç:</b> [Zayıf/Orta/Güçlü] | <b>Ufuk:</b> [X ay/yıl] | <b>Güven:</b> [%X]

<b>Alan 1 — [isim]:</b> [sinyal, spesifik]
<b>Alan 2 — [isim]:</b> [sinyal, spesifik]
<b>Alan 3 — [isim]:</b> [sinyal, spesifik]

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


# ─────────────────────────────────────────────────────────────────────────────
# AJAN 4: BİLİŞSEL KENAR
# ─────────────────────────────────────────────────────────────────────────────
class CognitiveEdgeAgent(AgentBase):
    def __init__(self):
        t = config.AGENT_TEMPERATURES["cognitive_edge"]
        m = config.AGENT_MAX_TOKENS["cognitive_edge"]
        super().__init__("CognitiveEdgeAgent", temperature=t, max_tokens=m, use_search=True)

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        bio_signals = filter_intel_by_tags(ctx.bundle.intel, ["arxiv_neuro", "arxiv_bio", "biorxiv", "nature", "longevity"], 8)
        sci_signals = filter_intel_by_tags(ctx.bundle.intel, ["arxiv_ai", "arxiv_ml", "singularity", "futurism"], 5)

        cognitive_domain = USER["knowledge_domains"]["Cognitive_Enhancement"]["topics"]
        longevity_domain = USER["knowledge_domains"]["Longevity_Biotech"]["topics"]

        prompt = f"""
SEN: Nörobilim ve Bilişsel Optimizasyon Uzmanısın. Ampirik kanıta dayalı, mekanistik düşünürsün.
KULLANICI: {USER['name']}, {USER['age']}Y | Yüksek kognitif yük: kod, strateji, içerik üretimi
GÜN: {v['weekday']} {v['hour']}:00 — Zihinsel kaynak en yüksek kullanım saatleri
HEDEFLER: Bilişsel kapasite maksimizasyonu + longevity

BİLİŞSEL GELİŞTİRME ALANLARI:
{chr(10).join(f'• {t}' for t in cognitive_domain[:6])}

LONGEVİTY ALANLARI:
{chr(10).join(f'• {t}' for t in longevity_domain[:4])}

CANLI BİYO SİNYALLERİ:
{chr(10).join(bio_signals) or '[PubMed/bioRxiv son 7 gün: cognitive enhancement, neuroplasticity, longevity]'}

TEKNOLOJİ/AI SİNYALLERİ:
{chr(10).join(sci_signals) or '[arXiv son yayınlar]'}

KAÇINILACAKLAR (tekrar yapma): {self._avoid_str(ctx.avoid_concepts)}

GÖREV: Son araştırmalara dayanan, AMAÇ ODAKLI bir bilişsel/longevity müdahalesi öner.
Spesifik bileşen adı vermek yerine mekanizmayı ve hedef nöral devreyi açıkla.
Yiğit'in yüksek-üretkenlik + uzun vadeli beyin sağlığı hedefine hizmet etmeli.
KAYNAKLI olmalı (PMID, DOI veya preprint).

ÇIKTI FORMATI — Telegram HTML:
<b>🧬 BİLİŞSEL KENAR PROTOKOLÜ</b>
<b>📍 [Protokol adı — spesifik, amaç odaklı]</b>

<b>Hedef Devre:</b> [nöral devre/sistem] | <b>Etki Süresi:</b> [X saat/gün] | <b>Kanıt:</b> [kalite seviyesi]

<b>Mekanizma:</b>
[reseptör + sinyal yolu + biyolojik sonuç — teknik ama anlaşılır]

<b>Uygulama Protokolü:</b>
[yöntem, zamanlama, bağlam — spesifik talimat]

<b>Zirve Penceresi:</b>
<i>[başlangıç → zirve → bitiş]</i>

<b>Sinerjiler:</b>
[hangi diğer müdahalelerle kombine edilir, mekanistik gerekçe]

<b>Kontrendikasyonlar:</b>
[uyarılar, kümülatif risk, bireye özgü faktörler]

<b>Yiğit'in Hedefine Bağlantı:</b>
[kod yazma / strateji / içerik üretimine spesifik katkı]

<b>Kaynak:</b> <code>[PMID: XXXXX veya arXiv: XXXX.XXXXX veya DOI]</code>
"""
        return await self._gemini_call(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# AJAN 5: SİSTEM ÇÖZÜLME
# ─────────────────────────────────────────────────────────────────────────────
class SystemsBreakdownAgent(AgentBase):
    def __init__(self):
        t = config.AGENT_TEMPERATURES["systems_breakdown"]
        m = config.AGENT_MAX_TOKENS["systems_breakdown"]
        super().__init__("SystemsBreakdownAgent", temperature=t, max_tokens=m, use_search=True)

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        signals = [i.title for i in ctx.bundle.intel[:22]]
        dev = [f"{d['name']}({d.get('stars_today','?')}★): {d['desc']}" for d in ctx.bundle.dev_velocity[:10]]
        domain_context = self._domain_topics_str(v["domain_focus"], 4)

        prompt = f"""
SEN: Sistem Dönüşümü Analistinin. Çözülen eski sistemleri ve yükselen yeni sistemleri görürsün.
KULLANICI: {USER['name']} | PROJELER: {' | '.join(USER['active_projects'][:4])}
ARAMA MODU: {v['search_mode']} | ALAN: {', '.join(v['domain_focus'])}
KAÇINILACAKLAR: {self._avoid_str(ctx.avoid_concepts)}

DOMAIN KONULARI:
{domain_context}

SİNYALLER:
{chr(10).join(signals) or '[Google Search]'}

GELİŞTİRİCİ VELOCİTY:
{chr(10).join(dev) or '—'}

GÖREV: Aktif çözülme sürecindeki BİR sistemi tespit et.
First-mover fırsatı nerede? Nexa'nın hangi projesi bu boşluğu doldurabilir?
PropTech × AI × kripto kesişimine öncelik ver (Yiğit'in core domain'leri).

ÇIKTI FORMATI — Telegram HTML:
<b>🌀 SİSTEM ÇÖZÜLME SİNYALİ</b>
<b>📍 [Dönüşen sistem: isim + sektör]</b>

<b>Eski Sistem (Çözülen):</b>
[neden çözülüyor — mekanizma + kanıt]

<b>Yeni Sistem (Yükselen):</b>
[ne değiştiriyor, nasıl farklı çalışıyor]

<b>Dönüşüm Hızı:</b> [Yavaş/Orta/Hızlı] — [gösterge]

<b>Açılan Boşluk:</b>
[şu an kim dolduruyor, kim doldurabilir]

<b>Nexa Fırsatı:</b>
[Yiğit'e spesifik öneri — hangi proje, nasıl konumlanır]

<b>Tehlike Radari:</b>
[mevcut Nexa projelerinden herhangi birini tehdit ediyor mu]

<b>First-Mover Penceresi:</b>
[bu boşluğu doldurmak için ne kadar vakti var]
"""
        return await self._gemini_call(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# AJAN 6: NARATİF VELOCİTY
# ─────────────────────────────────────────────────────────────────────────────
class NarrativeVelocityAgent(AgentBase):
    def __init__(self):
        t = config.AGENT_TEMPERATURES["narrative_velocity"]
        m = config.AGENT_MAX_TOKENS["narrative_velocity"]
        super().__init__("NarrativeVelocityAgent", temperature=t, max_tokens=m, use_search=True)

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        hn = [f"[{h['score']}pts, {h['comments']} yorum] {h['title']}" for h in ctx.bundle.hn_signal[:8]]
        dev = [f"{d['name']}({d.get('stars_today','?')}★ bugün, dil:{d.get('language','')}): {d['desc']}" for d in ctx.bundle.dev_velocity[:8]]
        frontier = filter_intel_by_tags(ctx.bundle.intel, ["singularity", "futurism", "longevity", "biorxiv"], 8)

        prompt = f"""
SEN: Niche-to-Mainstream Analistinin. Niche topluluklarda ivme kazanan ama henüz büyük kitleye ulaşmamış fikirleri yakalarsın.
KULLANICI: {USER['name']} | ARAMA MODU: {v['search_mode']} | ÇERÇEVE: {v['cognitive_frame']}
KAÇINILACAKLAR: {self._avoid_str(ctx.avoid_concepts)}

HackerNews (öne çıkanlar):
{chr(10).join(hn) or '—'}

GitHub Dev Velocity (bugün yıldız patlaması):
{chr(10).join(dev) or '—'}

Frontier Sinyalleri:
{chr(10).join(frontier) or '—'}

AKTİF PROJELER: {' | '.join(USER['active_projects'][:4])}

GÖREV: Sadece niche'de tartışılan, 6-18 ay içinde mainstream'e ulaşacak TEK fikir/teknoloji/framework bul.
Bu fikrin ivmesinin göstergeleri ne? Katalizör nedir?
Yiğit'in projesine nasıl entegre edilir?

ÇIKTI FORMATI — Telegram HTML:
<b>🚀 NARATİF VELOCİTY TARAMASI</b>
<b>📍 [Fikir/Teknoloji adı]</b>

<b>Kategori:</b> [AI/Biotech/Kripto/Diğer] | <b>Olgunluk:</b> [aşama] | <b>Mainstream'e:</b> ~[X ay]

<b>Bu Nedir:</b>
[özlü teknik açıklama, 2 cümle]

<b>Neden Şimdi Hızlanıyor:</b>
[spesifik göstergeler — star sayısı, commit hızı, akademik atıf, yatırım]

<b>Katalizör (Ne ile patlar):</b>
[spesifik olay/ürün/regülasyon/keşif]

<b>Nexa Entegrasyonu:</b>
[Yiğit'in hangi projesine nasıl giriyor]

<b>İlk Adım:</b>
[öğren / dene / pozisyon al — somut]

<b>Kaynaklar:</b>
<code>[GitHub repo / arXiv / topluluk linki]</code>
"""
        return await self._gemini_call(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# AJAN 7: DERİN BİLİM ATILIMI
# ─────────────────────────────────────────────────────────────────────────────
class DeepScienceAgent(AgentBase):
    def __init__(self):
        t = config.AGENT_TEMPERATURES["deep_science"]
        m = config.AGENT_MAX_TOKENS["deep_science"]
        super().__init__("DeepScienceAgent", temperature=t, max_tokens=m, use_search=True)

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        sci_papers = [
            f"[{i.tag.replace('arxiv_', '').replace('biorxiv', 'bio')}] {i.title} — {i.desc[:120]}"
            for i in ctx.bundle.intel
            if i.tag.startswith("arxiv") or i.tag in ("biorxiv", "nature", "longevity")
        ]

        priority_domains = ["Longevity_Biotech", "Cognitive_Enhancement", "AI_Systems_Architecture", "Quantum_Advanced_Computing"]
        domain_context = self._domain_topics_str(priority_domains, 3)

        prompt = f"""
SEN: Derin Bilim İstihbarat Analistinin. Henüz mainstream radara girmemiş bilimsel atılımları tespit edersin.
KULLANICI: {USER['name']} | Öncelik alanlar: longevity > nörobilim > CRISPR > AI mimarisi > kuantum
ÇERÇEVE: {v['cognitive_frame']} | UFUK: {v['temporal_lens']}
KAÇINILACAKLAR: {self._avoid_str(ctx.avoid_concepts)}

BİLİM ALAN KONULARI:
{domain_context}

PREPRINT/PAPER SİNYALLERİ:
{chr(10).join(sci_papers[:20]) or '[Google Scholar: son 7 gün longevity neuroscience AI breakthrough CRISPR]'}

GÖREV: Mevcut paradigmayı kıracak potansiyeli olan TEK bilimsel gelişmeyi seç.
Şüphe payını dürüstçe değerlendir. Kanıt kalitesi nedir?
Bu keşfin pratik uygulamaya geçmesi için ne gerekiyor?

ÇIKTI FORMATI — Telegram HTML:
<b>🔬 DERİN BİLİM ATILIMI</b>
<b>📍 [Keşfin başlığı]</b>

<b>Alan:</b> [disiplin] | <b>Olgunluk:</b> [Preprint/Published/Replicated] | <b>Etki Ufku:</b> [X yıl]

<b>Ne Bulundu:</b>
[özet — mekanizma dahil]

<b>Eski Paradigma:</b>
[bugüne kadar ne biliniyordu]

<b>Paradigma Kırılması:</b>
[neyi değiştiriyor — spesifik]

<b>Pratik Uygulama:</b>
[ne zaman gerçek hayata geçer, hangi adımlar gerekli]

<b>Yiğit'in Hedeflerine Bağlantı:</b>
[longevity / bilişsel / AI / PropTech ile kesişim]

<b>Şüphe Payı:</b>
<i>[yanıltıcı olabilecek faktörler, replication sorunu, finansman çıkarları]</i>

<b>Kaynak:</b> <code>[arXiv: XXXX.XXXXX | DOI: ... | PMID: ...]</code>
"""
        return await self._gemini_call(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# AJAN 8: PROPTECH OSINT
# ─────────────────────────────────────────────────────────────────────────────
class PropTechOSINTAgent(AgentBase):
    def __init__(self):
        t = config.AGENT_TEMPERATURES["proptech_osint"]
        m = config.AGENT_MAX_TOKENS["proptech_osint"]
        super().__init__("PropTechOSINTAgent", temperature=t, max_tokens=m, use_search=True)

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        fin_signals = filter_intel_by_tags(ctx.bundle.intel, ["coindesk", "theblock", "decrypt", "cointelegraph", "hbr"], 8)
        tech_signals = filter_intel_by_tags(ctx.bundle.intel, ["techcrunch", "arstechnica", "verge"], 6)
        dev = [f"{d['name']}({d.get('stars_today','?')}★): {d['desc']}" for d in ctx.bundle.dev_velocity[:6]]

        proptech_topics = USER["knowledge_domains"]["PropTech_Business"]["topics"]
        crypto_topics = USER["knowledge_domains"]["Crypto_DeFi"]["topics"][:4]

        prompt = f"""
SEN: PropTech × AI × Kripto İstihbarat Uzmanısın. Bu üç alan kesişimindeki fırsatları görürsün.
KULLANICI: {USER['name']} | Türkiye PropTech'de tek kategori: PropTech × AI Security × Solopreneurship
ÇERÇEVE: {v['cognitive_frame']} | ARAMA MODU: {v['search_mode']}
KAÇINILACAKLAR: {self._avoid_str(ctx.avoid_concepts)}

PROPTECH İŞ ALANLARI:
{chr(10).join(f'• {t}' for t in proptech_topics[:5])}

KRİPTO/RWA ALANLARI:
{chr(10).join(f'• {t}' for t in crypto_topics)}

FİNANS/İŞ SİNYALLERİ:
{chr(10).join(fin_signals) or '[Google Search: PropTech AI CRM SaaS 2025-2026]'}

TEKNOLOJİ SİNYALLERİ:
{chr(10).join(tech_signals) or '—'}

GELİŞTİRİCİ ARAÇLARI:
{chr(10).join(dev) or '—'}

AKTİF PROJELER: {' | '.join(USER['active_projects'][:5])}

HEDEF: İlk SaaS müşteri — CB Dikmen danışmanı | 2026 Prio 1
RAKIP AVANTAJI: Playwright OSINT + Gemini CRM + Adversarial AI — Türkiye'de TEK kombinasyon

GÖREV: Yiğit'in PropTech pozisyonunu güçlendirecek, bugünkü piyasadan ÖZEL bir sinyal bul.
AI × gayrimenkul, RWA tokenizasyonu, CRM inovasyonu, veya Türkiye piyasasına özgü fırsat.
Rakiplerin görmediği ama Yiğit'in Playwright+AI stack'iyle exploit edebileceği boşluk.

ÇIKTI FORMATI — Telegram HTML:
<b>🏢 PROPTECH OSINT İSTİHBARATI</b>
<b>📍 [Fırsat/Sinyal başlığı]</b>

<b>Kategori:</b> [CRM/Pazarlama/RWA/AI-Emlak/Diğer] | <b>Pazar:</b> [Türkiye/Global] | <b>Aciliyet:</b> [X/10]

<b>Sinyal:</b>
[ne oldu/değişti/çıktı — spesifik]

<b>Türkiye Bağlantısı:</b>
[Türkiye gayrimenkul piyasasına etkisi]

<b>Rakip Kör Noktası:</b>
[standart danışmanların göremediği neden]

<b>Nexa Stack Avantajı:</b>
[Playwright OSINT + Gemini CRM + WA bot bunu nasıl exploit eder]

<b>CB VIP / SaaS Önceliği:</b>
[Nexa CRM'e veya gayrimenkul portföyüne somut nasıl eklenir]

<b>Aksiyon:</b>
[ilk somut adım — kod, outreach, analiz, içerik]
"""
        return await self._gemini_call(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# AJAN 9: STRATEJİK SİLAH (Sentez)
# ─────────────────────────────────────────────────────────────────────────────
class StrategicWeaponAgent(AgentBase):
    def __init__(self):
        t = config.AGENT_TEMPERATURES["strategic_weapon"]
        m = config.AGENT_MAX_TOKENS["strategic_weapon"]
        super().__init__("StrategicWeaponAgent", temperature=t, max_tokens=m, use_search=False)

    async def run(self, ctx: AgentContext) -> str:
        v = ctx.vector
        import re
        # Tüm ajan çıktılarını özet olarak al
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

GÖREV: Bugünün tüm istihbaratını sentezle. Yiğit için EN YÜKSEK kaldıraçlı TEK eylemi belirle.
14 yıllık rekabetçi yüzücünün disiplini + INTJ sistem mimarisini çağır.
Sun Tzu: Rakip körken konuşlan. Taleb: Pozitif asimetri kur. Feynman: Varsayımı kır.

ÇIKTI FORMATI — Telegram HTML:
<b>🗡️ STRATEJİK SİLAH</b>

<blockquote>[3-4 satır manifesto — Sun Tzu/Taleb/Feynman ruhunda, BUGÜNÜN bulgularına özgü, Yiğit için kişisel. Her cümle bir şimşek.]</blockquote>

<b>Bugünün Savaşı:</b>
[ölçülebilir tek hedef — net ve somut]

<b>İçsel Düşman:</b>
[bugün yenilecek psikolojik/operasyonel engel — dürüst ve spesifik]

<b>Kaldıraç Noktası:</b>
[bugün yapılabilecek en yüksek asimetrik kaldıraçlı tek eylem]

<b>Sinerjik Hareket:</b>
[bu eylem aynı anda hangi 2 hedefi birden ilerletiyor]

<b>23:59 Zafer Kriteri:</b>
<b>[bu gerçekleştiyse günü kazandın: net ve ölçülebilir çıktı]</b>

<b>▶ [SON KOMUT — emir kipi, tek cümle, sadece Yiğit için, ona özel]</b>
"""
        return await self._gemini_call(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# KALİTE DEĞERLENDİRİCİ
# ─────────────────────────────────────────────────────────────────────────────
class QualityEvaluator(AgentBase):
    def __init__(self):
        t = config.AGENT_TEMPERATURES["quality_evaluator"]
        m = config.AGENT_MAX_TOKENS["quality_evaluator"]
        super().__init__("QualityEvaluator", temperature=t, max_tokens=m, use_search=False)

    async def run(self, ctx: AgentContext) -> str:
        """Abstract method implementation — QualityEvaluator uses evaluate() directly."""
        return ""

    async def evaluate(self, report_text: str) -> dict:
        import re
        clean = re.sub(r"<[^>]+>", " ", report_text)
        clean = re.sub(r"\s+", " ", clean)[:5000]

        prompt = f"""
Kullanıcı: {USER['name']}, {USER['age']}Y, {USER['role']}
Kullanıcının hedefleri: {' | '.join(USER['strategic_goals'][:4])}

Aşağıdaki sabah istihbarat raporunu 6 kriterde puanla (1.0-10.0):
- novelty: Yeni bilgi mi, yoksa herkesin bildiği mi?
- specificity: Veri destekli ve spesifik mi, yoksa belirsiz mi?
- actionability: Somut aksiyon var mı?
- depth: 2. ve 3. derece çıkarım var mı?
- diversity: Farklı domain'ler kapsandı mı?
- personalization: Yiğit'e özgü mü, yoksa herkes için mi?

RAPOR:
{clean}

SADECE geçerli JSON döndür, başka hiçbir şey yok:
{{"scores":{{"novelty":X.X,"specificity":X.X,"actionability":X.X,"depth":X.X,"diversity":X.X,"personalization":X.X}},"average":X.X,"weakest":"alan","strongest":"alan","should_send":true}}
"""
        try:
            raw = await self._gemini_call(prompt)
            import json, re
            raw = re.sub(r"```json|```", "", raw).strip()
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"Quality eval failed: {e}")
            return {
                "average": 7.5,
                "should_send": True,
                "weakest": "unknown",
                "strongest": "unknown",
                "scores": {},
            }


# ─────────────────────────────────────────────────────────────────────────────
# AJAN TANIMI LİSTESİ
# ─────────────────────────────────────────────────────────────────────────────
AGENT_DEFINITIONS = [
    {"key": "temporal",    "class": TemporalArbitrageAgent,  "label": "⏱️  Temporal Arbitraj"},
    {"key": "contra",      "class": ContraSentimentAgent,    "label": "🔄  Kontra-Sentiment"},
    {"key": "weak_signal", "class": WeakSignalAggregatorAgent,"label": "🔮  Zayıf Sinyal"},
    {"key": "cognitive",   "class": CognitiveEdgeAgent,      "label": "🧬  Bilişsel Kenar"},
    {"key": "systems",     "class": SystemsBreakdownAgent,   "label": "🌀  Sistem Çözülme"},
    {"key": "narrative",   "class": NarrativeVelocityAgent,  "label": "🚀  Narratif Velocity"},
    {"key": "deep_science","class": DeepScienceAgent,        "label": "🔬  Derin Bilim"},
    {"key": "proptech",    "class": PropTechOSINTAgent,      "label": "🏢  PropTech OSINT"},
]