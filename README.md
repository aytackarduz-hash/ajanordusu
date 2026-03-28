# ⚡ NEXA DEEP INTELLIGENCE v5.0

**Yiğit Narin için Kişisel Stratejik İstihbarat Sistemi**

```
PropTech × AI Security × Solopreneurship
9-Ajan Pipeline · Google Grounding · SQLite Hafıza · Telegram Bot
```

---

## 🏗️ Mimari

```
nexa_intel/
├── main.py                 # Giriş noktası, bot + zamanlayıcı
├── config.py               # Konfigürasyon + kullanıcı profili
├── memory.py               # SQLite hafıza motoru
├── diversity_engine.py     # Günlük keşif vektörü
├── data_mesh.py            # Async veri toplama (RSS, API, GitHub, HN)
├── agents.py               # 9 uzman ajan
├── intelligence_engine.py  # Orkestratör
├── telegram_bot.py         # Bot komutları ve mesaj gönderimi
├── report_builder.py       # Telegram HTML format
├── requirements.txt
├── .env.example
└── nexa_memory.db          # (Otomatik oluşur)
```

---

## 🤖 Ajanlar (9 Adet)

| Ajan | Görev |
|------|-------|
| ⏱️ Temporal Arbitraj | 48 saatlik fırsat pencereleri |
| 🔄 Kontra-Sentiment | Konsensus yanılgılarını tespit |
| 🔮 Zayıf Sinyal Konverjans | 3+ alandan aynı yönü gösteren sinyaller |
| 🧬 Bilişsel Kenar Protokolü | Ampirik bilişsel/longevity optimizasyon |
| 🌀 Sistem Çözülme | Dönüşen sistemler, first-mover fırsatı |
| 🚀 Narratif Velocity | Niche→mainstream geçiş takibi |
| 🔬 Derin Bilim Atılımı | Paradigma kıran bilimsel bulgular |
| 🏢 PropTech OSINT | Türkiye PropTech × AI fırsatları |
| 🗡️ Stratejik Silah | Tüm ajanların sentezi + günün komutu |

---

## 🌐 Veri Kaynakları (20+ Kaynak)

**Akademi:** arXiv (AI, ML, Neuro, Quantum, Bio), bioRxiv, Nature  
**Teknoloji:** TechCrunch, Ars Technica, MIT Tech Review, Wired, The Verge  
**Kripto:** CoinDesk, The Block, Decrypt, CoinTelegraph  
**Frontier:** Singularity Hub, Futurism, Longevity.Technology  
**İş:** HBR, Stratechery  
**Piyasa:** CoinGecko (fiyatlar, trending, F&G, global stats)  
**Dev:** GitHub Trending, HackerNews Top Stories  

---

## 🔧 Kurulum

### 1. Python Ortamı

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# veya: venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. API Anahtarları

#### Gemini API
1. https://aistudio.google.com → API Keys → Create API Key
2. `.env` dosyasına yaz: `GEMINI_API_KEY=your_key`

#### Telegram Bot
1. Telegram'da @BotFather → `/newbot` → isim ver
2. Verilen token'ı kopyala: `TELEGRAM_BOT_TOKEN=token`

#### Chat ID
1. Botuna herhangi bir mesaj gönder
2. Tarayıcıda aç: `https://api.telegram.org/bot{TOKEN}/getUpdates`
3. `"chat":{"id": XXXXXX}` — bu sayıyı kopyala
4. `.env`: `TELEGRAM_CHAT_ID=XXXXXX`

### 3. Ortam Dosyası

```bash
cp .env.example .env
# .env dosyasını düzenle, API anahtarlarını gir
```

### 4. Test

```bash
# Veri toplama testi (API key gerektirmez)
python main.py --mode dry-run

# Tek ajan testi
python main.py --mode test-agent --agent temporal

# Mevcut ajanlar: temporal, contra, weak_signal, cognitive,
#                  systems, narrative, deep_science, proptech

# Tam rapor testi (Telegram'a göndermez)
python main.py --mode test-report
```

### 5. Çalıştırma

```bash
# Normal mod (Bot + Zamanlayıcı)
python main.py

# veya
python main.py --mode run
```

---

## 📱 Telegram Komutları

| Komut | Açıklama |
|-------|----------|
| `/report` | Tam 9-ajan raporu oluştur (~2-4 dk) |
| `/quick` | Hızlı Stratejik Silah özeti |
| `/status` | Sistem durumu ve son çalışma |
| `/memory` | Hafıza özeti (kapsanan kavramlar) |
| `/vector` | Bugünün keşif vektörü |
| `/help` | Yardım mesajı |

---

## 🔁 Çeşitlilik Motoru

Sistem her gün farklı bir **bilişsel çerçeve** (14 seçenek), **domain odağı** (14 rotasyon), ve **arama modu** (11 seçenek) kullanır.

- Son 14 günde kapsanan kavramlar hafızada tutulur
- Ajanlar bu kavramları tekrar etmekten kaçınır
- Hafta içi bağlamsal odak: Perşembe→Kripto, Cumartesi→Longevity, Pazar→Derin Bilim

---

## 🖥️ Sunucu / VPS Kurulumu (7/24)

```bash
# systemd service dosyası oluştur
sudo nano /etc/systemd/system/nexa-intel.service
```

```ini
[Unit]
Description=Nexa Deep Intelligence v5.0
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/nexa_intel
Environment=PATH=/home/ubuntu/nexa_intel/venv/bin
ExecStart=/home/ubuntu/nexa_intel/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable nexa-intel
sudo systemctl start nexa-intel
sudo systemctl status nexa-intel

# Logları izle
journalctl -u nexa-intel -f
```

---

## 📦 Docker (Opsiyonel)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

```bash
docker build -t nexa-intel .
docker run -d --env-file .env -v $(pwd)/nexa_memory.db:/app/nexa_memory.db nexa-intel
```

---

## ⚙️ Konfigürasyon Özelleştirme

`config.py` dosyasındaki `USER` dict'ini düzenleyerek:
- Yeni projeler ekle (`active_projects`)
- Domain konularını güncelle (`knowledge_domains`)
- Stratejik hedefleri güncelle (`strategic_goals`)
- Rapor saatini değiştir (`.env`: `DAILY_HOUR=7`)

---

## 🛠️ Sorun Giderme

**"GEMINI_API_KEY ayarlanmamış" hatası:**
→ `.env` dosyasının `nexa_intel/` klasöründe olduğunu kontrol et

**"No candidates returned" hatası:**
→ Gemini API kotasını kontrol et (ücretsiz limit: 15 istek/dakika)

**Telegram mesaj gelmiyor:**
→ `TELEGRAM_CHAT_ID`'nin doğru olduğunu kontrol et
→ Bot'a daha önce mesaj gönderdin mi? (Bot önce kullanıcıdan mesaj almalı)

**Rate limit hatası (503/429):**
→ `config.py` → `AGENT_CONCURRENCY=2` olarak düşür
→ `RETRY_DELAY_S=3.0` olarak artır

---

*FOR YIĞIT NARİN ONLY · NEXA HQ · v5.0 · MART 2026*
