# reprompt

Ham, eksik, tek satırlık istekleri hedef LLM'in tam anlayacağı yapılandırılmış prompta çeviren açık kaynak yapay zeka.

İki model hattı bulunur: yaklaşık 4–5 GiB Qwen 2.5 7B Q4_K_M üretim paketi için QLoRA
ve deneysel 359M parametreli ClarifyGPT scratch mimarisi. Model ağırlıkları depoda yer
almaz; yayımlanmadan önce ayrı değerlendirme raporu gerekir.

---

## Ne yapıyor?

Sen `"şu bug'ı çöz"` yazdığında, reprompt arada durup bu isteği alıyor, ne istediğini anlıyor ve hedef LLM'e (Claude Code, ChatGPT, Cursor) göndermeden önce şu yapıya oturtuyor:

```
Görev → Bağlam → Kısıtlar → Kabul kriterleri → Çıktı formatı
```

Amaç, hedef modelin eksik bağlam yüzünden gereksiz tur harcamasını azaltmak. Araç hedef
modelin doğruluğunu garanti etmez.

## Kısa demo

```bash
# kurulum
pip install reprompt[all]

# CLI ile doğrudan kullanım
reprompt "reflection kodu yeni sürümde patlıyor, düzelt"

# farklı hedef LLM için
reprompt -t chatgpt "write a blog post about SEO"
reprompt -t cursor  "bu component'i temizle"
echo "uzun karışık istek" | reprompt rewrite --stdin -t claude-code

# API sunucusu başlat
reprompt serve --port 8741

# Python SDK
from reprompt import RepromptEngine
engine = RepromptEngine(model="model.gguf")
result = engine.rewrite("login yap", target="claude-code")
```

**Girdi:**
```
reflection kodu yeni sürümde patlıyor, düzelt
```

**Çıktı (claude-code hedefi):**
```xml
<task>
Reflection kodunu yeni Java sürümüne uyarla — mevcut kod derlemede hata veriyor.
</task>

<context>
- Etkilenen dosya(lar): src/main/java/... alt yolunu ver.
- Hedef Java sürümü: JDK 21.
- Compiler output verilmediyse mvn -q -DskipTests package çıktısını iste.
</context>

<constraints>
- Kullanılmayan importları temizle.
- Test varsa geçsin; yoksa değiştirdiğin sınıfa smoke test ekle.
</constraints>

<acceptance>
- mvn -q -DskipTests package başarıyla derlensin.
- Uyarı bırakma.
</acceptance>
```

## Neden reprompt?

| Sorun | reprompt ile |
|---|---|
| "Şunu yap" yazıyorsun, LLM yanlış anlıyor, 3 tur düzeltiyorsun | Prompt optimize ediliyor, LLM ilk seferde doğru çıktı veriyor |
| Her LLM'in farklı prompt stili var (XML, markdown, direktif) | `--target` bayrağıyla hedef LLM'e göre profil seçiliyor |
| Online olmadan prompt düzenleyemiyorsun | Tamamen lokal, offline çalışıyor |
| Büyük modele API çağrısı pahalı, boşa tur harcıyorsun | Küçük lokal model önden çalışıyor, büyük model tek seferde bitiyor |

---

## Model mimarisi

**ClarifyGPT araştırma hattı** — sıfırdan eğitim için tasarlanmış decoder-only transformer:

| Özellik | Değer |
|---|---|
| Toplam parametre | **~359M** |
| Mimari | Decoder-only Transformer |
| Boyut (dim) | 1280 |
| Katman sayısı | 20 |
| Attention başlıkları | 20 (GQA: 4 KV head) |
| FFN gizli boyut | 3456 (SwiGLU) |
| Pozisyon kodlaması | RoPE (θ=10000) |
| Maks. sekans | 1024 token |
| Vocab boyutu | 12.000 (özel BPE tokenizer) |
| Norm | RMSNorm (ε=1e-5) |
| FP16 boyut | ~720 MB |
| Eğitim VRAM | < 7 GB (gradient checkpointing + mixed precision) |

### Neden sıfırdan?

Scratch hattı şu araştırma soruları için tutulur:
- **Görev odaklı mimari:** Prompt dönüştürme spesifik bir görev — genel dil modeli kapasitesi gereksiz ağırlık.
- **Küçük ve hızlı:** 359M parametre, 7B+ fine-tune modellerden 19x daha küçük.
- **Tam kontrol:** Tokenizer, mimari, eğitim süreci — her katmanda optimizasyon mümkün.
- **Lisans temizliği:** Başka modelin ağırlıklarını miras almıyor.

## Eğitim verisi

| Metrik | Değer |
|---|---|
| Sentetik üretim hedefi | **100.000** |
| El yapımı altın örnekler | 50 |
| Augmentation örnekleri | 110+ |
| Sentetik üretim | 100.000 |
| Desteklenen diller | **10** (TR, EN, DE, FR, ES, PT, RU, JA, ZH, KO) |
| Hedef profiller | 9 |
| Veri sızıntısı | Yayın öncesi doğrulama kapısı |
| Train / Val / Test | Veri üretiminden sonra raporlanır |

### Dil dağılımı

| Dil | Kısaltma | Yaklaşık oran |
|---|---|---|
| Türkçe | tr | ~15% |
| İngilizce | en | ~15% |
| Almanca | de | ~10% |
| Fransızca | fr | ~10% |
| İspanyolca | es | ~10% |
| Portekizce | pt | ~10% |
| Rusça | ru | ~10% |
| Japonca | ja | ~8% |
| Çince | zh | ~8% |
| Korece | ko | ~7% |

