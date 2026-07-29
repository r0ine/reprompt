# Prompt sistemi

Bu belge, çalışma zamanı promptunun nasıl derlendiğini ve neden tek bir dev metin yerine
profillerden oluştuğunu anlatır.

## Tasarım hedefi

Yeniden yazıcı şu iki hatayı aynı anda önlemelidir:

1. Ham isteği neredeyse değiştirmeden döndürmek.
2. Kullanıcının söylemediği ürün kapsamını, teknik seçimi veya kabul ölçütünü uydurmak.

Çekirdek protokol bu sınırı “yapı ve uygulama disiplini ekle, ürün kapsamı ekleme” şeklinde
kurar. Görev profili hangi ayrıntıların işe yaradığını, hedef profili ise bu ayrıntıların
nasıl paketleneceğini belirler.

## Derleme sırası

`select_system_prompt()` bileşenleri sabit sırada birleştirir:

```text
system.md
tasks/<task>.md
depths/<detail>.md
targets/<target>.md
explain talimatı (isteğe bağlı)
```

Sıra önemlidir. Çekirdek rol ve değişmezler önce gelir. Görev ve ayrıntı kuralları içeriği
şekillendirir. Hedef araç profili en sonda biçimi ve araç varsayımlarını netleştirir.
`--explain` yalnızca son çıktı davranışını ekler.

Ayraç olarak `---` kullanılır. Profil dosyaları kendi başlarına okunabilir; derlenmiş prompt
ise tek bir sistem mesajı olarak çıkarım backend'ine gönderilir.

## Çekirdek protokol

`system.md` beş sorumluluğu taşır.

### Niyet koruma

Kullanıcının hedefi, sınırları, tercihleri, yasakları, özel adları ve teslimleri korunur.
Model daha iyi bildiğini düşünerek framework, veritabanı, servis, ekran veya dağıtım
ekleyemez.

### Gerçek ile varsayımı ayırma

Dosya yolu, sürüm, performans hedefi, mevzuat, kişi, kaynak ve ölçüm gibi bilgiler
uydurulmaz. Düşük riskli ve geri alınabilir boşluklarda varsayım yapılabilir; bu varsayım
çıktıda açıkça görünür.

### Belirsizlik yönetimi

Her eksik bilgi soru değildir. Soru ancak cevap:

- teslim türünü ciddi biçimde değiştirecekse;
- dış veya yıkıcı bir işleme izin verecekse;
- geri alınması zor bir mimariyi belirleyecekse;
- başarıyı ölçmeyi imkânsız bırakıyorsa

sorulur. En fazla üç soru üretilir ve en yüksek etkili karar önce gelir.

### Kabul ölçütü üretme

Ölçütler görevle orantılıdır. Kod için her zaman tarayıcı testi, yazı için her zaman kaynak,
araştırma için her zaman kod çalıştırma istenmez. Model yalnızca tarif edilen ortamda
gerçekten uygulanabilecek doğrulamaları ekler.

### Çıktı disiplini

Çıktı doğrudan hedef araca yapıştırılabilir olmalıdır. Preamble, sistem promptunun
açıklaması, gizli düşünme zinciri ve aynı gereksinimin farklı başlıklarda tekrar edilmesi
yasaktır.

## Görev profilleri

Görev profili ürün alanını tahmin etmez; çalışma türünün kalite kapısını ekler.

Örneğin `debugging`:

- semptom ve ortamı korur;
- reprodüksiyon ister;
- gözlem, hipotez ve kök nedeni ayırır;
- geniş refactor'a otomatik yetki vermez;
- regresyon kontrolü ister.

`review` ise tam tersine değişiklik yetkisi çıkarmaz. Bulgunun dosya, satır veya gözlenebilir
davranışla kanıtlanmasını ister ve “bulgu yok” sonucunu geçerli kabul eder.

`auto`, bu ayrımı istenen sonuca bakarak sessizce yapar. İki görev gerçekten iç içeyse
kuralları birleştirir; bağımsız teslimleri tek şekle zorlamaz.

## Ayrıntı seviyesi

Ayrıntı seviyesi kapsamı değiştirmez.

`compact` ile `exhaustive` arasındaki fark, istenen ürüne yeni özellikler eklemek değildir.
Fark; mevcut isteğin hata yolları, karar noktaları, kabul kanıtı ve işletim ihtiyaçlarının ne
kadar açık yazıldığıdır.

`exhaustive` profilin bütün kalite konularını her prompta eklememesi özellikle belirtilir.
Bir logo üretim promptunda veritabanı migration'ı, kısa metin düzenlemesinde rollback planı
ve salt-okunur incelemede deployment adımı yer almamalıdır.

## Hedef profilleri

Hedef profil, model markasına göre süslü biçim üretmek için değil, çalışma ortamındaki gerçek
farkları temsil etmek için vardır.

- `codex` ve `claude-code`, depo talimatlarını okuyan ve dosya değiştirebilen ajanlardır.
- `cursor` ve `github-copilot`, açık dosya veya seçili sembol bağlamında daha kısa talimatla
  çalışır.
