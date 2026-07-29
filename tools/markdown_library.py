from __future__ import annotations

import argparse
import hashlib
import math
import os
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

GIB = 1024**3
MIB = 1024**2
GENERATOR_VERSION = "1.0"
FILE_SIGNATURE = "<!-- clarify-prompt-library:v1 -->"
MANIFEST_ROW = re.compile(r"^\| `(?P<path>[^`]+)` \| (?P<size>\d+) \| `(?P<sha>[0-9a-f]{64})` \|$")

DOMAINS = (
    ("software-architecture", "Yazılım Mimarisi", "mimari karar kaydı ve teknik tasarım"),
    ("backend-engineering", "Backend Geliştirme", "güvenilir servis ve iş mantığı"),
    ("frontend-engineering", "Frontend Geliştirme", "erişilebilir ve hızlı kullanıcı arayüzü"),
    ("mobile-development", "Mobil Geliştirme", "yerel mobil deneyim ve çevrimdışı çalışma"),
    ("data-engineering", "Veri Mühendisliği", "izlenebilir veri hattı ve veri kalitesi"),
    ("machine-learning", "Makine Öğrenmesi", "ölçülebilir model geliştirme süreci"),
    ("generative-ai", "Üretken Yapay Zekâ", "LLM tabanlı ürün ve değerlendirme sistemi"),
    ("database-systems", "Veritabanı Sistemleri", "veri modeli, sorgu ve yaşam döngüsü"),
    ("devops-platform", "DevOps ve Platform", "tekrarlanabilir teslimat ve platform işletimi"),
    ("cloud-infrastructure", "Bulut Altyapısı", "ölçeklenebilir ve maliyet kontrollü altyapı"),
    ("cyber-security", "Siber Güvenlik", "tehdit odaklı savunma ve güvenli geliştirme"),
    ("quality-engineering", "Kalite Mühendisliği", "risk temelli test ve sürüm güveni"),
    ("observability-sre", "Gözlemlenebilirlik ve SRE", "SLO, telemetri ve olay müdahalesi"),
    ("product-management", "Ürün Yönetimi", "kanıta dayalı ürün kararı ve yol haritası"),
    ("ux-research", "UX Araştırması", "kullanıcı araştırması ve deneyim doğrulama"),
    ("technical-writing", "Teknik Yazarlık", "okunabilir dokümantasyon ve bilgi mimarisi"),
    ("research-analysis", "Araştırma ve Analiz", "kaynaklı inceleme ve karar desteği"),
    ("business-operations", "İş Operasyonları", "ölçülebilir süreç ve operasyon tasarımı"),
    ("game-development", "Oyun Geliştirme", "oynanış sistemi ve içerik üretim hattı"),
    ("automation-bots", "Otomasyon ve Botlar", "güvenli iş akışı otomasyonu"),
    ("api-integration", "API ve Entegrasyon", "dayanıklı sistemler arası sözleşme"),
    ("privacy-compliance", "Gizlilik ve Uyum", "veri koruma ve denetlenebilir kontrol"),
    ("performance-engineering", "Performans Mühendisliği", "ölçüm odaklı kapasite iyileştirme"),
    (
        "developer-experience",
        "Geliştirici Deneyimi",
        "hızlı geri bildirim ve araç kullanılabilirliği",
    ),
)

SCENARIOS = (
    "sıfırdan tasarım",
    "mevcut sistemin iyileştirilmesi",
    "üretim arızasının kök neden analizi",
    "yüksek riskli geçiş planı",
    "teknik borç azaltma programı",
    "ölçek büyütme hazırlığı",
    "maliyet düşürme çalışması",
    "güvenlik sertleştirmesi",
    "kalite kapısı oluşturma",
    "eski sistemden kademeli ayrışma",
    "çok ekipli teslimat koordinasyonu",
    "deney ve hipotez doğrulaması",
)

AUDIENCES = (
    "kıdemli geliştiriciler",
    "ürün ve mühendislik liderleri",
    "alana yeni katılan ekip üyeleri",
    "operasyon ve destek ekibi",
    "güvenlik ve uyum paydaşları",
    "teknik olmayan karar vericiler",
    "dağıtık çalışan çapraz fonksiyonlu ekip",
    "harici entegrasyon ortakları",
)

