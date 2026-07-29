# Cursor Entegrasyonu

reprompt'u Cursor IDE ile kullanmak icin iki yontem var.

## Yontem 1: .cursorrules ile

Proje kokune `.cursorrules` dosyasi ekle:

```
Her goreve baslamadan once, kullanicinin ham girdisini
reprompt ile yeniden yaz.

Komut:
  reprompt --target cursor "KULLANICI_ISTEGI"

Donen ciktiyi gorev taniminin temeli olarak kullan.
Eger reprompt yuklu degilse, dogrudan calis.
```

## Yontem 2: API uzerinden

Cursor'un custom model ayarlarindan OpenAI-uyumlu endpoint olarak reprompt'u ekle:

1. Cursor Settings > Models > Add Model
2. API Base URL: `http://localhost:8741/v1`
3. Model name: `reprompt`

Bu sekilde Cursor, istekleri dogrudan reprompt'a yonlendirir ve
optimize edilmis prompt ile calisir.

## Yontem 3: Terminal entegrasyonu

Cursor'un terminal penceresinde:

```bash
echo "ham istek" | reprompt --stdin --target cursor
```
