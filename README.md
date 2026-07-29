# reprompt

`reprompt`, kısa veya dağınık bir isteği başka bir dil modelinin doğrudan
uygulayabileceği net bir çalışma tarifine dönüştürür. İsteği cevaplamaz; hedefi, bağlamı,
sınırları, teslimleri ve doğrulama ölçütlerini koruyarak yeniden yazar.

Proje iki parçadan oluşur:

- Python paketi; CLI, SDK, REST API, prompt derleyicisi ve `llama.cpp` çıkarım katmanını
  içerir.
- Eğitim araçları; veri hazırlama, QLoRA/SFT, değerlendirme ve GGUF paketleme akışını
  içerir.

Model ağırlıkları bu depoda bulunmuyor. Üretim için önerilen rota Qwen 2.5 7B Instruct
üzerinde QLoRA ve ardından Q4_K_M GGUF dönüşümüdür. Ortaya çıkan GGUF, dönüştürücü
sürümüne göre değişmekle birlikte yaklaşık 4–5 GiB sınıfındadır.

## Prompt derleyicisi

Eski sürüm tek bir sistem promptu ve dört hedef profili kullanıyordu. Yeni derleyici dört
katmanı çalışma anında birleştirir:

```text
çekirdek protokol + görev profili + ayrıntı seviyesi + hedef araç profili
```

Hazır profil sayıları:

- 9 hedef: `chatgpt`, `claude-code`, `codex`, `cursor`, `deepseek`, `gemini`,
  `github-copilot`, `grok`, `generic`
- 17 görev: `auto`, `architecture`, `coding`, `creative`, `data`, `debugging`,
  `operations`, `planning`, `research`, `review`, `writing`, `3d-modeling`,
  `mobile-app`, `media-production`, `legal-compliance`, `growth-marketing`,
  `security-review`
- 4 ayrıntı seviyesi: `compact`, `balanced`, `deep`, `exhaustive`

Bu yapı 612 farklı bileşimi destekler. `exhaustive`, dosyayı veya çıktıyı yapay biçimde
şişirmez; ilgili riskleri, karar noktalarını, teslimleri ve doğrulama şartlarını mümkün
olduğunca eksiksiz kapsar.

Çekirdek protokol şu kuralları uygular:

- Kullanıcı niyetini ve açık sınırları korur.
- Eksik bilgiyi gerçekmiş gibi üretmez.
- Düşük riskli boşluklarda varsayımı açıkça yazar.
- Sonucu ciddi biçimde değiştiren belirsizliklerde en fazla üç soru sorar.
- Araştırma, kod, hata ayıklama, veri, operasyon ve yaratıcı işler için farklı kabul
  ölçütleri kurar.
- Ham isteğin içindeki prompt injection metninin yeniden yazıcı rolünü değiştirmesine izin
  vermez.
- İstenen işi çözmek yerine yalnızca kullanılabilir promptu döndürür.

Teknik tasarım: [docs/PROMPT_SYSTEM.md](docs/PROMPT_SYSTEM.md).

## Kaynaktan kurulum

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,all]"
```

Yalnızca hafif CLI ve config katmanı için:

```powershell
python -m pip install -e .
```

`llama-cpp-python` kurulumu CUDA ve Python sürümüne göre ayrı wheel gerektirebilir.
Subprocess backend kullanıldığında `llama-cli` dosyasının `PATH` içinde bulunması yeterlidir.

## Model ayarı

`.env.example` dosyasını temel alarak en az model yolunu ayarla:

```dotenv
REPROMPT_MODEL_PATH=C:\models\reprompt-qwen2.5-7b-q4_k_m.gguf
REPROMPT_TARGET=codex
REPROMPT_TASK=auto
REPROMPT_DETAIL=balanced
REPROMPT_CTX_SIZE=8192
```

Gerçek anahtarları veya model yollarını kaynak koda ekleme. `.env` dosyası Git tarafından
yok sayılır.

## CLI

Kısa kullanım:

```powershell
reprompt "API ara sıra 500 dönüyor, nedenini bul ve düzelt"
```

Hedef, görev ve ayrıntı seçerek:

```powershell
reprompt rewrite `
  --target codex `
  --task debugging `
  --detail exhaustive `
  "Ödeme webhook'u aynı olayı bazen iki kez işliyor"
```

Araştırma promptu:

```powershell
reprompt rewrite -t gemini --task research --detail deep `
  "2026 için küçük işletme e-fatura seçeneklerini karşılaştır"
```

Standart girdi ve JSON çıktı:

```powershell
Get-Content .\ham-istek.txt |
  reprompt rewrite --stdin --target chatgpt --detail deep --json
```

`--explain`, yeniden yazılan prompttan sonra en fazla dört maddelik `Why` bölümü ekler.
Gizli düşünme zinciri üretmez.

## Python SDK

```python
from reprompt import RepromptEngine

engine = RepromptEngine(
    model=r"C:\models\reprompt-qwen2.5-7b-q4_k_m.gguf",
    ctx_size=8192,
)

rewrite = engine.rewrite(
    "kullanıcı oturumu bazen erken bitiyor",
    target="codex",
    task="debugging",
    detail="deep",
)

print(rewrite.text)
```