SCALES = (
    "günde on bin işlem",
    "günde bir milyon işlem",
    "ani trafikte saniyede beş bin istek",
    "on kişilik iç ekip",
    "yüz bin aktif kullanıcı",
    "çok bölgeli üretim ortamı",
    "kısıtlı donanımlı uç cihazlar",
    "yasal olarak ayrılmış müşteri verileri",
)

CONSTRAINTS = (
    "kesinti penceresi yok",
    "ek altyapı bütçesi sınırlı",
    "geriye dönük uyumluluk zorunlu",
    "kişisel veri kalıcı loglara yazılamaz",
    "çözüm küçük adımlarla devreye alınmalı",
    "mevcut ekip üç ay içinde sahipliği devralmalı",
    "kritik yol üçüncü taraf hizmete bağımlı olmamalı",
    "her karar ölçülebilir kabul ölçütüne bağlanmalı",
)

OUTPUTS = (
    "uygulanabilir teknik tasarım",
    "önceliklendirilmiş çalışma planı",
    "karar seçenekleri ve karşılaştırma tablosu",
    "test stratejisi ve kabul ölçütleri",
    "olay müdahale kılavuzu",
    "aşamalı geçiş ve geri dönüş planı",
    "ölçüm planı ve gösterge sözlüğü",
    "risk kaydı ve azaltma eylemleri",
)

RISKS = (
    "sessiz veri kaybı",
    "yetki sınırının aşılması",
    "geri dönüşü zor sözleşme değişikliği",
    "yük altında kuyruk birikmesi",
    "ölçümlerin yanlış başarı sinyali üretmesi",
    "operasyon bilgisinin tek kişide kalması",
    "tedarikçi bağımlılığının kritik yolu kilitlemesi",
    "istisna akışlarının normal akışı bozması",
)

METHODS = (
    "önce varsayımları görünür kıl",
    "sistemi sınırlar ve veri akışları üzerinden modelle",
    "başarıyı ölçülebilir sonuçlarla tanımla",
    "en pahalı belirsizliği küçük bir deneyle azalt",
    "normal akış kadar hata ve geri alma yolunu da tasarla",
    "kararları sahip, tarih ve kanıtla kayda geçir",
    "gözlemlenebilirliği uygulamanın parçası olarak ele al",
    "teslimatı bağımsız doğrulanabilen dilimlere ayır",
)

REVIEW_LENSES = (
    "doğruluk ve kapsam",
    "güvenlik ve gizlilik",
    "işletilebilirlik",
    "performans ve kapasite",
    "bakım maliyeti",
    "kullanıcı etkisi",
    "geri döndürülebilirlik",
    "kanıtlanabilirlik",
)


@dataclass(frozen=True)
class LibraryFile:
    relative_path: str
    size: int
    sha256: str


def mixed_number(seed: int, salt: int) -> int:
    payload = f"{seed}:{salt}:clarify-prompt-library".encode()
    return int.from_bytes(hashlib.blake2s(payload, digest_size=8).digest(), "big")


def choose(values: tuple, seed: int, salt: int = 1):
    return values[mixed_number(seed, salt) % len(values)]


def domain_for(index: int) -> tuple[str, str, str]:
    return DOMAINS[index % len(DOMAINS)]


