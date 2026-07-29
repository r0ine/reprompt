# Clarify Prompt Markdown Kütüphanesi

Bu dizin, ham bir isteği uygulanabilir ve denetlenebilir bir prompta dönüştürmek için
hazırlanmış 1 GiB'lık yerel başvuru corpus'unu barındırır. Kütüphane yalnızca Markdown
dosyalarından oluşur; her kayıt bağlam, kısıtlar, hata yolları, çıktı sözleşmesi, kabul
ölçütleri ve eleştirel inceleme adımları içerir.

## Yapı

- `corpus-1gib/`: Alanlara ayrılmış 1.024 Markdown cildi.
- `INDEX.md`: Alan, kapsam, cilt, prompt kaydı ve bayt dağılımı.
- `MANIFEST.md`: Her cildin bayt boyutu ve SHA-256 özeti.
- `../tools/markdown_library.py`: Kütüphaneyi deterministik biçimde kuran ve doğrulayan araç.

Corpus; yazılım mimarisi, backend, frontend, mobil, veri, yapay zekâ, veritabanı,
DevOps, bulut, güvenlik, kalite, SRE, ürün, UX, teknik yazarlık, araştırma, operasyon,
oyun, botlar, entegrasyon, gizlilik, performans ve geliştirici deneyimi alanlarını kapsar.

## Kurulum

Proje kökünde:

```powershell
python tools\markdown_library.py build
```

Varsayılan hedef ikili ölçüyle tam 1 GiB, yani en az `1.073.741.824` bayttır. Araç
mevcut ve kendisine ait ciltleri korur, eksik olanları tamamlar. Başka bir dosyanın
üzerine yazmaz.

Üretici mantığı değiştiğinde yalnızca üretici imzası doğrulanan ciltler güvenli ve atomik
biçimde yeniden kurulabilir:

```powershell
python tools\markdown_library.py build --rebuild
```

## Doğrulama

```powershell
python tools\markdown_library.py verify
```

Doğrulama bütün dosyaları yeniden okur. Dosya sayısını, uzantıları, toplam boyutu,
manifest kayıtlarını ve her dosyanın SHA-256 özetini karşılaştırır. Yarım kalmış
`.partial` dosyaları veya corpus'a karışmış Markdown dışı dosyalar hata sayılır.

## Küçük corpus üretme

Geliştirme ve deneme için hedef ile cilt boyutu değiştirilebilir:

```powershell
python tools\markdown_library.py `
  --output .tmp\prompt-library `
  --manifest .tmp\MANIFEST.md `
  build --target 64MiB --volume-size 1MiB
```

Boyut değerlerinde `GiB`, `GB`, `MiB`, `MB`, `KiB`, `KB` ve ham bayt kullanılabilir.

## Sürüm kontrolü

1 GiB'lık corpus Git'e eklenmez; üretici, belgeler ve manifest sürüm kontrolünde kalır.
Bu sayede depo klonlanabilir boyutta tutulurken yerel kütüphane aynı içerikle tekrar
kurulabilir. Corpus içeriğinin bütünlüğü `MANIFEST.md` üzerinden denetlenir.
