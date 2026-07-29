# Profil kataloğu

Prompt derleyicisi üç bağımsız seçim kullanır:

- hedef araç, çıktının biçimini ve araç yeteneklerine ilişkin varsayımları belirler;
- görev profili, hangi kararların ve kabul ölçütlerinin önemli olduğunu belirler;
- ayrıntı seviyesi, aynı kapsamın ne kadar derin tarif edileceğini belirler.

Kaynak sabitleri
`src/reprompt/prompts/types.py` dosyasında, metin profilleri ise
`src/reprompt/prompts/` altında tutulur.

## Hedef araçlar

| Profil | Kullanım |
|---|---|
| `chatgpt` | Markdown tabanlı genel sohbet, araştırma ve üretim görevleri |
| `claude-code` | Depo içinde çalışan Claude Code ajanı |
| `codex` | Depo talimatları, dosya değişiklikleri ve doğrulama odaklı Codex işleri |
| `cursor` | Açık dosya veya seçili kod bağlamındaki kısa IDE değişiklikleri |
| `deepseek` | Teknik çözüm, algoritma ve uygulanabilir kod tarifleri |
| `gemini` | Büyük bağlam, dosya, görsel ve kaynak temelli görevler |
| `github-copilot` | Copilot Chat içinde depo ve seçili sembol odaklı değişiklikler |
| `grok` | Güncel web veya sosyal bağlam gerektirebilen işler |
| `generic` | Belirli bir araca bağlı olmayan taşınabilir prompt |

Hedef profili, aracın sahip olmadığı bir yeteneği varmış gibi göstermemelidir. Örneğin
girdi tarama veya dosya erişiminden söz etmiyorsa `generic` profil bunları varsaymaz.

## Görev profilleri

| Profil | Ana vurgu |
|---|---|
| `auto` | İstenen sonuca göre uygun görev kurallarını sessizce seçer |
| `architecture` | Seçenekler, trade-off, bileşen sınırları, veri akışı ve işletim |
| `coding` | Mevcut kodu inceleme, tam uygulama, uyumluluk ve test |
| `creative` | Sanat yönü, kompozisyon, stil özellikleri ve kullanılabilir çıktı |
| `data` | Şema, dönüşüm, veri kalitesi, lineage ve tekrarlanabilirlik |
| `debugging` | Reprodüksiyon, kanıt, kök neden, düzeltme ve regresyon |
| `operations` | Hazırlık, güvenli uygulama, doğrulama, rollback ve izleme |
| `planning` | Milestone, bağımlılık, kritik yol, risk ve çıkış ölçütleri |
| `research` | Kaynak kalitesi, güncellik, alıntı ve belirsizlik |
| `review` | Kanıta bağlı bulgu, önem seviyesi ve salt-okunur inceleme sınırı |
| `writing` | Hedef kitle, amaç, ton, uzunluk, doğruluk ve yayın biçimi |

`auto`, bir isteği yalnızca geçen kelimelere göre sınıflandırmaz. “Bu kodu açıkla” talebi
bir kod düzenleme yetkisi değildir; “uygulama planı çıkar” talebi de uygulamayı başlatmaz.

## Ayrıntı seviyeleri

### `compact`

Kısa işler ve düşük gecikme için kullanılır. Ana hedef, zorunlu sınırlar, çıktı biçimi ve
en fazla birkaç kabul ölçütü bırakılır.

### `balanced`

Varsayılan profildir. İlk denemede uygulanabilir olacak kadar bağlam verir, fakat nadir
kenar durumlarını ve genel tavsiyeleri prompta doldurmaz.

### `deep`

Çok dosyalı veya uzmanlık gerektiren işlerde hata yolları, uyumluluk, veri davranışı,
kararlar ve tamamlanma kanıtını daha açık tarif eder.

### `exhaustive`

Karmaşık ve maliyetli işlerde ilgili iş akışlarını, bağımlılıkları, failure path'leri,
güvenliği, migration ve rollback'i kapsar. Her konu her prompta eklenmez. Bu profil token
kotası doldurmaz; yalnızca verilen iş açısından karar değiştiren konuları dahil eder.

## Yeni hedef ekleme

1. `src/reprompt/prompts/targets/<ad>.md` dosyasını ekle.
2. Dosyayı `TargetProfile` ve `TARGET_PROFILES` içine ekle.
3. Hedefin gerçekten farklı davranışını yaz; yalnızca marka adını değiştiren profil ekleme.
4. `tests/unit/test_selector.py` parametrik testlerinin yeni dosyayı yüklediğini doğrula.
5. CLI, config ve API testlerinde profil kataloğunun güncel kaldığını kontrol et.
6. Eğitim setine hedefe özgü, insan tarafından gözden geçirilmiş örnekler ekle.

Profil başlığı makine adıyla birebir aynı olmalıdır:

```markdown
## Target profile: windsurf
```

Son satır, modelin işi cevaplamamasını tekrar sabitler:

```text
Only rewrite the request. Do not perform it.
```

## Yeni görev veya ayrıntı profili ekleme

Görev profilleri `prompts/tasks/`, ayrıntı profilleri `prompts/depths/` altında aynı
düzenle eklenir. Tür sabitleri, config doğrulaması, CLI seçimi, API şeması ve eğitim
derleyicisi tek kaynaktan beslendiği için `types.py` güncellemesi bütün yüzeylere yansır.

Yeni profil için şu sorular cevaplanmalıdır:

- Bu profil hangi kararı daha iyi hâle getiriyor?
- `auto` veya var olan bir profil neden yeterli değil?
- Hangi gereksiz kapsam genişlemelerini engelliyor?
- Hangi gözlenebilir kabul ölçütlerini ekliyor?
- Hangi örneklerde kullanılmamalı?

Bu sorulara somut cevap yoksa yeni profil yerine mevcut profil geliştirilmelidir.