def render_entry(file_index: int, entry_index: int) -> str:
    seed = file_index * 100_003 + entry_index
    slug, title, purpose = domain_for(file_index)
    scenario = choose(SCENARIOS, seed, 5)
    audience = choose(AUDIENCES, seed + 3, 3)
    scale = choose(SCALES, seed + 7, 5)
    constraint_a = choose(CONSTRAINTS, seed + 11, 3)
    constraint_b = choose(CONSTRAINTS, seed + 17, 5)
    output = choose(OUTPUTS, seed + 19, 7)
    risk_a = choose(RISKS, seed + 23, 3)
    risk_b = choose(RISKS, seed + 29, 5)
    method_a = choose(METHODS, seed + 31, 3)
    method_b = choose(METHODS, seed + 37, 5)
    lens_a = choose(REVIEW_LENSES, seed + 41, 3)
    lens_b = choose(REVIEW_LENSES, seed + 43, 5)
    planning_days = 5 + mixed_number(seed, 47) % 86
    evidence_items = 20 + mixed_number(seed, 53) % 981
    review_hours = 4 + mixed_number(seed, 59) % 165
    error_budget = choose(("0,1", "0,25", "0,5", "1", "2"), seed + 61, 7)
    record_id = f"{slug}-{file_index:04d}-{entry_index:04d}"

    return f"""
## {record_id}: {scenario.capitalize()}

- **Alan:** {title}
- **Amaç:** {purpose}
- **Hedef kitle:** {audience}
- **Çalışma ölçeği:** {scale}
- **Beklenen çıktı:** {output}

### Ham istek

> {title} alanında {scenario} için ayrıntılı bir çözüm hazırla. Hızlı uygulanabilsin,
> mevcut sistemi bozmasın ve ekip tarafından sürdürülebilsin.

### Netleştirilmiş prompt

{title} konusunda deneyimli bir uzman gibi çalış. Görevin, **{scenario}** ihtiyacı için
{audience} tarafından doğrudan kullanılabilecek bir **{output}** hazırlamak.

Bağlam:

- Çözümün ana amacı: {purpose}.
- Sistem veya süreç ölçeği: {scale}.
- Birincil kısıt: {constraint_a}.
- İkincil kısıt: {constraint_b}.
- Özellikle yönetilecek riskler: {risk_a} ve {risk_b}.
- Planlama ufku: {planning_days} gün; ilk karar gözden geçirmesi en geç {review_hours} saat içinde.
- Kanıt tabanı: en az {evidence_items} gözlem; kabul edilen ölçüm hata bütçesi yüzde {error_budget}.
- Eksik bilgi varsa tahminini gerçek gibi sunma; varsayımı, etkisini ve doğrulama yolunu yaz.

Çalışma yöntemi:

1. İsteği amaç, kapsam, kapsam dışı alanlar ve başarı ölçütleri olarak yeniden ifade et.
2. Bilinmeyenleri karar üzerindeki etkilerine göre kritik, önemli ve düşük etkili diye ayır.
3. Önce "{method_a}", ardından "{method_b}" ilkesini uygula.
4. En az üç çözüm seçeneği üret; uygulanabilirlik, maliyet, risk ve geri alınabilirlik
   bakımından karşılaştır.
5. Önerilen seçeneğin bileşenlerini, bağımlılıklarını, veri akışını ve sahiplik sınırlarını
   açıkça göster.
6. Normal akışın yanında zaman aşımı, kısmi başarısızlık, yinelenen istek, bozuk veri,
   yetkisiz erişim ve bağımlılık kesintisi senaryolarını işle.
7. Uygulamayı küçük, bağımsız doğrulanabilir aşamalara böl. Her aşamaya giriş koşulu,
   çıkış ölçütü, sorumlu rol ve geri dönüş tetikleyicisi ekle.
8. Sonucun nasıl ölçüleceğini başlangıç değeri, hedef, ölçüm aralığı ve veri sahibiyle tanımla.

Zorunlu sınırlar:

- Genel tavsiyelerle yetinme; her öneriyi bu bağlama ve ölçeğe bağla.
- Doğrulanmamış ürün, mevzuat, performans veya maliyet iddiası üretme.
- Güvenlik, gizlilik ve erişilebilirliği sonradan eklenecek işler gibi ele alma.
- Geri dönüş planı olmayan yıkıcı değişiklik önerme.
- Örnekte gizli anahtar, gerçek kişisel veri veya üretim kimliği kullanma.
- Belirsiz fiiller yerine gözlenebilir sonuçlar yaz: "iyileştir" yerine ölçü ve hedef belirt.

### Çıktı sözleşmesi

Yanıtı aşağıdaki sırayla ver:

1. **Yönetici özeti:** Sorun, öneri, beklenen sonuç ve en önemli ödünleşim.
2. **Varsayımlar ve açık sorular:** Her maddenin karar üzerindeki etkisi ve doğrulama yöntemi.
3. **Mevcut durum modeli:** Aktörler, sınırlar, veri veya iş akışı ve bilinen darboğazlar.
4. **Seçenek analizi:** En az üç seçenek; yarar, maliyet, risk, bağımlılık ve vazgeçme koşulu.
5. **Önerilen tasarım:** Bileşenler, sözleşmeler, hata davranışı, sahiplik ve güvenlik kontrolleri.
6. **Uygulama planı:** Sıralı aşamalar, teslimatlar, doğrulama adımları ve geri dönüş noktaları.
7. **Test ve ölçüm planı:** Fonksiyonel, olumsuz, yük, güvenlik ve operasyon senaryoları.
8. **Risk kaydı:** Olasılık, etki, erken sinyal, azaltma eylemi ve sorumlu rol.
9. **Bitti tanımı:** Başarıyı tartışmasız gösterecek somut kabul ölçütleri.

### Kabul ölçütleri

- Kapsam ve kapsam dışı alanlar birbirine karışmayacak kadar nettir.
- Her kritik varsayımın sahibi ve doğrulama tarihi vardır.
- Öneri, {constraint_a} ve {constraint_b} koşullarını nasıl karşıladığını gösterir.
- {risk_a} ile {risk_b} için önleyici kontrol, tespit sinyali ve müdahale adımı bulunur.
- Planın her aşaması bağımsız test edilebilir ve geri alınabilir.
- Ölçüler karar vermeye yarar; yalnızca kolay toplanabildiği için seçilmiş gösterge yoktur.
- Okuyucu, ek açıklama beklemeden ilk uygulama adımını başlatabilir.

### Eleştirel inceleme

Son taslağı teslim etmeden önce iki ayrı bakışla denetle:

- **{lens_a.capitalize()}:** Kanıtsız iddia, atlanan sınır, çelişki ve ölçülemeyen hedefleri bul.
- **{lens_b.capitalize()}:** İşletme yükünü, hata anındaki davranışı ve uzun vadeli sahipliği sorgula.

Bulduğun sorunları sessizce düzelt. Çözülemeyen belirsizlikleri "Açık kararlar" bölümünde,
hangi bilginin kimden ve ne zamana kadar alınması gerektiğiyle birlikte bırak.

"""


