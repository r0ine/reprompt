# DeepSeek Entegrasyonu

reprompt'u DeepSeek ile kullanmak icin API proxy yontemi kullanilir.
DeepSeek, OpenAI-uyumlu API kullanir.

## Python ile kullanim

```python
import httpx

CLARIFY_URL = "http://localhost:8741/v1/rewrite"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

def ask_deepseek(raw_prompt: str, api_key: str) -> str:
    clarified = httpx.post(CLARIFY_URL, json={
        "prompt": raw_prompt,
        "target": "generic",
    }).json()["rewritten_prompt"]

    resp = httpx.post(DEEPSEEK_URL, headers={
        "Authorization": f"Bearer {api_key}",
    }, json={
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": clarified}],
    })
    return resp.json()["choices"][0]["message"]["content"]
```

## curl ile kullanim

```bash
OPTIMIZED=$(curl -s http://localhost:8741/v1/rewrite \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"$RAW_PROMPT\", \"target\": \"generic\"}" \
  | jq -r .rewritten_prompt)

curl https://api.deepseek.com/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"deepseek-chat\", \"messages\": [{\"role\": \"user\", \"content\": \"$OPTIMIZED\"}]}"
```

## NVIDIA NIM uzerinden

DeepSeek modellerini NVIDIA NIM ile kullaniyorsan:

```python
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

resp = httpx.post(NVIDIA_URL, headers={
    "Authorization": f"Bearer {nvidia_key}",
}, json={
    "model": "deepseek-ai/deepseek-v4-flash",
    "messages": [{"role": "user", "content": clarified}],
})
```
