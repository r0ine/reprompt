# Grok Entegrasyonu

reprompt'u Grok (xAI) ile kullanmak icin API proxy yontemi kullanilir.

## Kurulum

1. reprompt sunucusunu baslat:

```bash
reprompt serve --port 8741
```

2. Grok API isteklerini gondermeden once prompt'u reprompt'tan gecir:

```python
import httpx

CLARIFY_URL = "http://localhost:8741/v1/rewrite"
GROK_URL = "https://api.x.ai/v1/chat/completions"

def ask_grok(raw_prompt: str, grok_api_key: str) -> str:
    clarified = httpx.post(CLARIFY_URL, json={
        "prompt": raw_prompt,
        "target": "generic",
    }).json()["rewritten_prompt"]

    resp = httpx.post(GROK_URL, headers={
        "Authorization": f"Bearer {grok_api_key}",
    }, json={
        "model": "grok-3",
        "messages": [{"role": "user", "content": clarified}],
    })
    return resp.json()["choices"][0]["message"]["content"]
```

## Alternatif: OpenAI-uyumlu endpoint

Grok, OpenAI-uyumlu API kullanir. reprompt'un
`/v1/chat/completions` endpoint'i de ayni formati destekler,
dogrudan pipe'layabilirsin:

```bash
# once reprompt ile optimize et
OPTIMIZED=$(curl -s http://localhost:8741/v1/rewrite \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"$RAW_PROMPT\", \"target\": \"generic\"}" \
  | jq -r .rewritten_prompt)

# sonra Grok'a gonder
curl https://api.x.ai/v1/chat/completions \
  -H "Authorization: Bearer $GROK_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"grok-3\", \"messages\": [{\"role\": \"user\", \"content\": \"$OPTIMIZED\"}]}"
```
