# ChatGPT Entegrasyonu

clarify-prompt'u ChatGPT Custom GPT olarak veya API uzerinden kullanabilirsin.

## Yontem 1: Custom GPT

1. [ChatGPT GPT Builder](https://chat.openai.com/gpts/editor) sayfasina git
2. "Actions" bolumune asagidaki OpenAPI spec'ini yapistir
3. Server URL'ini kendi sunucunun adresiyle degistir

### OpenAPI Spec

```yaml
openapi: "3.1.0"
info:
  title: clarify-prompt
  version: "0.1.0"
  description: Prompt rewriting service
servers:
  - url: https://YOUR_SERVER:8741
paths:
  /v1/rewrite:
    post:
      operationId: rewritePrompt
      summary: Rewrite a raw prompt into an optimized one
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [prompt]
              properties:
                prompt:
                  type: string
                  description: The raw user prompt to rewrite
                target:
                  type: string
                  enum: [claude-code, chatgpt, cursor, generic]
                  default: chatgpt
                explain:
                  type: boolean
                  default: false
      responses:
        "200":
          description: Rewritten prompt
          content:
            application/json:
              schema:
                type: object
                properties:
                  rewritten_prompt:
                    type: string
                  target:
                    type: string
                  elapsed_ms:
                    type: integer
```

## Yontem 2: Custom Instructions

ChatGPT ayarlarindan "Custom Instructions" bolumune su metni ekle:

```
Her aldığım isteği önce clarify-prompt API'sine gönder
(POST https://YOUR_SERVER:8741/v1/rewrite, target: "chatgpt").
Dönen rewritten_prompt'u asıl görev tanımın olarak kullan.
```

## Yontem 3: API Proxy

clarify-prompt'un OpenAI-uyumlu endpoint'ini kullan:

```bash
curl http://localhost:8741/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "chatgpt target"},
      {"role": "user", "content": "login sayfasi yap"}
    ]
  }'
```