## Hedef profilleri

| Profil | Stil | Ne zaman |
|---|---|---|
| `claude-code` | XML etiketler (`<task>`, `<context>`, `<constraints>`) | Claude Code veya Claude API kullanırken |
| `chatgpt` | Markdown başlıklar, numaralı acceptance | ChatGPT web/API kullanırken |
| `cursor` | Kısa direktifler, numaralı adımlar, "Do not" listesi | Cursor IDE içinde |
| `generic` | Vendor-neutral, portable, sade yapı | Herhangi bir LLM veya genel amaç |

## Teknik altyapı

- **Tokenizer:** Özel SentencePiece BPE, 12.000 token, 10 dil desteği
- **Eğitim:** PyTorch, mixed precision (FP16), cosine LR scheduler, gradient accumulation
- **Donanım:** RTX 4060 8GB — tam eğitim tek GPU'da
- **Inference:** PyTorch native veya GGUF export (llama.cpp uyumlu)
- **API:** FastAPI REST server, OpenAI-uyumlu endpoint, batch desteği
- **SDK:** Python SDK (`RepromptEngine` sınıfı) — tek satır entegrasyon
- **Docker:** Self-hosting için hazır Dockerfile + docker-compose
- **Dağıtım:** PyPI (`pip install reprompt[all]`) + model ağırlıkları ayrı

## Beklenen metrikler

| Boyut | Baseline (ham prompt) | ClarifyGPT | İyileşme |
|---|---|---|---|
| Yapı skoru | ~15% | >70% | +370% |
| Uzunluk uyumu | ~30% | >80% | +167% |
| Doldurulmuş çıktı | ~40% | >95% | +138% |
| Hedef format uyumu | ~10% | >65% | +550% |

## Klasör düzeni

```
reprompt/
├── src/reprompt/              # inference paketi
│   ├── cli/                   # Click CLI
│   ├── engine/                # llama.cpp + python backend
│   ├── prompts/               # sistem promptu + 4 profil
│   ├── config/                # pydantic v2 config
│   ├── postproc/              # çıktı temizleme
│   └── errors.py              # exception hiyerarşisi
├── training/                  # eğitim pipeline
│   ├── model/                 # ClarifyGPT transformer mimarisi
│   │   ├── config.py          # SMALL/BASE/LARGE/XLARGE konfigürasyonları
│   │   └── transformer.py     # RoPE + GQA + SwiGLU + gradient checkpointing
│   ├── tokenizer/             # SentencePiece BPE eğitimi
│   ├── data/                  # veri üretimi, augmentation, split
│   ├── configs/               # YAML eğitim konfigürasyonları
│   ├── train_scratch.py       # sıfırdan eğitim döngüsü
│   ├── evaluate.py            # test seti değerlendirmesi
│   ├── inference.py           # checkpoint'ten inference
│   └── run_all.py             # tek komutla tam pipeline
├── integrations/              # platform entegrasyonları
│   ├── claude-code/           # CLAUDE.md şablonu
│   ├── chatgpt/               # Custom GPT + OpenAPI spec
│   ├── cursor/                # .cursorrules şablonu
│   ├── grok/                  # xAI Grok entegrasyonu
│   ├── gemini/                # Google Gemini entegrasyonu
│   ├── deepseek/              # DeepSeek entegrasyonu
│   └── generic/               # genel kullanım rehberi
├── tests/                     # 109+ birim + entegrasyon testi
├── bench/                     # gecikme + bellek ölçümleri
├── docs/                      # gold örnekleri, model kartı
├── Dockerfile                 # self-hosting
├── docker-compose.yml         # tek komutla başlatma
└── PLAN.md                    # uygulama planı
```

## Entegrasyon sistemi

Her platformla tak-çalıştır entegrasyon. Üç yol var:

1. **CLI:** `reprompt "istediğin şey"` — doğrudan kullan
2. **API:** `reprompt serve` — self-hosted REST API sunucusu
3. **SDK:** `RepromptEngine(model=...).rewrite(...)` — Python'dan programatik erişim

API'nin OpenAI-uyumlu endpointi var: mevcut araçların base URL'ini değiştirip doğrudan bağlayabilirsin.

Detaylı rehberler `integrations/` klasöründe: Claude Code, ChatGPT, Cursor, Grok, Gemini, DeepSeek.

## Test durumu

- **109 test** (104 `.venv` + 5 skip `.train-venv` bağımlılıkları) — birim + entegrasyon
- Model mimarisi: parametre sayısı, forward/backward pass, weight tying, RoPE, GQA, generate
- Tokenizer: 10 dil round-trip, özel tokenlar, ChatML format, kod parçacıkları
- Veri kalitesi: dil dağılımı, hedef profil dengesi, sızıntı, tekrar kontrolü
- Evaluation: structure_score (4 profil), length_ratio sınır değerleri
- REST API: health, targets, rewrite, batch, OpenAI-compat endpoint
- SDK: RepromptEngine, RewriteResult, batch_rewrite
- CLI: rewrite komutu, serve subcommand, kısayol sözdizimi
- Config, postprocessing, selector testleri

## Lisans

- Kod: [MIT](LICENSE)
- Model ağırlıkları: [Apache-2.0](LICENSE-model)

---

## Yapımcı

**hypline**

- Discord: `hypline`
- E-posta: kemgen01@gmail.com
- GitHub: [github.com/hypline](https://github.com/hypline)

---

> reprompt, prompt mühendisliğini otomatikleştiren açık kaynak bir araçtır.
> Bir sorunuz veya katkınız varsa GitHub Issues veya Discord üzerinden ulaşabilirsiniz.
