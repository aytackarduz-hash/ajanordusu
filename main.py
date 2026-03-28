"""
NEXA DEEP INTELLIGENCE v5.0 — main.py
Ana giriş noktası. Telegram bot + APScheduler.
Hem manuel (/report komutu) hem otomatik (günlük 09:00) çalışır.
"""

import asyncio
import logging
import sys
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import config
from intelligence_engine import IntelligenceEngine
from memory import MemoryEngine, memory as global_memory
from telegram_bot import NexaBot

# ─────────────────────────────────────────────────────────────────────────────
# LOGLAMA KURULUMU
# ─────────────────────────────────────────────────────────────────────────────
def setup_logging():
    fmt = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
    ]

    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
        format=fmt,
        datefmt=datefmt,
        handlers=handlers,
    )

    # Sessiz loggerlar
    for quiet in ["httpx", "httpcore", "telegram", "apscheduler"]:
        logging.getLogger(quiet).setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info("Loglama sistemi başlatıldı.")
    return logger


# ─────────────────────────────────────────────────────────────────────────────
# ZAMANLI RAPOR JOB'U
# ─────────────────────────────────────────────────────────────────────────────
async def scheduled_report_job(bot: NexaBot, mem: MemoryEngine):
    """APScheduler tarafından her gün çağrılan job."""
    logger = logging.getLogger("scheduler")
    logger.info(f"⏰ Zamanlanmış rapor başlıyor: {datetime.now().strftime('%H:%M')}")

    engine = IntelligenceEngine(mem)
    try:
        result = await engine.run(triggered_by="schedule")
        avg_q = await mem.avg_quality(10)
        await bot.send_scheduled_report(result, avg_quality_10d=avg_q)
        logger.info("✅ Zamanlanmış rapor başarıyla gönderildi.")
    except Exception as e:
        logger.error(f"❌ Zamanlanmış rapor hatası: {e}", exc_info=True)
        # Hata bildirimi gönder
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


# ─────────────────────────────────────────────────────────────────────────────
# DOĞRULAMA
# ─────────────────────────────────────────────────────────────────────────────
def validate_config() -> list[str]:
    errors = []
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "":
        errors.append("GEMINI_API_KEY ayarlanmamış!")
    if not config.TELEGRAM_BOT_TOKEN or config.TELEGRAM_BOT_TOKEN == "":
        errors.append("TELEGRAM_BOT_TOKEN ayarlanmamış!")
    if not config.TELEGRAM_CHAT_ID:
        print("⚠️  UYARI: TELEGRAM_CHAT_ID ayarlanmamış. Zamanlanmış raporlar gönderilemez.")
    return errors


