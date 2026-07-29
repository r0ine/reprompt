# Entegrasyonlar

reprompt'u her turlu AI platformuyla kullanabilirsin.
Tek satir komutla veya API uzerinden — tak ve calistir.

## Desteklenen platformlar

| Platform    | Entegrasyon                          | Rehber                          |
|------------|--------------------------------------|--------------------------------|
| Claude Code | CLAUDE.md + CLI                     | [claude-code/](claude-code/)   |
| ChatGPT     | Custom GPT / Custom Instructions     | [chatgpt/](chatgpt/)           |
| Cursor      | .cursorrules / API                   | [cursor/](cursor/)             |
| Grok        | API proxy                            | [grok/](grok/)                 |
| Gemini      | API proxy / AI Studio                | [gemini/](gemini/)             |
| DeepSeek    | API proxy                            | [deepseek/](deepseek/)         |
| Diger       | REST API / Python SDK                | [generic/](generic/)           |

## Nasil calisir

```
Kullanici Girdisi ──> reprompt ──> Optimize Edilmis Prompt ──> Hedef LLM
                          │
                    (lokal model)
```

1. Kullanici ham bir istek yazar: `"login yap guzel olsun"`
2. reprompt bunu yapisal bir prompt'a cevirir
3. Optimize edilmis prompt hedef LLM'e gonderilir
4. LLM daha iyi cikti uretir

## Hizli baslangic

```bash
# kur
pip install reprompt[all]

# CLI
reprompt "login sayfasi yap" --target chatgpt

# API sunucusu
reprompt serve --port 8741

# Python
from reprompt import RepromptEngine
engine = RepromptEngine(model="model.gguf")
result = engine.rewrite("login yap", target="claude-code")
```

## Self-hosting

```bash
# Docker ile
docker compose up -d

# veya dogrudan
reprompt serve --port 8741 --model ./models/reprompt.gguf
```

Sunucu basladiktan sonra tum platformlar `http://localhost:8741/v1/rewrite`
endpoint'ini kullanabilir.