def render_file_header(file_index: int, target_size: int) -> bytes:
    slug, title, purpose = domain_for(file_index)
    text = f"""# {title} Prompt Kayıtları — Cilt {file_index + 1:04d}

{FILE_SIGNATURE}

Bu cilt, {purpose} için yapılandırılmış prompt örnekleri içerir. Kayıtlar deterministik
olarak üretilmiştir; her biri bağlam, kısıt, hata yolu, çıktı sözleşmesi ve kabul ölçütü taşır.

- Alan kodu: `{slug}`
- Cilt sıra numarası: `{file_index + 1}`
- Asgari cilt boyutu: `{target_size}` bayt
- Üretici sürümü: `{GENERATOR_VERSION}`

---
"""
    return text.encode("utf-8")


def hash_file(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as source:
        for block in iter(lambda: source.read(4 * MIB), b""):
            size += len(block)
            digest.update(block)
    return size, digest.hexdigest()


def write_volume(path: Path, file_index: int, target_size: int) -> LibraryFile:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".partial")
    digest = hashlib.sha256()
    written = 0

    try:
        with partial.open("wb") as target:
            header = render_file_header(file_index, target_size)
            target.write(header)
            digest.update(header)
            written += len(header)

            entry_index = 0
            while written < target_size:
                entry = render_entry(file_index, entry_index).encode("utf-8")
                target.write(entry)
                digest.update(entry)
                written += len(entry)
                entry_index += 1

            target.flush()
            os.fsync(target.fileno())

        partial.replace(path)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise

    return LibraryFile(
        relative_path=path.as_posix(),
        size=written,
        sha256=digest.hexdigest(),
    )


def volume_path(output: Path, file_index: int) -> Path:
    slug, _, _ = domain_for(file_index)
    return output / slug / f"{slug}-{file_index + 1:04d}.md"


def inspect_existing(path: Path, output_parent: Path) -> LibraryFile:
    with path.open("rb") as source:
        opening = source.read(4096).decode("utf-8", errors="replace")
    if FILE_SIGNATURE not in opening:
        raise RuntimeError(f"Mevcut dosya bu üreticiye ait değil; üzerine yazılmadı: {path}")
    size, sha256 = hash_file(path)
    return LibraryFile(path.relative_to(output_parent).as_posix(), size, sha256)


def normalize_records(records: Iterable[LibraryFile], base: Path) -> list[LibraryFile]:
    normalized = []
    for record in records:
        path = Path(record.relative_path)
        relative = path.relative_to(base).as_posix() if path.is_absolute() else path.as_posix()
        normalized.append(LibraryFile(relative, record.size, record.sha256))
    return sorted(normalized, key=lambda item: item.relative_path)