# ─────────────────────────────────────────────────────────────────────────────
# ANA DÖNGÜ
# ─────────────────────────────────────────────────────────────────────────────
async def main():
    logger = setup_logging()

    logger.info("=" * 60)
    logger.info("  NEXA DEEP INTELLIGENCE v5.0 BAŞLATIYOR")
    logger.info(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Konfigürasyon doğrulama
    errors = validate_config()
    if errors:
        for err in errors:
            logger.critical(f"KONFİGÜRASYON HATASI: {err}")
        logger.critical(".env dosyasını kontrol et ve tekrar dene.")
        sys.exit(1)

    # Hafıza başlatma
    await global_memory.init()
    logger.info("✅ Hafıza motoru başlatıldı.")

    # Bot oluşturma
    bot = NexaBot(global_memory)
    app = bot.build()

    # Zamanlayıcı kurulumu
    scheduler = AsyncIOScheduler(timezone="Europe/Istanbul")
    scheduler.add_job(
        scheduled_report_job,
        CronTrigger(
            hour=config.DAILY_HOUR,
            minute=config.DAILY_MINUTE,
            timezone="Europe/Istanbul",
        ),
        id="daily_report",
        name=f"Günlük Rapor ({config.DAILY_HOUR:02d}:{config.DAILY_MINUTE:02d})",
        args=[bot, global_memory],
        max_instances=1,
        misfire_grace_time=300,  # 5 dakika gecikme toleransı
    )
    scheduler.start()
    logger.info(
        f"✅ Zamanlayıcı başlatıldı: her gün "
        f"{config.DAILY_HOUR:02d}:{config.DAILY_MINUTE:02d} Türkiye saati"
    )

    # Bir sonraki çalışma zamanını göster
    job = scheduler.get_job("daily_report")
    if job and job.next_run_time:
        logger.info(f"📅 Sonraki çalışma: {job.next_run_time.strftime('%Y-%m-%d %H:%M %Z')}")

    logger.info("🤖 Telegram bot polling başlatılıyor...")
    logger.info("Hazır! /report komutuyla manuel rapor alabilirsin.")
    logger.info("-" * 60)

    # Bot'u başlat (PTB v21+ async pattern — event loop çakışmasını önler)
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        logger.info("✅ Bot polling aktif. Durdurmak için Ctrl+C.")
        # Sonsuz döngü — scheduler ve polling birlikte çalışır
        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logger.info("⛔ Kapatılıyor...")
        finally:
            scheduler.shutdown(wait=False)
            await app.updater.stop()
            await app.stop()


# ─────────────────────────────────────────────────────────────────────────────
# CLI ARAÇLARI (Geliştirme/Test)
# ─────────────────────────────────────────────────────────────────────────────
async def dry_run():
    """Bot olmadan sadece veri toplama ve ajan testini çalıştır."""
    logger = setup_logging()
    logger.info("🔧 DRY RUN modu başlatıldı (Telegram yok)")

    await global_memory.init()

    from data_mesh import DataMesh

    dm = DataMesh()
    bundle = await dm.fetch_all()
    await dm.close()

    print(f"\n📊 Veri Özeti:")
    print(f"  Intel items: {len(bundle.intel)}")
    print(f"  Dev velocity: {len(bundle.dev_velocity)}")
    print(f"  HN stories: {len(bundle.hn_signal)}")
    print(f"  Prices: {bool(bundle.market.get('prices'))}")
    print(f"  Fear&Greed: {bundle.market.get('fear_greed', [{}])[0].get('value_classification', '?')}")

    from diversity_engine import DiversityEngine
    vector = DiversityEngine.today_vector()
    print(f"\n🔭 Bugünün Vektörü:")
    print(f"  Lens: {vector['temporal_lens']}")
    print(f"  Frame: {vector['cognitive_frame']}")
    print(f"  Domain: {vector['domain_focus']}")
    print(f"  Mode: {vector['search_mode']}")
    print(f"  Weekday: {vector['weekday']}")

    print("\n✅ Dry run tamamlandı.")


async def test_single_agent(agent_key: str = "temporal"):
    """Tek bir ajanı test et."""
    logger = setup_logging()
    logger.info(f"🧪 Ajan test: {agent_key}")

    await global_memory.init()

    from agents import AGENT_DEFINITIONS, AgentContext
    from data_mesh import DataMesh
    from diversity_engine import DiversityEngine
    from datetime import datetime

    dm = DataMesh()
    bundle = await dm.fetch_all()
    await dm.close()

    vector = DiversityEngine.today_vector()
    now = datetime.now()
    ctx = AgentContext(
        bundle=bundle,
        vector=vector,
        avoid_concepts=[],
        insights={},
        date_str=now.strftime("%d %B %Y"),
        time_str=now.strftime("%H:%M"),
    )

    defn = next((d for d in AGENT_DEFINITIONS if d["key"] == agent_key), None)
    if not defn:
        print(f"Ajan bulunamadı: {agent_key}")
        print(f"Mevcut ajanlar: {[d['key'] for d in AGENT_DEFINITIONS]}")
        return

    agent = defn["class"]()
    result = await agent.run(ctx)
    await agent.close()

    print(f"\n{'='*60}")
    print(f"AJAN: {defn['label']}")
    print(f"ÇIKTI ({len(result)} karakter):")
    print(f"{'='*60}")
    # HTML etiketleri olmadan göster
    import re
    plain = re.sub(r"<[^>]+>", "", result)
    print(plain[:2000])


# ─────────────────────────────────────────────────────────────────────────────
# GİRİŞ NOKTASI
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Nexa Deep Intelligence v5.0")
    parser.add_argument(
        "--mode",
        choices=["run", "dry-run", "test-agent", "test-report"],
        default="run",
        help="Çalışma modu",
    )
    parser.add_argument(
        "--agent",
        default="temporal",
        help="test-agent modu için ajan anahtarı",
    )
    args = parser.parse_args()

    if args.mode == "run":
        asyncio.run(main())
    elif args.mode == "dry-run":
        asyncio.run(dry_run())
    elif args.mode == "test-agent":
        asyncio.run(test_single_agent(args.agent))
    elif args.mode == "test-report":
        async def _test_report():
            await global_memory.init()
            engine = IntelligenceEngine(global_memory)
            result = await engine.run(triggered_by="test")
            await engine.close()
            from report_builder import build_telegram_messages
            messages = build_telegram_messages(result)
            print(f"\n✅ {len(messages)} mesaj oluşturuldu.")
            for i, msg in enumerate(messages):
                print(f"\n--- MESAJ {i+1} ({len(msg)} karakter) ---")
                import re
                print(re.sub(r"<[^>]+>", "", msg)[:500])
        asyncio.run(_test_report())