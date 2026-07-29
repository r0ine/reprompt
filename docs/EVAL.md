# Değerlendirme Metodolojisi

## Genel yaklaşım

Fine-tune edilmiş model + baseline yan yana konur; her test örneği için ikisi de aynı
promptu üretir; bir "judge" LLM her ikisini rubric'e göre skorlar; kazanma oranı
rapor edilir.

## Judge

- **Model:** [Prometheus 2 7B](https://huggingface.co/prometheus-eval/prometheus-7b-v2.0)
- **Neden:** Açık kaynak, lokal çalıştırılabilir, judge özel eğitilmiş. Proprietary judge (GPT-4o-mini) gerekince test setinin %10'una uygulanır (bütçe).
- **Ailenin ayrılması:** Bizim model Qwen ailesi; judge Prometheus (Mistral tabanlı). Judge kendi ailesini tercih bias'ını azaltır.

## Rubric

`training/eval/rubric.md` — beş boyutta 1-5 puan:

1. Clarity
2. Structure
3. Faithfulness
4. Actionability
5. Concision

Judge her puanla birlikte kısa bir rationale döner (max 40 kelime).

## Test seti

- 200 örnek `gold` etiketli.
- 100 Türkçe + 100 İngilizce.
- Kategoriler: kod (50), metin yazımı (50), debug (30), refactor (30), veri analizi (20), tasarım (20).
- Eğitim ve val setine SIZMIŞ değildir. Test'e ekleme yapılabilir, silme YOK.

## Baseline

Aynı base model (Qwen 2.5 7B Instruct) + generic sistem promptu. Fine-tune öncesinin
performansı — bizim modelin ne kadar üstüne bindiğini ölçer.

## Bilinen bias'lar

- **Position bias:** A/B karşılaştırmalarında A tarafı iyi görünür. Judge çağrılarında A/B randomize edilir.
- **Verbosity bias:** Judge uzun cevabı iyi sanabilir. Rubric "concision" boyutuyla cezalandırır.
- **Self-preference bias:** Judge kendi ailesindekini tercih eder. Prometheus, Qwen'e karşı bize daha az bias yapar (farklı aile).
- **Rubric drift:** Rubric soyutsa skorlar rastgele. Bu yüzden operasyonel tanımlar (`Structure = goal + context + acceptance + format present?`) kullanılıyor.

## Kabul kriterleri

- LLM-as-judge kazanma oranı ≥ %65 → geç.
- Kemal spot-check ≥ %70 iyi/orta → geç.
- İkisi de geçmeden release yok.

## İnsan spot-check

- Her iterasyon sonu 30 örnek rastgele seçilir.
- Kemal terminal aracıyla (`spot_check.py`) tek tek görür.
- Verdict: `good` / `orta` / `kotu`.
- Sonuç judge doğruluğunu ölçmek için de kullanılır (Kemal-vs-judge tutarlılığı).

## Rapor formatı

`training/eval/reports/report-YYYYMMDDTHHMMSSZ.jsonl` — her satır bir test örneği.
Alanlar: `test_example_id`, `input`, `our_output`, `baseline_output`, `gold_output`,
`our_score`, `baseline_score`, `our_win`.

Özet metrik (kazanma oranı) rapor sonunda konsola basılır ve
`bench/results/` altına özet dosyası düşer.
