# Genel Entegrasyon Rehberi

clarify-prompt herhangi bir LLM ile calisir. Tek yapman gereken,
kullanici girdisini once clarify-prompt'tan gecirmek.

## Hizli baslangic

### 1. Kur

```bash
pip install clarify-prompt[all]
```

### 2. Modeli indir

Egitilmis GGUF modelini `models/` klasorune koy:

```bash
mkdir models
# model dosyasini buraya kopyala
export CLARIFY_PROMPT_MODEL_PATH=./models/clarify-prompt.gguf
```

### 3. CLI ile kullan

```bash
clarify-prompt "login sayfasi yap mobilden de erisilebiilsin"
clarify-prompt --target chatgpt "api rate limiting ekle"
clarify-prompt --target claude-code --explain "veritabani baglantisi patliyor duzelt"
echo "karmasik istek" | clarify-prompt --stdin --target cursor
```

### 4. API sunucusu baslat

```bash
clarify-prompt serve --port 8741
```

### 5. API'yi kullan

```bash
curl -X POST http://localhost:8741/v1/rewrite \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "login yap", "target": "generic"}'
```

## Python SDK

```python
from clarify_prompt import ClarifyEngine

engine = ClarifyEngine(model="models/clarify-prompt.gguf")
result = engine.rewrite("login sayfasi yap", target="claude-code")
print(result.text)

# toplu islem
results = engine.batch_rewrite(
    ["istek 1", "istek 2", "istek 3"],
    target="chatgpt",
)
```

## Docker ile self-hosting

```bash
# modeli models/ klasorune koy
docker compose up -d
# sunucu http://localhost:8741 adresinde calisir
```

## Herhangi bir LLM ile entegrasyon kalıbi

```python
import httpx

CLARIFY_URL = "http://localhost:8741/v1/rewrite"

def with_clarify(raw_prompt: str, target: str = "generic") -> str:
    """Ham prompt'u clarify-prompt ile optimize eder."""
    resp = httpx.post(CLARIFY_URL, json={
        "prompt": raw_prompt,
        "target": target,
    })
    return resp.json()["rewritten_prompt"]

# herhangi bir LLM API'siyle kullan
optimized = with_clarify("login yap guzel olsun", target="chatgpt")
llm_response = your_llm_api(optimized)
```

## Hedef profiller

| Profil       | Cikti formati              | En iyi kullanim          |
|-------------|---------------------------|-------------------------|
| claude-code | XML etiketli              | Claude Code, Claude API |
| chatgpt     | Markdown baslikli         | ChatGPT, OpenAI API    |
| cursor      | Numarali adimlar          | Cursor IDE              |
| generic     | Tasinabilir yapisal metin | Diger tum LLM'ler      |

## Ortam degiskenleri

| Degisken                     | Aciklama                    | Varsayilan     |
|-----------------------------|-----------------------------|---------------|
| CLARIFY_PROMPT_MODEL_PATH   | GGUF model dosya yolu       | (zorunlu)     |
| CLARIFY_PROMPT_TARGET       | Varsayilan hedef profil     | generic       |
| CLARIFY_PROMPT_BACKEND      | Inference backend           | llama         |
| CLARIFY_PROMPT_GPU_LAYERS   | GPU'ya yuklenecek katman    | 33            |
| CLARIFY_PROMPT_CTX_SIZE     | Context pencere boyutu      | 4096          |
| CLARIFY_PROMPT_LOG_LEVEL    | Log seviyesi                | INFO          |
