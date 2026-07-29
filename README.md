# clarify-prompt

Ham, dağınık, eksik bağlamlı istekleri; hedef bir büyük dil modelinin (Claude Code, ChatGPT, Cursor…) tam anlayacağı, yapılandırılmış prompta çeviren küçük ve açık kaynak bir yapay zeka.

Yani: sen kısaca "şu bug'ı çöz" dediğinde, arada duran bu model isteği düzeltip hedef LLM'e "Görev / Bağlam / Kabul kriterleri / Format" iskeletinde tam donanımlı bir prompt hazırlar. Sonuç: hedef LLM ilk denemede istediğin cevabı üretir, sen üç tur boş yere yazışmazsın.

## Durum

Proje şu an **Faz 0 — kurulum ve dry-run** aşamasında. Eğitim, değerlendirme ve release henüz yok; MVP planı [PLAN.md](PLAN.md) altında (2200+ satır, 20 bölüm).

## Ne için, ne için değil

**Kullanabileceğin yerler**
- Claude Code'a yarım-yamalak istek yazıp tur harcamak yerine, önce `clarify-prompt` üzerinden geçirmek.
- ChatGPT / Cursor gibi araçlara verilecek uzun ve dağınık isteği yapılandırmak.
- Offline / uçak modunda promptu düzenlemek (hedef LLM sonradan online kullanılır).

**Kullanmayacağın yerler**
- Hedef LLM'in cevabının doğruluğunu garantilemez; sadece isteğin netliğini artırır.
- Prompt injection / jailbreak filtresi değildir — o güvenlik hedef modelin sorumluluğu.
- Kişisel bilgi (şifre, e-posta içeriği) tarayıcı değildir; hassas veriyi elle sansürle.

## Kurulum (MVP hazır olduğunda)

Şimdilik iskelet var; model henüz eğitilmedi. Faz 4 sonrası bu bölüm gerçek komutlarla dolacak. Planlanan akış:

```bash
pip install clarify-prompt
# GGUF model dosyasını Hugging Face Hub'dan indir:
huggingface-cli download clarify/clarify-prompt-qwen2.5-7b-v1 --local-dir ~/.clarify-prompt/models
export CLARIFY_PROMPT_MODEL_PATH=~/.clarify-prompt/models/clarify-prompt-qwen2.5-7b-q4_k_m.gguf
```

## Kullanım (planlanan)

```bash
clarify-prompt "reflection kodu yeni sürümde patlıyor, düzelt"
```

Çıktı olarak temizlenmiş, yapılandırılmış bir prompt — hedef LLM'e (Claude Code, ChatGPT, Cursor) yapıştırılmaya hazır.

Farklı hedef LLM için profil:

```bash
clarify-prompt --target chatgpt "long messy request..."
clarify-prompt --target cursor "bu component'i temizle"
echo "uzun karışık istek" | clarify-prompt --stdin --target claude-code
```

## Nasıl çalışır (özet)

- **Base model:** Qwen 2.5 7B Instruct (yedek Phi-4-mini 3.8B).
- **Eğitim:** LoRA r=16 + 4-bit NF4 (QLoRA) — Unsloth framework'ü ile. RTX 4060 8GB VRAM'e sığar.
- **Veri seti:** yaklaşık 1500-2500 örnek — %20 gerçek transkript, %60 teacher distillation (Claude Opus 4.7), %20 el yapımı altın örnek. Türkçe + İngilizce.
- **Değerlendirme:** LLM-as-judge (Prometheus 2) + insan spot-check. Kabul eşiği: test setinde %65+ kazanma.
- **Dağıtım:** HF Hub'da adapter + GGUF, GitHub'da kod. Lokal `llama.cpp` ile çıkarım.

Tam teknik ayrıntı: [PLAN.md](PLAN.md).

## Klasör düzeni

```
clarify-prompt/
├── src/clarify_prompt/   # inference paketi (kullanıcının kurduğu)
├── training/             # eğitim pipeline (proje geliştiricisinin)
├── tests/                # birim + entegrasyon testleri
├── bench/                # gecikme + bellek ölçümleri
├── docs/                 # QUICKSTART, MODEL_CARD, TRAINING, EVAL, TARGETS
└── PLAN.md               # tam uygulama planı (2200+ satır)
```

## Katkı

MVP hazır olana kadar tek geliştirici (kişisel proje). MVP sonrası GitHub Issues + PR açıktır. Katkı rehberi `CONTRIBUTING.md` içinde (henüz yazılmadı).

## Lisans

- Kod: [MIT](LICENSE)
- Model ağırlıkları (Hugging Face'te yayınlanınca): [Apache-2.0](LICENSE-model) — base modelin (Qwen 2.5) lisansına saygı.

## clarify ailesi

Bu proje "clarify" adında AI aracı serisinin ilki. Sonrası: fikirler `PLAN.md` §19'da.

---

**Ana belge:** [PLAN.md](PLAN.md) — 2200+ satır uygulama planı, 20 bölüm, ağaç motoru çıktısı ile.
