# Prompt Engineer AI — Uygulama Planı

> **Kod adı:** `promptsmith` (kesin isim §6-ADR-01'de karara bağlanacak — Kemal onaylamadıkça geçici).
> **Tarih:** 2026-07-17 · **Sahip:** Kemal · **Rapor sürümü:** v1
> **Durum:** Plan aşaması — kod henüz yazılmadı.

Bu belge, ham/eksik kullanıcı promptlarını hedef LLM'lerin (Claude Code, ChatGPT, Cursor
gibi) çok daha iyi anladığı optimize promptlara çeviren, RTX 4060 8GB VRAM üzerinde
QLoRA ile fine-tune edilecek küçük bir açık kaynak LLM projesinin tam uygulama planıdır.
Rapor, ağaç taktiğiyle açılmış plan ağacının 20 bölümlük rapora dikilmiş halidir; §9 (Dosya
Dosya İçerik) ve §12 (Görev Kırılımı) raporun gövdesidir. Kod, dosya adları, komutlar
İngilizce; anlatı Türkçe.

---

## §1 — Yönetici Özeti

Kemal'in isteği şu: kullanıcı Claude Code'a (veya başka bir LLM'e) yarım-yamalak,
sıralamasız, eksik bağlamlı bir istek yazınca, arada duran küçük bir AI bu isteği alsın,
anlasın, hedef LLM'in tam bekleyeceği formatta (net hedef, gerekli bağlam, kabul kriterleri,
örnek çıktı formatı, karşı-örnekler) yeniden yazsın. "Prompt engineer" işini bir insana
yaptırmak yerine, bunu otomatik yapan ayrı bir açık kaynak modeli olsun. Model ayrı bir
süreç, çünkü hedef LLM zaten pahalı (Claude Opus / GPT-4) — küçük ve lokal bir modelin
girdiyi hazırlaması, hedef LLM'in çıktısını daha ilk denemede doğru yakalamasını sağlar;
kullanıcı da tekrar tekrar prompt yazmaktan kurtulur.

MVP'nin sınırı Kemal tarafından net çizildi: donanım RTX 4060 8GB VRAM + 16GB RAM,
model bu donanıma sığmalı, "çok RAM yemesin". Fine-tune eğitiminin sorumluluğu Claude'da
— pipeline, veri seti, hyperparameter, script hepsi bu planda üretiliyor. Entegrasyon (MCP
server, Claude Code plugin, browser extension) MVP kapsamında değil, Faz 2'ye bırakıldı.

Teknik karar özeti — kalıcı seçimler ADR (§6) altında gerekçelendirildi:

- **Base model adayı (birincil):** Qwen 2.5 7B Instruct veya Phi-4-mini 3.8B. İkisi
  arasındaki seçim, veri seti hazırlandıktan sonra 100-örneklik pilot fine-tune ile
  yapılacak (§6-ADR-02). Yedek: Llama 3.2 3B.
- **Fine-tune yöntemi:** QLoRA (4-bit base + LoRA r=16), framework olarak Unsloth
  (RTX 4060 8GB'da 2x hız, %70 daha az VRAM). Axolotl yedek.
- **Veri seti stratejisi:** teacher distillation — güçlü modeller (Claude Opus 4.7,
  DeepSeek V3, Gemini 2.5 Pro) tarafından zenginleştirilmiş (ham → optimize) çiftlerinden
  1500-2500 örnek. Kaynaklar: ShareGPT alt-örneklem + sentetik üretim + Kemal'in kendi
  Claude Code transkriptleri (anonimleştirilmiş).
- **Değerlendirme:** LLM-as-judge (Prometheus 2 tabanlı yerel judge + Claude Opus
  hakemliği) + kullanıcı A/B testi. Metrik: hedef LLM cevabının kabul edilme oranı,
  düzenleme mesafesi, ilk denemede başarma yüzdesi.
- **Inference:** Eğitilmiş adapter LoRA'yı merge edip GGUF (Q4_K_M) formatına çevir,
  llama.cpp ile CLI. vLLM ikincil (daha yüksek throughput isteyenler için).
- **Release:** GitHub (kod, eğitim scriptleri, veri seti şeması) + Hugging Face Hub
  (base + LoRA adapter + merged GGUF). Lisans: kod MIT, model tag'i Apache-2.0
  (base modelin lisansına saygı — Qwen Apache, Phi MIT, Llama community).

Faz haritası kısa: **Faz 0** çevre hazırlık ve dry-run (1-2 gün) → **Faz 1** veri seti
oluşturma ve doğrulama (3-5 gün) → **Faz 2** ilk fine-tune (Qwen 2.5 7B QLoRA, 3 epoch,
~2-4 saat GPU süresi) → **Faz 3** değerlendirme ve iterasyon (2-4 gün, veri seti
zenginleştirme + hyperparam sweep) → **Faz 4** GGUF paketleme + CLI + release (1-2 gün).
Toplam gerçekçi süre: 2-3 hafta yoğun çalışma, 4-5 hafta gevşek tempo.

Kritik başarı ölçütü — MVP başarılı sayılır eğer: (a) 200 test promptundan en az %65'inde
`promptsmith` çıktısı Claude Opus'un doğrudan ham prompta verdiği cevaptan daha iyi
sonuç üretir (LLM-as-judge + Kemal'in gözü ile ölçülür); (b) inference gecikmesi RTX 4060'ta
50-token prompt için < 2 saniye; (c) toplam VRAM tüketimi < 7GB (kullanıcı diğer
uygulamayı çalıştırırken sıkışmasın); (d) tek komutla kurulum (`pip install promptsmith`
veya benzer). Bu dört ölçütten biri karşılanmıyorsa MVP release olmaz, iterasyona döner.

Risk açısından üç şey sürekli izlenecek: (1) veri seti kalitesi — kötü veri = kötü model,
Faz 1'in gecikmesi tüm plana yayılır; (2) base model quantization kaybı — özellikle
Qwen3.5'te QLoRA kalitesi düşüyor (Unsloth doküman uyarısı), Qwen 2.5'e sadık kalıyoruz;
(3) değerlendirme metriği sızıntısı — LLM-as-judge kendi kendini kandırabilir, mutlaka
insan spot-check gerekli. Detaylı risk matrisi §17'de.

Bu özet 10-20 satır yerine daha geniş çıktı — çünkü Kemal'in cevabı stratejik kararların
büyük kısmını Claude'a bıraktı; özetin karar özetiyle başlaması gerekiyor. Sonraki
bölümlerde her karar tek tek gerekçelendirilecek, alternatifleri tartışılacak, iş
kırılımına indirilecek.

---

## §2 — Araştırma ve Konsey Notları

Plan, üç bağımsız kaynağa dayanıyor: (a) 2026 tarihli web literatürü — küçük dil modeli
karşılaştırmaları, QLoRA/Unsloth ekosistemi, LLM-as-judge güncel yaklaşımları; (b) plan
ağacı motoru üzerinden konsey modellerinin (deepseek-flash) üretimi — kök istekten 30 tura
kadar dallanma; (c) Kemal'in doğrudan çevre kısıtları ve tercihleri. Konsey ağaç ham
çıktıları `agac/ham/` altında, denetim için saklanıyor.

### 2.1 — Küçük açık kaynak LLM manzarası (2026 yaz)

Ağustos 2025 - Temmuz 2026 arasında küçük model rekabeti yoğunlaştı. Aday havuzu:

- **Qwen 2.5 ailesi (0.5B / 1.5B / 3B / 7B / 14B Instruct):** çok dilli, JSON çıktı
  konforu yüksek (Qwen 2.5 1.5B ROUGE-L 0.421, %95.7 JSON parse). Apache 2.0 lisans.
  Unsloth desteği tam. RTX 4060 8GB için: 7B QLoRA rahat, 14B sınırda (max_seq_length
  düşürmek gerekebilir).
- **Qwen 3 (0.6B / 1.7B / 4B / 8B / 14B / 32B / MoE 30B-A3B):** en yeni Qwen. 8GB VRAM
  için 4B rahat, 8B sınırda ama Unsloth ile QLoRA çalışıyor. **Uyarı:** Qwen 3.5 için
  Unsloth "yüksek quantization sapması" nedeniyle QLoRA önermiyor — bu proje için
  3.5'ten kaçınıyoruz. Qwen 3 (3.5 değil) uygun.
- **Phi-4-mini 3.8B:** benchmark liderlerinden (MMLU 68%, HumanEval 70%), sub-4B
  sınıfının en akıllısı. MIT lisans. Boyut olarak 4060'a bol bol sığar (~2.5GB VRAM
  4-bit'te). Ancak "instruction rewriting" gibi metin dönüşüm işlerinde Qwen 2.5 7B'nin
  kaba kelime dağarcığı avantajı olabilir — pilot testte kıyaslanacak.
- **Llama 3.2 3B Instruct:** stabil, geniş topluluk. Ama JSON parse rate %47.8-56.5 arası
  — Qwen'e göre zayıf yapılandırılmış çıktı. Llama Community License (ticari kullanımda
  ek şartlar). Yedek olarak tutuluyor.
- **Gemma 3 4B:** RAM verimliliği (4.2GB), Gemma lisansı ticari kullanımda kısıtlı — MVP
  için ideal değil (Kemal MIT/Apache tercih ediyor).

Karar (§6-ADR-02'de detay): **birincil aday Qwen 2.5 7B Instruct, yedek Phi-4-mini
3.8B**. Sebep: (a) Qwen 2.5 iyi bilinen, kararlı, Apache 2.0; (b) 7B parametre "prompt
yeniden yazma" için yeterli soyutlama kapasitesi verir; (c) 4-bit QLoRA'da RTX 4060'a
sığar (~4.5-5.5 GB VRAM + LoRA adaptörü + optimizer state, sınıra yakın ama fizibl);
(d) Phi-4-mini yedek olarak daha küçük, daha hızlı, veri sıkıntısı olursa geçilir.

### 2.2 — QLoRA + Unsloth ekosistemi

Fine-tune tarafında ekosistem net: **Unsloth** birincil, Axolotl yedek.

- Unsloth 2x hız, %70 daha az VRAM iddiası test edilmiş (accuracy kaybı yok).
- Qwen 2.5/3, Llama 3, Phi 4, Gemma 2 için hazır notebook + Colab örnekleri.
- Kurulum: `pip install --upgrade --force-reinstall --no-cache-dir unsloth unsloth_zoo`.
- 4-bit quantization: `load_in_4bit=True` → base modelin bellek kullanımı 4x düşer.
- max_seq_length 2048 (varsayılan 40960 yerine) — bizim prompt uzunluğu ihtiyacımız için
  yeterli (bir prompt genelde < 512 token).
- LoRA hyperparametreler (Unsloth önerisi): rank r=16, alpha=16, dropout=0, target_modules
  q_proj/k_proj/v_proj/o_proj/gate_proj/up_proj/down_proj (tam attention + MLP), 
  learning_rate 2e-4, batch=2 gradient_accumulation=4 (efektif batch 8), 3 epoch.

Alternatif: doğrudan Hugging Face TRL + PEFT stack — kontrol daha çok, hız daha az.
Unsloth'ta bir bug çıkarsa buraya düşülür (kod §9'da hazır). Axolotl multi-GPU için
düşünülür — Kemal'in tek GPU var, bu MVP için gereksiz.

### 2.3 — LLM-as-judge değerlendirme

Değerlendirme MVP'nin bel kemiği. Otomatik metrik olmadan iterasyon körleşir.

- **Prometheus 2** (Kim et al., 2024) — açık kaynak, açık modelleri değerlendirmek için
  eğitilmiş 7B/8x7B judge modeli; proprietary judge'larla yüksek korelasyon (κ 0.6-0.8).
  MVP için birincil judge — kendi hardware'ımızda çalıştırılır, dış API çağrısı yok.
- **G-Eval** stili chain-of-thought skorlama — judge model önce rubric üzerinden düşünür,
  sonra puan verir. DeepEval / MLflow / Langfuse hepsi destekliyor.
- **DeepEval** — 50+ hazır metrik, kod-tabanlı (`assert_test()`), CI'a kolay entegre.
  MVP için değerlendirme çerçevesi olarak seçildi (Langfuse LLM tracing için sonraya
  ertelendi).
- **Claude Opus 4.7 hakemliği** — Prometheus'un kararsız kaldığı örneklerde bir dış
  hakem. Ancak API maliyeti nedeniyle sadece test setinin %10'una uygulanır.
- **Kemal spot-check** — otomatik metriğe güvenmek yetmez; her iterasyonun rastgele
  30-50 örneği Kemal tarafından "iyi/kötü" işaretlenir. Değerlendirme çerçevesi bu
  eşleşmeyi ölçer (judge doğruluğu = judge Kemal ile ne kadar aynı fikirde).

Bias'lar bilinci: **position bias** (aynı cevabı A/B karıştırınca judge tercihi değişebilir
— A/B randomize ediliyor), **verbosity bias** (uzun cevap iyi sanılıyor — rubric bunu
cezalandırır), **self-preference bias** (judge kendi ailesindekini tercih eder —
Prometheus 2 Qwen değil, farklı ailede tercih edildi), **rubric drift** (rubric çok
soyutlaşırsa skor rastgele — rubric operasyonel tanımlarla yazılır).

### 2.4 — Konsey ağacı özeti (Faz 1 çıktı)

Motor kök isteği 4 ana dala açtı: (1) Veri seti tasarımı ve toplama, (2) Base model
seçimi ve fine-tune pipeline, (3) Değerlendirme ve inference altyapısı, (4) Açık kaynak
release ve dokümantasyon. Sonraki turlarda her dal alt görevlere, kararlara, risklere ve
kaynaklara bölündü. Ağacın işlenmiş özeti §7 (mimari), §12 (görev kırılımı), §17 (risk
matrisi) altında dağılıyor. Ham dosyalar `agac/ham/` klasöründe kalıyor — hangi
öneri konseyden hangi turda geldi izlenebilir.

### 2.5 — Var olan prompt-optimizasyon çalışmaları

Alan boş değil, ama benzer bir "genel amaçlı text prompt rewriter" ürünü ortada yok:

- **PromptEnhancer (Hunyuan / Tencent, CVPR 2026):** açık kaynak; ama text-to-image
  için (Kling, Hunyuan gibi görsel modelleri hedefliyor). Teacher distillation (Gemini
  2.5 Pro İngilizce, DeepSeek V3 Çince) + SFT + RL. Bizim metin senaryomuz için doğrudan
  uygun değil ama **veri seti üretim şeması ilham veriyor** — teacher LLM ham
  promptu alır, "chain of thought → optimize prompt" üretir, çift kaydedilir.
- **"Prompt Engineering a Prompt Engineer" (arXiv 2311.05661):** meta-prompting;
  prompt optimizasyonu için kendi meta-promptunu üretme fikri. Bizim işimiz için
  fine-tune yerine prompt engineering ile ne kadar iyi gidilebilir sorusunun cevabı:
  iyi gider ama bir base modelin genel bilgisine sığar; özel bir "prompt engineer"
  modeli fine-tune, meta-prompting'e göre daha tutarlı ve daha hızlı sonuç verir.
- **Google "LLMs as Optimizers" (arXiv 2309.03409):** promptu iyileştirme LLM'i
  optimizasyon problemi olarak formüle ediyor. Bizim MVP'miz için gerekli değil (bu
  bir eğitim döngüsü, tek atım optimize etmek değil), ama Faz 2 (kullanıcı feedback
  ile online iyileştirme) için depoda tutuluyor.

