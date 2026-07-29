# Konu Dizini

Bu dizin, 1 GiB Markdown corpus içindeki alanları ve fiziksel dağılımı gösterir.
Bir alana başlamak için ilgili klasördeki en düşük sıra numaralı ciltten ilerlenebilir.
Belirli bir kabul ölçütü veya risk ifadesi aranacaksa `rg` ile bütün corpus taranabilir.

| Alan | Kapsam | Cilt | Prompt kaydı | Bayt |
|---|---|---:|---:|---:|
| [API ve Entegrasyon](corpus-1gib/api-integration/) | Dayanıklı sistemler arası sözleşmeler | 42 | 8.474 | 44.171.750 |
| [Otomasyon ve Botlar](corpus-1gib/automation-bots/) | Güvenli iş akışı otomasyonu | 42 | 8.487 | 44.142.255 |
| [Backend Geliştirme](corpus-1gib/backend-engineering/) | Servis, iş mantığı ve hata davranışı | 43 | 8.675 | 45.206.904 |
| [İş Operasyonları](corpus-1gib/business-operations/) | Ölçülebilir süreç ve operasyon tasarımı | 42 | 8.438 | 44.169.568 |
| [Bulut Altyapısı](corpus-1gib/cloud-infrastructure/) | Ölçek, süreklilik ve maliyet kontrolü | 43 | 8.642 | 45.203.558 |
| [Siber Güvenlik](corpus-1gib/cyber-security/) | Tehdit odaklı savunma ve güvenli geliştirme | 43 | 8.665 | 45.199.154 |
| [Veritabanı Sistemleri](corpus-1gib/database-systems/) | Veri modeli, sorgular ve yaşam döngüsü | 43 | 8.646 | 45.181.723 |
| [Veri Mühendisliği](corpus-1gib/data-engineering/) | Veri hattı, köken ve kalite | 43 | 8.664 | 45.209.406 |
| [Geliştirici Deneyimi](corpus-1gib/developer-experience/) | Araç kullanılabilirliği ve geri bildirim süresi | 42 | 8.403 | 44.133.015 |
| [DevOps ve Platform](corpus-1gib/devops-platform/) | Teslimat otomasyonu ve platform işletimi | 43 | 8.646 | 45.188.914 |
| [Frontend Geliştirme](corpus-1gib/frontend-engineering/) | Erişilebilirlik, durum ve arayüz performansı | 43 | 8.635 | 45.226.516 |
| [Oyun Geliştirme](corpus-1gib/game-development/) | Oynanış sistemleri ve içerik üretim hattı | 42 | 8.469 | 44.169.540 |
| [Üretken Yapay Zekâ](corpus-1gib/generative-ai/) | LLM ürünleri, korumalar ve değerlendirme | 43 | 8.647 | 45.192.971 |
| [Makine Öğrenmesi](corpus-1gib/machine-learning/) | Model geliştirme ve deney yönetimi | 43 | 8.670 | 45.209.083 |
| [Mobil Geliştirme](corpus-1gib/mobile-development/) | Yerel mobil deneyim ve çevrimdışı çalışma | 43 | 8.641 | 45.204.241 |
| [Gözlemlenebilirlik ve SRE](corpus-1gib/observability-sre/) | SLO, telemetri ve olay müdahalesi | 43 | 8.643 | 45.190.226 |
| [Performans Mühendisliği](corpus-1gib/performance-engineering/) | Profil çıkarma, kapasite ve gecikme | 42 | 8.435 | 44.179.103 |
| [Gizlilik ve Uyum](corpus-1gib/privacy-compliance/) | Veri koruma ve denetlenebilir kontroller | 42 | 8.484 | 44.162.635 |
| [Ürün Yönetimi](corpus-1gib/product-management/) | Hipotez, öncelik ve yol haritası kararları | 43 | 8.646 | 45.180.159 |
| [Kalite Mühendisliği](corpus-1gib/quality-engineering/) | Risk temelli test ve sürüm güveni | 43 | 8.652 | 45.175.808 |
| [Araştırma ve Analiz](corpus-1gib/research-analysis/) | Kaynaklı inceleme ve karar desteği | 42 | 8.463 | 44.162.590 |
| [Yazılım Mimarisi](corpus-1gib/software-architecture/) | Mimari karar ve teknik tasarım | 43 | 8.661 | 45.188.259 |
| [Teknik Yazarlık](corpus-1gib/technical-writing/) | Dokümantasyon ve bilgi mimarisi | 43 | 8.667 | 45.210.155 |
| [UX Araştırması](corpus-1gib/ux-research/) | Kullanıcı araştırması ve deneyim doğrulama | 43 | 8.648 | 45.178.183 |
| **Toplam** | **24 alan** | **1.024** | **206.101** | **1.076.435.716** |

## Arama örnekleri

Belirli bir riskin işlendiği kayıtları bulma:

```powershell
rg -l "sessiz veri kaybı" library\corpus-1gib
```

Bir alandaki kabul ölçütlerini listeleme:

```powershell
rg -n "^### Kabul ölçütleri" library\corpus-1gib\cyber-security
```

Belirli bir ölçeğe göre prompt seçme:

```powershell
rg -l "çok bölgeli üretim ortamı" library\corpus-1gib
```
