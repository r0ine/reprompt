# reprompt

Open-source AI that turns raw, incomplete, one-line requests into a structured prompt the
target LLM fully understands.

Two model tracks exist: QLoRA for the roughly 4–5 GiB Qwen 2.5 7B Q4_K_M production
package, and the experimental 359M-parameter ClarifyGPT scratch architecture. Model
weights are not included in the repository; a separate evaluation report is required
before release.

---

## What does it do?

When you type `"fix that bug"`, reprompt intercepts the request, figures out what you
actually want, and shapes it into this structure before sending it to the target LLM
(Claude Code, ChatGPT, Cursor):

```
Task → Context → Constraints → Acceptance criteria → Output format
```

The goal is reducing the extra turns a target model burns due to missing context. The
tool does not guarantee the target model's accuracy.

## Quick demo

```bash
# install
pip install reprompt[all]

# direct CLI use
reprompt "the reflection code is failing on the new version, fix it"

# for a different target LLM
reprompt -t chatgpt "write a blog post about SEO"
reprompt -t cursor  "clean up this component"
echo "long messy request" | reprompt rewrite --stdin -t claude-code

# start the API server
reprompt serve --port 8741

# Python SDK
from reprompt import RepromptEngine
engine = RepromptEngine(model="model.gguf")
result = engine.rewrite("build a login page", target="claude-code")
```

**Input:**
```
the reflection code is failing on the new version, fix it
```

**Output (claude-code target):**
```xml
<task>
Adapt the reflection code to the new Java version — the current code fails to compile.
</task>

<context>
- Affected file(s): provide the subpath under src/main/java/...
- Target Java version: JDK 21.
- If no compiler output is provided, request the output of mvn -q -DskipTests package.
</context>

<constraints>
- Remove unused imports.
- If tests exist, they must pass; if not, add a smoke test for the changed class.
</constraints>

<acceptance>
- mvn -q -DskipTests package must build successfully.
- Leave no warnings.
</acceptance>
```

## Why reprompt?

| Problem | With reprompt |
|---|---|
| You type "do this", the LLM misunderstands, you spend 3 turns correcting it | The prompt is optimized, the LLM produces the right output on the first try |
| Every LLM has a different prompt style (XML, markdown, directive) | The `--target` flag selects the profile matching the target LLM |
| You can't edit a prompt without being online | Runs entirely locally, offline |
| Calling the big model is expensive, you waste turns | A small local model runs first, the big model finishes in one pass |

---

## Model architecture

**ClarifyGPT research track** — a decoder-only transformer designed for training from
scratch:

| Property | Value |
|---|---|
| Total parameters | **~359M** |
| Architecture | Decoder-only Transformer |
| Dimension | 1280 |
| Layer count | 20 |
| Attention heads | 20 (GQA: 4 KV heads) |
| FFN hidden size | 3456 (SwiGLU) |
| Positional encoding | RoPE (θ=10000) |
| Max sequence | 1024 tokens |
| Vocab size | 12,000 (custom BPE tokenizer) |
| Norm | RMSNorm (ε=1e-5) |
| FP16 size | ~720 MB |
| Training VRAM | < 7 GB (gradient checkpointing + mixed precision) |

### Why from scratch?

The scratch track exists for these research questions:
- **Task-focused architecture:** prompt rewriting is a specific task — general-purpose
  language model capacity is unneeded weight.
- **Small and fast:** 359M parameters, 19x smaller than 7B+ fine-tuned models.
- **Full control:** tokenizer, architecture, and training process are all optimizable at
  every layer.
- **License clarity:** does not inherit another model's weights.

## Training data

| Metric | Value |
|---|---|
| Synthetic generation target | **100,000** |
| Hand-written gold examples | 50 |
| Augmentation examples | 110+ |
| Synthetic generation | 100,000 |
| Supported languages | **10** (TR, EN, DE, FR, ES, PT, RU, JA, ZH, KO) |
| Target profiles | 9 |
| Data leakage | Pre-release validation gate |
| Train / Val / Test | Reported after data generation |

### Language distribution

| Language | Code | Approx. share |
|---|---|---|
| Turkish | tr | ~15% |
| English | en | ~15% |
| German | de | ~10% |
| French | fr | ~10% |
| Spanish | es | ~10% |
| Portuguese | pt | ~10% |
| Russian | ru | ~10% |
| Japanese | ja | ~8% |
| Chinese | zh | ~8% |
| Korean | ko | ~7% |

## Profile system

Three layers combine at runtime: **target** (which LLM the prompt is for), **task**
(what kind of work it is), and **detail** (how exhaustive the rewrite should be).

