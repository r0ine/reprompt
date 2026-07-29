# Changelog

Bu belge [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) formatını takip eder;
sürümleme [Semantic Versioning](https://semver.org/spec/v2.0.0.html)'e uyar.

## [Unreleased]

### Added
- Çekirdek protokol, 11 görev profili, 4 ayrıntı seviyesi ve 9 hedef profili kullanan
  modüler prompt derleyicisi.
- Codex, Gemini, DeepSeek, Grok ve GitHub Copilot hedefleri.
- CLI, SDK ve REST API için `task` ile `detail` seçimleri; `/v1/profiles` kataloğu.
- Qwen 2.5 7B üretim QLoRA konfigürasyonu ve 4,5 GiB sınıfı GGUF doğrulama aracı.
- Prompt sistemi tasarım belgesi ve profil geliştirme rehberi.
- Proje iskeleti, klasör düzeni, kök dosyaları.
- Inference paketi (`src/clarify_prompt/`) taslak halinde: CLI, engine (llama.cpp backend), prompts (target profilleri), config, postproc.
- Eğitim pipeline'ı (`training/`) taslak halinde: data toplama, SFT, eval, pack.
- Test iskeleti, bench scriptleri, docs klasörü.
- PLAN.md — 2200+ satır uygulama planı, 20 bölüm.

### Notlar
- Model ağırlıkları depoya dahil değil; ölçüm iddiaları yayın öncesi değerlendirme
  raporuyla doğrulanacak.
- MVP release hedefi Faz 4 sonu (v0.1.0).

## [0.1.0] — TBD

Planlanan MVP release. Kabul kriterleri PLAN.md §13.2'de.
