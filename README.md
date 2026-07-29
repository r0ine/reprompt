# reprompt

`reprompt` turns a short or messy request into a clear work brief another language model
can act on directly. It never answers the request — it rewrites it while preserving the
goal, context, constraints, deliverables, and acceptance criteria.

The project has two parts:

- A Python package: CLI, SDK, REST API, prompt compiler, and a `llama.cpp` inference
  layer.
- Training tooling: data preparation, QLoRA/SFT, evaluation, and GGUF packaging.

Model weights are not included in this repository. The recommended production route is
QLoRA on Qwen 2.5 7B Instruct followed by a Q4_K_M GGUF conversion. The resulting GGUF is
roughly in the 4–5 GiB class, depending on the converter version.

## Prompt compiler

The earlier version used a single system prompt and four target profiles. The current
compiler merges four layers at runtime:

```text
core protocol + task profile + detail level + target tool profile
```

Available profile counts:

- 9 targets: `chatgpt`, `claude-code`, `codex`, `cursor`, `deepseek`, `gemini`,
  `github-copilot`, `grok`, `generic`
- 17 tasks: `auto`, `architecture`, `coding`, `creative`, `data`, `debugging`,
  `operations`, `planning`, `research`, `review`, `writing`, `3d-modeling`,
  `mobile-app`, `media-production`, `legal-compliance`, `growth-marketing`,
  `security-review`
- 4 detail levels: `compact`, `balanced`, `deep`, `exhaustive`

This supports 612 distinct combinations. `exhaustive` does not artificially inflate the
file or the output; it covers relevant risks, decision points, deliverables, and
verification requirements as completely as reasonably possible.

The core protocol enforces the following rules:

- Preserves user intent and explicit boundaries.
- Never invents missing information as if it were fact.
- States assumptions explicitly in low-risk gaps.
- Asks at most three questions when ambiguity would materially change the outcome.
- Sets different acceptance criteria for research, code, debugging, data, operations, and
  creative work.
- Does not let prompt-injection text inside the raw request change the rewriter's role.
- Returns only a usable prompt instead of solving the requested task itself.

Technical design: [docs/PROMPT_SYSTEM.md](docs/PROMPT_SYSTEM.md).

## Install from source

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,all]"
```

For the lightweight CLI and config layer only:

```powershell
python -m pip install -e .
```

Installing `llama-cpp-python` may require a separate wheel depending on your CUDA and
Python version. With the subprocess backend, having `llama-cli` on `PATH` is enough.

## Model configuration

Based on `.env.example`, set at least the model path:

```dotenv
REPROMPT_MODEL_PATH=C:\models\reprompt-qwen2.5-7b-q4_k_m.gguf
REPROMPT_TARGET=codex
REPROMPT_TASK=auto
REPROMPT_DETAIL=balanced
REPROMPT_CTX_SIZE=8192
```

Do not commit real keys or model paths to source control. `.env` is ignored by Git.

## CLI

Quick usage:

```powershell
reprompt "the API occasionally returns 500, find and fix the cause"
```

Choosing target, task, and detail:

```powershell
reprompt rewrite `
  --target codex `
  --task debugging `
  --detail exhaustive `
  "the payment webhook sometimes processes the same event twice"
```

A research prompt:

```powershell
reprompt rewrite -t gemini --task research --detail deep `
  "compare small-business e-invoicing options for 2026"
```

Reading from stdin with JSON output:

```powershell
Get-Content .\raw-request.txt |
  reprompt rewrite --stdin --target chatgpt --detail deep --json
```

`--explain` appends a `Why` section of at most four bullets after the rewritten prompt.
It does not produce a hidden chain of thought.

## Python SDK

```python
from reprompt import RepromptEngine

engine = RepromptEngine(
    model=r"C:\models\reprompt-qwen2.5-7b-q4_k_m.gguf",
    ctx_size=8192,
)

rewrite = engine.rewrite(
    "the user session sometimes ends early",
    target="codex",
    task="debugging",
    detail="deep",
)

print(rewrite.text)
```

Batch usage applies the same profile to every input:

```python
rewrites = engine.batch_rewrite(
    ["fix the README", "verify the setup steps"],
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
  prompt = "this endpoint is slow, find the root cause"
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

Profile catalog:

```text
GET /v1/profiles
```

A `POST /v1/chat/completions` compatibility endpoint is also available for clients
expecting the OpenAI Chat Completions shape.

## 1 GiB Markdown prompt library

The project includes a prompt library that physically lives under
`library/corpus-1gib/` and consists only of `.md` files. The corpus spans 24 areas of
expertise across 1,024 volumes and holds more than 200,000 structured prompt records.

```powershell
python tools\markdown_library.py verify
```

Verification checks total size, file types, and the SHA-256 digests in the manifest.
Library structure, generation, and rebuild options are documented in
[library/README.md](library/README.md).

## Optional production model

The roughly 4.5 GiB target is not the size of a prompt string. A single prompt reaching
that size would be unusable in any practical context window. The target is a Q4_K_M GGUF
distribution package built on Qwen 2.5 7B.

Production configuration:

```powershell
python -m training.sft.train `
  --config training/configs/qwen2.5-7b-production.yaml
```

This profile uses a 4-bit base model, rank-32 rsLoRA, a 4096-token training context,
gradient checkpointing, and batch size 1 for an RTX 4060 8 GB. Memory usage varies with
sequence length, CUDA version, and Unsloth version; run a short pilot before full
training.

Merging and GGUF conversion:

```powershell
python -m training.pack.merge_lora `
  --adapter training/outputs/qwen2.5-7b-production/final `
  --out training/outputs/qwen2.5-7b-merged

python -m training.pack.convert_to_gguf `
  --model training/outputs/qwen2.5-7b-merged `
  --quant q4_k_m `
  --out training/outputs/gguf
```

File header and size-range check:

```powershell
python -m training.pack.verify_gguf `
  training/outputs/gguf/reprompt-qwen2.5-7b-q4_k_m.gguf `
  --target-gib 4.5 `
  --tolerance-gib 0.75
```

This check does not measure model quality. It only verifies the file carries a valid
GGUF header and falls within the expected distribution size range. Quality requires a
separate evaluation set.

Training details: [docs/TRAINING.md](docs/TRAINING.md).

## Tests and quality gates

```powershell
python -m pytest
ruff check .
ruff format --check .
mypy src
```

Tests requiring a GPU or a real `llama-cli` are marked; standard unit tests run without
model weights.

## Limits

- The tool does not guarantee the target model's response will be correct.
- The `exhaustive` profile does not authorize adding product features the user did not
  request.
- The rewriter treats prompt-injection text as data; it does not replace the target
  model's own security policy.
- It tries not to needlessly repeat sensitive input, but it is not a complete data-loss-
  prevention system.
- The roughly 4–5 GiB GGUF file is not produced or versioned in this repository; it is
  built in the training and packaging environment.

## Layout

```text
src/reprompt/         CLI, SDK, API, prompts, and inference
training/             data, SFT, evaluation, and packaging
tests/                unit and integration tests
bench/                latency and memory measurements
docs/                 usage and model documentation
library/              1 GiB Markdown prompt library and SHA-256 manifest
tools/                corpus generation and verification tools
```

Code is [MIT](LICENSE); model weights, once published, are covered under
[LICENSE-model](LICENSE-model) alongside the base model's own license terms.

---

## Türkçe

`reprompt`, kısa veya dağınık bir isteği başka bir dil modelinin doğrudan uygulayabileceği
net bir çalışma tarifine dönüştürür. İsteği cevaplamaz; hedefi, bağlamı, sınırları,
teslimleri ve doğrulama ölçütlerini koruyarak yeniden yazar.

Proje iki parçadan oluşur:

- Python paketi; CLI, SDK, REST API, prompt derleyicisi ve `llama.cpp` çıkarım katmanını
  içerir.
- Eğitim araçları; veri hazırlama, QLoRA/SFT, değerlendirme ve GGUF paketleme akışını
  içerir.

Model ağırlıkları bu depoda bulunmuyor. Üretim için önerilen rota Qwen 2.5 7B Instruct
üzerinde QLoRA ve ardından Q4_K_M GGUF dönüşümüdür. Ortaya çıkan GGUF, dönüştürücü
sürümüne göre değişmekle birlikte yaklaşık 4–5 GiB sınıfındadır.

**Prompt derleyicisi** dört katmanı çalışma anında birleştirir: çekirdek protokol + görev
profili + ayrıntı seviyesi + hedef araç profili. 9 hedef, 17 görev ve 4 ayrıntı
seviyesiyle 612 farklı bileşim desteklenir. Teknik tasarım için
[docs/PROMPT_SYSTEM.md](docs/PROMPT_SYSTEM.md) dosyasına bakılabilir.

**Kurulum:**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,all]"
```

**Model ayarı** için `.env.example` dosyasını temel alarak en az model yolu ayarlanmalı
(`REPROMPT_MODEL_PATH`). Gerçek anahtarları veya model yollarını kaynak koda ekleme;
`.env` dosyası Git tarafından yok sayılır.

**CLI kullanımı:**

```powershell
reprompt "API ara sıra 500 dönüyor, nedenini bul ve düzelt"
reprompt rewrite --target codex --task debugging --detail exhaustive "..."
```

`--explain`, yeniden yazılan prompttan sonra en fazla dört maddelik `Why` bölümü ekler;
gizli düşünme zinciri üretmez.

**Python SDK** üzerinden `RepromptEngine` sınıfıyla programatik erişim, **REST API**
üzerinden `reprompt serve` komutuyla self-hosted sunucu, OpenAI Chat Completions uyumlu
`/v1/chat/completions` endpoint'i mevcuttur.

Proje ayrıca `library/corpus-1gib/` altında, 24 uzmanlık alanına ayrılmış 1.024 cilt ve
200 binden fazla yapılandırılmış prompt kaydı barındıran 1 GiB'lık bir Markdown prompt
kütüphanesi içerir. Yapı ve üretim seçenekleri [library/README.md](library/README.md)
içinde açıklanır.

Yaklaşık 4,5 GiB'lık isteğe bağlı üretim modeli, Qwen 2.5 7B tabanlı Q4_K_M GGUF dağıtım
paketidir — bu boyut bir prompt metninin boyutu değil, eğitim ve paketleme sürecinin
çıktısıdır. Eğitim ayrıntıları: [docs/TRAINING.md](docs/TRAINING.md).

**Sınırlar:** Araç, hedef modelin cevabının doğru olacağını garanti etmez. `exhaustive`
profili, kullanıcının istemediği ürün özelliklerini ekleme yetkisi vermez. Yeniden yazıcı
prompt injection metnini veri olarak ele alır; hedef modelin güvenlik politikasının yerine
geçmez.

Kod [MIT](LICENSE), yayınlanacak model ağırlıkları ise taban modelin lisans şartlarıyla
birlikte [LICENSE-model](LICENSE-model) altında ele alınır.