def write_manifest(
    manifest: Path,
    records: list[LibraryFile],
    target_bytes: int,
    output: Path,
) -> None:
    manifest.parent.mkdir(parents=True, exist_ok=True)
    total_bytes = sum(record.size for record in records)
    relative_output = os.path.relpath(output, manifest.parent).replace("\\", "/")
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    lines = [
        "# Clarify Prompt Markdown Kütüphanesi Manifesti",
        "",
        "Bu dosya `tools/markdown_library.py` tarafından üretilir. Boyut ve özet değerleri",
        "kütüphane doğrulamasında kaynak olarak kullanılır.",
        "",
        f"- Üretici sürümü: `{GENERATOR_VERSION}`",
        f"- Üretim zamanı (UTC): `{generated_at}`",
        f"- Corpus yolu: `{relative_output}`",
        f"- Hedef boyut: `{target_bytes}` bayt",
        f"- Gerçek boyut: `{total_bytes}` bayt",
        f"- Dosya sayısı: `{len(records)}`",
        "- Özet algoritması: `SHA-256`",
        "",
        "| Dosya | Bayt | SHA-256 |",
        "|---|---:|---|",
    ]
    lines.extend(
        f"| `{record.relative_path}` | {record.size} | `{record.sha256}` |" for record in records
    )
    lines.append("")

    partial = manifest.with_suffix(manifest.suffix + ".partial")
    partial.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    partial.replace(manifest)


def read_manifest(manifest: Path) -> tuple[dict[str, LibraryFile], int, int]:
    records: dict[str, LibraryFile] = {}
    target_bytes = -1
    declared_total = -1
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if line.startswith("- Hedef boyut: `"):
            target_bytes = int(line.split("`")[1].split()[0])
        elif line.startswith("- Gerçek boyut: `"):
            declared_total = int(line.split("`")[1].split()[0])
        else:
            match = MANIFEST_ROW.match(line)
            if match:
                record = LibraryFile(
                    match.group("path"),
                    int(match.group("size")),
                    match.group("sha"),
                )
                records[record.relative_path] = record
    if target_bytes < 0 or declared_total < 0 or not records:
        raise RuntimeError(f"Manifest eksik veya geçersiz: {manifest}")
    return records, target_bytes, declared_total


def build_library(
    output: Path,
    manifest: Path,
    target_bytes: int,
    volume_bytes: int,
    progress_every: int = 32,
    rebuild: bool = False,
) -> list[LibraryFile]:
    if target_bytes <= 0:
        raise ValueError("Hedef boyut sıfırdan büyük olmalı.")
    if volume_bytes <= 0:
        raise ValueError("Cilt boyutu sıfırdan büyük olmalı.")

    output = output.resolve()
    manifest = manifest.resolve()
    output.mkdir(parents=True, exist_ok=True)
    volume_count = math.ceil(target_bytes / volume_bytes)
    records: list[LibraryFile] = []

    for file_index in range(volume_count):
        path = volume_path(output, file_index)
        if path.exists():
            existing = inspect_existing(path, output.parent)
            if rebuild:
                created = write_volume(path, file_index, volume_bytes)
                record = LibraryFile(
                    path.relative_to(output.parent).as_posix(),
                    created.size,
                    created.sha256,
                )
            else:
                record = existing
                if record.size < volume_bytes:
                    raise RuntimeError(f"Mevcut cilt beklenenden küçük: {path}")
        else:
            created = write_volume(path, file_index, volume_bytes)
            record = LibraryFile(
                path.relative_to(output.parent).as_posix(),
                created.size,
                created.sha256,
            )
        records.append(record)

        completed = file_index + 1
        if completed % progress_every == 0 or completed == volume_count:
            current_bytes = sum(item.size for item in records)
            print(
                f"[{completed:04d}/{volume_count:04d}] {current_bytes / GIB:.3f} GiB hazır",
                flush=True,
            )

    unexpected = [
        path
        for path in output.rglob("*")
        if path.is_file() and (path.suffix.lower() != ".md" or path.name.endswith(".partial"))
    ]
    if unexpected:
        raise RuntimeError(f"Corpus içinde Markdown dışı dosya bulundu: {unexpected[0]}")

    records = normalize_records(records, output.parent)
    write_manifest(manifest, records, target_bytes, output)
    return records


