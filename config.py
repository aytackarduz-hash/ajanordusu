"""
NEXA DEEP INTELLIGENCE v5.0 — config.py
Tüm konfigürasyon ve kullanıcı profili burada.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# KULLANICI PROFİLİ — Sistemin beyni
# ─────────────────────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────────────────────
# SİSTEM KONFİGÜRASYONU
# ─────────────────────────────────────────────────────────────────────────────
class Config:
    # API Anahtarları
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # Gemini Ayarları
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Sistem
    MAX_RETRIES: int = 3
    RETRY_DELAY_S: float = 2.0
    QUALITY_THRESHOLD: float = 7.0
    MAX_MEMORY_ENTRIES: int = 120
    DIVERSITY_WINDOW_DAYS: int = 14
    REPORT_VERSION: str = "v5.0"

    # Zamanlayıcı
    DAILY_HOUR: int = int(os.getenv("DAILY_HOUR", "9"))
    DAILY_MINUTE: int = int(os.getenv("DAILY_MINUTE", "0"))

    # Veritabanı
    DB_PATH: str = os.getenv("DB_PATH", "nexa_memory.db")

    # HTTP
    HTTP_TIMEOUT: float = 45.0
    AGENT_CONCURRENCY: int = 3  # Eş zamanlı agent sayısı

    # Telegram mesaj ayarları
    TELEGRAM_MAX_CHARS: int = 4000  # 4096 limit, güvenli marj bırak
    TELEGRAM_PARSE_MODE: str = "HTML"

    # Log
    LOG_FILE: str = "nexa_intel.log"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Ajan sıcaklıkları
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
    }

    # Ajan token limitleri
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
    }


config = Config()
