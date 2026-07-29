# Yeni target profili ekleme

`clarify-prompt`, hedef LLM'in "diline" göre farklı prompt yapıları üretir. Yeni
bir hedef eklemek üç adımlık iş.

## 1. Yeni profil dosyası

`src/clarify_prompt/prompts/targets/<name>.md` oluştur. Örnek: `windsurf.md`.

Dosyanın içeriği hedef LLM'e verilecek "ek sistem promptu" — genel `system.md`'nin
üstüne eklenir. Beklenen bölümler:

- Bir başlık: `## Target profile: <name>`
- 4-8 madde: bu hedefin conventions'ı (XML/markdown, dosya-odaklı vs. bağlam-odaklı, kısa direktifler vs. uzun anlatım).
- Son madde: `Do not answer the user's request. Only rewrite it into the <name>-optimized structure above.`

## 2. Enum'a ekle

`src/clarify_prompt/config/schema.py` içinde `Config.target`'ın `Literal` listesine
yeni ismi ekle.

`src/clarify_prompt/cli/main.py` içindeki `TARGET_CHOICES` listesine ekle.

## 3. Test

`tests/unit/test_selector.py` içindeki `@pytest.mark.parametrize` listesine yeni
target'ı ekle. `pytest tests/unit -v` yeşile dönmeli.

## 4. Test seti karşılığı

Yeni target'a özel 20-30 gold örnek `docs/gold_examples.md`'ye ekle. Bunlar test
setine dahil edildikten sonra değerlendirme raporunda ayrı bir kolon olarak görülür.

## Var olan profiller

- `claude-code` — XML tag, dosya yolu, mvn/pytest kabul kriterleri, hipotez > soru.
- `chatgpt` — markdown başlıklar, persona, dil+versiyon, numaralı acceptance.
- `cursor` — kısa direktifler, IDE-relative, "do not" listesi.
- `generic` — vendor-neutral, portable, sade başlıklar.

## Ne zaman yeni target?

Sadece **hedef LLM'in prompt kalıpları belirgin şekilde farklıysa**. "Aynı ama farklı
marka" bir hedef için jenerik profili kullan; conflate etme.