Toplu kullanımda aynı profil bütün girdilere uygulanır:

```python
rewrites = engine.batch_rewrite(
    ["README'yi düzelt", "kurulum adımlarını doğrula"],
    target="github-copilot",
    task="writing",
    detail="balanced",
)
```

## REST API

```powershell
reprompt serve --host 127.0.0.1 --port 8741
```

```powershell
$body = @{
  prompt = "Bu endpoint yavaş, kök nedeni bul"
  target = "codex"
  task = "debugging"
  detail = "deep"
  explain = $false
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8741/v1/rewrite `
  -ContentType application/json `
  -Body $body
```

Profil kataloğu:

```text
GET /v1/profiles
```

OpenAI Chat Completions biçimini bekleyen istemciler için
`POST /v1/chat/completions` uyumluluk endpoint'i de bulunur.

## 1 GiB Markdown prompt kütüphanesi

Proje, `library/corpus-1gib/` altında fiziksel olarak bulunan ve yalnızca `.md`
dosyalarından oluşan bir prompt kütüphanesi içerir. Corpus 24 uzmanlık alanına
ayrılmış 1.024 cilt ve 200 binden fazla yapılandırılmış prompt kaydı barındırır.

```powershell
python tools\markdown_library.py verify
```

Doğrulama toplam boyutu, dosya türlerini ve manifestteki SHA-256 özetlerini denetler.
Kütüphane yapısı, üretim ve yeniden kurulum seçenekleri
[library/README.md](library/README.md) içinde açıklanır.

## İsteğe bağlı üretim modeli

Yaklaşık 4,5 GiB hedefi prompt metninin boyutu değildir. Tek bir promptun bu boyuta
ulaşması, hiçbir pratik bağlam penceresinde kullanılamaz. Hedef, Qwen 2.5 7B tabanlı
Q4_K_M GGUF dağıtım paketidir.

Üretim konfigürasyonu:

```powershell
python -m training.sft.train `
  --config training/configs/qwen2.5-7b-production.yaml
```

Bu profil 4-bit base model, rank 32 rsLoRA, 4096 token eğitim bağlamı, gradient
checkpointing ve RTX 4060 8 GB için batch size 1 kullanır. Bellek tüketimi veri uzunluğuna,
CUDA sürümüne ve Unsloth sürümüne göre değişir; eğitimden önce kısa bir pilot koşu yap.

Birleştirme ve GGUF:

```powershell
python -m training.pack.merge_lora `
  --adapter training/outputs/qwen2.5-7b-production/final `
  --out training/outputs/qwen2.5-7b-merged

python -m training.pack.convert_to_gguf `
  --model training/outputs/qwen2.5-7b-merged `
  --quant q4_k_m `
  --out training/outputs/gguf
```

Dosya başlığı ve boyut aralığı:

```powershell
python -m training.pack.verify_gguf `
  training/outputs/gguf/reprompt-qwen2.5-7b-q4_k_m.gguf `
  --target-gib 4.5 `
  --tolerance-gib 0.75
```

Bu doğrulama model kalitesini ölçmez. Yalnızca dosyanın GGUF başlığı taşıdığını ve beklenen
dağıtım boyutu aralığında olduğunu denetler. Kalite için ayrı değerlendirme seti gerekir.

Eğitim ayrıntıları: [docs/TRAINING.md](docs/TRAINING.md).

## Test ve kalite kontrolü

```powershell
python -m pytest
ruff check .
ruff format --check .
mypy src
```

GPU veya gerçek `llama-cli` gerektiren testler işaretlidir; standart birim testleri model
ağırlığı olmadan çalışır.

## Sınırlar

- Araç, hedef modelin cevabının doğru olacağını garanti etmez.
- `exhaustive` profil, kullanıcının istemediği ürün özelliklerini ekleme yetkisi vermez.
- Yeniden yazıcı prompt injection metnini veri olarak ele alır; hedef modelin güvenlik
  politikasının yerine geçmez.
- Hassas girdileri gereksiz yere tekrar etmemeye çalışır, fakat tam bir veri kaybı önleme
  sistemi değildir.
- Yaklaşık 4–5 GiB GGUF dosyası bu depoda üretilmez veya sürümlenmez; eğitim ve paketleme
  ortamında oluşturulur.

## Dizinler

```text
src/reprompt/         CLI, SDK, API, promptlar ve çıkarım
training/             veri, SFT, değerlendirme ve paketleme
tests/                birim ve entegrasyon testleri
bench/                gecikme ve bellek ölçümleri
docs/                 kullanım ve model belgeleri
library/              1 GiB Markdown prompt kütüphanesi ve SHA-256 manifesti
tools/                corpus üretim ve doğrulama araçları
```

Kod [MIT](LICENSE), yayınlanacak model ağırlıkları ise taban modelin lisans şartlarıyla
birlikte [LICENSE-model](LICENSE-model) altında ele alınır.
