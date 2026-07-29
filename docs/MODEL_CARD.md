# Model Card — clarify-prompt

> **Durum:** Bu model kartı MVP release öncesi için taslak. Gerçek rakamlar Faz 4
> sonrası doldurulacak.

## Model detayları

- **Ad:** `clarify-prompt-qwen2.5-7b-v1` (planlanan)
- **Base:** [Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)
- **Yöntem:** LoRA r=16 (QLoRA / 4-bit NF4), Unsloth framework
- **Boyut:** LoRA adapter ~200 MB; GGUF Q4_K_M ~4.4 GB
- **Diller:** Türkçe, İngilizce (birincil); diğerleri denenmedi
- **Bağlam uzunluğu:** 4096 (varsayılan config)
- **Lisans:** Apache 2.0 (base modelin lisansına uyum)

## Amaçlanan kullanım

Ham/dağınık/eksik bağlamlı kullanıcı isteklerini, hedef bir büyük dil modeli (Claude
Code, ChatGPT, Cursor gibi) için yapılandırılmış prompta çevirir. Doğrudan soru
cevaplama, kod üretme, güvenlik filtresi değildir — sadece prompt yeniden yazıcıdır.

## Eğitim verisi

- ~1500–2500 örnek karma dataset
- **Kaynaklar:** kullanıcı transkriptleri (anonimleştirilmiş, ~%20), teacher
  distillation (Claude Opus 4.7, ~%60), el yapımı altın örnekler (~%20)
- **Anonimleştirme:** `training/data/anonymize.py` regex tabanlı — e-posta, IP, API
  anahtarları, dosya yolları maskelenir
- **Test seti:** 200 örnek gold, %50 Türkçe %50 İngilizce, eğitime SIZMAMIŞ

## Değerlendirme

- **Judge:** [Prometheus 2 7B](https://huggingface.co/prometheus-eval/prometheus-7b-v2.0), rubric-based scoring
- **Metrik:** LLM-as-judge kazanma oranı (baseline: base model + generic sistem promptu)
- **İkincil metrik:** insan spot-check (30 örnek Kemal işaretlemesi)
- **Hedef:** ≥ %65 kazanma
- **Gerçek rakam:** _Faz 4 sonrası_

## Sınırlamalar

- Hedef LLM'in cevabının **doğruluğunu** garanti etmez. Sadece isteğin netliğini artırır.
- **Prompt injection / jailbreak filtresi değil**. Kötü niyetli isteği yeniden yazar; hedef LLM'in güvenlik önlemleri geçerli olmalı.
- **PII (kişisel bilgi) taraması yapmaz.** Şifre, e-posta içeriği, kimlik bilgisi vb. modeli verilen ham istekte yazıldıysa modele gider.
- **Kısa istekler** (< 20 karakter) düşük kalitede yeniden yazılır — model az bilgi ile uydurma yapabilir.
- **Türkçe ve İngilizce** eğitildi. Diğer dillerde beklentiler düşük tutulmalı.
- Target profilleri (`claude-code`, `chatgpt`, `cursor`, `generic`) heuristik. Hedef LLM'in sürümü değişince prompt tercihleri kayabilir.

## Yanlılık ve etik

- Eğitim verisinin çoğu Batı Avrupa / İngilizce ve Türkçe internet kaynaklıdır. Diğer dil ve kültürlerdeki nüansları temsil etmiyor olabilir.
- Teacher distillation (Claude Opus 4.7) modeli, bu modelin stiline "meyilli" olarak kalibre eder — Anthropic'in prompt tercih kalıpları sızabilir.
- Model, telemetri toplamaz; kullanım verisi asla merkeze gönderilmez.

## Atıf

```bibtex
@software{clarify_prompt_2026,
  title = {clarify-prompt: Local Prompt Engineer AI},
  author = {Kemal},
  year = {2026},
  url = {https://github.com/clarify/clarify-prompt},
}
```

## Sürüm geçmişi

- v0.1.0 (planlanan) — İlk MVP release.
