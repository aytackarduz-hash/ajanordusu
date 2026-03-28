"""
NEXA DEEP INTELLIGENCE v5.0 — intelligence_engine.py
Ana orkestratör. Tüm ajanları çalıştırır, kaliteyi değerlendirir, hafızayı günceller.
"""

import asyncio
import logging
from datetime import datetime
from typing import Callable

from agents import (
    AGENT_DEFINITIONS,
    AgentContext,
    QualityEvaluator,
    StrategicWeaponAgent,
)
from config import config, USER
from data_mesh import DataMesh, bundle_summary
from diversity_engine import DiversityEngine
from memory import MemoryEngine, extract_concepts

logger = logging.getLogger(__name__)


class IntelligenceEngine:
    def __init__(self, memory: MemoryEngine):
        self.memory = memory
        self.data_mesh = DataMesh()

    # ─── ANA ÇALIŞTIRMA ──────────────────────────────────────────────────────
    async def run(
        self,
        triggered_by: str = "schedule",
        progress_callback: Callable[[str], None] | None = None,
    ) -> dict:
        """
        Tam istihbarat döngüsünü çalıştır.
        Döndürür: {"sections": {...}, "quality": {...}, "vector": {...}, "market_summary": str}
        """
        now = datetime.now()
        date_str = now.strftime("%d %B %Y %A")
        time_str = now.strftime("%H:%M")

        def notify(msg: str):
            logger.info(msg)
            if progress_callback:
                progress_callback(msg)

        notify("🚀 Nexa Deep Intelligence v5.0 başlatıldı")

        # ─── VEK TÖR VE HAFIZA ────────────────────────────────────────────
        vector = DiversityEngine.today_vector()
        avoid_concepts = await self.memory.recent_concepts()
        recent_focuses = await self.memory.recent_domain_focuses(7)

        # Eğer son 3 gün içinde aynı domain ağır biçimde kullanıldıysa, hafifçe kaydır
        for domain in list(vector["domain_focus"]):
            if recent_focuses.count(domain) >= 3:
                logger.info(f"Domain {domain} son 3 günde çok kullanıldı, çeşitlilik artırılıyor")

        notify(
            f"📍 Vektör: {vector['cognitive_frame']} | "
            f"{vector['search_mode']} | "
            f"{' + '.join(vector['domain_focus'])}"
        )
        notify(f"🧠 Kaçınılacak kavramlar: {len(avoid_concepts)}")

        # ─── VERİ TOPLAMA ─────────────────────────────────────────────────
        notify("🌐 Veri toplama başlıyor...")
        bundle = await self.data_mesh.fetch_all()
        market_summary = bundle_summary(bundle)
        notify(
            f"📊 Veri hazır: {len(bundle.intel)} haber | "
            f"{len(bundle.dev_velocity)} repo | "
            f"{len(bundle.hn_signal)} HN"
        )

        # ─── AJAN BAĞLAMI ─────────────────────────────────────────────────
        ctx = AgentContext(
            bundle=bundle,
            vector=vector,
            avoid_concepts=avoid_concepts,
            insights={},
            date_str=date_str,
            time_str=time_str,
        )

        # ─── AJANLAR PARALEL ÇALIŞIR (Semaphore ile limitle) ──────────────
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
                    return key, f"<b>{label}</b>\n<i>Ajan geçici olarak kullanılamıyor. Hata: {err_msg[:100]}</i>"

        notify("🤖 8 ajan eş zamanlı başlatılıyor...")
        tasks = [run_agent(defn) for defn in AGENT_DEFINITIONS]
        results = await asyncio.gather(*tasks)

        for key, output in results:
            sections[key] = output
            ctx.insights[key] = output

        # ─── STRATEJİK SİLAH (Tüm ajanlara bağımlı, sonda çalışır) ───────
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

        # ─── KALİTE DEĞERLENDİRME ─────────────────────────────────────────
        notify("🔍 Kalite değerlendiriliyor...")
        all_text = "\n".join(sections.values())
        evaluator = QualityEvaluator()
        quality = await evaluator.evaluate(all_text)
        await evaluator.close()

        avg_q = float(quality.get("average", 7.5))
        await self.memory.log_quality(avg_q, agent="overall")
        notify(f"📈 Kalite: {avg_q:.1f}/10 | En zayıf: {quality.get('weakest', '?')}")

        # ─── HAFIZAYI GÜNCELLE ────────────────────────────────────────────
        concepts = extract_concepts(all_text)
        ts = datetime.utcnow().isoformat()
        await self.memory.save_report(
            ts=ts,
            date_str=date_str,
            quality=avg_q,
            vector=dict(vector),
            concepts=concepts,
            domain_focus=vector["domain_focus"],
            triggered_by=triggered_by,
        )
        notify(f"💾 Hafıza güncellendi: {len(concepts)} kavram kaydedildi")

        # Eski veriyi temizle
        await self.memory.cleanup_old_data(keep_days=90)

        return {
            "sections": sections,
            "quality": quality,
            "vector": dict(vector),
            "market": bundle.market,
            "market_summary": market_summary,
            "date_str": date_str,
            "time_str": time_str,
            "ts": ts,
        }

    async def close(self):
        await self.data_mesh.close()