- `gemini`, ekli dosya ve görsel kaynakların nasıl kullanılacağını açıkça ayırır.
- `grok`, canlı bilgi gerekiyorsa tarih ve kaynak ayrımını öne çıkarır.
- `generic`, hiçbir araç yeteneğini varsaymaz.

Yeni hedef yalnızca bu tür gözlenebilir bir fark taşıyorsa eklenmelidir.

## Prompt injection sınırı

Ham istek sistem mesajına eklenmez; kullanıcı mesajı olarak gönderilir. Çekirdek protokol,
ham metni dönüştürülecek veri olarak tanımlar. Böylece “önceki kuralları yok say” benzeri
bir metin yeniden yazıcının görevini değiştiremez.

Bu davranış downstream güvenlik filtresi değildir. Kullanıcı gerçekten bir güvenlik testi
promptu hazırlıyorsa bu niyet korunabilir. Yeniden yazıcı yalnızca kendi rolünün ele
geçirilmesini engeller; hedef model kendi güvenlik politikasını uygulamaya devam eder.

## Eğitim ile çalışma zamanının hizası

Hem Unsloth hem Hugging Face SFT akışı `select_system_prompt()` kullanır. Eğitim kaydındaki
`target`, `task` ve `detail` alanları aynı çalışma zamanı profillerini seçer. Alanlar eski
veri setinde yoksa sırasıyla `generic`, `auto` ve `balanced` kullanılır.

Teacher-distillation hattı da aynı derleyiciyi kullanır. Böylece üç farklı kısa sistem
promptunun zamanla birbirinden kopması önlenir:

- teacher veri üretimi;
- SFT eğitim girdisi;
- gerçek çıkarım.

Profil metni değiştiğinde değerlendirme seti yeniden çalıştırılmalıdır. Büyük bir çekirdek
değişikliği, eski adapter'ın aynı davranışı göstereceği anlamına gelmez.

## Bağlam bütçesi

Prompt kalitesi dosya boyutuyla ölçülmez. Yaklaşık 4,5 GiB ifadesi Qwen 2.5 7B Q4_K_M model
paketini anlatır. Sistem promptu bağlam penceresini tüketmeyecek kadar sınırlı kalmalıdır.

4096 token eğitim bağlamında bütçe kabaca şu parçalara ayrılır:

- derlenmiş sistem promptu;
- ham kullanıcı isteği;
- hedef optimize prompt;
- chat template özel tokenları.

Çok uzun ham girdilerde sistem + çıktı için yer kalmıyorsa veri hazırlama aşaması kaydı
reddetmeli veya kontrollü biçimde kırpmalıdır. Çıktının ortadan kesilmesi sessizce kabul
edilmemelidir.

## Sürümleme

Profil metinleri model davranışının parçasıdır. Şu değişiklikler changelog'a yazılmalıdır:

- çekirdek niyet veya belirsizlik kuralı değişikliği;
- yeni hedef, görev veya ayrıntı profili;
- varsayılan profil değişikliği;
- sistem promptu ile eğitim promptu hizasını etkileyen değişiklik;
- çıktı formatını geriye dönük uyumsuz hâle getiren karar.

Profil dosyaları Python kodundan bağımsız incelenebilir, fakat tür sabitleri ve testler aynı
değişiklikte güncellenmelidir.

## Test stratejisi

Birim testleri şunları doğrular:

- bütün kayıtlı profil dosyaları yükleniyor;
- bileşen sırası değişmiyor;
- bilinmeyen ve path traversal benzeri profil adları reddediliyor;
- `--explain` yalnızca en sona ekleniyor;
- CLI, SDK ve API seçilen profilleri sistem promptuna iletiyor;
- config ve ortam değişkenleri aynı değer kümesini kullanıyor;
- eğitim hatları kısa kopya promptlar yerine derleyiciyi çağırıyor.

Bunlar dil kalitesini tek başına ölçmez. Model değerlendirmesinde ayrıca şu davranışlar için
gold örnek gerekir:

- niyet kayması;
- uydurma bağlam;
- gereksiz soru;
- çözümü cevaplama;
- hedef biçime uymama;
- düşük riskli varsayımı gerçek gibi sunma;
- `exhaustive` profil altında gereksiz kapsam şişirmesi;
- hassas veriyi gereksiz tekrar etme.

## Değişiklik kontrol listesi

Prompt sisteminde değişiklik yaparken:

1. İlgili profil dosyasını ve çekirdek protokolü birlikte oku.
2. Yeni kuralın başka bir katmanda zaten bulunup bulunmadığını kontrol et.
3. Kuralın kullanıcı kapsamını genişletmediğini doğrula.
4. En az bir olumlu ve bir karşı örnek düşün.
5. Selector, CLI, SDK, API ve eğitim testlerini çalıştır.
6. Gold değerlendirme setinde niyet koruma ve gereksiz kapsam metriklerini karşılaştır.
7. Varsayılan davranış değiştiyse README ve changelog'u güncelle.
