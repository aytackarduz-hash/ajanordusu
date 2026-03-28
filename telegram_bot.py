"""
NEXA DEEP INTELLIGENCE v5.0 — telegram_bot.py
Telegram bot: komut işleme, rapor gönderme, mesaj bölme.
"""

import asyncio
import logging
from datetime import datetime

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import config, USER
from diversity_engine import DiversityEngine
from intelligence_engine import IntelligenceEngine
from memory import MemoryEngine
from report_builder import (
    build_help_message,
    build_memory_message,
    build_status_message,
    build_telegram_messages,
    clean_agent_output,
    split_message,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# YETKİLENDİRME KONTROLÜ
# ─────────────────────────────────────────────────────────────────────────────
def is_authorized(update: Update) -> bool:
    """Sadece konfigüre edilmiş chat_id'ye izin ver."""
    if not config.TELEGRAM_CHAT_ID:
        return True  # Chat ID ayarlanmamışsa herkese açık
    user_id = str(update.effective_chat.id)
    return user_id == config.TELEGRAM_CHAT_ID


# ─────────────────────────────────────────────────────────────────────────────
# MESAJ GÖNDERİCİ
# ─────────────────────────────────────────────────────────────────────────────
async def send_messages(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    messages: list[str],
    parse_mode: str = ParseMode.HTML,
):
    """Mesaj listesini sırayla gönder, rate limit için bekle."""
    chat_id = update.effective_chat.id
    for i, msg in enumerate(messages):
        if not msg.strip():
            continue
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=msg,
                parse_mode=parse_mode,
                disable_web_page_preview=True,
            )
            if i < len(messages) - 1:
                await asyncio.sleep(0.5)  # Rate limit koruma
        except Exception as e:
            logger.error(f"Mesaj gönderme hatası (mesaj {i+1}): {e}")
            # HTML parse hatası ise düz metin dene
            try:
                plain = msg.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "").replace("<code>", "").replace("</code>", "").replace("<blockquote>", "").replace("</blockquote>", "")
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=plain[:4000],
                    disable_web_page_preview=True,
                )
            except Exception as e2:
                logger.error(f"Düz metin gönderme de başarısız: {e2}")


async def send_typing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yazıyor... göster."""
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing",
    )


# ─────────────────────────────────────────────────────────────────────────────
# KOMUT HANDLERLARı
# ─────────────────────────────────────────────────────────────────────────────
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
    """Tam 9-ajan raporu oluştur ve gönder."""
    if not is_authorized(update):
        await update.message.reply_text("⛔ Yetkisiz erişim.")
        return

    await send_typing(update, context)
    start_msg = await update.message.reply_text(
        "🚀 <b>Nexa Deep Intelligence v5.0 başlatılıyor...</b>\n"
        "9 ajan eş zamanlı çalışacak. ~2-4 dakika sürebilir.",
        parse_mode=ParseMode.HTML,
    )

    memory = context.bot_data.get("memory")
    engine = IntelligenceEngine(memory)

    progress_messages = []

    def on_progress(msg: str):
        progress_messages.append(msg)
        logger.info(msg)

    try:
        result = await engine.run(triggered_by="telegram_command", progress_callback=on_progress)
        await engine.close()

        avg_q = await memory.avg_quality(10)
        messages = build_telegram_messages(result, avg_quality_10d=avg_q)

        # Başlangıç mesajını sil
        try:
            await start_msg.delete()
        except Exception:
            pass

        await send_messages(update, context, messages)
        logger.info(f"Rapor gönderildi: {len(messages)} mesaj")

    except Exception as e:
        logger.error(f"Rapor hatası: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ <b>Rapor oluşturulurken hata:</b>\n<code>{str(e)[:300]}</code>",
            parse_mode=ParseMode.HTML,
        )


async def cmd_quick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sadece Stratejik Silah çalıştır (hızlı özet)."""
    if not is_authorized(update):
        return

    await send_typing(update, context)
    await update.message.reply_text(
        "⚡ <b>Hızlı Stratejik Özet hazırlanıyor...</b>",
        parse_mode=ParseMode.HTML,
    )

    from agents import AgentContext, StrategicWeaponAgent
    from data_mesh import DataBundle

    memory = context.bot_data.get("memory")
    vector = DiversityEngine.today_vector()
    now = datetime.now()

    ctx = AgentContext(
        bundle=DataBundle(),
        vector=vector,
        avoid_concepts=[],
        insights={},
        date_str=now.strftime("%d %B %Y %A"),
        time_str=now.strftime("%H:%M"),
    )

    try:
        agent = StrategicWeaponAgent()
        result = await agent.run(ctx)
        await agent.close()

        cleaned = clean_agent_output(result)
        for part in split_message(cleaned):
            await send_messages(update, context, [part])
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)[:200]}", parse_mode=ParseMode.HTML)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    memory: MemoryEngine = context.bot_data.get("memory")
    summary = await memory.summary()
    vector = DiversityEngine.today_vector()
    msg = build_status_message(summary, dict(vector))
    await send_messages(update, context, [msg])


async def cmd_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    memory: MemoryEngine = context.bot_data.get("memory")
    concepts = await memory.recent_concepts(config.DIVERSITY_WINDOW_DAYS)
    domain_focuses = await memory.recent_domain_focuses(7)
    msg = build_memory_message(concepts, domain_focuses)
    await send_messages(update, context, [msg])


async def cmd_vector(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bugünün keşif vektörünü göster."""
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


# ─────────────────────────────────────────────────────────────────────────────
# BOT UYGULAMASI
# ─────────────────────────────────────────────────────────────────────────────
class NexaBot:
    def __init__(self, memory: MemoryEngine):
        self.memory = memory
        self.app: Application | None = None

    def build(self) -> Application:
        self.app = (
            Application.builder()
            .token(config.TELEGRAM_BOT_TOKEN)
            .build()
        )

        # Hafızayı bot_data'ya ekle
        self.app.bot_data["memory"] = self.memory

        # Komutları kaydet
        self.app.add_handler(CommandHandler("start",   cmd_start))
        self.app.add_handler(CommandHandler("help",    cmd_help))
        self.app.add_handler(CommandHandler("report",  cmd_report))
        self.app.add_handler(CommandHandler("quick",   cmd_quick))
        self.app.add_handler(CommandHandler("status",  cmd_status))
        self.app.add_handler(CommandHandler("memory",  cmd_memory))
        self.app.add_handler(CommandHandler("vector",  cmd_vector))
        self.app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

        logger.info("Telegram bot oluşturuldu.")
        return self.app

    async def send_scheduled_report(self, result: dict, avg_quality_10d: str = "?"):
        """Zamanlayıcıdan tetiklenen raporu gönder."""
        if not config.TELEGRAM_CHAT_ID:
            logger.warning("TELEGRAM_CHAT_ID ayarlanmamış, zamanlı rapor gönderilemedi.")
            return

        messages = build_telegram_messages(result, avg_quality_10d=avg_quality_10d)
        for i, msg in enumerate(messages):
            if not msg.strip():
                continue
            try:
                await self.app.bot.send_message(
                    chat_id=config.TELEGRAM_CHAT_ID,
                    text=msg,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
                if i < len(messages) - 1:
                    await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Zamanlı rapor mesaj {i+1} hatası: {e}")
        logger.info(f"Zamanlı rapor gönderildi: {len(messages)} mesaj")