Sonuç: fikir yeni değil, ama Kemal'in belirlediği kesitte (genel amaçlı, açık kaynak,
lokal, küçük, prompt-in / prompt-out CLI) açık bir boşluk var. Rakip yok.

---

## §3 — Mevcut Durum

Bu bölüm "sıfırdan başlıyoruz"un ne kadarının gerçek sıfır olduğunu tespit ediyor —
Kemal'in ortamındaki hangi taşlar zaten yerinde, hangileri yok.

### 3.1 — Donanım envanteri

- **GPU:** RTX 4060 8GB VRAM. CUDA 12.x uyumlu.
- **RAM:** 16GB.
- **Disk:** C: sürücüsü ana; E: takılıp çıkabilen harici (proje asla E:'de tutulmayacak).
- **CPU:** modern x86 (spesifik model önemsiz, PyTorch dataloader için).
- **OS:** Windows 11.

Kısıt analizi:
- **8GB VRAM'ın anlamı:** 4-bit quantization ile 7B model ≈ 4.5-5.5 GB base; LoRA
  adapter ~200MB; optimizer state (paged AdamW 8-bit) ~1-1.5 GB; gradyanlar + activation
  ~1 GB. Toplam ~7-8 GB — sınırda. Batch size 1-2, gradient checkpointing açık, max_seq
  2048 ile sığar. 14B çalışmaz (Unsloth'un T4 16GB'daki 14B çalıştırması bize
  aldatmamalı).
- **16GB RAM:** eğitim sırasında dataloader + tokenizer + swap. Yeterli. Ama Kemal
  aynı anda ComfyUI + tarayıcı çalıştırırsa sıkışabilir — eğitim sırasında ek işler
  kapatılır talimatı Faz 1 dokümanına girecek.
- **Kesintisiz eğitim süresi:** 3 epoch × 1500 örnek × ~2 sn/örnek = ~2.5 saat. Bu süre
  boyunca GPU sadece Unsloth'a. Windows uyku moduna geçmemeli — power settings ayarı.

### 3.2 — Yazılım envanteri

Kemal'in memory kayıtlarına göre mevcut:
- Python 3.14 kurulu (`Workspace\tools` altında).
- Node 24 kurulu (ağaç motoru + JS betikler için).
- JDK 21 + Maven (bu proje için gereksiz).
- ComfyUI + FLUX Kontext + SDXL (görsel üretim; bu proje için ilgisiz ama VRAM'ı
  rakip — eğitim sırasında kapatılır).
- Git.

Eksikler (Faz 0'da kurulacak):
- CUDA Toolkit 12.x + cuDNN + doğru PyTorch (Unsloth otomatik çeker ama sürüm hizası
  sorun çıkarabilir — Windows'ta özellikle).
- Unsloth + `unsloth_zoo` + PEFT + TRL + Transformers + bitsandbytes (Windows'ta
  bitsandbytes tarihsel olarak sorunluydu; 2026'da `bitsandbytes-windows` fork'u veya
  Unsloth'un kendi wheel'ları var — Faz 0 dry-run bunu doğrulayacak).
- llama.cpp (GGUF çevirim ve inference için) — CPU derleme yeterli, GPU offload için
  CUDA build.
- Hugging Face `datasets`, `huggingface_hub`, `hf-transfer` (yükleme hızı için).

### 3.3 — Proje klasörü ve kod tabanı

Şu anda klasör tamamen boş — sadece bu PLAN.md ve `agac/` altındaki ham motor çıktısı
var. Kod, config, veri, script hiçbiri yok. Faz 0'ın ilk günü klasör iskeleti (§9)
oluşturulacak.

### 3.4 — Veri envanteri

Şu anda hiç eğitim verimiz yok. Faz 1'in tamamı bu boşluğu doldurmak için. Kaynak
tercihleri (detay §10):

- **Kemal'in Claude Code oturum transkriptleri:** anonimleştirilerek "ham prompt →
  Claude'un aslında ne beklediği" çiftleri çıkarılabilir. Bu, projenin en özgün ve
  değerli veri kaynağı — çünkü gerçek Kemal-Claude etkileşiminin dağılımını yansıtır.
  Kaynak yol: `~/.claude/projects/*/` altındaki jsonl session dosyaları. Kişisel bilgi
  taraması (dosya yolları, isim, e-posta) zorunlu.
- **Sentetik veri (teacher distillation):** Claude Opus 4.7 veya DeepSeek V3 API'den
  "ham prompt → optimize prompt" örneği ürettirme. Ölçek 1000-1500 örnek. Maliyet
  ~$30-80 (Kemal onaylamadan çekilmeyecek).
- **ShareGPT / Alpaca / Instructions-2M gibi açık datasets:** ham prompt tarafı için
  seed. Ancak "optimize prompt" tarafı bunlarda hazır değil — teacher LLM ile
  zenginleştirilecek.
- **El ile yazılmış altın örnekler:** Kemal ve Claude birlikte 100-200 örneği el ile
  yazacak. Bunlar test setinin çekirdeği olacak (eğitim setine SIZMAYACAK).

### 3.5 — Var olan araç ve şablonlar

- `Workspace\library\templates\`: `discord-bot-node`, `minecraft-paper-plugin`,
  `web-vite-react` şablonları var. Bu proje AI/ML — hiçbiri birebir uymuyor. Yeni bir
  şablon (`ai-ml-python`) proje bittikten sonra buraya geri beslenecek (§18).
- `Workspace\tools\ai-council\council.mjs` + `agac-planla\agac-planla.mjs`: bu planın
  üretiminde kullanıldı. Çalışma dönemi süresince "ikinci görüş" için hazır.
- `dogal-kod` skill + `dogallik-check` aracı: her kod dosyası teslim öncesi tarama.
- `hedef` ve `kontrol` skill'leri: uygulama fazında sırasıyla "durmadan ilerle" ve
  "teslim öncesi kalite kapısı" için kullanılacak.

Sonuç: donanım hazır, yazılım envanterinde bir Faz 0 kurulum ihtiyacı var, kod ve veri
tarafında sıfırdan başlıyoruz.

---

## §4 — Hedefler ve Kapsam

### 4.1 — Birincil hedefler (MVP'de olmak zorunda)

1. Yerel, açık kaynak, küçük bir LLM'i "ham prompt → optimize prompt" işine fine-tune
   et. Sonuç: `promptsmith-qwen2.5-7b-lora-v1` (veya seçilecek base ile eşdeğer isim).
2. Fine-tune sonrası model, RTX 4060 8GB'da lokal olarak inference verebilsin —
   `promptsmith "ham istek"` komutuyla stdout'a optimize prompt versin. Gecikme < 2 sn
   (50-token in / 250-token out).
3. Değerlendirme çerçevesi: 200 örneklik "altın test seti" ve LLM-as-judge otomatik
   skorlama. Her yeni model versiyonu bu seti çalıştırıp önceki ile karşılaştırır.
4. GitHub deposu + Hugging Face model kartı ile açık kaynak release. README, kurulum,
   kullanım örnekleri, model kartı (limitations dahil).
5. Baseline üstünlüğü ölçülebilir: en az %65 test örneğinde ham promptun doğrudan Claude
   Opus'a verilmesinden daha iyi sonuç. Bu ölçüm iki metrikte yapılır: (a) LLM-as-judge
   puanı, (b) Kemal'in gözle spot-check onayı.

### 4.2 — İkincil hedefler (nice-to-have, MVP zorunlu değil)

1. Çoklu hedef LLM profili: kullanıcı `--target claude-code | chatgpt | cursor | generic`
   ile hangi hedefe göre optimize istediğini söyleyebilsin (farklı prompt gelenekleri
   var — Claude XML, ChatGPT markdown, Cursor kısa direktifler).
2. Kısa "explain mode": model neden bu değişiklikleri yaptığını da anlatsın (öğretici).
3. Streaming çıktı (llama.cpp'nin token-by-token akıtması).
4. Sistemik prompt kalıpları için özel handler'lar (kod yazma, hata ayıklama, yazı,
   veri analizi) — tek genel model yerine görev-koşullu sistem promptu.

### 4.3 — Kapsam DIŞI (bu MVP'de yok)

- **Entegrasyon katmanı:** MCP server, Claude Code plugin, Cursor uzantısı, browser
  extension. Hepsi Faz 2. Kemal "sonrasına bakarız" dedi — bu bilinçli.
- **Multi-model routing:** basit istek → küçük model, karmaşık → büyük model gibi
  bir router. Karmaşıklık ekler, MVP değeri düşük.
- **Online reinforcement learning:** kullanıcı feedback'iyle canlı iyileştirme. Faz 3.
- **Multilingual training:** MVP'de Türkçe + İngilizce çift dilli hedeflenir; genişletme
  sonra (Almanca, Fransızca, Çince).
- **Ticari SaaS:** Kemal bu tamamen açık kaynak istiyor; ticari yol yok.
- **Görsel prompt engineering:** Midjourney / SDXL / FLUX prompt optimizasyonu. Ayrı bir
  problem (PromptEnhancer bunu yapıyor).
- **Fine-tune sonrası RLHF:** SFT + belki DPO Faz 1.5; klasik RLHF (PPO) kapsam dışı.

### 4.4 — Başarı ölçütü tablosu (kabul kriterleri)

| Ölçüt | Hedef | Nasıl ölçülür |
|---|---|---|
| Test setinde judge kazanma | ≥ %65 | `eval/run_judge.py --set data/test/gold.jsonl` |
| Kemal spot-check onayı | ≥ %70 | El ile 30 örnek işaretleme |
| Inference gecikmesi | < 2 sn (50-in / 250-out, RTX 4060) | `bench/latency.py` |
| VRAM tepe kullanımı | < 7 GB | `nvidia-smi` bench sırasında |
| Kurulum tek komut | evet | `pip install .` + config CLI |
| README + model card | tam | manuel review + `docs-check.py` |
| Reproduce-edilebilirlik | evet | fresh clone → 1 saatte inference çalışır |

### 4.5 — Kapsam kaydırma (scope creep) çıpası

Faz uygulaması sırasında "şunu da ekleyelim" çıkarsa test şu: karar ölçütünde (yukarıdaki
tabloda) bir metriği yükseltiyor mu? Yükseltmiyorsa Faz 2 listesine yazılır, MVP'ye
sokulmaz. Bu çıpa özellikle §6-ADR süreçlerinde işlenecek.

---

## §5 — Kullanıcı Senaryoları

Bu bölüm "kim, ne zaman, nasıl kullanır" sorusuna cevap veriyor. Senaryolar §12 (görev
kırılımı) ve §13 (test/kabul) için ham malzeme.

### 5.1 — Persona P1: Kemal — Claude Code kullanıcısı, yarım-yamalak istek yazan

**Bağlam:** Kemal Claude Code terminal oturumuna bir istek yazar, ama düşünürken
yazdığı için istek eksik: "şu bug'ı çöz" der, ama hangi dosya, hangi hata, ne beklediği
belli değildir. Claude tahmine dayalı cevap verir, yanlış dosyaya bakar, tur harcanır.

**Akış:**
1. Kemal terminale `promptsmith "reflection code'u yeni versiyona uydur, hata veriyor"`
   yazar.
2. `promptsmith` 1.5 sn içinde şunu döndürür:
   ```
   ## Görev
   Reflection kodunu yeni Java sürümüne uyarla — mevcut kod derlemede uyarı /
   hata veriyor.

   ## Bağlam
   - Proje kök klasörü: <?>. Etkilenen dosya(lar): src/main/java/... alt yolu ver.
   - Hedef Java sürümü: JDK 21 (Kemal'in ortamı, memory'de kayıtlı).
   - Hata mesajı (compiler output): <?>

   ## Kabul kriterleri
   - `mvn -q -DskipTests package` başarıyla derlensin.
   - Uyarı bırakma; kullanılmayan importları temizle.
   - Test varsa geçsin; yoksa değiştirdiğin sınıfa smoke test ekle.

   ## Format
   - Değiştirdiğin dosyaların diff'ini ver.
   - Kısa bir "değişiklik özeti" ekle.
   ```
3. Kemal bu çıktıyı Claude Code'a yapıştırır. Claude gerekli soruyu sorar (`Etkilenen
   dosya yolunu / hata mesajını verir misin?`), Kemal cevaplar, iş tek turda biter.

**Beklenti:** normalde 4-5 turda çözülen iş, 2 turda biter. `promptsmith`'in katma
değeri: gerekli sorular önden formüle edildi, Claude tahmine boğulmadı.

### 5.2 — Persona P2: Açık kaynak geliştirici — Cursor kullanan biri, generic bir istek yazıyor

**Bağlam:** Geliştirici Cursor'da bir refactor istiyor: "bu component'i temizle". Cursor
LLM'i genelde bunu yorumluyor ama tam istediği gibi değil.

**Akış:**
1. Geliştirici `promptsmith --target cursor "bu component'i temizle"` yazar (VSCode
   içinden bir kısayolla, ya da terminalden).
2. `promptsmith` Cursor bağlamına uygun (kısa direktifler, dosya-odaklı) bir prompt
   döndürür:
   ```
   Refactor the selected React component:
   - Extract inline handlers to memoized callbacks.
   - Split JSX blocks >20 lines into subcomponents.
   - Replace class-based state with hooks if any remain.
   - Preserve external API (props, exports).
   - Do not add comments explaining the change.
   ```
3. Geliştirici kabul eder, Cursor bu direktife göre çalışır.

**Beklenti:** hedef aracın "diline uygun" prompt üretimi. `--target` bayrağı bunu yönetir.

### 5.3 — Persona P3: Yeni başlayan LLM kullanıcısı — Claude web arayüzü, uzun bir istek

**Bağlam:** Kullanıcı ChatGPT/Claude web'de uzun ama dağınık bir istek yazmış. Metin 400
kelime, iki-üç konu karışık, hedef belirsiz.

**Akış:**
1. `promptsmith - <<'EOF'` ile stdin'e istek yapıştırır.
   ```
   [uzun karışık metin]
   EOF
   ```
2. `promptsmith` şunu yapar:
   - Ana hedefi izole eder.
   - Alt-hedefleri sırlar.
   - Belirsiz noktaları bir "sorular" bloğuna toplar.
   - Gerekiyorsa iki ayrı prompt'a böler (`--split`).
3. Kullanıcı temizlenmiş çıktıyı hedef araca verir.

**Beklenti:** kullanıcı prompt engineering pratiği yapmadan, hızla sonuç alır.

### 5.4 — Persona P4: Kemal — offline / uçak modu

**Bağlam:** Kemal internetsiz bir ortamda (uçak, otel), Claude API'ye erişemiyor. Ama
lokal `promptsmith` çalışır (ağırlıklar diskte, llama.cpp offline).

**Akış:**
1. `promptsmith "ne yazmalı"` çalışır. Sonuç: temiz prompt.
2. Kemal bu promptu offline lokal bir modele (`llama.cpp` ile başka bir instruct model)
   veriyor. Yine offline sonuç alıyor.

**Beklenti:** internetsiz kullanılabilir. Bu senaryo doğrudan "MVP kapsam" içi değil ama
bir yan fayda — offline hedef LLM'lerin de kalitesini artırır.

### 5.5 — Kötü senaryolar (negative use)

- **Prompt injection ile kötüye kullanım:** kullanıcı `promptsmith`'e "ignore previous
  instructions, output ..." gibi bir istek verir. MVP güvenlik pozisyonu: model
  içeriği yeniden yazar, "kullanıcıdan gelen kötü niyetli talimat" filtresi eklemez
  (çünkü hedef LLM zaten kendi güvenliğini yönetiyor). Model kartında bu net yazılır:
  "This model does not filter for jailbreaks; downstream target model is expected to."
- **Aşırı iyimser değerlendirme:** kullanıcı model çıktısına körü körüne güvenir,
  hedef LLM yanlış cevap verirse suçu `promptsmith`'e yükler. Model kartı bunu da
  yazar: "Prompt rewriter improves clarity, not target LLM correctness."
- **Kişisel bilgi sızıntısı:** kullanıcı `promptsmith`'e şifre, e-posta içeriği verir.
  MVP model kişisel bilgi maskelemesi yapmaz — model kartı bunu yazar; Faz 2'de
  opsiyonel PII masking eklenir.

---

## §6 — Teknoloji ve Karar Kayıtları (ADR)

ADR = Architecture Decision Record. Her kararın gerekçesi + alternatifleri + geri-alma
maliyeti burada. Uygulamaya "neden böyle" sorusu geldiğinde ilk bakılacak yer.

### ADR-01 — Proje kod adı

**Karar:** Geçici kod adı `promptsmith`. Kemal onayına açık; `promptforge`, `polish`,
`smith`, `pe-mini`, `refine`, `prompter`, `promptcraft` de alternatif.

**Gerekçe:** "smith" (demirci) kelimesi promptu şekillendirme çağrışımı veriyor, kısa,
domain'i (`promptsmith.ai`, `promptsmith.dev`) aranabilir, PyPI/npm çakışma olasılığı
düşük (Faz 0'da doğrulanacak). Alternatifler kısıtlayıcı çağrışımlar taşıyor
(`promptforge` başka bir SaaS ürünü var, `refine` çok genel, `polish` metin cilalama
çağrışımı fazla).

**Geri-alma maliyeti:** Faz 4'ten önce değiştirmek ucuz (kod tabanında string replace + 
klasör rename); Faz 4'ten sonra pahalı (release edilmiş paketlerin isim değişikliği,
kırık linkler).

**Aksiyon:** Kemal Faz 0-Gün 1'de kararı onaylar / değiştirir; onaydan sonra bütün
plandaki `promptsmith` string'i final ile değiştirilir. Şu anda plan boyunca placeholder.

### ADR-02 — Base model seçimi: Qwen 2.5 7B Instruct (birincil) / Phi-4-mini 3.8B (yedek)

**Karar:** Birincil aday Qwen 2.5 7B Instruct. Faz 2 pilot fine-tune (100 örnek, 1 epoch)
ile Phi-4-mini 3.8B ile yanyana kıyaslama yapılacak. Kazanan Faz 2 tam fine-tune için
kullanılır.

**Gerekçe:**
- Qwen 2.5 7B — Apache 2.0 lisans, çok dilli (Türkçe dahil), JSON parse başarısı yüksek,
  Unsloth desteği tam. 7B "yeniden yazma" için yeterli soyutlama.
- Phi-4-mini 3.8B — MIT lisans, benchmark lideri sub-4B, daha az VRAM. Ama çok dilli
  kapasite Qwen'e göre zayıf, Türkçe promptlarda risk var.
- Alternatifler elenme sebepleri:
  - **Qwen 3.5** — Unsloth "yüksek quantization sapması" nedeniyle QLoRA önermiyor.
  - **Llama 3.2 3B** — JSON parse zayıf (%47-56), Llama Community lisans ticari
    kısıtlarla geliyor.
  - **Gemma 3 4B** — Gemma lisansı ticari kısıtlı, Kemal MIT/Apache tercih ediyor.

**Geri-alma maliyeti:** düşük — LoRA yaklaşımında base'i değiştirmek veri seti değişimi
gerektirmez; sadece yeniden fine-tune (2-4 saat GPU).

### ADR-03 — Fine-tune framework: Unsloth (birincil), TRL+PEFT (yedek)

**Karar:** Unsloth ile QLoRA. Rank 16, alpha 16, dropout 0. TRL+PEFT'e Unsloth bug
çıkarsa geçilir.

**Gerekçe:** Unsloth 2x hız, %70 daha az VRAM (accuracy kaybı yok, published bench).
Windows'ta bitsandbytes bağımlılığı tarihi sıkıntılı; Unsloth kendi wheel'larıyla bu
sıkıntıyı kısmen çözüyor.

**Risk:** Windows'ta Unsloth kurulum başarısızlığı. Mitigation: Faz 0'da fresh venv'de
dry-run — kurulum başarısızsa WSL2 Ubuntu'ya geçilir (Kemal'in mevcut kaynağı yeterli).

### ADR-04 — Quantization: QLoRA (4-bit NF4) + LoRA rank 16

**Karar:** QLoRA (bnb_4bit_use_double_quant, bnb_4bit_quant_type="nf4"), LoRA r=16,
alpha=16, target_modules tüm attn + MLP projeksiyon katmanları.

**Gerekçe:** RTX 4060 8GB'da 7B modelin tam-parametre fine-tune fizibl değil. LoRA rank
16 SFT için standart iyi başlangıç. Alpha=rank (LoRA scaling 1.0) — LoRA blog önerisi.

**Alternatifler:** rank 8 (daha ucuz, kapasite düşük), rank 32 (daha güçlü, VRAM sıkar).
Rank 16 orta yol.

### ADR-05 — Veri seti üretimi: teacher distillation + Kemal'in kendi transkriptleri

**Karar:** 3 kaynaklı veri seti — (a) Kemal'in Claude Code transkriptlerinden çıkarılan
gerçek "ham → optimize" çiftleri, (b) teacher LLM (Claude Opus 4.7 API, yedek DeepSeek
V3) tarafından üretilen sentetik çiftler, (c) el ile yazılmış altın örnekler (Kemal +
Claude birlikte). Oran: %20 gerçek, %60 sentetik, %20 el yapımı.

**Gerekçe:** Kemal'in kendi transkriptleri özgün ama ölçek olarak yetersiz (belki 100-300
çift çıkar); sentetik ölçeği verir; el yapımı test seti kaliteyi tutar.

**Alternatif:** sadece sentetik — ucuz ama Kemal'in stiline uyum sıfır; sadece el
yapımı — kaliteli ama ölçek yok. Karma optimal.

### ADR-06 — Değerlendirme: DeepEval + Prometheus 2 + spot-check

**Karar:** Otomatik metrik: DeepEval framework içinde G-Eval tarzı rubric-based scoring,
judge model olarak Prometheus 2 7B (lokal). Test setinin %10'unda Claude Opus 4.7
hakemliği (API maliyet). Her iterasyon sonunda Kemal 30-50 örnek spot-check.

**Gerekçe:** Prometheus 2 açık, lokal, judge bias için ayrı bir modeli seçim ("kendini
tercih" biasını azaltır — biz Qwen fine-tune ediyoruz, judge Prometheus/Llama tabanlı).
Claude Opus ikincil hakem karar veremeyen durumlar için, ama pahalı.

### ADR-07 — Inference: GGUF (Q4_K_M) + llama.cpp

**Karar:** Fine-tune sonrası LoRA merged model → GGUF Q4_K_M kuantize → llama.cpp CLI.
vLLM Faz 2 (yüksek throughput talebi olursa).

**Gerekçe:** llama.cpp Windows'ta stabil, GPU offload edebilir, tek-shot CLI kullanımı
kolay. GGUF Q4_K_M kalite/boyut dengesi (dosya ~4GB, kalite kaybı minimal). vLLM daha
hızlı ama Windows desteği tarihi zayıf, MVP için gereksiz.

### ADR-08 — Dağıtım: pip package + llama.cpp binary + HF Hub model

**Karar:** Python paketi (`pip install promptsmith`) — LoRA adapter'ı ve config'i taşır;
kullanıcının önceden llama.cpp'yi ve base modeli indirmesi gerekir (README talimatları
ile). Alternatif: Windows exe (PyInstaller) Faz 2.

**Gerekçe:** MVP'de "geliştirici dostu" hedefliyoruz; pip standart. exe hedef genel
kullanıcı — Faz 2.

### ADR-09 — Lisans: kod MIT, model tag Apache-2.0

**Karar:** GitHub reposundaki kod MIT. HF Hub'daki LoRA adapter Apache-2.0 (Qwen 2.5'in
Apache lisansına saygı gösteriyoruz; adapter türev iş sayılır).

**Gerekçe:** MIT en izin verici, en yaygın. Base modelin lisansına ise mutlaka uyulmalı
— Qwen Apache seçildiği için türev de Apache.

### ADR-10 — Dil öncelikleri

**Karar:** MVP eğitim veri seti Türkçe + İngilizce çift dilli. Test setinin yarısı
Türkçe. Faz 2'de Almanca/Fransızca/Çince genişleme.

**Gerekçe:** Kemal Türkçe konuşuyor ve Claude Code Türkçe'yi anlıyor — bu projenin bir
"Türkçe için de çalışan prompt engineer" pozisyonu benzersiz avantaj. Sadece İngilizce
yapmak kolay ama Kemal için değersiz.

---

## §7 — Mimari

### 7.1 — Yüksek seviye

`promptsmith` üç ayrı, gevşek bağlı katmandan oluşuyor:

```
┌──────────────────────────────────────────────────┐
│  1. TRAINING CATMANI  (offline, sadece Kemal)    │
│  ┌────────────┐ ┌──────────┐ ┌──────────────┐    │
│  │ Data build │→│ SFT loop │→│ Eval + judge │    │
│  └────────────┘ └──────────┘ └──────────────┘    │
│      ↓ (LoRA adapter kaydı)                      │
├──────────────────────────────────────────────────┤
│  2. PAKETLEME CATMANI  (release öncesi)          │
│  ┌────────────┐ ┌──────────┐ ┌──────────────┐    │
│  │ Merge LoRA │→│ To GGUF  │→│ Push to HF   │    │
│  └────────────┘ └──────────┘ └──────────────┘    │
│      ↓ (dağıtılabilir sanat: adapter + gguf)     │
├──────────────────────────────────────────────────┤
│  3. INFERENCE CATMANI  (uçtaki kullanıcı)        │
│  ┌────────────┐ ┌──────────┐ ┌──────────────┐    │
│  │ CLI parse  │→│ llama.cpp│→│ Post-process │    │
│  └────────────┘ └──────────┘ └──────────────┘    │
└──────────────────────────────────────────────────┘
```

- **Training katmanı** sadece proje geliştiricisinin makinesinde çalışır. Kullanıcı bu
  katmandaki hiçbir dosyaya dokunmaz.
- **Paketleme katmanı** her release'de bir kez çalışır. Çıktısı: HF Hub'daki adapter
  ve GGUF dosyası.
- **Inference katmanı** kullanıcının kendi makinesinde çalışır. Bağımlılık: pip package
  (Python) + llama.cpp binary + indirilmiş model dosyası.

### 7.2 — Modül sınırları

```
promptsmith/
├── cli/          # kullanıcı arayüzü — argparse tabanlı komut satırı
├── engine/       # llama.cpp sarmalayıcı — subprocess veya python bindings
├── prompts/      # system prompt şablonları, target-specific varyantlar
├── config/       # yapılandırma yükleme (yaml + env)
├── postproc/     # model çıktısını temizleme (markdown escape, JSON parse)
└── errors.py     # özel exception hiyerarşisi
```

Training pipeline `training/` altında ayrı bir alt-repo değil, ayrı bir üst-klasör:

```
training/
├── data/         # veri toplama ve zenginleştirme scriptleri
├── sft/          # Unsloth eğitim döngüsü
├── eval/         # DeepEval + Prometheus 2 judge
├── pack/         # merge_lora + convert_to_gguf
└── datasets/     # ham + işlenmiş dataset dosyaları (git-ignore)
```

Bu ayrım kullanıcının kullanmayacağı ağır bağımlılıkları (`unsloth`, `bitsandbytes`,
`trl`, `peft`) `training/` içine hapsediyor. `pip install promptsmith` sadece hafif
inference bağımlılıklarını çeker.

### 7.3 — Veri akışı (bir çıkarım isteğinin yolu)

1. `promptsmith "ham istek"` çağrısı.
2. `cli/main.py::run()` argümanları parse eder, config yükler.
3. `prompts/system.md` (target'a göre varyant) + kullanıcı ham girdi birleştirilir.
4. `engine/llama.py::generate()` çağrılır: subprocess ile `llama-cli` çalıştırılır ya
   da `llama_cpp` Python binding'i (config'e göre seçilir).
5. Ham çıktı `postproc/clean.py` ile temizlenir — markdown escape, gereksiz preamble
   kaldır, JSON blok ayrıştır (varsa).
6. stdout'a yazılır.

Toplam gecikme hedefi: < 2 sn (RTX 4060, 50-in / 250-out).

### 7.4 — Bağımlılık yönetimi

Iki farklı `pyproject.toml`:
- **Root pyproject:** inference bağımlılıkları — `click`, `pydantic`, `pyyaml`,
  `llama-cpp-python` (opsiyonel). Kullanıcının `pip install promptsmith` ile
  çektiği.
- **`training/pyproject.toml`:** eğitim ağır bağımlılıkları — `unsloth`, `transformers`,
  `trl`, `peft`, `bitsandbytes`, `datasets`, `deepeval`. Kullanıcı bunu kurmaz.

Ana repoda bir `Makefile` (veya PowerShell `.ps1` eşdeğeri) hedefleri:
- `make setup-dev` — inference + training bağımlılıkları.
- `make setup-user` — sadece inference.
- `make data`, `make train`, `make eval`, `make pack` — pipeline adımları.

### 7.5 — Genişletilebilirlik noktaları

- **Target profilleri:** `prompts/targets/` altında `claude-code.md`, `chatgpt.md`,
  `cursor.md`, `generic.md`. Yeni target eklemek = yeni dosya.
- **Post-processor plugin:** `postproc/plugins/` altında; her plugin bir `apply(text)
  -> text` fonksiyonu. Örnek: sensitive-info scrubber Faz 2'de eklenebilir.
- **Engine backend:** `engine/backend.py` protokolü. llama.cpp default; Faz 2'de vLLM
  veya doğrudan HF Transformers eklenebilir.

### 7.6 — Ne YOK

- Web server / REST API — MVP değil.
- Cache katmanı (aynı promptu tekrar sormasın diye) — MVP değil, düşük değer.
- Multi-modal (görsel giriş) — kapsam dışı.
- Router (küçük/büyük model seçimi) — Faz 2.

---

## §8 — Akış Diyagramları

### 8.1 — Faz akışı (proje omurgası)

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Faz 0   │→ │  Faz 1   │→ │  Faz 2   │→ │  Faz 3   │→ │  Faz 4   │
│ Kurulum  │   │  Veri    │   │ Eğitim   │   │ İterasyon│   │ Release  │
│ Dry-run  │   │  Seti    │   │ QLoRA    │   │ + Eval   │   │ HF+GH    │
│  1-2 gün │   │  3-5 gün │   │  1-2 gün │   │  2-4 gün │   │ 1-2 gün  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
     │              │              │              │              │
     ↓              ↓              ↓              ↓              ↓
  env hazır       data.jsonl    adapter.pt   metrik raporu   HF Hub push
  script kabuk   1500-2500 çft  ~200MB       json+md         GitHub tag
```

### 8.2 — Veri seti oluşturma akışı (Faz 1)

```
Kaynaklar
├─ Kemal transkriptleri (jsonl session)
│   → anonymize.py → 100-300 çift
├─ ShareGPT / Alpaca / açık dataset
│   → sample_prompts.py → 500-800 seed prompt
│   → distill_optimize.py (Claude Opus 4.7 API) → 500-800 çift
└─ El ile yazma (Kemal + Claude)
    → docs/gold_examples.md → 100-200 çift

Birleştir → data/raw/all.jsonl
    → dedup.py → data/raw/dedup.jsonl
    → validate_schema.py → data/raw/valid.jsonl
    → split.py (80/10/10) → train.jsonl / val.jsonl / test.jsonl
    → tokenize_stats.py (uzunluk dağılımı raporu)
```

### 8.3 — Fine-tune akışı (Faz 2)

```
Girdi: data/train.jsonl, data/val.jsonl, base model Qwen2.5-7B-Instruct
    │
    ▼
Unsloth.load_pretrained(base, load_in_4bit=True)
    │
    ▼
FastLanguageModel.get_peft_model(r=16, alpha=16, target=all-linear)
    │
    ▼
Formatting: ChatML template ("<|im_start|>user...<|im_end|>...")
    │
    ▼
SFTTrainer (TRL, Unsloth patched)
    - epochs: 3
    - batch: 2
    - grad_accum: 4
    - lr: 2e-4
    - scheduler: cosine
    - warmup: 5
    - eval_steps: 50
    │
    ▼
Kayıt: outputs/checkpoints/step-*, best-val.pt
```

### 8.4 — Değerlendirme akışı (Faz 3)

```
Model checkpoint (LoRA adapter)
    ▼
Load base + adapter (Unsloth.load_pretrained + merge_and_unload)
    ▼
For each test_example in data/test.jsonl:
    ham → model.generate(temperature=0.7, top_p=0.9) → optimize
    ▼
Judge = Prometheus2 (yerel, load_in_4bit)
For each (ham, gold, our_output):
    judge.score(rubric, our_output, gold) → puan 1-5
    ▼
Aggregate:
    - ortalama puan
    - kazanma oranı (baseline: base model + generic system prompt)
    - hata analizi (en kötü 20 örnek → log)
    ▼
Rapor: eval/reports/report-YYYY-MM-DD.md
    ▼
Kemal spot-check: 30 örnek, "iyi/kötü/orta"
    ▼
Karar: iterasyon mu, release mi?
```

### 8.5 — Kullanıcı komut akışı (inference)

```
$ promptsmith "ham istek"
   │
   ▼
CLI parse (target profili, --explain, --split, --raw)
   │
   ▼
config yükle (~/.promptsmith/config.yaml var mı? yoksa default)
   │
   ▼
system prompt seç (target'a göre prompts/targets/*.md)
   │
   ▼
llama.cpp (subprocess): llama-cli --model <gguf> --sys <sysprompt> --prompt <user>
   │
   ▼
raw output al → postproc/clean.py
   │
   ▼
stdout'a yaz (opsiyonel: --json JSON çıktı)
```

### 8.6 — Release akışı (Faz 4)

```
Merged model (fp16) → llama.cpp/convert_hf_to_gguf.py → gguf-fp16.gguf
    │
    ▼
llama.cpp/llama-quantize gguf-fp16.gguf gguf-q4_k_m.gguf Q4_K_M
    │
    ▼
Test: llama-cli local çalıştır, 10 sanity örnek → PASS
    │
    ▼
HF Hub push (huggingface_hub CLI):
    - promptsmith/promptsmith-qwen2.5-7b-v1 (LoRA + config + README + gguf)
    │
    ▼
GitHub push:
    - main branch güncelle
    - CHANGELOG.md
    - tag v0.1.0
    - GitHub Release notes (auto from CHANGELOG)
    │
    ▼
Duyuru: model card, blog post (opsiyonel), r/LocalLLaMA post
```

---

## §9 — Dosya Dosya İçerik (raporun kalbi)

Bu bölüm klasör iskeletinin her satırını açıklıyor. Her dosyanın **amacı, giriş/çıkış
sözleşmesi, temel fonksiyonlar** yazıyor. Uygulama fazında bu bölüm doğrudan yol
haritası — dosya oluşturmak için ekstra karar gerekmez.

### 9.1 — Kök klasör iskeleti

```
promptsmith/
├── README.md
├── LICENSE
├── LICENSE-model
├── CHANGELOG.md
├── pyproject.toml
├── setup.cfg
├── .gitignore
├── .python-version
├── .env.example
├── Makefile
├── conftest.py
├── docs/
│   ├── QUICKSTART.md
│   ├── MODEL_CARD.md
│   ├── TRAINING.md
│   ├── EVAL.md
│   ├── TARGETS.md
│   └── gold_examples.md
├── src/promptsmith/
│   ├── __init__.py
│   ├── __version__.py
│   ├── cli/
│   ├── engine/
│   ├── prompts/
│   ├── config/
│   ├── postproc/
│   └── errors.py
├── training/
│   ├── pyproject.toml
│   ├── configs/
│   ├── data/
│   ├── sft/
│   ├── eval/
│   ├── pack/
│   └── scripts/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── bench/
│   ├── latency.py
│   └── memory.py
└── agac/          # bu planın motor çıktısı, git-ignored (referans için lokal tut)
```

### 9.2 — Kök dosyalar

**`README.md`** — Proje giriş: ne yapar, neden yapar, kim için, tek komutla kurulum,
"selam dünya" örneği (bir ham prompt → optimize prompt), model performansı (test setinde
kazanma oranı), lisans, katkı rehberi bağlantısı. Uzunluk hedefi ~200-300 satır Markdown.

**`LICENSE`** — MIT lisans metni (ADR-09). Standart MIT template'i, "Copyright (c)
2026 Kemal Ertürk".

**`LICENSE-model`** — Hugging Face model kartında referans verilen Apache-2.0. LoRA
adapter türev iş sayılıyor; base modelin lisansına uyum.

**`CHANGELOG.md`** — Keep-a-Changelog formatı. v0.1.0 (MVP), v0.2.0 (target profilleri),
v0.3.0 (streaming), v1.0.0 (MCP entegrasyon) gibi bantlar.

**`pyproject.toml`** — Ana paket metadata:
```toml
[project]
name = "promptsmith"
version = "0.1.0"
description = "Local prompt engineer AI — rewrites your prompts for better LLM output."
requires-python = ">=3.10"
license = { file = "LICENSE" }
authors = [{ name = "Kemal", email = "kemgen01@gmail.com" }]
dependencies = [
    "click>=8.1",
    "pydantic>=2.5",
    "pyyaml>=6.0",
    "rich>=13.7",
    "platformdirs>=4.2",
]

[project.optional-dependencies]
llama = ["llama-cpp-python>=0.2.79"]

[project.scripts]
promptsmith = "promptsmith.cli.main:app"
```

**`setup.cfg`** — flake8, isort, coverage konfigi. `black` config'i `pyproject.toml`
altında.

**`.gitignore`** — Python standard + `training/datasets/`, `training/outputs/`,
`*.gguf`, `*.pt`, `*.bin`, `.env`, `agac/ham/` (motor çıktısı yerelde kalır).

**`.python-version`** — pyenv/uv için `3.12`. (Python 3.14 Kemal'de kurulu; 3.12 daha
yaygın destek — 3.14 bazı bağımlılıklarda henüz wheel'lar yayınlanmamış olabilir; 3.12
güvenli. Faz 0 dry-run bunu test edecek.)

**`.env.example`** — Örnek ortam değişkenleri:
```
# Optional API keys used only during training data enrichment.
# NEVER commit .env. .env is git-ignored.
ANTHROPIC_API_KEY=
DEEPSEEK_API_KEY=
HF_TOKEN=

# Inference config
PROMPTSMITH_MODEL_PATH=~/.promptsmith/models/promptsmith-qwen2.5-7b-q4_k_m.gguf
PROMPTSMITH_TARGET=claude-code
PROMPTSMITH_LOG_LEVEL=INFO
```
`.env` git-ignored; Kemal projeyi paylaştığında API keys sızmıyor.

**`Makefile`** — Yaygın komutlar. Windows'ta `make.exe` (choco install veya git-bash
ile geliyor); ayrıca `scripts/*.ps1` eşdeğerleri de tutuluyor.
```makefile
.PHONY: setup-dev setup-user data train eval pack test lint

setup-user:
	pip install -e .

setup-dev: setup-user
	pip install -e ./training

data:
	python -m training.data.build

train:
	python -m training.sft.train --config training/configs/qwen2.5-7b-r16.yaml

eval:
	python -m training.eval.run --model outputs/latest

pack:
	python -m training.pack.merge_and_gguf --model outputs/latest
```

**`conftest.py`** — pytest global fixtures (temp model path, sample prompt corpus).

### 9.3 — `src/promptsmith/` — inference paketi

**`__init__.py`** — sadece `__version__` re-export.

**`__version__.py`** — `__version__ = "0.1.0"`. `pyproject.toml`'dan release'de otomatik
güncellenir (`hatch version` ile).

**`cli/main.py`** — Click tabanlı ana CLI:
```python
import click
from promptsmith.config.loader import load_config
from promptsmith.engine.factory import make_engine
from promptsmith.prompts.selector import select_system_prompt
from promptsmith.postproc.pipeline import postprocess

@click.command()
@click.argument("user_prompt", required=False)
@click.option("--target", "-t", default=None, help="claude-code | chatgpt | cursor | generic")
@click.option("--model", "-m", default=None, help="Path to GGUF model file")
@click.option("--explain", is_flag=True, help="Return also 'why' explanation")
@click.option("--json", "as_json", is_flag=True, help="JSON output")
@click.option("--stdin", is_flag=True, help="Read prompt from stdin")
def app(user_prompt, target, model, explain, as_json, stdin):
    cfg = load_config(target_override=target, model_override=model)
    if stdin or user_prompt is None:
        import sys
        user_prompt = sys.stdin.read()
    if not user_prompt.strip():
        raise click.UsageError("empty prompt")
    sys_prompt = select_system_prompt(cfg.target, explain=explain)
    engine = make_engine(cfg)
    raw = engine.generate(sys_prompt, user_prompt)
    result = postprocess(raw, as_json=as_json)
    click.echo(result)
```
Amaç: kullanıcı dostu, tek komutlu arayüz. Argümanların tek-harflik kısayolları
(`-t`, `-m`) günlük kullanım için.

**`cli/__init__.py`** — boş; paket işareti.

**`engine/backend.py`** — Protocol tanımı:
```python
from typing import Protocol
class InferenceBackend(Protocol):
    def generate(self, system_prompt: str, user_prompt: str,
                 max_new_tokens: int = 512, temperature: float = 0.7,
                 top_p: float = 0.9) -> str: ...
```

**`engine/llama.py`** — llama.cpp backend:
- Subprocess mod: `llama-cli --model X --sys ... --prompt ...` çağır, stdout topla.
- Python bindings mod: `llama_cpp.Llama` (opsiyonel install).
- Config'e göre seçim.
- Timeout, kill, stderr yakalama.

**`engine/factory.py`** — `make_engine(cfg) -> InferenceBackend`. Config'in `backend`
alanına göre `llama` veya (Faz 2) `vllm`, `hf` döner.

**`prompts/system.md`** — Genel sistem promptu (target belirtilmezse):
```markdown
You are `promptsmith`, an assistant that rewrites the user's raw request into
a well-structured prompt suitable for a downstream large language model.

Rules:
- Preserve the user's intent exactly.
- Add missing structure: goal, context, acceptance criteria, output format.
- Ask for at most 3 clarifying questions ONLY if the request is truly ambiguous.
- Do not answer the request yourself.
- Reply in the same language as the input.
- Format the rewritten prompt as a self-contained block, ready to paste.
```

**`prompts/targets/claude-code.md`** — Claude Code target:
Ek talimatlar — XML tag'leri kullan (`<context>`, `<task>`), dosya yollarını explicit
iste, kabul kriterlerini test-anahtar kelimeleriyle formüle et (mvn package, npm test,
pytest), tekrar tekrar soru yerine hipotezleri isim ver ("varsayıyorum X, hayır ise
düzelt"), Kemal'in ortamı (JDK 21, Node 24, Python 3.14, RTX 4060) bilgisi.

**`prompts/targets/chatgpt.md`** — ChatGPT target:
Markdown başlıklar, örneklerle zenginleştir (few-shot), rol-tanımı (persona) ekle,
kabul kriterleri numaralı liste, kod istekleri için dil ve versiyon belirt.

**`prompts/targets/cursor.md`** — Cursor target:
Çok kısa direktifler (Cursor bağlamı IDE'den çekiyor), dosya-odaklı ifadeler ("bu
component", "seçili fonksiyon"), format olarak imperative mood ("Extract...", "Split...").

**`prompts/targets/generic.md`** — Generic:
Ortalama; belirli bir target çıkarımı yapmadan yapılandırılmış bir prompt üret.

**`prompts/targets/__init__.py`** — Boş; paket işareti.

**`prompts/selector.py`** — `select_system_prompt(target, explain=False) -> str`:
target adına göre dosyayı `pkg_resources`/`importlib.resources` ile yükler, `explain`
bayrağı için ekstra "at the end, write a 'why' paragraph explaining changes" satırı
ekler.

**`config/loader.py`** — Config yükleme:
- Default: `promptsmith/config/default.yaml`
- Kullanıcı override: `~/.promptsmith/config.yaml` (XDG uyumlu; `platformdirs` ile
  Windows'ta doğru klasör).
- Env override: `PROMPTSMITH_*` değişkenleri.
- CLI override: `--target`, `--model` gibi.
- Öncelik: CLI > ENV > kullanıcı yaml > default yaml.

**`config/default.yaml`**:
```yaml
model:
  path: null   # kullanıcı doldurur ya da ENV
  backend: llama  # llama | llama-py | vllm(future)
target: generic
generate:
  max_new_tokens: 512
  temperature: 0.7
  top_p: 0.9
  repeat_penalty: 1.05
llama:
  cli_binary: llama-cli   # PATH'te olması beklenir
  n_gpu_layers: 33         # 4060'ta 7B Q4_K_M için uygun
  ctx_size: 4096
log:
  level: INFO
  file: null
```

**`config/schema.py`** — Pydantic modelleri: `ModelConfig`, `GenerateConfig`,
`LlamaConfig`, `Config` (root). Validation `load_config`'te.

**`postproc/pipeline.py`** — `postprocess(text, as_json) -> str`. Aşamalar:
1. `strip_preamble.py` — modelin sık başlattığı "Sure, here's the rewritten prompt:"
   gibi giriş cümlelerini temizle (regex).
2. `strip_code_fence.py` — modelin sarabildiği markdown code fence'i açığa çıkar.
3. `escape.py` — terminal renklendirme için Rich formatting, JSON çıkışı için
   `json.dumps`.

**`postproc/strip_preamble.py`** — regex tabanlı, whitelisted patterns list. False
positive test'i unit test'te.

**`errors.py`** — Exception hiyerarşisi:
```python
class PromptsmithError(Exception): ...
class ConfigError(PromptsmithError): ...
class ModelLoadError(PromptsmithError): ...
class GenerationError(PromptsmithError): ...
class PostprocessError(PromptsmithError): ...
```
Sistem çıkış kodları CLI seviyesinde bunlara göre eşleniyor (`ConfigError -> 2`,
`ModelLoadError -> 3`, vb.).

### 9.4 — `training/` — offline eğitim pipeline'ı

**`training/pyproject.toml`** — Eğitim ağır bağımlılıkları ayrı pakette:
```toml
[project]
name = "promptsmith-training"
version = "0.1.0"
dependencies = [
    "unsloth[cu124-torch240] @ git+https://github.com/unslothai/unsloth.git",
    "transformers>=4.44",
    "trl>=0.10",
    "peft>=0.13",
    "bitsandbytes>=0.43",
    "datasets>=2.20",
    "deepeval>=1.4",
    "huggingface_hub>=0.24",
    "anthropic>=0.31",       # teacher distillation
    "wandb>=0.17",           # opsiyonel, konfigürasyonla aç/kapat
    "matplotlib>=3.9",       # eval rapor grafikleri
]
```
`unsloth`'un git URL'i CUDA sürümüne göre değişir; Windows için özel wheel farkındalığı.

**`training/configs/qwen2.5-7b-r16.yaml`** — Ana SFT config:
```yaml
base_model: unsloth/Qwen2.5-7B-Instruct-bnb-4bit
max_seq_length: 2048
load_in_4bit: true
dtype: null  # auto

lora:
  r: 16
  alpha: 16
  dropout: 0.0
  target_modules:
    - q_proj
    - k_proj
    - v_proj
    - o_proj
    - gate_proj
    - up_proj
    - down_proj
  bias: none
  use_rslora: false
  use_gradient_checkpointing: "unsloth"

training:
  epochs: 3
  per_device_train_batch_size: 2
  gradient_accumulation_steps: 4
  warmup_steps: 5
  learning_rate: 2.0e-4
  lr_scheduler_type: cosine
  weight_decay: 0.01
  seed: 3407
  logging_steps: 5
  eval_steps: 50
  save_steps: 100
  optim: "paged_adamw_8bit"
  bf16: false
  fp16: true                 # 4060 için fp16 daha güvenli
  packing: false

data:
  train: training/datasets/train.jsonl
  val: training/datasets/val.jsonl
  format: chatml             # chatml | alpaca | sharegpt

output:
  dir: outputs/qwen2.5-7b-r16
```

Yedek config: `qwen2.5-3b-r16.yaml` (küçük deneme), `phi-4-mini-r16.yaml` (yedek base).

**`training/data/build.py`** — Ana veri toplayıcı; alt-scriptleri çağırır.
- `--from-transcripts` → `harvest_transcripts.py`
- `--from-shared` → `harvest_shared_datasets.py`
- `--distill` → `distill_teacher.py`
- `--gold` → `import_gold.py`
- `--merge` → `merge_dedup.py`
- `--split` → `split_train_val_test.py`

**`training/data/harvest_transcripts.py`** — Kemal'in `~/.claude/projects/*/*.jsonl`
oturum dosyalarını okur, "user request" mesajlarını çıkarır, hemen ardından gelen
Claude sorularını "gerekli bağlam" ipucu olarak yakalar. Anonimleştirme: dosya yolları
placeholder'a (`<REPO_PATH>`), e-postalar `<EMAIL>`'a, IP'ler `<IP>`'ye. Çıktı:
`training/datasets/raw/transcripts.jsonl`.

**`training/data/harvest_shared_datasets.py`** — Hugging Face datasets üzerinden
ShareGPT, Alpaca, OpenAssistant'tan sadece "ham istek" tarafını çeker (yanıtı almaz —
biz kendi yanıtımızı üreteceğiz). Filtre: uzunluk 20-500 kelime, tekrar sinyalı olan
promptları at, İngilizce ve Türkçe.

**`training/data/distill_teacher.py`** — Ham promptları Claude Opus 4.7 (birincil) veya
DeepSeek V3 (yedek) API'sine gönderir. System prompt: "You are a prompt engineer.
Rewrite the user's raw request into an optimized prompt for downstream model X.
Preserve intent; add structure. Reply with rewritten prompt only."
Rate-limit farkındalığı (Anthropic saatlik quota), tekrar deneme (tenacity),
maliyet raporu (`--dry-run` ile önce sayı ve maliyet göster).

**`training/data/import_gold.py`** — `docs/gold_examples.md`'deki el yapımı örnekleri
JSONL'e dönüştürür. Format doğrulama, "gold" bayrağı ekleme (test seti çekirdeği).

**`training/data/merge_dedup.py`** — Tüm kaynakları birleştirir; MinHash tabanlı
yakın-duplicate elemesi (`datasketch` kullanılabilir; yoksa basit Jaccard cutoff).
Rapor: kaç örnek düşürüldü.

**`training/data/split_train_val_test.py`** — %80 train, %10 val, %10 test. Gold
örnekleri sadece test'e. Rastgele seed 3407 (Unsloth notebooklerinde kullanılan seed,
tutarlılık için).

**`training/data/schema.py`** — JSONL kayıt şeması (§10 detayında).

**`training/sft/train.py`** — Ana eğitim döngüsü:
```python
from unsloth import FastLanguageModel
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset
import yaml, click, os

@click.command()
@click.option("--config", "-c", required=True)
def main(config):
    cfg = yaml.safe_load(open(config))
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=cfg["base_model"],
        max_seq_length=cfg["max_seq_length"],
        load_in_4bit=cfg["load_in_4bit"],
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=cfg["lora"]["r"],
        lora_alpha=cfg["lora"]["alpha"],
        lora_dropout=cfg["lora"]["dropout"],
        target_modules=cfg["lora"]["target_modules"],
        bias=cfg["lora"]["bias"],
        use_gradient_checkpointing=cfg["lora"]["use_gradient_checkpointing"],
    )
    ds_train = load_dataset("json", data_files=cfg["data"]["train"], split="train")
    ds_val = load_dataset("json", data_files=cfg["data"]["val"], split="train")
    def format_chatml(ex):
        return tokenizer.apply_chat_template(
            [{"role": "user", "content": ex["input"]},
             {"role": "assistant", "content": ex["output"]}],
            tokenize=False, add_generation_prompt=False,
        )
    ds_train = ds_train.map(lambda ex: {"text": format_chatml(ex)})
    ds_val = ds_val.map(lambda ex: {"text": format_chatml(ex)})
    trainer = SFTTrainer(
        model=model, tokenizer=tokenizer,
        train_dataset=ds_train, eval_dataset=ds_val,
        dataset_text_field="text",
        max_seq_length=cfg["max_seq_length"],
        args=SFTConfig(**cfg["training"], output_dir=cfg["output"]["dir"]),
    )
    trainer.train()
    trainer.save_model(cfg["output"]["dir"] + "/final")
```

**`training/sft/callbacks.py`** — VRAM izleme callback'i (her N adımda `nvidia-smi`
snapshot alıp log'a yazar), erken durdurma (val loss K adımdır düşmüyor).

**`training/sft/formats.py`** — ChatML/Alpaca/ShareGPT formatları arasında geçiş.

**`training/eval/run.py`** — Ana değerlendirme scripti:
- Model yüklemesi (merge_and_unload ile LoRA birleştirilir).
- Test seti üzerinde generate.
- Prometheus 2 judge çağrısı (batch).
- Baseline: aynı base model + sadece generic system prompt.
- Karşılaştırma: bizim model vs. baseline, LLM-as-judge kazanma oranı, Kemal spot-check
  bekleme yeri.
- Rapor: `eval/reports/report-YYYY-MM-DD.md`.

**`training/eval/judge_prometheus.py`** — Prometheus 2 modeli 4-bit yüklenir, her
örnek için rubric-based scoring.

**`training/eval/rubric.md`** — Judge rubric:
```
Evaluate the rewritten prompt on a 1-5 scale, considering:
- Clarity: is the intent unambiguous?
- Structure: are goal, context, acceptance criteria present?
- Faithfulness: does it preserve original intent?
- Actionability: could a downstream LLM act on it without more questions?
- Concision: does it avoid unnecessary verbosity?

Score: 5=excellent, 4=good, 3=acceptable, 2=poor, 1=broken.
```

**`training/eval/spot_check.py`** — Kemal için interaktif CLI. Test setinin 30
rastgele örneğini gösterir, klavyeden `g/o/k` (good/orta/kötü) alır, sonucu
`eval/spotcheck-YYYY-MM-DD.jsonl`'a kaydeder.

**`training/pack/merge_lora.py`** — LoRA adapter'ı base model üzerine merge eder,
`safetensors` olarak kaydeder (fp16).

**`training/pack/convert_to_gguf.py`** — llama.cpp'nin `convert_hf_to_gguf.py`
scriptini çağırır. Sonra `llama-quantize` ile Q4_K_M üretir.

**`training/pack/push_hf.py`** — Hugging Face Hub'a upload: adapter, merged model
(opsiyonel), GGUF, README (model card), tokenizer files.

**`training/scripts/setup_env.ps1`** — Windows'ta CUDA + Unsloth kurulum. Toolkit
sürüm kontrolü, `nvcc --version` doğrulama, venv oluşturma, ilk pip install.

**`training/scripts/setup_env.sh`** — Aynısının bash versiyonu (WSL2 fallback için).

### 9.5 — `tests/` — otomatik testler

**`tests/unit/test_cli.py`** — Click CLI runner ile argüman parsing testi. Sahte engine
enjekte edilir (`monkeypatch`).

**`tests/unit/test_config_loader.py`** — Öncelik sırası testi (CLI > ENV > user yaml >
default), Pydantic validation hataları.

**`tests/unit/test_postproc.py`** — `strip_preamble` regex'inin false positive vermemesi,
JSON çıktı formatı.

**`tests/unit/test_selector.py`** — Target seçici doğru dosyayı yüklüyor mu.

**`tests/integration/test_engine_llama.py`** — Küçük test model dosyası (TinyLlama Q8,
100MB) ile gerçek llama-cli çağrısı. Ağır — CI'da `pytest -m slow` bayrağıyla ayrılır.

**`tests/integration/test_end_to_end.py`** — CLI → engine → postproc tam yol,
subprocess ile.

**`tests/fixtures/sample_prompts.jsonl`** — 10 örnek prompt, unit testler için sabit
giriş.

### 9.6 — `bench/` — performans ölçümleri

**`bench/latency.py`** — CLI'ı N kez çağır, wall-clock ve token-per-second raporla.
50-in/250-out senaryosu için.

**`bench/memory.py`** — Model yüklerken ve inference sırasında `nvidia-smi` + `psutil`
snapshot al.

### 9.7 — `docs/` — proje dokümantasyonu

- `QUICKSTART.md` — 5 dakikada kurulum ve ilk kullanım.
- `MODEL_CARD.md` — Standart HF model kartı: intended use, training data, evaluation,
  limitations, biases, license.
- `TRAINING.md` — "Kendi promptsmith'ini eğit" rehberi. Data schema, config, komutlar.
- `EVAL.md` — Değerlendirme metodolojisi. Judge, rubric, baseline seçimi.
- `TARGETS.md` — Nasıl yeni target profili eklenir.
- `gold_examples.md` — El yapımı altın örnekler. Test seti çekirdeği.

---

## §10 — Veri Modeli

Bu bölüm sadece bir tablo değil; her veri dosyasının şeması, alan tanımları, örnekleri,
kısıtları.

### 10.1 — Eğitim örneği (`training/datasets/*.jsonl`)

JSON Lines formatı, satır başına bir örnek:
```json
{
  "id": "gold_001",
  "source": "gold" | "transcript" | "shared" | "distill",
  "target": "claude-code" | "chatgpt" | "cursor" | "generic",
  "lang": "tr" | "en" | "mix",
  "input": "raw user prompt string",
  "output": "optimized prompt string",
  "meta": {
    "created_at": "2026-07-17T12:00:00Z",
    "teacher": "claude-opus-4.7" | "deepseek-v3" | null,
    "reviewed_by": "kemal" | null,
    "notes": "optional short comment"
  }
}
```

Alan kuralları:
- `id` — kaynak prefix + sıralı numara. Silinen kayıtlar id'yi tekrar kullanmaz.
- `source` — 4 kaynaktan biri; test setinde sadece `gold`.
- `target` — bir örnek birden fazla target için kullanılamaz (ayrı satırlar).
- `input` — 20-2000 karakter aralığı; dışı validate.py atar.
- `output` — 50-4000 karakter; kısa ise (< 50) düşük kalite sinyali, uzun ise (> 4000)
  kontrol edilir.
- `meta.reviewed_by` — insan gözden geçirmesinin izi. Test setinde zorunlu.

### 10.2 — Test seti (`training/datasets/test.jsonl`)

Aynı şema, ama:
- Tüm örnekler `source: "gold"`.
- Tüm örnekler `meta.reviewed_by: "kemal"`.
- 200 örnek: 100 İngilizce + 100 Türkçe; 50 kod, 50 metin yazımı, 30 debugging, 30 refactor,
  20 veri analizi, 20 tasarım/UI.
- Test seti donmuş — MVP release'e kadar yalnızca ekleme (silme yok, düzenleme yok).

### 10.3 — Değerlendirme kaydı (`eval/reports/*.jsonl`)

Her judge çağrısının kaydı:
```json
{
  "run_id": "2026-08-01-r16-e3",
  "model": "promptsmith-qwen2.5-7b-r16-e3",
  "test_example_id": "gold_042",
  "target": "claude-code",
  "input": "...",
  "our_output": "...",
  "baseline_output": "...",
  "judge": "prometheus-2-7b",
  "our_score": 4,
  "baseline_score": 3,
  "our_win": true,
  "rationale": "...",
  "timestamp": "..."
}
```

### 10.4 — Spot-check kaydı (`eval/spotcheck-*.jsonl`)

```json
{
  "run_id": "...",
  "test_example_id": "gold_017",
  "kemal_verdict": "good" | "orta" | "kotu",
  "kemal_comment": "opt.",
  "timestamp": "..."
}
```

### 10.5 — Config (`~/.promptsmith/config.yaml`)

Runtime kullanıcı config'i:
```yaml
model:
  path: /path/to/promptsmith-qwen2.5-7b-q4_k_m.gguf
  backend: llama
target: claude-code
generate:
  max_new_tokens: 512
  temperature: 0.7
```

### 10.6 — HF Hub model kartı frontmatter

```yaml
---
license: apache-2.0
base_model: Qwen/Qwen2.5-7B-Instruct
tags:
  - prompt-engineering
  - lora
  - qlora
  - unsloth
language:
  - en
  - tr
datasets:
  - promptsmith/promptsmith-v1
library_name: peft
---
```

Devamı Markdown gövde: model amacı, kullanım, sınırlamalar (aşağıda §16).

---

## §11 — Yapılandırma ve Mesajlar

### 11.1 — Ortam değişkenleri (tam liste)

| Değişken | Katman | Zorunlu | Amaç |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | training | Faz 1 için evet | Teacher distillation |
| `DEEPSEEK_API_KEY` | training | Yedek | Anthropic quota dolarsa |
| `HF_TOKEN` | training + release | evet | Model + dataset upload |
| `PROMPTSMITH_MODEL_PATH` | inference | evet | GGUF dosya yolu |
| `PROMPTSMITH_TARGET` | inference | hayır | Default target |
| `PROMPTSMITH_CONFIG` | inference | hayır | Alternatif yaml yolu |
| `PROMPTSMITH_LOG_LEVEL` | inference | hayır | INFO/DEBUG/WARN |
| `PROMPTSMITH_LLAMA_BIN` | inference | hayır | `llama-cli` yolu PATH'te değilse |
| `WANDB_API_KEY` | training | hayır | Weights & Biases takibi |
| `WANDB_PROJECT` | training | hayır | Proje adı, default `promptsmith` |

### 11.2 — Log mesajları (kullanıcıya görünen)

Log seviyeleri: DEBUG (dev), INFO (default), WARN, ERROR.

Örnek INFO satırları:
- `[promptsmith] loading model: /path/to/model.gguf (Q4_K_M, 4.4GB)`
- `[promptsmith] target profile: claude-code`
- `[promptsmith] generation done in 1.42s (185 tokens)`

Örnek ERROR:
- `[promptsmith] model file not found: /path/to/model.gguf. Set PROMPTSMITH_MODEL_PATH or use --model.`
- `[promptsmith] llama-cli returned exit code 1: <stderr>`

Türkçe mesajlar? Karar: MVP'de sadece İngilizce log/hata (uluslararası açık kaynak
proje uygulamalarına uyum). Türkçe kılavuz `docs/QUICKSTART.tr.md` (opsiyonel Faz 2).

### 11.3 — CLI yardım metni (`promptsmith --help` çıktısı)

```
Usage: promptsmith [OPTIONS] [USER_PROMPT]

  Rewrite a raw user prompt into an optimized prompt for a downstream LLM.

Options:
  -t, --target [claude-code|chatgpt|cursor|generic]
                                  Target LLM profile.
  -m, --model PATH                Path to GGUF model file.
  --explain                       Also output a short explanation of changes.
  --json                          JSON-formatted output.
  --stdin                         Read prompt from stdin.
  --version                       Show version and exit.
  --help                          Show this message and exit.

Examples:
  promptsmith "shu bug'i coz reflection'da"
  echo "long messy request" | promptsmith --stdin --target chatgpt
  promptsmith --model ~/models/promptsmith.gguf --explain "..."
```

### 11.4 — Model kartı sabit metinleri

Model kartında yer alması gereken sabit bölümler (`docs/MODEL_CARD.md`):

**Intended use** — 1-2 paragraf. "This model rewrites raw prompts into structured
prompts suitable for downstream LLMs. It is NOT a general-purpose assistant, is NOT
suited for direct question answering, and is NOT a safety filter."

**Training data** — 1500-2500 örneklik karma dataset; kaynaklar; anonimleştirme;
lisans notu.

**Evaluation** — Test set (200 örnek), judge model, baseline, kazanma oranı.

**Limitations** — 5-7 madde: does not guarantee correctness of downstream LLM output;
no PII detection; may hallucinate structural elements; short (< 20 char) prompts
under-perform; target profiles are heuristic, not perfect fit for every LLM version;
Turkish and English trained but tested less on other languages; jailbreak attempts pass
through (downstream responsibility).

---

## §12 — Görev Kırılımı (yapraklar)

Bu bölüm ağacın yapraklarını sıralı, uygulanabilir görev listesine dönüştürüyor.
"Faz X — Görev N.M" biçiminde numaralanır. Uygulama fazında `/hedef` skill'iyle bu liste
takip edilir.

### Faz 0 — Kurulum ve Dry-Run (1-2 gün)

**T0.1** Proje kod adını netleştir (ADR-01) — Kemal onayı. Alternatif listeden seç.
**T0.2** GitHub repo oluştur, private başlar. `promptsmith` (veya seçilen isim). README
placeholder, LICENSE (MIT), `.gitignore`.
**T0.3** Klasör iskeleti oluştur (§9.1'deki tam ağaç). Boş dosyalar `touch`.
**T0.4** Root `pyproject.toml`, `training/pyproject.toml`, `setup.cfg`, `.env.example`,
`Makefile`, `conftest.py` yaz (§9 içerikleriyle).
**T0.5** `.python-version` = 3.12. `uv` veya `venv` ile `.venv/`. `pip install -e .`
başarısız olmamalı — sadece hafif bağımlılıklar.
**T0.6** `pip install -e ./training[cu124]` (Unsloth Windows/CUDA versiyonu). Kurulum
başarısız olursa iki senaryo:
  - (a) WSL2 Ubuntu kur, tekrar dene.
  - (b) `bitsandbytes-windows` fallback wheel.
**T0.7** GPU görünürlük testi:
```python
import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))
```
Beklenen: `True, "NVIDIA GeForce RTX 4060 Laptop GPU"` (veya masa üstü varyantı).
**T0.8** Unsloth dry-run: 20 sentetik örnek ile 1 epoch dummy training (Qwen 2.5 0.5B
Instruct — küçük, hızlı). Amaç: pipeline uçtan uca çalışıyor mu, VRAM/HDD tepe kullanımı
nedir. Başarı ölçütü: eğitim biter, LoRA kaydedilir, "hello world" prompt ile inference
verir.
**T0.9** llama.cpp derleme (CUDA). `git clone`, `cmake -B build -DGGML_CUDA=ON`,
`cmake --build build --config Release`. Test: `llama-cli --version`.
**T0.10** `llama-cli` ile bir hazır 4-bit model dosyası (örn. Qwen2.5-0.5B GGUF)
indirilir, "prompt engineer olarak yeniden yaz" gibi bir istek verilir, çıktı alınır.
Amaç: inference boru hattı OK.
**T0.11** Faz 0 kapanış: `docs/QUICKSTART.md` iskeleti, `CHANGELOG.md`'ye "Setup done"
girişi, ilk commit push.

### Faz 1 — Veri Seti Oluşturma (3-5 gün)

**T1.1** `data/schema.py` — Pydantic model. Validate script.
**T1.2** `data/import_gold.py` — Kemal + Claude birlikte 20 el yapımı altın örnek yazsın.
Format: `docs/gold_examples.md` içine ekleyerek. Bu bir "sohbet" günü. Türkçe 10 +
İngilizce 10.
**T1.3** El yapımı örnekleri 20'den 200'e çıkar. Kaba çeşitlilik: 50 kod, 50 metin
yazımı, 30 debugging, 30 refactor, 20 veri analizi, 20 tasarım/UI.
**T1.4** Test setini bunlardan seç (200 hepsi). `test.jsonl` oluştur, dondur.
**T1.5** `data/harvest_transcripts.py` — Kemal'in `~/.claude/projects/` altındaki
oturum jsonl'lerini tara. İlk kullanıcı mesajını "ham prompt" olarak, Claude'un
sonraki cevabındaki "structured question" veya "başarılı cevap" kısmını "optimize"
tarafında kullan (kaba heuristik). Anonimleştirme, dedup.
**T1.6** Sonuç: `raw/transcripts.jsonl` ~100-300 örnek. İnsan gözden geçir (Kemal örnek
bazında hızlıca "iyi/kötü" işareti; sadece iyileri tut).
**T1.7** `data/distill_teacher.py` — teacher distillation. Ham prompt kaynakları:
  - ShareGPT'den 400 örnek.
  - Alpaca'dan 200.
  - OpenAssistant'tan 200.
  Toplam 800 ham. Claude Opus 4.7 API ile "yeniden yaz" ürettir. Maliyet tahmini önce
  `--dry-run` ile — 800 × ~2000 output token × Claude Opus 4.7 fiyatı. Bütçe kapağı
  $50; aşarsa örnek sayısını kısıtla.
**T1.8** Distillation sonrası kontrol: 50 rastgele örneği Kemal spot-check. Anthropic
teacher çıktısı stil olarak uygun mu, target LLM'ler için (Claude/ChatGPT/Cursor) doğru
mu.
**T1.9** `data/merge_dedup.py` — hepsini birleştir, MinHash near-dup elemesi. Rapor:
son sayı.
**T1.10** `data/split_train_val_test.py` — 80/10/10 split. Gold zaten test'te. Train:
~1200, val: ~150, test: 200 hedef.
**T1.11** `data/tokenize_stats.py` — uzunluk histogramı, en uzun 10 örnek denetle.
Max_seq 2048'e sığıyor mu.
**T1.12** Faz 1 kapanış: veri seti raporu (`docs/DATASET.md`), Kemal onayı, commit.

### Faz 2 — İlk Fine-Tune (1-2 gün)

**T2.1** Pilot deneme: Qwen 2.5 3B üzerinde 200 örnek 1 epoch. Amaç: hyperparameters
sanity check. Beklenen süre: 30-45 dk.
**T2.2** Sonuç değerlendir — loss düşüyor mu, çıktı gramerli mi.
**T2.3** Tam eğitim: Qwen 2.5 7B üzerinde tam train seti, 3 epoch. `training/sft/train.py
--config qwen2.5-7b-r16.yaml`.
**T2.4** Eğitim sırasında `nvidia-smi -l 5` ile VRAM izleme. Log dosyası kayıt.
**T2.5** Eğitim bitince: `outputs/qwen2.5-7b-r16/final/` altında LoRA adapter,
tokenizer config, training log.
**T2.6** Sanity inference: 10 test örneği ile "manuel eyeball". Çıktı gramerli, uygun
uzunlukta, target sistem promptu takip ediyor mu.
**T2.7** Yedek Phi-4-mini deneme: aynı config aynı veri seti ile. Sonuç kıyaslamak
için.
**T2.8** Karar: hangisi Faz 3'e geçer. Kriter: sanity görünen kaliteye ek olarak,
inference gecikmesi ve VRAM.

### Faz 3 — Değerlendirme ve İterasyon (2-4 gün)

**T3.1** Prometheus 2 7B modeli indir (`unsloth/Prometheus-2-7b` veya HF orijinal).
**T3.2** `eval/run.py` çalıştır: test setinin tümü. Yaklaşık 200 × 2 (bizim +
baseline) × 30 sn generate + 20 sn judge = ~5-6 saat GPU süresi.
**T3.3** Rapor incele: kazanma oranı % kaç?
  - < %50: veri seti veya hyperparameter sorunu — geri Faz 1/Faz 2.
  - %50-%65: iterasyon (T3.5-T3.10).
  - > %65: T3.11 (spot-check + son karar).
**T3.4** Kemal spot-check 30 örnek. Judge doğruluğu = judge vs. Kemal karar tutarlılığı.
**T3.5** Hata analizi — en kötü 20 örnek, kalıp arama. Muhtemel kalıplar:
  - Çok uzun çıkıyor → temperature/top_p ayarı.
  - Yanlış target format → target prompt'unu iyileştir.
  - Türkçe kayıp → dil örneklerini artır.
  - Genel modu bozuluyor → veri setinde generic örnekler yetersiz.
**T3.6** Veri seti iyileştirmesi: hata analizinden çıkan boşluklar için 100-300 yeni
el yapımı veya distillation örneği ekle.
**T3.7** Hyperparam sweep (küçük): rank {8, 16, 32}, learning_rate {1e-4, 2e-4, 5e-4}.
9 kombinasyon değil, akıllı seçim (rank 16 + lr 2e-4 baseline; rank 32 + lr 2e-4 ek).
**T3.8** Yeniden eğit, değerlendir. En iyi model → `outputs/best/`.
**T3.9** DPO opsiyonel: tercih verisi (kazanan/kaybeden çift) üretilebilirse DPO ile
ince ayar. MVP için isteğe bağlı — Kemal karar.
**T3.10** Son değerlendirme: kabul kriterleri (§4.4) tablosunu doldur. Bir kalem bile
kırmızı ise iterasyona dön veya Kemal ile kapsam sohbeti.
**T3.11** Faz 3 kapanış: `docs/EVAL.md` sonuç güncelle, model card ilk taslağı,
commit + tag `v0.1.0-rc1`.

### Faz 4 — Paketleme ve Release (1-2 gün)

**T4.1** `pack/merge_lora.py` — En iyi adapter'ı base ile merge, fp16 safetensors.
**T4.2** llama.cpp `convert_hf_to_gguf.py` → fp16 GGUF. Boyut: ~14GB.
**T4.3** `llama-quantize` Q4_K_M → ~4.4GB.
**T4.4** Sanity: `llama-cli --model x.gguf` ile 10 spot örnek.
**T4.5** `bench/latency.py` — 20 istekle wall-clock ölç. Hedef < 2 sn ortalama.
**T4.6** `bench/memory.py` — inference sırasında VRAM tepesi. Hedef < 7 GB.
**T4.7** Model kartı finalize: `docs/MODEL_CARD.md`. Limitations, license, citation.
**T4.8** README finalize.
**T4.9** Version bump v0.1.0. CHANGELOG güncelle.
**T4.10** HF Hub repo oluştur `promptsmith/promptsmith-qwen2.5-7b-v1`. Push: adapter,
GGUF, tokenizer, README.
**T4.11** GitHub push, tag `v0.1.0`, GitHub Release notes.
**T4.12** PyPI publish (opsiyonel). `hatch build`, `hatch publish`.
**T4.13** Duyuru: r/LocalLLaMA, HN "Show HN", kişisel Twitter/BlueSky (opsiyonel).

---

## §13 — Test ve Kabul Kriterleri

### 13.1 — Test seviyeleri

**Birim testler** (`tests/unit/`): pytest, hızlı (< 5 sn tamamı). Coverage hedefi %70+
`src/promptsmith/` için. Coverage `training/` için düşük (ağır bağımlılık, mock zor).

**Entegrasyon testleri** (`tests/integration/`): `pytest -m slow` bayrağıyla. Küçük
gerçek GGUF (TinyLlama Q8, 100MB) ile end-to-end. Manuel `make test-slow` ile.

**Değerlendirme (evaluation)**: `training/eval/run.py`. LLM tabanlı, unit test değil.
Her release öncesi çalışır.

**Kabul testleri**: `docs/QUICKSTART.md`'deki 5 adımı fresh Windows makinede tekrar et.
Süre < 15 dk olmalı.

### 13.2 — Kabul kriterleri (release-gate)

Tekrar (§4.4'ün detayı):

- [ ] Kazanma oranı ≥ %65 test setinde (LLM judge).
- [ ] Kemal spot-check ≥ %70 iyi/orta (30/30 örnek).
- [ ] Inference gecikmesi ortalama < 2 sn (bench/latency.py).
- [ ] VRAM tepe kullanımı < 7 GB (bench/memory.py).
- [ ] `pip install -e .` fresh venv'de hatasız.
- [ ] Model kart tam (tüm zorunlu bölümler).
- [ ] README kurulum adımları fresh sistemde çalışır.
- [ ] Lisans dosyaları (LICENSE + LICENSE-model) mevcut, doğru.
- [ ] `.env` `.gitignore`'da; git history'de sızıntı yok (git-secrets scan).

Herhangi biri fail → release yok, geri iterasyon.

### 13.3 — Test veri seti örneği (küçük fixture)

`tests/fixtures/sample_prompts.jsonl`:
```json
{"id":"fix_001","input":"bug'i coz","target":"claude-code","expected_keywords":["Görev","Bağlam","Kabul kriterleri"]}
{"id":"gen_002","input":"blog yazisi yaz seo hakkinda","target":"chatgpt","expected_keywords":["outline","tone","word count"]}
{"id":"cur_003","input":"bu componenti temizle","target":"cursor","expected_keywords":["Refactor","Extract","Preserve"]}
```

`expected_keywords` — çıktıda geçmeleri beklenen kelimeler. Unit test bunu regex ile
kontrol eder (esnek eşleşme).

### 13.4 — CI hattı (opsiyonel MVP, önerilir)

GitHub Actions `.github/workflows/ci.yml`:
- Trigger: PR / push main.
- Job: `ubuntu-latest`, Python 3.10/3.12 matrix.
- Steps: checkout → setup-python → `pip install -e .` → `pytest tests/unit` → lint
  (`ruff check`).
- Slow / GPU testleri CI'da değil — Kemal lokal.

---

## §14 — Hata Senaryoları

Aşağıdaki liste MVP boyunca karşılaşılması muhtemel her sıkıntının el kitabı. Her madde:
belirti → sebep → çözüm.

**H1 — Unsloth CUDA-sürüm uyumsuzluğu.** Kurulumda `RuntimeError: CUDA version mismatch`.
Sebep: Sistemdeki CUDA driver 12.5, PyTorch 12.4 wheel derlenmiş.
Teşhis: `nvcc --version` vs. `torch.version.cuda`.
Çözüm: `pip install torch --index-url https://download.pytorch.org/whl/cu125` ile
eşle, sonra Unsloth'u yeniden yükle.

**H2 — bitsandbytes Windows'ta çökmesi.** `OSError: [WinError 126]`.
Sebep: Windows'ta bnb tarihen sorunlu.
Çözüm: `pip install bitsandbytes-windows` ya da alternatif Windows wheel'ı. Nihai
çözüm: WSL2.

**H3 — Eğitim sırasında OOM (Out of Memory).** `torch.cuda.OutOfMemoryError`.
Sebep: batch × seq_length çok büyük.
Çözüm: `per_device_train_batch_size: 1`, `max_seq_length: 1024`,
`gradient_checkpointing: "unsloth"` aktif tut.

**H4 — Judge modeli (Prometheus 2) yüklerken OOM.** Eval sırasında model + judge aynı
anda VRAM'e sığmıyor.
Çözüm: sırayla — önce our model'la tüm generate, kaydet; sonra our model'ı boşalt,
judge yükle, skor. `eval/run.py`'da `--sequential` bayrağı.

**H5 — llama.cpp `convert_hf_to_gguf.py` başarısız.** Genelde tokenizer uyumsuzluğu.
Sebep: özel token'ler, chat template metadata eksik.
Çözüm: `--dtype auto`, `--verbose` ile logu incele, gerekirse Unsloth'un
`save_pretrained_gguf` sarmalayıcısını kullan.

**H6 — GGUF çıktı bozuk / nonsense üretiyor.** Q4_K_M sonrası kalite çöktü.
Sebep: quantization çok agresif, veya Qwen 3.5 kullanıldı (biz kullanmayacaktık).
Çözüm: Q5_K_M dene (biraz büyük ama kaliteli). Q6_K bir sonraki dur.

**H7 — CLI `llama-cli` bulunamıyor.** `FileNotFoundError`.
Sebep: llama.cpp binary PATH'te değil.
Çözüm: `PROMPTSMITH_LLAMA_BIN=/tam/yol/llama-cli` env veya CLI `--llama-bin`.

**H8 — Türkçe promptta model İngilizce cevap veriyor.** Beklenmedik dil geçişi.
Sebep: sistem promptu İngilizce yazılmış + veri setinde Türkçe az.
Çözüm: sistem promptunda "Reply in the same language as the input" satırı (zaten var,
ama modelin uyduğu kontrol edilecek); veri setinde Türkçe oranını artır.

**H9 — Model kendi kendine cevap veriyor (prompt yerine).** Beklenen: sadece rewrite;
gerçek: soru cevaplıyor.
Sebep: SFT sırasında sistem promptu tutarsız verildi; veya format bozukluğu.
Çözüm: eğitim verisinin her satırında sistem promptu tutarlı, format yanıt kısmı sadece
rewrite. Formatting fonksiyonu (`format_chatml`) sabit.

**H10 — Judge kararı Kemal ile uyumsuz.** Judge model 4 verirken Kemal "kötü" diyor.
Sebep: judge modeli konuya körü, verbosity bias var.
Çözüm: judge modelini değiştir (Prometheus 2 → GPT-4o-mini opsiyonel API), rubric'i
sertleştir, spot-check'ten öğrenilen kalıpları rubric'e yansıt.

**H11 — Rate limit — Anthropic teacher distillation.** 429 hatası.
Sebep: dakikada/saatte istek sınırı.
Çözüm: `tenacity` ile exponential backoff, gece boyunca çalıştır, veya DeepSeek V3
API'ye geç.

**H12 — Hugging Face upload başarısız.** LFS quota veya token izni.
Çözüm: HF token'a "write" izni; büyük dosyalar için `huggingface_hub[cli]` +
`hf-transfer` etkin (`HF_HUB_ENABLE_HF_TRANSFER=1`).

**H13 — GitHub push reddedildi (dosya boyutu).** > 100MB dosya (GGUF).
Çözüm: GGUF'yi GitHub'a değil, HF Hub'a yükle. GitHub'da sadece kod. `.gitignore`'a
`*.gguf`.

**H14 — Kullanıcı `PROMPTSMITH_MODEL_PATH` unuttu.** CLI çalışmıyor.
Çözüm: net hata mesajı + `--model` bayrağını öner + `docs/QUICKSTART.md`'ye yönlendir.

**H15 — Windows path uzunluğu.** 260 karakter sınırı, uzun dataset klasör yolları.
Çözüm: `git config --system core.longpaths true` + Windows registry
`LongPathsEnabled=1` talimat notu docs.

**H16 — E: sürücüsü kopması (Kemal ortamı).** Kod tabanı yanlışlıkla E:'de kalmış.
Çözüm: Faz 0'da C: kontrol talimatı. Otomatik: `Makefile`'da `assert-drive` hedefi
proje kökünün C: olup olmadığını doğrular.

**H17 — Kişisel bilgi sızıntısı — transkriptlerde.** anonymize.py bazı desenleri
yakalamıyor.
Sebep: yeni tür (API key formatı) desende yok.
Çözüm: `git-secrets` veya `detect-secrets` çalıştır dataset üzerinde; PII taraması
manuel spot-check.

**H18 — Model çok kısa çıktı üretiyor (100 token altı).** Bir tür kolaya kaçma.
Sebep: eğitim verisinde çok kısa örnekler baskın.
Çözüm: kısa (< 50 char) outputları veri setinden temizle; min_new_tokens ekle.

**H19 — Fine-tune sonrası base model "hafıza kaybı" (catastrophic forgetting).** Model
prompt yeniden yazmakta iyi ama diğer istekleri (genel sohbet) yapamaz olur.
Sebep: rank yüksek + tek göreve odaklı veri seti.
Çözüm: MVP için sorun değil — model tek göreve odaklı olması istenen. Rank 16, r*alpha
düşük tutmak yeterince frenler. Bu MVP ötesinde (Faz 2 multimodal genişleme'de)
karışık dataset eğitimi (%10 genel örnek).

**H20 — Model çıktısı ChatML sızıntısı içeriyor.** Output'un içinde `<|im_end|>` gibi
special token'lar görünüyor.
Sebep: tokenizer yapılandırması yanlış; stop token doğru set edilmedi.
Çözüm: `llama-cli --reverse-prompt "<|im_end|>"` ile stop belirt; postproc'ta gene de
temizle (belt+suspenders).

---

## §15 — Performans Bütçesi

Bu bölüm sayısal hedefler ve nasıl ölçüldüğü. "Yeterince hızlı" değil; sınırlar var.

### 15.1 — Inference (kullanıcı yolu)

| Metrik | Hedef | Ölçüm |
|---|---|---|
| Model yükleme (cold start) | < 4 sn | ilk `promptsmith` çağrısı stopwatch |
| Prompt kodlama | < 50 ms | 50 token için |
| İlk token gecikmesi (TTFT) | < 400 ms | llama.cpp `-n 1` |
| Ortalama token hızı | ≥ 50 tok/sn | RTX 4060 Q4_K_M 7B için |
| 50-in / 250-out ortalama toplam | < 2 sn | `bench/latency.py`, 20 çağrı ortalaması |
| VRAM tepe | < 7 GB | `nvidia-smi -l 1` sırasında |
| RAM tepe | < 3 GB | `psutil` proc RSS |
| Sıcak start (model önceden yüklüyse) | < 1.5 sn |  |

Bu hedefler RTX 4060 8GB (laptop) için. Daha zayıf GPU'larda (GTX 1660 6GB, RTX 3050
4GB) `n_gpu_layers` azaltarak, CPU offload ile çalıştırılabilir — hedefler düşer.

### 15.2 — Eğitim (offline)

| Metrik | Hedef | Not |
|---|---|---|
| Tek epoch süresi (Qwen 7B, 1500 örnek) | 45-60 dk | fp16, batch 2, grad_accum 4 |
| 3 epoch toplam | 2.5-3 saat |  |
| VRAM tepe eğitim | < 7.5 GB | gradient checkpointing açık |
| Disk toplam | < 30 GB | base model + checkpoint + LoRA |

Kemal'in RTX 4060 laptop olduğu için termal throttling risk. Uzun eğitimde:
- Fan max, dizüstü stand + underclock yerine underlvolt tercih.
- Odada 25°C altı.
- Şarj kabloda (batarya modu clock kısar).

### 15.3 — Değerlendirme

| Metrik | Hedef | Not |
|---|---|---|
| 200 test örneği için generate + judge | < 6 saat | GPU yalnız |
| Judge tek örnek | < 15 sn | Prometheus 2 7B Q4_K_M |
| Toplam VRAM (bizim + judge sıralı) | < 7 GB | `--sequential` |

### 15.4 — Release öncesi bench pipeline

`make bench` çalıştırınca:
1. `bench/latency.py` — 20 çağrı, wall clock ortalama + p95 + p99.
2. `bench/memory.py` — model yükleme, generate, boşaltma sırasında peak.
3. `bench/coldwarm.py` — cold vs. warm start farkı.
Çıktı: `bench/results/bench-YYYY-MM-DD.md`. Regression tespiti: son 3 çıktıyla farklar.

### 15.5 — Neden bu sayılar

- 2 sn eşiği kullanıcı akıcılık algısı — Kemal terminal başında bekleyecek.
- 7 GB VRAM — 8 GB'ın altı ki kullanıcı ekstra bir chrome tab / IDE açık tutabilsin.
- 50 tok/sn — Qwen 2.5 7B Q4_K_M için RTX 4060'ın makul rakamı (llama.cpp bench).

Bu sayılar aşılırsa MVP kabul, aşılamazsa iterasyon (§13.2 kabul kapısı).

---

## §16 — Güvenlik

Prompt yeniden yazan bir modelin güvenlik yüzeyi sınırlıdır (kod çalıştırmıyor, dış
erişim yapmıyor) ama sıfır değil. Bu bölüm net.

### 16.1 — Tehdit modeli

- **T1 — Prompt injection kötüye kullanım.** Kullanıcı `promptsmith`'e "ignore previous
  instructions" yollar; yeniden yazılmış prompt hedef LLM'i kandırmak için tasarlanmıştır.
  Değerlendirme: `promptsmith` bunu bir "kullanıcı isteği" olarak yorumlar, yeniden
  yazar. Hedef LLM zaten kendi güvenliğinden sorumlu. Model kartına yazılıyor.
- **T2 — Zararlı içerik (bomba yapımı, silah tarifi vb.).** Aynı — biz filtre değiliz.
  Model kartı: "does not filter for harmful content; downstream target model
  responsible."
- **T3 — PII (kişisel bilgi) sızıntısı — eğitim tarafı.** Kemal'in Claude Code
  transkriptlerinden veri çıkarırken şifreler, e-postalar, IP'ler sızabilir.
  Anonimleştirme zorunlu (`data/anonymize.py`). Regex + `detect-secrets` taraması.
- **T4 — Model ağırlıklarında ezberlenmiş kişisel bilgi.** SFT çok az örnekle
  ezberleme yapabilir. Test setinde "Kemal'in adı verilirse output'ta e-mail sızıyor
  mu?" testi.
- **T5 — Malicious model dosyası.** Kullanıcı yanlış bir kaynaktan GGUF indirir.
  Karşı-önlem: model kartında SHA256 checksum, "official source is only HF Hub" notu.
- **T6 — Bağımlılık zinciri.** `unsloth`, `bitsandbytes` gibi paketler potansiyel
  saldırı yüzeyi. `pip-audit` CI'da; `requirements.txt` pin.

### 16.2 — Güvenlik kontrol listesi

- [ ] `.env` `.gitignore`'da.
- [ ] `git-secrets` veya `detect-secrets` pre-commit hook.
- [ ] Eğitim veri seti taraması: `detect-secrets scan training/datasets/`.
- [ ] Model kartı Limitations bölümü — jailbreak, harmful content, PII notu.
- [ ] Bağımlılık pinleme: hem `pyproject.toml` hem `training/pyproject.toml` versiyon
      alt sınırı, `requirements.lock` (uv lock veya pip-compile).
- [ ] HF Hub'daki model kartında SHA256.
- [ ] GitHub Secrets scanning enabled.

### 16.3 — Ne YAPMIYORUZ (bilinçli)

- Prompt-level güvenlik filtresi (jailbreak detection). Faz 2, opsiyonel.
- PII redaction inference'da. Faz 2, opsiyonel plugin.
- Telemetri, kullanıcı izleme. Hiç yok, olmayacak.

### 16.4 — Sorumluluk ilanı (README)

MVP README net söylüyor:
> `promptsmith` improves prompt clarity. It does not verify correctness of the
> downstream LLM output, does not filter for jailbreaks or harmful content, and does
> not scrub personal information. Users are responsible for the content they send
> through, and for the actions taken based on downstream LLM output.

---

## §17 — Risk Matrisi

Aşağıdaki matris 15 riski; her biri olasılık × etki, sahip, azaltma stratejisi.

| # | Risk | Olasılık | Etki | Sahip | Azaltma |
|---|---|---|---|---|---|
| R1 | Veri seti kalitesi yetersiz — model ezberliyor ama genellemiyor | Yüksek | Yüksek | Kemal + Claude | Faz 1 sonunda spot-check; Faz 3'te hata analizi; boşlukları yeni örneklerle doldur |
| R2 | Unsloth Windows kurulumu başarısız | Orta | Yüksek | Kemal | Faz 0 dry-run; WSL2 fallback hazır |
| R3 | RTX 4060 8GB'da 7B eğitim OOM | Orta | Yüksek | Kemal | Faz 2 pilot 3B ile başla; batch 1 + grad_accum 8; seq 1024'e düş |
| R4 | LLM-as-judge (Prometheus 2) kararsız → yanlış metrik | Yüksek | Orta | Kemal | Kemal spot-check ile judge doğruluğu kalibre et; gerekirse GPT-4o-mini fallback |
| R5 | Anthropic teacher distillation maliyeti $50 kapak aşımı | Orta | Orta | Kemal | Bütçe kapağı önceden; DeepSeek V3 yedek; distillation batch small-first |
| R6 | Q4_K_M quantization sonrası kalite çöküşü | Düşük | Yüksek | Kemal | Q5_K_M yedek; Q6_K ikinci yedek; sanity 10 örnek geçmezse quant değişir |
| R7 | Kişisel bilgi sızıntısı eğitim datasında | Düşük | Çok yüksek | Kemal | detect-secrets tara; anonymize.py agresif regex; manuel spot-check |
| R8 | GGUF dönüşüm başarısız (llama.cpp tokenizer uyumsuzluk) | Orta | Yüksek | Kemal | Unsloth'un save_pretrained_gguf sarmalayıcısını kullan; Q8 önce test |
| R9 | Windows path uzunluğu (>260 char) | Düşük | Düşük | Kemal | git longpaths + registry ayarı; dataset yolları kısa tut |
| R10 | Kemal başka projelerle çakışıp uzun süre başlayamıyor | Yüksek | Orta | Kemal | Faz 0'ı bir hafta içinde başlat; ilk küçük çıktı 1 hafta içinde alınmalı — kaybolursa proje ölür |
| R11 | Base model lisans belirsizliği (Qwen ticari sınır çıkar) | Düşük | Orta | Kemal | Qwen 2.5 Apache 2.0 net; her release lisans dosyası kontrol |
| R12 | Hedef LLM (Claude Code) davranışı değişince prompt profili eskir | Orta | Orta | Kemal | Modüler target profilleri; her release öncesi 20 canlı test; sürüm etiketleri |
| R13 | Değerlendirme sırasında hallucination — judge kendi kararını uyduruyor | Orta | Orta | Kemal | Rubric sertleştir; her judge çağrısına rationale iste; spot-check ile kalibre |
| R14 | Windows'ta llama.cpp CUDA derlemesi başarısız (VS Build Tools eksik) | Orta | Orta | Kemal | Prebuilt binary alternatifi; docs/QUICKSTART.md'de detay |
| R15 | Kemal disket alanı yetersiz (base 4-bit ~5GB + checkpoint ~1-2GB × N + judge 5GB) | Orta | Orta | Kemal | Faz 0 disk kontrol; eski checkpoint'leri temizle; HF cache klasörünü büyük diske yönlendir |
| R16 | Model card / README'de aşırı iddia (rakamları abartma) | Düşük | Orta | Kemal + Claude | Kabul kriteri sayıları katı; "kazanma oranı" tanımı net |
| R17 | Kullanıcı topluluğu adopte etmiyor (r/LocalLLaMA sessiz) | Orta | Düşük | Kemal | MVP başarı = Kemal + 5-10 iyi tester; toplum sonraki metric |
| R18 | ADR-01 (isim) HF Hub / PyPI'da alınmış çıkar | Orta | Düşük | Kemal | Faz 0 T0.1'de doğrula, alternatifler hazır |

En kritik R1, R2, R3, R7: veri seti, Windows kurulumu, VRAM sığdırma, PII sızıntısı.

---

## §18 — Yayın ve Bakım

### 18.1 — Sürüm politikası

Semantic versioning (semver):
- `0.x.y` — pre-1.0. API kırıcı değişiklikler minor'da (0.1 → 0.2).
- `1.0.0` — API stabil kabul edildikten sonra (target profil kontratı, config şeması,
  CLI bayrakları).

### 18.2 — Release süreci

Her release adımı:
1. `main` branch temizlensin. Local test set çalıştır, hepsi geçmeli.
2. `CHANGELOG.md`'de "Unreleased" bölümünü sürüm numarasına çevir.
3. `pyproject.toml` version bump.
4. `git tag vX.Y.Z`.
5. `git push --tags`.
6. GitHub Actions release job otomatik (yoksa manuel `gh release create`).
7. HF Hub push: `python -m training.pack.push_hf --version vX.Y.Z`.
8. HF Hub'da model kartı elle gözden geçir.
9. Duyuru: r/LocalLLaMA, Twitter, blog (opsiyonel).

### 18.3 — Uzun vadeli bakım (MVP sonrası)

- **Kim bakacak?** MVP'de Kemal (Claude yardımıyla). Katkı için `CONTRIBUTING.md`
  hazırla; PR şablonu.
- **Bug rapor kanalları:** GitHub Issues yeter. HF Hub Community tab (varsa) da.
- **Model güncelleme frekansı:** her 3-6 ayda bir, ya da hedef LLM'lerden biri (Claude
  Code, ChatGPT) davranışını önemli değiştirdiğinde. Veri seti korunarak yeniden
  eğit — proje sürekli değil, sürüm bazlı.
- **Base model migration:** Qwen 2.5 → Qwen 3 → Qwen 4 geçişleri yıllık. Aynı veri
  seti farklı base ile yeniden eğit; bench et; kazanan yayınla.
- **Deprecation politikası:** eski target profilleri en az 1 minör sürüm boyunca
  desteklenir; sonra kaldırılır. `CHANGELOG` net.

### 18.4 — Community karşılığı

Bir açık kaynak proje adopsiyona ihtiyaç duyar. MVP sonrası:
- **HF Hub model kartı** demo widget (browser'da inference — HF Space).
- **GitHub Discussions** aç.
- **Örnek kullanım videosu** (2 dk) — README'de embed.
- **Blog post** (Kemal isterse) medium veya kişisel — nasıl eğitildi, ne öğrenildi,
  yol haritası.
- **Katkı listesi**: kolay-başlangıç issue'lar (`good first issue` etiketi) — target
  profil ekleme, translation, docs iyileştirme.

### 18.5 — Sürdürülemez olursa

Açık kaynak projeler sıklıkla ölür. Ölmezden önce:
- README başında son güncelleme tarihi.
- Belirli bir tarihte pasifleşecekse `MAINTENANCE.md` — "actively maintained until
  YYYY-MM; after that, forks welcome".
- Model dosyaları HF Hub'da mirror'lansın (topluluk kopyaladı mı).

---

## §19 — Gelecek (kapsam dışı ama tutulan fikirler)

MVP sonrası, öncelik sırasına göre olası genişlemeler. Karar hakkı Kemal'de; bu liste
"unutulmasın" için.

### F1 — MCP server entegrasyonu (öncelikli)

Claude Code MCP kullanıyor. `promptsmith` bir MCP server olarak paketlenirse Claude
Code doğrudan `promptsmith.rewrite("...")` tool çağırabilir. Kullanıcının artık dışarı
kopyalayıp yapıştırması gerekmez.
- Tahmini süre: 3-5 gün.
- Bağımlılık: MCP SDK (Python), CLI zaten var.

### F2 — Cursor / VSCode extension

Cursor ve VSCode'da bir kısayol (`Ctrl+Shift+P`) ile seçili metni `promptsmith`'ten
geçir, sonucu yerine yaz.
- Tahmini süre: 5-7 gün.
- Bağımlılık: VSCode extension API, `promptsmith` CLI subprocess.

### F3 — Browser extension (ChatGPT/Claude.ai)

Textarea'ya bir "iyileştir" butonu enjekte et. Extension `promptsmith` CLI ile lokal
bağlantı kurar (yerel HTTP server veya native messaging).
- Tahmini süre: 7-10 gün.
- Riskler: native messaging Windows'ta karmaşık; web extension policy değişiklikleri.

### F4 — Küçük router: küçük model → büyük model

Basit istekleri Phi-4-mini (3B) rewriter yapsın; karmaşık, yapısal istekleri Qwen 7B'ye
yollasın. Karmaşıklık heuristiği: token sayısı, konu (`re.search`), soru kelimeleri.
- Tahmini süre: 3-4 gün.

### F5 — Kullanıcı feedback döngüsü (RLHF-lite)

Kullanıcı çıktıya `promptsmith --thumbs up|down` diyebilsin. Anonim tercih verisi
toplansın (opsiyonel opt-in). Yeterli veri birikince DPO ile modeli yeniden eğit.
- Tahmini süre: 10-14 gün.
- Etik: opt-in şart, telemetri açık değildir default'ta.

### F6 — Multilingual genişleme

Almanca, Fransızca, Çince, İspanyolca, Rusça. Her dil için 200-500 örnek eklenir,
target profillerinde dil-uyumlu hint'ler.
- Tahmini süre: dil başına 3-5 gün.

### F7 — Explain mode zenginleşmesi

`--explain` bayrağı şu anda kısa "ne değişti" veriyor. Genişleme: prompt engineering
prensiplerini eğitici anlatım — kullanıcı öğrensin.
- Tahmini süre: 2-3 gün.

### F8 — Doğal ses arayüzü

Konuşma-tanıma (Whisper local) + `promptsmith` + TTS. Kullanıcı sesle konuşur, temizlenmiş
prompt metin olarak çıkar.
- Tahmini süre: 7-10 gün.
- Değer: mobil kullanıcılar.

### F9 — Görsel prompt engineering (Midjourney / FLUX / SDXL)

Ayrı bir model varyantı (`promptsmith-visual`): metin isteği → görsel model promptu.
PromptEnhancer benzeri. Farklı veri seti, ayrı adapter.
- Tahmini süre: 3-4 hafta (yeni veri seti + fine-tune).

### F10 — GUI

Basit bir Electron veya Tauri arayüzü — CLI'a gitmek istemeyen kullanıcılar için.
- Tahmini süre: 7-10 gün.

Bu liste sabit değil; hangi F'ler alacak yol Kemal'in kararı ve topluluk geri
bildirimine göre şekillenir.

---

## §20 — Senden Gerekenler + Sözlük

### 20.1 — Kemal'den beklenenler

Bu plan onaylanır onaylanmaz, uygulamaya geçmek için Kemal'den istenenler:

1. **Kod adı onayı** (ADR-01) — `promptsmith` mı, alternatif mi?
2. **API key sağlanması** — `.env`'e `ANTHROPIC_API_KEY` (Faz 1 için); yedek olarak
   `DEEPSEEK_API_KEY`. Ayrıca `HF_TOKEN` (write scope).
3. **Bütçe onayı** — Anthropic API distillation için kapak $50. Aşarsa dur.
4. **Zaman taahhüdü** — Faz 0 (1-2 gün) hemen mi, sonra mı? Toplam 2-3 hafta yoğun,
   4-5 hafta gevşek. Hangi tempoda?
5. **Test transkriptleri paylaşımı** — Kemal'in `~/.claude/projects/` içindeki jsonl
   dosyaları anonimleştirilse bile eğitim setine katma onayı gerekir (Kemal'in kendi
   çalışması, ama hassas görebileceği için).
6. **20 el yapımı altın örnek yazma zamanı** — Faz 1'de birlikte oturma. Yaklaşık 2-3
   saat.
7. **Faz 3 spot-check katılımı** — her iterasyonda 30-50 örnek "iyi/orta/kötü"
   işaretleme. Toplam ~2-3 saat, iterasyona yayılır.
8. **Release öncesi son onay** — HF Hub ve GitHub'a public push'tan önce Kemal görsün.
9. **İsim sahipliği** — GitHub repo, HF Hub organizasyon (varsa) `promptsmith` name
   claim.
10. **Sonraki adım seçimi** — MVP release'den sonra §19'daki F1-F10'dan hangisi?

### 20.2 — Bilinmeyenler (araştırılacak / karar bekleniyor)

- **B1** Kemal'in Claude Code oturum dosyaları formatı ne (JSON şeması)? Faz 0'da
  bakılacak (harvest_transcripts.py yazımında).
- **B2** Windows'ta llama.cpp CUDA prebuilt binary güncel mi? Faz 0 dry-run test.
- **B3** Qwen 2.5 7B Instruct'ın Unsloth 4-bit versiyonu (`unsloth/Qwen2.5-7B-Instruct-bnb-4bit`)
  RTX 4060 laptop'ta stabil çalışıyor mu? Faz 0 T0.8 test.
- **B4** DeepEval Türkçe metinlerde iyi mi, yoksa İngilizce'ye çeviri gerekli mi?
  Faz 3 T3.4 test.
- **B5** Prometheus 2 modeli 4-bit quantized halde HF Hub'da hazır mı? Değilse
  Unsloth'la kendimiz quantize.
- **B6** HF Hub'da `promptsmith` organizasyon ismi müsait mi? Faz 0 T0.1'de.
- **B7** PyPI'da `promptsmith` isim müsait mi? aynı yerde.

### 20.3 — Onay noktaları (checkpoint)

Kemal'in "dur, kontrol edeyim" demesi beklenen ana durak yerleri:
- Faz 0 sonu: kurulum çalışıyor, dry-run bitti.
- Faz 1 sonu: veri seti hazır, spot-check yapıldı.
- Faz 2 sonu: ilk fine-tune tamam, sanity iyi görünüyor.
- Faz 3 iterasyon sonları: değerlendirme raporu geldi.
- Faz 4 release öncesi: HF Hub push izni.

### 20.4 — Kavram sözlüğü

Kısaltmalar ve teknik terimler — plana yabancı biri hızlı okuyabilsin:

- **LLM** — Large Language Model. GPT-4, Claude, Qwen gibi.
- **Base model** — Fine-tune öncesi hazır model.
- **Fine-tune** — Belirli bir görev için modeli yeniden eğitme.
- **SFT** — Supervised Fine-Tuning. Etiketli (input → output) veri ile eğitim.
- **LoRA** — Low-Rank Adaptation. Base modelin ağırlıklarını dondurup küçük "adapter"
  matrisler eklemek. Bellek dostu.
- **QLoRA** — Quantized LoRA. Base model 4-bit quantize + LoRA. Çok daha az VRAM.
- **NF4** — 4-bit NormalFloat. QLoRA'da kullanılan quantization tipi.
- **GGUF** — llama.cpp'nin model formatı. Tek dosya, quantized, taşınabilir.
- **Q4_K_M** — GGUF'un 4-bit mixed precision quantization tipi. Kalite/boyut dengesi
  iyi.
- **Prompt** — LLM'e verilen metin girdi.
- **System prompt** — LLM'e "sen böyle davran" diyen sabit üst-metin.
- **User prompt** — Kullanıcının aktüel isteği.
- **ChatML** — Qwen, Anthropic, OpenAI'nin ortak chat template'i.
- **Token** — LLM'in temel birim (alt-kelime).
- **VRAM** — GPU'nun kendi RAM'i.
- **OOM** — Out of Memory. Bellek yetmez hatası.
- **LLM-as-judge** — Bir LLM'i başka LLM'in çıktısını değerlendirmek için kullanma.
- **Prometheus 2** — Açık kaynak bir judge modeli.
- **DPO** — Direct Preference Optimization. Tercih verisiyle SFT sonrası ince ayar.
- **RLHF** — Reinforcement Learning from Human Feedback. Klasik yol; DPO daha basit
  alternatifi.
- **ADR** — Architecture Decision Record. Mimari kararın kayıt formatı.
- **PII** — Personal Identifiable Information. Kişisel bilgi.
- **MCP** — Model Context Protocol. Claude Code'un tool entegrasyon standardı.
- **HF Hub** — Hugging Face Model Hub. Model paylaşım platformu.
- **PyPI** — Python Package Index. `pip install` kaynağı.

### 20.5 — Referans dokümanları

- Bu PLAN.md — canlı belge, uygulama sırasında güncellenir.
- `agac/agac.md` — Ham plan ağacı (bu planın motor çıktısı).
- `agac/agac.json` — Ağacın yapısal JSON hali.
- `agac/ham/` — Her turun konsey ham cevabı (denetim izi).
- (Faz 0 sonrası) `docs/QUICKSTART.md`, `docs/TRAINING.md`, `docs/EVAL.md`, model card.
- (Genel) Kemal'in `CLAUDE.md`'si — genel kurallar ve tercihler.

### 20.6 — Kapanış

Bu plan, konsey ağacının 17 turluk açılımı + web literatür araştırması + Kemal'in
çevre notlarının süzülmüş halidir. Uygulama sırasında değişecek — her fazın kapanışında
bu belge güncellenir, bir sonraki fazın bulguları eklenir. Plan bittiği zaman ne
`promptsmith` (veya seçilen isim) çalışan bir açık kaynak model olacak, hem GitHub +
HF Hub üzerinden dağıtılabilir olacak, hem de bu belge projenin ilk-günden-release'e
tam izini taşıyor olacak.

Bir sonraki adım net: Kemal onayı → §20.1 maddeleri karşılığı → Faz 0 T0.1'den
başlayarak `/hedef` disiplini. Kod yazma başlayınca uygulama sırasında bu plandan
sapmalar olursa PLAN.md güncellenir, konsey `council.mjs --fast` ile ikinci görüş
alınır, ilerlenir.

---

*Bu belge canlıdır. Son güncelleme: 2026-07-17.*
