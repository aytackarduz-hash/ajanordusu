"""
NEXA DEEP INTELLIGENCE v5.0 — diversity_engine.py
Günlük keşif vektörü üretimi.
Her gün farklı bilişsel çerçeve, domain odağı ve arama modu.
"""

import math
from datetime import datetime
from typing import TypedDict

from config import USER


class DailyVector(TypedDict):
    temporal_lens: str
    cognitive_frame: str
    domain_focus: list[str]
    search_mode: str
    weekday: str
    hour: int
    day_of_year: int
    days_left_year: int
    week_number: int
    primary_domain: str
    secondary_domain: str


class DiversityEngine:
    # ─── ZAMANSAL MERCEKLer ──────────────────────────────────────────────────
    TEMPORAL_LENSES = [
        "imminent_48h",      # Son 48 saatte patlayan fırsatlar
        "weekly_cycle",       # Haftalık trend ve momentum
        "monthly_shift",      # Aylık piyasa döngüsü
        "quarter_trend",      # Çeyrek strateji penceresi
        "year_horizon",       # Yıllık büyük bahis
        "decade_shift",       # On yıllık paradigma dönüşümü
        "contrarian_now",     # Konsensus tersine çevrimleri
    ]

    # ─── BİLİŞSEL ÇERÇEVELER ─────────────────────────────────────────────────
    COGNITIVE_FRAMES = [
        "adversarial",        # Kim/ne kazanır? Kim/ne kaybeder?
        "first_principles",   # Temel varsayımları kır, sıfırdan inşa et
        "second_order",       # 2. ve 3. derece domino etkileri
        "inversion",          # Ters çevir: başarısızlık koşullarını tanımla
        "bayesian_update",    # Yeni kanıt eski inancı nasıl güncelliyor?
        "narrative_lens",     # Hangi hikaye anlatılıyor, gerçek hikaye ne?
        "systems_lens",       # Geri bildirim döngüleri, kaldıraç noktaları
        "optionality",        # Pozitif simetri — sınırlı kayıp, sınırsız kazanç
        "steelman",           # En güçlü karşı argüman nedir?
        "arbitrage_lens",     # Nerede asimetri var? Kim fiyatsız bilgiye sahip?
        "velocity_lens",      # Hangi fikir/teknoloji en hızlı ivme kazanıyor?
        "decay_lens",         # Hangi sistem/paradigma çözülüyor?
        "singularity_lens",   # Hangi fikir 10x büyümeye işaret ediyor?
        "sunzi_lens",         # Rakip körken nereye konuşlan? Boşluğu doldur.
    ]

    # ─── DOMAIN ROTASYON TABLOSU ──────────────────────────────────────────────
    # Her gün 2-3 farklı domain kombine edilir
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

    # ─── ARAMA MODLARı ─────────────────────────────────────────────────────────
    SEARCH_MODES = [
        "bleeding_edge_papers",       # Son arxiv/preprint bulguları
        "smart_money_footprint",       # Balina/VC para hareketleri
        "developer_velocity",          # GitHub star patlamaları, yeni kütüphaneler
        "niche_community_signal",      # Reddit/Discord/HN niche konuşmaları
        "regulatory_shadow",           # Yaklaşan düzenleme/ban/onay sinyalleri
        "cross_domain_collision",      # 2 farklı alanın beklenmedik kesişimi
        "contrarian_data_point",       # Mainstream inanca ters kanıt
        "founder_intelligence",        # Kurucuların yaptıkları, söyledikleri
        "patent_signal",               # Yakın dönem patent başvuruları
        "acquisition_radar",           # M&A sinyalleri, stratejik satın almalar
        "talent_flow",                 # Yeteneklerin hangi şirkete aktığı
    ]

    # ─── HAFTA İÇİ BAĞLAMSAL ODAKLAR ─────────────────────────────────────────
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
    def today_vector(cls) -> DailyVector:
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

        # Haftalık bağlam bazlı domain ek ağırlığı
        if weekday == "Cumartesi":
            if "Longevity_Biotech" not in domain_combo:
                domain_combo = ["Longevity_Biotech", "Cognitive_Enhancement"]
        elif weekday == "Pazar":
            if "Quantum_Advanced_Computing" not in domain_combo:
                domain_combo = ["Quantum_Advanced_Computing", "AI_Systems_Architecture"]
        elif weekday == "Perşembe":
            if "Crypto_DeFi" not in domain_combo:
                domain_combo = ["Crypto_DeFi"] + [d for d in domain_combo if d != "Crypto_DeFi"][:2]

        return DailyVector(
            temporal_lens=temporal,
            cognitive_frame=cognitive,
            domain_focus=domain_combo,
            search_mode=search_mode,
            weekday=weekday,
            hour=now.hour,
            day_of_year=day_of_year,
            days_left_year=days_left_year,
            week_number=now.isocalendar()[1],
            primary_domain=domain_combo[0],
            secondary_domain=domain_combo[1] if len(domain_combo) > 1 else domain_combo[0],
        )

    @classmethod
    def weekday_context(cls, weekday: str) -> str:
        return cls.WEEKDAY_CONTEXT.get(weekday, "Odaklan ve üret.")

    @classmethod
    def domain_topics(cls, domain_name: str) -> list[str]:
        """Belirli bir domain'in konularını döndür."""
        domain_data = USER["knowledge_domains"].get(domain_name, {})
        return domain_data.get("topics", [])

    @classmethod
    def all_domain_topics(cls, domain_names: list[str]) -> dict[str, list[str]]:
        """Birden fazla domain'in konularını döndür."""
        result = {}
        for name in domain_names:
            topics = cls.domain_topics(name)
            if topics:
                result[name] = topics
        return result

    @classmethod
    def format_vector_info(cls, vector: DailyVector) -> str:
        """Vektör bilgisini insan-okunabilir formatta döndür."""
        return (
            f"📅 {vector['weekday']} · Gün {vector['day_of_year']}/365 · Hafta {vector['week_number']}\n"
            f"🔭 Zaman: <code>{vector['temporal_lens']}</code>\n"
            f"🧠 Çerçeve: <code>{vector['cognitive_frame']}</code>\n"
            f"🎯 Domain: <code>{' | '.join(vector['domain_focus'])}</code>\n"
            f"🔍 Mod: <code>{vector['search_mode']}</code>\n"
            f"⏳ Yıla {vector['days_left_year']} gün kaldı"
        )