| Target | Style | When |
|---|---|---|
| `claude-code` | XML tags (`<task>`, `<context>`, `<constraints>`) | Using Claude Code or the Claude API |
| `chatgpt` | Markdown headings, numbered acceptance | Using ChatGPT web/API |
| `cursor` | Short directives, numbered steps, a "Do not" list | Inside the Cursor IDE |
| `codex` | Terse instructions tuned for agentic coding loops | Using OpenAI Codex-style agents |
| `gemini` | Structured sections aligned with Gemini's formatting habits | Using Google Gemini |
| `deepseek` | Direct technical framing | Using DeepSeek models |
| `github-copilot` | Inline-comment-friendly, scoped to the current file/selection | Using GitHub Copilot |
| `grok` | Concise, low-ceremony phrasing | Using xAI Grok |
| `generic` | Vendor-neutral, portable, plain structure | Any LLM or general purpose |

17 task profiles cover software work (`coding`, `debugging`, `architecture`, `review`,
`operations`), non-software work (`research`, `writing`, `data`, `planning`, `creative`),
and specialized domains (`3d-modeling`, `mobile-app`, `media-production`,
`legal-compliance`, `growth-marketing`, `security-review`), plus `auto` for automatic
inference. 4 detail levels (`compact`, `balanced`, `deep`, `exhaustive`) control how
exhaustively the rewrite covers the task.

## Technical stack

- **Tokenizer:** custom SentencePiece BPE, 12,000 tokens, 10-language support
- **Training:** PyTorch, mixed precision (FP16), cosine LR scheduler, gradient
  accumulation
- **Hardware:** RTX 4060 8GB — full training on a single GPU
- **Inference:** native PyTorch or GGUF export (llama.cpp compatible)
- **API:** FastAPI REST server, OpenAI-compatible endpoint, batch support
- **SDK:** Python SDK (`RepromptEngine` class) — one-line integration
- **Docker:** ready-made Dockerfile + docker-compose for self-hosting
- **Distribution:** PyPI (`pip install reprompt[all]`) + model weights distributed
  separately

## Target metrics

| Dimension | Baseline (raw prompt) | ClarifyGPT | Improvement |
|---|---|---|---|
| Structure score | ~15% | >70% | +370% |
| Length compliance | ~30% | >80% | +167% |
| Filled-out output | ~40% | >95% | +138% |
| Target format compliance | ~10% | >65% | +550% |

## Directory layout

```
reprompt/
├── src/reprompt/              # inference package
│   ├── cli/                   # Click CLI
│   ├── engine/                # llama.cpp + python backend
│   ├── prompts/                # system prompt + target/task/depth profiles
│   ├── config/                # pydantic v2 config
│   ├── postproc/               # output cleanup
│   └── errors.py               # exception hierarchy
├── training/                  # training pipeline
│   ├── model/                 # ClarifyGPT transformer architecture
│   │   ├── config.py          # SMALL/BASE/LARGE/XLARGE configurations
│   │   └── transformer.py     # RoPE + GQA + SwiGLU + gradient checkpointing
│   ├── tokenizer/              # SentencePiece BPE training
│   ├── data/                  # data generation, augmentation, split
│   ├── configs/                # YAML training configurations
│   ├── train_scratch.py        # from-scratch training loop
│   ├── evaluate.py             # test-set evaluation
│   ├── inference.py            # inference from checkpoint
│   └── run_all.py              # full pipeline in one command
├── integrations/               # platform integrations
│   ├── claude-code/            # CLAUDE.md template
│   ├── chatgpt/                 # Custom GPT + OpenAPI spec
│   ├── cursor/                  # .cursorrules template
│   ├── grok/                    # xAI Grok integration
│   ├── gemini/                  # Google Gemini integration
│   ├── deepseek/                # DeepSeek integration
│   └── generic/                 # general-purpose guide
├── library/                    # 1 GiB Markdown prompt library
├── tests/                       # 154+ unit + integration tests
├── bench/                       # latency + memory measurements
├── docs/                        # gold examples, model card
├── Dockerfile                   # self-hosting
├── docker-compose.yml           # one-command startup
└── PLAN.md                      # implementation plan
```

## Integration system

Drop-in integration with every platform. Three ways in:

1. **CLI:** `reprompt "whatever you need"` — use it directly
2. **API:** `reprompt serve` — self-hosted REST API server
3. **SDK:** `RepromptEngine(model=...).rewrite(...)` — programmatic access from Python

The API has an OpenAI-compatible endpoint: point an existing tool's base URL at it and
connect directly.

Detailed guides live under `integrations/`: Claude Code, ChatGPT, Cursor, Grok, Gemini,
DeepSeek.

## Test status

- **154 tests** (unit + integration; a handful require training dependencies not
  installed by default and are skipped)
- Model architecture: parameter count, forward/backward pass, weight tying, RoPE, GQA,
  generate
- Tokenizer: round-trip across 10 languages, special tokens, ChatML format, code
  fragments
- Data quality: language distribution, target-profile balance, leakage, duplicate checks
- Evaluation: structure_score across profiles, length_ratio boundary values
- REST API: health, targets, rewrite, batch, OpenAI-compatible endpoint
- SDK: RepromptEngine, RewriteResult, batch_rewrite
- CLI: rewrite command, serve subcommand, shorthand syntax
- Config, postprocessing, and selector tests

