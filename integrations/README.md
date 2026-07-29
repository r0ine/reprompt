# Entegrasyonlar

clarify-prompt'u her turlu AI platformuyla kullanabilirsin.
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
Kullanici Girdisi ──> clarify-prompt ──> Optimize Edilmis Prompt ──> Hedef LLM
                          │
                    (lokal model)
```

1. Kullanici ham bir istek yazar: `"login yap guzel olsun"`
2. clarify-prompt bunu yapisal bir prompt'a cevirir
3. Optimize edilmis prompt hedef LLM'e gonderilir
4. LLM daha iyi cikti uretir

## Hizli baslangic

```bash
# kur
pip install clarify-prompt[all]

# CLI
clarify-prompt "login sayfasi yap" --target chatgpt

# API sunucusu
clarify-prompt serve --port 8741

# Python
from clarify_prompt import ClarifyEngine
engine = ClarifyEngine(model="model.gguf")
result = engine.rewrite("login yap", target="claude-code")
```

## Self-hosting

```bash
# Docker ile
docker compose up -d

# veya dogrudan
clarify-prompt serve --port 8741 --model ./models/clarify-prompt.gguf
```

Sunucu basladiktan sonra tum platformlar `http://localhost:8741/v1/rewrite`
endpoint'ini kullanabilir.
