# Cursor Entegrasyonu

clarify-prompt'u Cursor IDE ile kullanmak icin iki yontem var.

## Yontem 1: .cursorrules ile

Proje kokune `.cursorrules` dosyasi ekle:

```
Her goreve baslamadan once, kullanicinin ham girdisini
clarify-prompt ile yeniden yaz.

Komut:
  clarify-prompt --target cursor "KULLANICI_ISTEGI"

Donen ciktiyi gorev taniminin temeli olarak kullan.
Eger clarify-prompt yuklu degilse, dogrudan calis.
```

## Yontem 2: API uzerinden

Cursor'un custom model ayarlarindan OpenAI-uyumlu endpoint olarak clarify-prompt'u ekle:

1. Cursor Settings > Models > Add Model
2. API Base URL: `http://localhost:8741/v1`
3. Model name: `clarify-prompt`

Bu sekilde Cursor, istekleri dogrudan clarify-prompt'a yonlendirir ve
optimize edilmis prompt ile calisir.

## Yontem 3: Terminal entegrasyonu

Cursor'un terminal penceresinde:

```bash
echo "ham istek" | clarify-prompt --stdin --target cursor
```