## License

- Code: [MIT](LICENSE)
- Model weights: [Apache-2.0](LICENSE-model)

---

## Maker

**r0ine**

- GitHub: [github.com/r0ine](https://github.com/r0ine)
- Email: r0ine@outlook.com

---

> reprompt is an open-source tool that automates prompt engineering.
> Questions or contributions are welcome via GitHub Issues.

---

## Türkçe

Ham, eksik, tek satırlık istekleri hedef LLM'in tam anlayacağı yapılandırılmış prompta
çeviren açık kaynak yapay zeka.

İki model hattı bulunur: yaklaşık 4–5 GiB Qwen 2.5 7B Q4_K_M üretim paketi için QLoRA
ve deneysel 359M parametreli ClarifyGPT scratch mimarisi. Model ağırlıkları depoda yer
almaz; yayımlanmadan önce ayrı değerlendirme raporu gerekir.

**Ne yapıyor?** Sen `"şu bug'ı çöz"` yazdığında, reprompt arada durup bu isteği alıyor,
ne istediğini anlıyor ve hedef LLM'e (Claude Code, ChatGPT, Cursor) göndermeden önce
`Görev → Bağlam → Kısıtlar → Kabul kriterleri → Çıktı formatı` yapısına oturtuyor. Amaç,
hedef modelin eksik bağlam yüzünden gereksiz tur harcamasını azaltmak. Araç hedef modelin
doğruluğunu garanti etmez.

**Neden reprompt?** "Şunu yap" yazdığında LLM yanlış anlar, üç tur düzeltirsin —
reprompt ile prompt optimize edilir, LLM ilk seferde doğru çıktı verir. Her LLM'in farklı
prompt stili vardır; `--target` bayrağıyla hedef LLM'e göre profil seçilir. Büyük modele
API çağrısı pahalıdır; küçük lokal model önden çalışır, büyük model tek seferde biter.

**Model mimarisi:** ClarifyGPT araştırma hattı, sıfırdan eğitim için tasarlanmış
~359M parametreli decoder-only transformer (dim 1280, 20 katman, GQA 4 KV head, SwiGLU,
RoPE, RMSNorm). Scratch hat görev odaklı mimari, küçük/hızlı boyut, tam kontrol ve lisans
temizliği için tercih edildi.

**Profil sistemi:** çalışma anında üç katman birleşir — hangi LLM için yazıldığı
(**hedef**), ne tür bir iş olduğu (**görev**), ne kadar ayrıntılı yeniden yazılacağı
(**ayrıntı**). 9 hedef profil (`claude-code`, `chatgpt`, `cursor`, `codex`, `gemini`,
`deepseek`, `github-copilot`, `grok`, `generic`), 17 görev profili (yazılım işleri:
coding/debugging/architecture/review/operations; yazılım dışı işler:
research/writing/data/planning/creative; özel alanlar: 3d-modeling/mobile-app/
media-production/legal-compliance/growth-marketing/security-review; ve otomatik çıkarım
için `auto`), 4 ayrıntı seviyesi (`compact`, `balanced`, `deep`, `exhaustive`).

**Teknik altyapı:** özel SentencePiece BPE tokenizer (12.000 token, 10 dil), PyTorch
eğitim (mixed precision, cosine LR scheduler), RTX 4060 8GB'de tek GPU eğitimi,
PyTorch native veya GGUF export ile inference, FastAPI REST server (OpenAI-uyumlu
endpoint dahil), Python SDK (`RepromptEngine`), self-hosting için Dockerfile +
docker-compose, PyPI dağıtımı.

**Entegrasyon sistemi:** CLI (`reprompt "..."`), API (`reprompt serve`) ve SDK
(`RepromptEngine(model=...).rewrite(...)`) olmak üzere üç giriş yolu. OpenAI-uyumlu
endpoint sayesinde mevcut araçların base URL'i değiştirilerek doğrudan bağlanabilir.
Detaylı rehberler `integrations/` klasöründe: Claude Code, ChatGPT, Cursor, Grok, Gemini,
DeepSeek.

**Test durumu:** 154 test — model mimarisi, tokenizer, veri kalitesi, evaluation,
REST API, SDK, CLI, config/postprocessing/selector katmanları için birim ve entegrasyon
testleri.

**Lisans:** Kod [MIT](LICENSE), model ağırlıkları [Apache-2.0](LICENSE-model).

**Yapımcı:** r0ine — GitHub: [github.com/r0ine](https://github.com/r0ine),
E-posta: r0ine@outlook.com

> reprompt, prompt mühendisliğini otomatikleştiren açık kaynak bir araçtır. Sorularınız
> veya katkılarınız için GitHub Issues üzerinden ulaşabilirsiniz.
