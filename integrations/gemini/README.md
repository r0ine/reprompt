# Gemini Entegrasyonu

clarify-prompt'u Google Gemini ile kullanmak icin API proxy yontemi kullanilir.

## Python ile kullanim

```python
import httpx
import google.generativeai as genai

CLARIFY_URL = "http://localhost:8741/v1/rewrite"

def ask_gemini(raw_prompt: str) -> str:
    clarified = httpx.post(CLARIFY_URL, json={
        "prompt": raw_prompt,
        "target": "generic",
    }).json()["rewritten_prompt"]

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(clarified)
    return response.text
```

## curl ile kullanim

```bash
# once clarify-prompt ile optimize et
OPTIMIZED=$(curl -s http://localhost:8741/v1/rewrite \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"$RAW_PROMPT\", \"target\": \"generic\"}" \
  | jq -r .rewritten_prompt)

# sonra Gemini'ye gonder
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"contents\": [{\"parts\": [{\"text\": \"$OPTIMIZED\"}]}]}"
```

## Google AI Studio ile

1. clarify-prompt'u calistir
2. Ham prompt'u clarify-prompt'a gonder
3. Donen optimize edilmis prompt'u Google AI Studio'ya yapistir

Alternatif: Gemini'nin sistem talimatina su notu ekle:

```
Kullanicinin her girdisini once asagidaki API'ye gondererek optimize et:
POST http://localhost:8741/v1/rewrite {"prompt": "<girdi>", "target": "generic"}
Donen rewritten_prompt'u asil gorev olarak kullan.
```
