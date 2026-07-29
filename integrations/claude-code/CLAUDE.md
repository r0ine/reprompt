# reprompt entegrasyonu

Bu proje reprompt kullanir. Her gorev basinda kullanicinin ham girdisini
reprompt ile yeniden yaz, sonra yeniden yazilmis haliyle calis.

## Kurulum

```bash
pip install reprompt[llama]
```

## Kullanim

Kullanicidan gelen her istegi once reprompt'a gonder:

```bash
reprompt --target claude-code "kullanicinin ham istegi"
```

Donen ciktiyi kendi gorev tanimlamanin temeli olarak kullan.

## API ile kullanim (self-hosted)

Eger reprompt sunucusu calisiyorsa:

```bash
curl -s http://localhost:8741/v1/rewrite \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "kullanici istegi", "target": "claude-code"}' | jq -r .rewritten_prompt
```

## Notlar

- `--target claude-code` secildiginde cikti XML etiketli formatta gelir
- `--explain` flagi ile neden bu degisikliklerin yapildigini da gorebilirsin
- Modeli degistirmek icin `REPROMPT_MODEL_PATH` env degiskenini ayarla
