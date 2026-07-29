# Planlama agaci: Acik kaynak 'prompt engineer AI' projesi: kullanicinin ham/eksik promptunu hedef LLM (Claude Code, ChatGPT, Cursor vb.) icin optimize edilmis, net, baglam-zengin, ornekli prompta ceviren kucuk (3B-8B) fine-tune edilmis acik kaynak LLM. Donanim sinirlari: RTX 4060 8GB VRAM + 16GB RAM (LoRA/QLoRA sart, tam fine-tune degil). MVP kapsami: veri seti tasarimi ve toplama, base model secimi (Qwen 2.5 / Llama 3.2 / Phi / Gemma ailelerinden), LoRA/QLoRA fine-tune (unsloth veya axolotl), degerlendirme (LLM-as-judge + kullanici A/B), inference (GGUF + llama.cpp veya vLLM), acik kaynak release (HF Hub + GitHub + MIT/Apache lisans), basit CLI kullanim. Entegrasyon (MCP server, Claude Code plugin) Faz 2'ye birakildi. Cikti: teknik plan degil, gercek uygulama planidir - kod, egitim scriptleri, degerlendirme scriptleri hepsi somut olarak tanimlanmali.

Toplam 69 dugum, 30 acilim turu (model: deepseek-flash).

Simgeler: `#` hedef  `+` ozellik  `-` gorev  `?` karar  `!` risk  `~` bilinmeyen  `@` kaynak