def verify_library(output: Path, manifest: Path) -> tuple[int, int]:
    output = output.resolve()
    manifest = manifest.resolve()
    expected, target_bytes, declared_total = read_manifest(manifest)
    actual_paths = sorted(path for path in output.rglob("*") if path.is_file())
    if not actual_paths:
        raise RuntimeError(f"Corpus boş: {output}")

    invalid = [
        path
        for path in actual_paths
        if path.suffix.lower() != ".md" or path.name.endswith(".partial")
    ]
    if invalid:
        raise RuntimeError(f"Markdown dışı veya yarım dosya bulundu: {invalid[0]}")

    seen: set[str] = set()
    total_bytes = 0
    for index, path in enumerate(actual_paths, start=1):
        relative = path.relative_to(output.parent).as_posix()
        record = expected.get(relative)
        if record is None:
            raise RuntimeError(f"Manifestte bulunmayan dosya: {relative}")
        size, sha256 = hash_file(path)
        if size != record.size:
            raise RuntimeError(
                f"Boyut uyuşmazlığı: {relative} (manifest={record.size}, gerçek={size})"
            )
        if sha256 != record.sha256:
            raise RuntimeError(f"SHA-256 uyuşmazlığı: {relative}")
        seen.add(relative)
        total_bytes += size
        if index % 64 == 0 or index == len(actual_paths):
            print(f"[doğrulama {index:04d}/{len(actual_paths):04d}]", flush=True)

    missing = sorted(set(expected) - seen)
    if missing:
        raise RuntimeError(f"Corpus içinde bulunmayan manifest kaydı: {missing[0]}")
    if total_bytes != declared_total:
        raise RuntimeError(
            f"Toplam boyut manifestle uyuşmuyor: manifest={declared_total}, gerçek={total_bytes}"
        )
    if total_bytes < target_bytes:
        raise RuntimeError(f"Corpus hedefin altında: {total_bytes} < {target_bytes}")
    return len(actual_paths), total_bytes


def parse_size(value: str) -> int:
    normalized = value.strip().lower().replace("_", "")
    units = {
        "gib": GIB,
        "gb": 1000**3,
        "mib": MIB,
        "mb": 1000**2,
        "kib": 1024,
        "kb": 1000,
        "b": 1,
    }
    for suffix in sorted(units, key=len, reverse=True):
        if normalized.endswith(suffix):
            number = normalized[: -len(suffix)].strip()
            return int(float(number) * units[suffix])
    return int(normalized)


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parser() -> argparse.ArgumentParser:
    root = project_root()
    cli = argparse.ArgumentParser(
        description="Deterministik Clarify Prompt Markdown kütüphanesini üretir ve doğrular."
    )
    cli.add_argument(
        "--output",
        type=Path,
        default=root / "library" / "corpus-1gib",
        help="Corpus dizini.",
    )
    cli.add_argument(
        "--manifest",
        type=Path,
        default=root / "library" / "MANIFEST.md",
        help="Markdown manifest dosyası.",
    )
    subcommands = cli.add_subparsers(dest="command", required=True)

    build = subcommands.add_parser("build", help="Corpus'u oluşturur veya eksik ciltleri tamamlar.")
    build.add_argument("--target", type=parse_size, default=GIB, help="Toplam asgari boyut.")
    build.add_argument(
        "--volume-size", type=parse_size, default=MIB, help="Cilt başına asgari boyut."
    )
    build.add_argument("--progress-every", type=int, default=32)
    build.add_argument(
        "--rebuild",
        action="store_true",
        help="Üretici imzalı mevcut ciltleri atomik olarak yeniden oluşturur.",
    )

    subcommands.add_parser("verify", help="Manifest, boyut ve SHA-256 değerlerini doğrular.")
    return cli


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "build":
            records = build_library(
                args.output,
                args.manifest,
                args.target,
                args.volume_size,
                args.progress_every,
                args.rebuild,
            )
            total = sum(record.size for record in records)
            print(f"Tamamlandı: {len(records)} dosya, {total} bayt ({total / GIB:.3f} GiB)")
        else:
            count, total = verify_library(args.output, args.manifest)
            print(f"Doğrulandı: {count} dosya, {total} bayt ({total / GIB:.3f} GiB)")
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Hata: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