# **Acik kaynak 'prompt engineer AI' projesi: kullanicinin ham/eksik promptunu hedef LLM (Claude Code, ChatGPT, Cursor vb.) icin optimize edilmis, net, baglam-zengin, ornekli prompta ceviren kucuk (3B-8B) fine-tune edilmis acik kaynak LLM. Donanim sinirlari: RTX 4060 8GB VRAM + 16GB RAM (LoRA/QLoRA sart, tam fine-tune degil). MVP kapsami: veri seti tasarimi ve toplama, base model secimi (Qwen 2.5 / Llama 3.2 / Phi / Gemma ailelerinden), LoRA/QLoRA fine-tune (unsloth veya axolotl), degerlendirme (LLM-as-judge + kullanici A/B), inference (GGUF + llama.cpp veya vLLM), acik kaynak release (HF Hub + GitHub + MIT/Apache lisans), basit CLI kullanim. Entegrasyon (MCP server, Claude Code plugin) Faz 2'ye birakildi. Cikti: teknik plan degil, gercek uygulama planidir - kod, egitim scriptleri, degerlendirme scriptleri hepsi somut olarak tanimlanmali.** — Kok hedef
  # **Veri seti tasarimi ve toplama** — Ham promptlardan hedef LLM icin optimize edilmis promptlara donusum orneklerinden olusan egitim veri setini tasarla ve topla.
    - **Prompt dönüşüm şablonlarının oluşturulması** — Her bir hedef LLM için ham prompttan optimize prompta dönüşüm kurallarını ve şablonlarını tanımla.
      - **Her hedef LLM için şablon yapısının tanımlanması** — Claude Code, ChatGPT, Cursor gibi her LLM için optimize prompt şablonunun yapısını (sistem mesajı, kullanıcı mesajı, format kuralları) belirle.
        - **Her LLM'in resmi prompt yapısını araştırma** — Claude Code, ChatGPT, Cursor gibi hedef LLM'lerin dokümantasyonundan sistem mesajı, kullanıcı mesajı ve format kurallarını çıkar.
        ? **Şablonların ortak mı yoksa LLM'e özel mi olacağına karar verme** — Tüm LLM'ler için tek bir soyut şablon mu kullanılacak yoksa her LLM'e ayrı şablon mu tanımlanacak? Seçim yap.
        - **Her LLM için sistem ve kullanıcı mesajı formatını belirleme** — Her bir hedef LLM'in beklediği sistem mesajı rolü, kullanıcı mesajı yapısı ve olası özel etiketleri (ör. Claude'da <task> gibi) tanımla.
        ! **LLM güncellemeleri nedeniyle şablonların geçersiz kalma riski** — Hedef LLM'lerin API veya prompt yapılarını değiştirmesi durumunda şablonların güncellenmesi gerekebilir; bu riski yönet.
      - **Dönüşüm kuralları kütüphanesinin oluşturulması** — Ham prompttaki eksik bağlam, net olmayan talimat, örnek eksikliği gibi yaygın sorunları gidermek için kural tabanlı dönüşüm şablonları yaz.
      ? **Şablon formatının seçilmesi** — Şablonların JSON, YAML veya metin yer tutuculu bir formatta mı saklanacağına karar ver; örn. {context}, {instruction}, {examples} gibi.
      - **Her LLM için prompt optimizasyon kılavuzunun derlenmesi** — Claude'ın XML etiketleri, ChatGPT'nin markdown, Cursor'ın kod bağlamı gibi hedef LLM'lerin prompt tercihlerini araştırıp şablonlara yansıt.
    - **Ham prompt örneklerinin toplanması** — Gerçek kullanıcı promptları veya sentetik veri üretimi ile en az 1000 ham prompt örneği topla.
      - **Gerçek kullanıcı prompt kaynaklarının belirlenmesi** — İnternet forumları, açık kaynak veri setleri veya gönüllü katkıları gibi gerçek kullanıcı promptlarının toplanacağı kaynakları tespit et.
      - **Sentetik prompt üretimi için şablonlar oluşturma** — Farklı LLM kullanım senaryolarını kapsayan sentetik prompt örnekleri üretmek için şablonlar ve varyasyonlar hazırla.
      - **Toplanan promptların filtrelenmesi ve kalite kontrolü** — Kopyaları kaldır, anlamsız veya çok kısa promptları ele ve en az 1000 geçerli örnek bırak.
      ? **Veri depolama formatı ve etiketleme şemasının seçimi** — Promptları JSON veya CSV formatında saklama ve her birine kaynak, hedef model gibi etiketler ekleme kararını ver.
    ? **Veri seti boyutu ve çeşitliliği** — Eğitim veri setinin kaç örnekten oluşacağına ve hangi prompt türlerini (kod, yazı, analiz) kapsayacağına karar ver.
    - **Veri seti formatlama ve bölme işlemleri** — Toplanan verileri JSONL formatına dönüştür, eğitim/doğrulama/test olarak ayır ve kalite kontrolü yap.
  # **Base model secimi ve fine-tune pipeline** — Qwen2.5/Llama3.2/Phi/Gemma ailelerinden uygun modeli sec, LoRA/QLoRA ile fine-tune icin Unsloth veya Axolotl kullanarak egitim scriptini olustur.
    ? **Hedef model ailesi ve boyutunun secimi** — Qwen2.5, Llama3.2, Phi, Gemma ailelerinden 3B-8B araliginda, 8GB VRAM ve 16GB RAM'e uygun modeli belirle (ornegin Qwen2.5-3B-Instruct).
    - **Fine-tune veri setinin formatlanmasi** — Toplanan prompt-cevap orneklerini Unsloth/Axolotl'un bekledigi formata (Alpaca, ShareGPT veya chat template) donusturup train/validation/test olarak ayir.
      ? **Format seçimi** — Unsloth/Axolotl için Alpaca, ShareGPT veya chat template formatlarından hangisinin kullanılacağına karar ver.
      - **Dönüştürme scripti yaz** — Toplanan ham veriyi seçilen formata dönüştüren bir Python scripti oluştur.
      - **Eğitim/doğrulama/test ayrımı** — Veri setini %80 eğitim, %10 doğrulama, %10 test olacak şekilde böl ve ayrı dosyalara kaydet.
      - **Format doğrulama** — Formatlanmış verinin alan yapısını, token uzunluğunu ve örneklerin geçerliliğini kontrol et.
        - **Alan yapısı doğrulama** — Her örneğin beklenen alanlara (instruction, input, output, system_prompt vb.) sahip olduğunu ve türlerinin doğru olduğunu kontrol et.
        - **Token uzunluğu ve kesme kontrolü** — Örneklerin token sayısını modelin maksimum bağlam uzunluğuyla karşılaştır, sınırı aşanları kes veya işaretle.
        - **Örnek geçerlilik ve kalite kontrolü** — Boş çıktı, anlamsız metin, yinelenen örnekler gibi hatalı girdileri tespit et ve raporla.
        ? **Geçersiz örnekler için işlem politikası** — Geçersiz bulunan örneklerin silineceğine, düzeltileceğine yoksa sadece uyarı verileceğine karar ver.
    - **LoRA/QLoRA egitim scriptinin yazilmasi** — Unsloth veya Axolotl ile LoRA rank, alpha, target modules, quantization (4-bit NF4) parametrelerini iceren egitim scriptini olustur ve RTX 4060'da calisabilirligini dogrula.
      - **Unsloth/Axolotl kutuphanesinin kurulumu ve dogrulugu** — Unsloth veya Axolotl'u pip ile kur, surumunu sabitle ve RTX 4060'da import edilebilirligini dogrula.
        ? **Unsloth veya Axolotl arasinda secim** — RTX 4060 ve 8GB VRAM icin hangi kutuphanenin LoRA/QLoRA destegi, performansi ve kolayligi daha uygun olduguna karar ver.
        - **CUDA ve PyTorch surum uyumlulugunu dogrulama** — Mevcut CUDA surumunu (ornegin 12.x) kontrol et, Unsloth/Axolotl ile uyumlu PyTorch surumunu pip ile kur.
        - **Kutuphaneyi pip ile kur ve surumunu sabitle** — Unsloth veya Axolotl'u requirements.txt'de belirtilen surumle pip install yap, ortami dondur.
        - **Import ve temel model yukleme testi** — Python'da kutuphaneyi import et, RTX 4060'da kucuk bir model (ornegin 1B) yukleyip LoRA konfigurasyonunu calistirarak dogrula.
      - **LoRA hiperparametrelerinin (rank, alpha, target_modules) secimi ve script'e eklenmesi** — LoRA rank (ornegin 8-16), alpha (ornegin 16-32) ve target modules (q_proj, v_proj vb.) degerlerini belirle ve egitim scriptinde tanimla.
        ? **LoRA rank ve alpha icin baslangic degerlerini sec** — Literatur ve model boyutuna gore rank (ornegin 8-16) ve alpha (ornegin 16-32) degerlerini belirle.
        - **Hedef modelin target_modules listesini cikar** — Secilen base modelin (Qwen/Llama/Phi) transformer katmanlarindaki projection matrislerini (q_proj, v_proj, k_proj, o_proj vb.) ogren ve listele.
        - **Egitim scriptinde LoRA yapilandirmasini kodla** — Unsloth veya Axolotl config dosyasinda rank, alpha, target_modules, dropout gibi parametreleri tanimla ve model yukleme fonksiyonuna ekle.
        - **Secilen hiperparametrelerle kucuk olcekli dogrulama egitimi calistir** — Az sayida ornekle (ornegin 100 adim) bir test egitimi baslatarak LoRA yapilandirmasinin calistigini ve VRAM sinirlarina uydugunu dogrula.
      - **4-bit NF4 quantization konfigurasyonunun script'e eklenmesi** — Bitsandbytes 4-bit NF4 quantization ayarlarini (compute_dtype, bnb_4bit_use_double_quant) model yukleme koduna ekle.
        ? **Bitsandbytes 4-bit parametre degerlerinin secimi** — compute_dtype (float16/bfloat16), bnb_4bit_use_double_quant (True/False) ve bnb_4bit_compute_dtype gibi parametrelerin belirlenmesi.
        - **BitsAndBytesConfig nesnesinin olusturulmasi ve model yukleme koduna eklenmesi** — Python kodunda BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4', ...) tanimlayip model.from_pretrained(... , quantization_config=config) ile entegre et.
        - **4-bit quantizasyonun bellek kullanimini dogrulama testi** — Egitim scriptini calistirip VRAM kullanimini kontrol eden kucuk bir test yaz, 8GB sinirini asmadigini dogrula.
        ! **Unsloth veya Axolotl ile 4-bit NF4 uyumsuzlugu** — Kullanilan fine-tune kutuphanesi (Unsloth/Axolotl) 4-bit NF4 quantization ile tam uyumlu olmayabilir; ek ayar veya workaround gerekebilir.
      - **Egitim scriptinde bellek yonetimi ayarlarinin eklenmesi** — RTX 4060 8GB VRAM icin gradient checkpointing, per_device_train_batch_size (ornegin 1-2) ve gradient_accumulation_steps ayarlarini script'e ekle.
    - **Degerlendirme metrigi ve judge scriptinin hazirlanmasi** — LLM-as-judge icin referans model (ornegin GPT-4o-mini) ve kullanici A/B testi icin basit bir karsilastirma scripti yaz, metrik olarak prompt kalitesi skoru belirle.
      ? **LLM-as-judge referans model secimi** — Hangi modelin (GPT-4o-mini, GPT-4, Claude 3.5, veya acik kaynak bir model) jude olarak kullanilacagina karar ver.
      + **Prompt kalitesi metrik tanimi** — Prompt'un netlik, baglam zenginligi, ornek icerme, hedef LLM uyumu gibi boyutlarini olcen skorlama kriterlerini belirle.
      - **Judge scriptinin yazilmasi** — Secilen referans modeli cagirip promptlari degerlendiren, metrik skorlarini donduren bir Python scripti olustur.
      - **Kullanici A/B test mekanizmasi** — Iki farkli model ciktisini karsilastirip kullanicinin tercihini kaydeden basit bir CLI veya web arayuzu scripti yaz.
  # **Degerlendirme ve inference altyapisi** — LLM-as-judge ve kullanici A/B testi ile model kalitesini olc, GGUF+llama.cpp veya vLLM ile inference yap, basit CLI kullanimini sagla.
    - **LLM-as-judge değerlendirme scripti** — Judge model (ör. GPT-4) kullanarak üretilen promptları puanlayacak ve metrikleri (doğruluk, netlik, bağlam) raporlayacak bir Python scripti yaz.
    - **Kullanıcı A/B testi altyapısı** — Kullanıcıların iki model çıktısını karşılaştırıp tercihini kaydedecek basit bir web/CLI arayüzü ve veri toplama mekanizması oluştur.
    ? **Inference motoru seçimi** — GGUF+llama.cpp ve vLLM arasında VRAM, hız ve kolaylık açısından karşılaştırma yap, MVP için hangisinin kullanılacağına karar ver.
    - **CLI arayüzü geliştirme** — Kullanıcının ham prompt girmesini, seçilen modeli çalıştırmasını ve optimize edilmiş promptu almasını sağlayan komut satırı aracı (Python argparse) yaz.
      - **Argüman ayrıştırma ve giriş doğrulama** — Python argparse ile ham prompt, model seçeneği (varsayılan model yolu), çıktı formatı (düz metin/JSON) argümanlarını tanımla ve giriş doğrula.
      - **Model yükleme ve çıkarım entegrasyonu** — Seçilen GGUF modelini llama.cpp (ctypes) veya vLLM API ile yükleyen, ham promptu işleyip optimize promptu döndüren bir fonksiyon yaz.
      - **Çıktı biçimlendirme ve görüntüleme** — Modelden gelen ham yanıtı temizle, isteğe bağlı renklendirme (rich veya colorama) ile kullanıcıya göster; JSON çıktı seçeneğini destekle.
      - **Hata yönetimi ve günlükleme** — Model yüklenememesi, bellek yetersizliği, geçersiz giriş gibi durumlar için try/except blokları ekle; hata mesajlarını stderr'e yaz ve isteğe bağlı log dosyası oluştur.
  # **Acik kaynak release ve dokumantasyon** — Modeli HF Hub'a, kodlari GitHub'a yayinla, MIT/Apache lisansi sec, kullanim dokumantasyonu ve ornekler ekle.
    - **Lisans dosyası ve README oluştur** — MIT veya Apache 2.0 lisansını seç, LICENSE dosyası ekle; README'ye proje amacı, kurulum, kullanım ve referansları yaz.
      ? **Lisans türü seçimi** — MIT ile Apache 2.0 arasında seçim yap; Apache 2.0 patent koruması sunar, MIT daha basittir.
      - **LICENSE dosyası oluştur** — Seçilen lisansın metnini (MIT veya Apache 2.0) proje köküne LICENSE dosyası olarak ekle.
      - **README giriş bölümü yaz** — Proje amacı, özellikler ve hedef kitleyi açıklayan kısa bir giriş paragrafı ekle.
      - **Kurulum ve kullanım kılavuzu yaz** — CLI kurulum adımları, bağımlılıklar ve temel kullanım örneği ile örnek prompt dönüşümü göster.
    - **Modeli Hugging Face Hub'a yükle** — Fine-tune edilmiş model ağırlıklarını (GGUF veya safetensors) HF Hub'da yeni bir repo'ya push et; model kartına eğitim detayları, benchmark sonuçları ve örnek promptları ekle.
    - **GitHub deposunu düzenle ve kodları yayınla** — GitHub'da yeni repo oluştur; fine-tune scriptleri, değerlendirme scriptleri, CLI aracı, requirements.txt ve setup.py dosyalarını yükle; .gitignore ekle.
    - **Kullanım dokümantasyonu ve örnekler hazırla** — CLI kullanım kılavuzu, örnek girdi-çıktı çiftleri, farklı LLM'ler için uyarlama notları ve hızlı başlangıç rehberi yaz; docs/ klasörüne ekle.