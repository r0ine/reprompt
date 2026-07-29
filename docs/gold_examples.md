# Altın örnekler

Test setinin çekirdeği. Elle yazılmış, Kemal onaylı `(ham prompt, optimize prompt)`
çiftleri. `training/data/import_gold.py` bu dosyayı okuyup JSONL'e çevirir.

Her örnek şu formatta:

    ### gold_XXX | target: <hedef> | lang: <tr|en>
    **Input:**
    ```
    ham istek metni
    ```
    **Output:**
    ```
    yapılandırılmış çıktı prompt'u
    ```

`XXX` sıralı üç haneli sayı. Geçerli `hedef` değerleri
`src/clarify_prompt/prompts/types.py` içindeki `TARGET_PROFILES` sabitinden alınır.

---

### gold_001 | target: claude-code | lang: tr
**Input:**
```
reflection code'unu yeni versiyona uydur, hata veriyor
```
**Output:**
```
<task>
Reflection kodunu yeni Java sürümüne uyarla — mevcut kod derlemede uyarı veya hata veriyor.
</task>

<context>
- Etkilenen dosya(lar): src/main/java/... alt yolunu ver.
- Hedef Java sürümü: JDK 21.
- Compiler output (hata mesajı) verildiyse yorumla; verilmediyse mvn -q -DskipTests package çıktısını iste.
</context>

<constraints>
- Kullanılmayan importları temizle.
- Test varsa geçsin; yoksa değiştirdiğin sınıfa smoke test ekle.
</constraints>

<acceptance>
- mvn -q -DskipTests package başarıyla derlensin.
- Uyarı bırakma.
</acceptance>

<output_format>
- Değiştirdiğin dosyaların diff'i.
- Kısa "değişiklik özeti" (3-5 madde).
</output_format>
```

---

### gold_002 | target: chatgpt | lang: en
**Input:**
```
write a blog post about SEO
```
**Output:**
```
## Goal
Write a 800-1200 word blog post about modern SEO best practices for 2026, aimed at small-business owners with no technical background.

## Context
- Audience: solo entrepreneurs and small e-commerce owners.
- Tone: friendly, direct, no jargon.
- The post will be published on the company blog and shared on LinkedIn.

## Constraints
- No AI-slop tropes ("in today's fast-paced digital landscape").
- Include one concrete example per section.
- Cite at least three credible sources (Google Search Central, Ahrefs blog, Search Engine Journal).

## Acceptance criteria
1. Word count between 800 and 1200.
2. At least four distinct actionable tips.
3. Uses ## and ### Markdown headings.
4. Ends with a 2-line conclusion + soft CTA.

## Output format
- Full Markdown post.
- Frontmatter block: title, description, tags.
- Reply in English.
```

---

### gold_003 | target: cursor | lang: tr
**Input:**
```
bu componenti temizle
```
**Output:**
```
Refactor the selected React component:

1. Extract inline event handlers into memoized useCallback hooks.
2. Split JSX blocks longer than 20 lines into subcomponents in the same file.
3. Replace any remaining class-based state with hooks.
4. Remove unused imports.
5. Preserve the component's public API — props, exports, and CSS class names.

Do not: touch tests, rename exports, add prop types, or change the module's default export.
```

---

### gold_004 | target: claude-code | lang: en
**Input:**
```
add dark mode to the settings page
```
**Output:**
```
<task>
Add a dark mode toggle to the settings page that persists the user's preference.
</task>

<context>
- Settings page location: likely src/pages/Settings or src/components/Settings.
- Current theming approach: check if a ThemeProvider, CSS variables, or Tailwind dark: prefix is already in use.
- Persistence: localStorage or user profile API — match whatever the app already uses for preferences.
</context>

<constraints>
- Reuse existing design tokens / CSS variables — do not introduce a parallel color system.
- The toggle must be accessible: proper aria-label, keyboard operable, visible focus ring.
- Respect prefers-color-scheme as the initial default when no saved preference exists.
</constraints>

<acceptance>
- Toggling dark mode changes the entire app, not just the settings page.
- Refreshing the page preserves the chosen theme.
- No flash of wrong theme on page load.
- Existing tests still pass.
</acceptance>

<output_format>
- Changed files with diffs.
- One-paragraph summary of the approach.
</output_format>
```

---

### gold_005 | target: chatgpt | lang: tr
**Input:**
```
bana bi kapak yazısı yaz linkedin için
```
**Output:**
```
## Hedef
LinkedIn profili için kısa, dikkat çekici ve profesyonel bir kapak yazısı (headline + about bölümü) yaz.

## Bağlam
- Kimin için: yazılım geliştirici (tam profil bilgisi verilmediyse genel bir backend/fullstack profili varsay).
- Ton: profesyonel ama samimi, klişelerden uzak ("passionate", "results-driven" gibi boş sıfatlar yasak).
- Dil: Türkçe.

## Kısıtlar
- Headline en fazla 120 karakter.
- About bölümü 3-5 paragraf, toplam 150-300 kelime.
- Her paragrafta somut bir beceri veya başarı örneği olsun.
- Emoji kullanma.

## Kabul kriterleri
1. LinkedIn karakter limitlerini aşmıyor.
2. Okunduğunda kişinin ne yaptığı ve neden iyi olduğu 10 saniyede anlaşılıyor.
3. Üçüncü tekil şahıs değil, birinci tekil şahıs ile yazılmış.

## Çıktı formatı
- Önce headline ayrı satırda.
- Sonra about bölümü paragraflar halinde.
```

---

### gold_006 | target: cursor | lang: en
**Input:**
```
this API endpoint is slow fix it
```
**Output:**
```
Diagnose and fix the performance bottleneck in the selected API endpoint:

1. Add timing logs at each major step (DB query, serialization, external call) to identify the slow segment.
2. If the bottleneck is a DB query: add missing indexes, reduce N+1 with eager loading, or paginate.
3. If the bottleneck is serialization: switch to a faster serializer or reduce the response payload.
4. If the bottleneck is an external call: add caching with a TTL or move to background processing.
5. After the fix, measure again — target < 200ms p95 for a typical request.

Do not: change the endpoint's public contract (URL, params, response shape), add new dependencies without justification, or remove existing validation.
```

---

### gold_007 | target: generic | lang: tr
**Input:**
```
websocket bağlantısı sürekli kopuyor neden olabilir
```
**Output:**
```
## Hedef
WebSocket bağlantısının sürekli kopma nedenini tespit et ve kalıcı çözüm öner.

## Bağlam
- Hangi WebSocket kütüphanesi/framework kullanılıyor (ws, Socket.IO, native WebSocket API)?
- Sunucu tarafı dili ve ortamı (Node.js, Python, Go, vb.).
- Kopma sıklığı ve koşulları: belirli bir süre sonra mı, yük altında mı, belirli bir event sonrası mı?
- Ağ ortamı: doğrudan bağlantı mı, reverse proxy (Nginx, Cloudflare) arkasında mı?

## Olası nedenler ve kontrol listesi
1. Proxy/load balancer timeout — Nginx proxy_read_timeout varsayılanı 60s; idle bağlantıları kapatır.
2. Heartbeat/ping eksikliği — sunucu veya client ping frame göndermiyorsa proxy idle sayar.
3. Sunucu bellek sızıntısı — bağlantı sayısı arttıkça OOM killer devreye giriyor olabilir.
4. Client tarafı ağ değişimi — mobilde WiFi/4G geçişleri bağlantıyı koparır.
5. SSL/TLS handshake hatası — sertifika yenileme sonrası mevcut bağlantılar düşebilir.

## Beklenen çıktı
- Kök neden tespiti (loglardan veya reproducing adımlarıyla).
- Çözüm: kod değişikliği, config ayarı veya mimari öneri.
- Reconnect stratejisi önerisi (exponential backoff + jitter).
```

---

### gold_008 | target: claude-code | lang: tr
**Input:**
```
discord botuna müzik çalma özelliği ekle
```
**Output:**
```
<task>
Mevcut Discord botuna sesli kanala bağlanıp YouTube/URL'den müzik çalma özelliği ekle.
</task>

<context>
- Bot framework: discord.js mi, discord.py mi? package.json veya requirements.txt kontrol et.
- Mevcut komut yapısı: slash command mı, prefix command mı?
- Ses kütüphanesi: @discordjs/voice veya discord.py[voice] kurulu mu?
- ffmpeg sisteme kurulu mu? (ses dönüştürme için zorunlu.)
</context>

<constraints>
- YouTube'dan ses çekmek için yt-dlp kullan (youtube-dl deprecated).
- Kuyruk sistemi olsun: /play eklerken sıradaki şarkıya geç, /skip, /stop, /queue komutları.
- Bot sesli kanalda 5 dakika yalnız kalırsa otomatik çıksın.
- Hata durumlarını kullanıcıya embed ile bildir (kırmızı embed + hata açıklaması).
</constraints>

<acceptance>
- /play <url> ile bot sesli kanala gelip müzik çalıyor.
- /skip sonraki şarkıya geçiyor.
- /queue sırayı gösteriyor.
- /stop müziği durdurup kanaldan çıkıyor.
- Geçersiz URL verildiğinde crash yok, hata mesajı var.
</acceptance>

<output_format>
- Yeni/değişen dosyaların tam içeriği.
- Gerekli npm/pip paketleri listesi.
- ffmpeg kurulum notu (gerekiyorsa).
</output_format>
```

---

### gold_009 | target: chatgpt | lang: en
**Input:**
```
explain kubernetes to me
```
**Output:**
```
## Goal
Write a clear, layered explanation of Kubernetes — what it is, why it exists, and how its core components work together.

## Context
- Audience: a developer who knows Docker containers but has never used Kubernetes.
- Start from the problem Kubernetes solves (orchestrating many containers across machines), then build up.
- Avoid dumping the full API surface; focus on the 5-6 concepts someone needs to deploy their first app.

## Constraints
- Use a concrete running example: deploying a simple web app with a database.
- No "Kubernetes is like an orchestra conductor" analogies — explain the actual mechanism.
- Define each term (Pod, Deployment, Service, Namespace, ConfigMap) when first introduced, in one sentence.
- Keep total length under 1500 words.

## Acceptance criteria
1. A reader who finishes this can write a basic Deployment + Service YAML from scratch.
2. The explanation covers: why not just Docker Compose, Pods, Deployments, Services, kubectl basics.
3. Includes one minimal YAML example (Deployment or Service).

## Output format
- Markdown with ## section headings.
- One YAML code block.
- No bullet-point walls — use short paragraphs.
```

---

### gold_010 | target: cursor | lang: tr
**Input:**
```
typescript hatalarını düzelt
```
**Output:**
```
Fix all TypeScript compiler errors in the current file:

1. Run tsc --noEmit on this file to get the full error list.
2. Fix type mismatches: add proper type annotations, use type guards, or adjust generics.
3. Replace any as casts with proper narrowing unless the cast is genuinely necessary.
4. Add missing null/undefined checks where strictNullChecks flags them.
5. If a third-party type definition is wrong or missing, install @types/... or add a minimal .d.ts declaration.

Do not: suppress errors with @ts-ignore or any, change tsconfig.json strictness settings, or refactor unrelated code.
```

---

### gold_011 | target: generic | lang: en
**Input:**
```
how to set up CI/CD for my project
```
**Output:**
```
## Goal
Design and implement a CI/CD pipeline for the project that automates testing, building, and deploying on every push.

## Context
- What platform is the code hosted on? (GitHub, GitLab, Bitbucket — determines the CI tool: Actions, GitLab CI, Pipelines.)
- What language/framework? (Determines build and test commands.)
- Where does the app deploy? (Vercel, AWS, Docker registry, bare server via SSH.)
- Is there an existing pipeline? If so, what's broken or missing?

## Pipeline stages
1. **Lint** — run the project's linter (eslint, ruff, clippy, etc.) and fail on errors.
2. **Test** — run the full test suite; report coverage if a coverage tool is configured.
3. **Build** — compile/bundle the project; cache dependencies across runs.
4. **Deploy** (main branch only) — push to the target environment; use environment secrets, never hardcode credentials.

## Acceptance criteria
1. Pipeline triggers on push to any branch and on pull request.
2. Deployment only happens on merge to main.
3. Total pipeline time under 5 minutes for an average commit.
4. Secrets are stored in the CI platform's secret store, not in the repo.

## Output format
- The CI config file (e.g. .github/workflows/ci.yml) with comments explaining each step.
- A summary of any required secrets to configure in the CI platform's settings.
```

---

### gold_012 | target: claude-code | lang: en
**Input:**
```
write tests for the auth module
```
**Output:**
```
<task>
Write unit and integration tests for the authentication module, covering login, registration, token refresh, and logout flows.
</task>

<context>
- Locate the auth module: likely src/auth/, src/modules/auth/, or app/auth/.
- Identify the test framework already in use (Jest, Vitest, pytest, JUnit) — match it.
- Check if a test database or mock setup already exists in the project.
- List the public functions/endpoints the auth module exposes.
</context>

<constraints>
- Test real behavior, not implementation details — call the public API, assert on outputs.
- Cover both happy paths and error paths: invalid credentials, expired tokens, duplicate registration, missing fields.
- Use fixtures or factories for test users — do not hardcode credentials.
- Each test must be independent and idempotent (no test-order dependency).
</constraints>

<acceptance>
- All new tests pass: npm test / pytest / mvn test.
- Coverage of the auth module increases by at least 30 percentage points (measure with coverage tool).
- No existing tests break.
- Edge cases covered: empty password, SQL injection attempt in username, expired JWT, revoked refresh token.
</acceptance>

<output_format>
- New test files with full content.
- A one-line command to run only the auth tests.
- Coverage report snippet showing before/after.
</output_format>
```

---

### gold_013 | target: chatgpt | lang: tr
**Input:**
```
python ile veri analizi yap
```
**Output:**
```
## Hedef
Verilen veri seti üzerinde keşifsel veri analizi (EDA) yap ve bulguları görselleştirmelerle birlikte sun.

## Bağlam
- Veri seti formatı: CSV mi, Excel mi, veritabanı sorgusu mu? Dosya yolu veya örnek veri verilmeli.
- Veri konusu bilinmiyorsa varsayım: satış verisi (tarih, ürün, miktar, gelir, bölge).
- Araçlar: pandas, matplotlib/seaborn, Jupyter notebook.

## Kısıtlar
- Veriyi okumadan önce ilk 5 satırı ve dtypes/shape bilgisini göster.
- Eksik veri analizi yap: yüzde ve dağılım. Silme/doldurma kararını gerekçelendir.
- En az 4 farklı görselleştirme: histogram, scatter, bar chart, heatmap (korelasyon).
- Her grafikte başlık, eksen etiketi ve legend olsun.
- Kod her hücrede çalıştırılabilir olsun — ara bağımlılık veya tanımsız değişken yok.

## Kabul kriterleri
1. Veri setinin özet istatistikleri (describe) paylaşılmış.
2. En az 3 somut bulgu cümleyle ifade edilmiş ("X ile Y arasında 0.82 korelasyon var").
3. Görselleştirmeler inline gösteriliyor (plt.show veya notebook display).
4. Tüm kod tek seferde çalışıyor.

## Çıktı formatı
- Jupyter notebook hücreleri sırayla: import → yükle → keşfet → temizle → görselleştir → sonuç.
- Her bölümün başında markdown hücresiyle kısa açıklama.
```

---

### gold_014 | target: cursor | lang: en
**Input:**
```
add pagination to the list endpoint
```
**Output:**
```
Add cursor-based pagination to the selected list/index API endpoint:

1. Accept optional query params: limit (default 20, max 100) and cursor (opaque string, base64-encoded ID).
2. Return a response envelope: { data: [...], next_cursor: "..." | null, has_more: boolean }.
3. Query the database with WHERE id > decoded_cursor ORDER BY id ASC LIMIT limit+1 to detect has_more.
4. Encode the last item's ID as the next_cursor.
5. Return 400 if limit is out of range or cursor is malformed.
6. Update existing tests or add new ones covering: first page, middle page, last page (has_more=false), invalid cursor.

Do not: use offset-based pagination, change the response shape of individual items, or break existing query filters.
```

---

### gold_015 | target: generic | lang: tr
**Input:**
```
git rebase ile merge arasındaki fark ne
```
**Output:**
```
## Hedef
Git rebase ve merge arasındaki farkı somut örneklerle açıkla; hangi durumda hangisinin tercih edilmesi gerektiğini belirt.

## Bağlam
- Hedef kitle: Git'i temel seviyede bilen, branch ve commit kavramlarını anlayan bir geliştirici.
- Açıklama teorik kalmasın — bir feature branch senaryosu üzerinden göster.

## Beklenen yapı
1. merge ne yapar: iki branch'in tarihçesini birleştirme commit'i ile birleştirir; tarihçe korunur ama dallanır.
2. rebase ne yapar: feature branch'teki commitleri main'in ucuna yeniden uygular; tarihçe düz kalır ama commit hash'leri değişir.
3. Görsel karşılaştırma: basit ASCII commit grafiği (merge sonrası vs rebase sonrası).
4. Ne zaman merge: paylaşılan branch, tarihçe önemli, conflict riski düşük.
5. Ne zaman rebase: kişisel feature branch, temiz tarihçe isteniyor, henüz push edilmemiş.
6. Altın kural: push edilmiş commit'i rebase etme.

## Kısıtlar
- 500 kelimeyi geçme.
- Jargon kullanırken parantez içinde kısa tanım ver.
- Türkçe yaz.

## Çıktı formatı
- Markdown, ## bölüm başlıkları ile.
- En az bir kod bloğu (git komutları).
- En az bir ASCII diyagram.
```

---

### gold_016 | target: claude-code | lang: tr
**Input:**
```
veritabanı şeması çok karışık, düzenle
```
**Output:**
```
<task>
Veritabanı şemasını normalleştir ve tutarlı bir adlandırma kuralına oturt.
</task>

<context>
- ORM/migration aracı: Prisma, TypeORM, Alembic, Django ORM, Flyway? Migration klasörünü kontrol et.
- Mevcut tablo sayısı ve ilişkileri: şemayı oku veya ER diyagramı çıkar.
- Hangi tablolar sorunlu? Tekrar eden sütunlar, eksik foreign key'ler, tutarsız isimlendirme.
</context>

<constraints>
- Adlandırma: tablo isimleri snake_case çoğul (users, orders), sütunlar snake_case tekil (created_at, user_id).
- Her tabloda: id (PK), created_at, updated_at zorunlu.
- Foreign key'ler ON DELETE CASCADE veya SET NULL — orphan kayıt bırakma.
- Var olan veriyi kaybetme: destructive migration yasak, ALTER ile dönüştür.
- Her migration geri alınabilir olsun (down/rollback tanımlı).
</constraints>

<acceptance>
- Migration'lar sırasıyla çalışıyor: migrate up + migrate down + migrate up sorunsuz.
- Mevcut testler geçiyor.
- Yeni şema ER diyagramı temiz ve okunabilir.
</acceptance>

<output_format>
- Migration dosyalarının tam içeriği.
- Önceki ve sonraki şema karşılaştırması (tablo listesi + sütunlar).
- Kısa açıklama: ne değişti, neden.
</output_format>
```

---

### gold_017 | target: chatgpt | lang: en
**Input:**
```
compare react and vue for my project
```
**Output:**
```
## Goal
Provide a structured comparison of React and Vue.js to help decide which framework fits a specific project better.

## Context
- What kind of project? If unknown, assume: a medium-sized SPA with 10-20 pages, REST API backend, 2-3 developer team.
- Decision factors: learning curve, ecosystem maturity, hiring pool, performance, TypeScript support, community size.
- The comparison should be opinionated — recommend one with clear reasoning, not a "both are great" cop-out.

## Constraints
- No older than 2025 data: compare React 19+ vs Vue 3.5+.
- Include a comparison table with 6-8 dimensions.
- Each dimension gets a one-sentence winner statement.
- Address the specific project type, not abstract "in general" comparisons.
- Total length: 600-900 words.

## Acceptance criteria
1. A clear recommendation with a 2-sentence justification.
2. A comparison table covering: learning curve, TypeScript DX, state management, routing, SSR, testing, bundle size, job market.
3. Mentions at least one gotcha/risk for the recommended option.
4. No filler phrases ("it depends on your needs" without specifying which needs).

## Output format
- Markdown with a comparison table.
- Recommendation section at the end with bold verdict.
```

---

### gold_018 | target: cursor | lang: tr
**Input:**
```
bu dosyadaki console.log'ları temizle
```
**Output:**
```
Remove all debugging artifacts from the current file:

1. Delete every console.log, console.warn, console.debug, and console.info statement.
2. Keep console.error statements — those are intentional error reporting.
3. Remove any debugger statements.
4. Remove commented-out console.log lines.
5. If removing a console.log leaves an empty block (if/else/try body), add a comment: // no-op.
6. Run the linter after cleanup to verify no issues were introduced.

Do not: remove console.error, modify any logic around the removed statements, or touch other files.
```

---

### gold_019 | target: generic | lang: en
**Input:**
```
make a REST API for a todo app
```
**Output:**
```
## Goal
Build a complete REST API for a to-do list application with CRUD operations, user authentication, and persistent storage.

## Context
- Technology: pick based on the project's existing stack. If greenfield, default to Node.js + Express + SQLite (or PostgreSQL for production).
- Scope: single-user MVP first; multi-user with auth as a follow-up.

## API endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | /todos | Create a new to-do item |
| GET | /todos | List all to-do items (with optional ?status=done filter) |
| GET | /todos/:id | Get a single to-do item |
| PATCH | /todos/:id | Update a to-do (title, description, status) |
| DELETE | /todos/:id | Delete a to-do item |

## Data model
- id: auto-generated UUID or integer PK
- title: string, required, max 200 chars
- description: string, optional, max 2000 chars
- status: enum (pending, in_progress, done), default pending
- created_at: ISO timestamp
- updated_at: ISO timestamp

## Acceptance criteria
1. All 5 endpoints work correctly (test with curl or Postman examples).
2. Input validation: missing title returns 400 with a clear error message.
3. Non-existent ID returns 404.
4. Data persists across server restarts (not in-memory).
5. Response format: { data: {...} } for single items, { data: [...], count: N } for lists.

## Output format
- Full source code, ready to run with npm start or equivalent.
- A README with setup instructions and example curl commands for each endpoint.
```

---

### gold_020 | target: claude-code | lang: en
**Input:**
```
the login page has a bug users cant sign in
```
**Output:**
```
<task>
Diagnose and fix the login bug that prevents users from signing in.
</task>

<context>
- Login page location: search for login, signin, or auth in src/pages/ or src/components/.
- Auth backend: check for auth routes in the API (POST /auth/login, /api/login, etc.).
- Error details: is it a frontend form issue, a network request failure, or a backend rejection? Check browser console and network tab output if available.
</context>

<constraints>
- Reproduce the bug first: identify the exact error message or behavior.
- Fix the root cause, not the symptom — if the form submits but the API returns 401, the bug is in the backend, not the form.
- Do not change the auth flow (OAuth, JWT, session) — only fix what's broken.
- If credentials are involved in test fixtures, use obviously fake values.
</constraints>

<acceptance>
- A user can sign in with valid credentials and reach the dashboard/home page.
- Invalid credentials show a clear error message (not a crash or blank screen).
- The fix does not break registration, logout, or password reset flows.
- Existing auth tests pass; add a regression test for the specific bug.
</acceptance>

<output_format>
- Root cause explanation (one paragraph).
- Changed files with diffs.
- Steps to reproduce and verify the fix.
</output_format>
```

---

### gold_021 | target: chatgpt | lang: tr
**Input:**
```
bana bir iş mektubu yaz
```
**Output:**
```
## Hedef
Profesyonel bir iş mektubu taslağı hazırla.

## Bağlam
- Mektubun türü belirtilmedi — en yaygın senaryo: iş başvurusu ön yazısı (cover letter) varsay.
- Gönderen: yazılım geliştirici profili (farklıysa belirt).
- Alıcı: insan kaynakları veya işe alım yöneticisi.
- Dil: Türkçe.

## Kısıtlar
- Uzunluk: tek sayfa, 250-400 kelime.
- Yapı: (1) açılış — hangi pozisyona başvurduğu ve nasıl duyduğu, (2) orta — 2-3 somut başarı/deneyim, (3) kapanış — görüşme talebi ve iletişim bilgisi.
- "Saygılarımla" ile bitir, imza bloğu ekle.
- Klişe cümle yasak: "Ekibinizin bir parçası olmaktan mutluluk duyarım" gibi boş kalıplar yerine somut bir motivasyon cümlesi yaz.
- Yazım hatası ve dilbilgisi hatası olmasın.

## Kabul kriterleri
1. Mektup okunduğunda kişinin ne iş yaptığı ve neden o pozisyona uygun olduğu anlaşılıyor.
2. Tone: özgüvenli ama kibirli değil.
3. Kelime sayısı 250-400 arasında.

## Çıktı formatı
- Düz metin, paragraflar halinde.
- Başlıkta tarih + alıcı bilgisi.
- Sonunda imza bloğu (ad, telefon, e-posta placeholder).
```

---

### gold_022 | target: cursor | lang: en
**Input:**
```
convert this to typescript
```
**Output:**
```
Convert the selected JavaScript file to TypeScript:

1. Rename the file from .js/.jsx to .ts/.tsx.
2. Add explicit type annotations to all function parameters and return types.
3. Define interfaces for object shapes used more than once (props, API responses, state).
4. Replace PropTypes with TypeScript interface + generics.
5. Type event handlers (React.ChangeEvent<HTMLInputElement>, React.FormEvent, etc.).
6. Fix any resulting compiler errors — run tsc --noEmit to verify zero errors.

Do not: use any or as unknown unless truly unavoidable (document why in a comment), change runtime behavior, or modify the component's public API.
```

---

### gold_023 | target: generic | lang: tr
**Input:**
```
docker compose ile proje ayağa kaldır
```
**Output:**
```
## Hedef
Projeyi Docker Compose ile tek komutla ayağa kalkacak şekilde yapılandır.

## Bağlam
- Projenin yapısı: web uygulaması + veritabanı + (opsiyonel) cache/queue servisi.
- Mevcut Dockerfile var mı? Yoksa yazılacak.
- Hangi veritabanı: PostgreSQL, MySQL, MongoDB? Proje bağımlılıklarından tespit et.
- Hangi port'larda yayın yapılacak?

## Beklenen compose.yaml yapısı
1. **app** servisi: proje kodunu build eder, hot-reload için volume mount, .env'den environment variables.
2. **db** servisi: resmi veritabanı image'ı, named volume ile kalıcı veri, healthcheck tanımlı.
3. **redis** (gerekiyorsa): cache veya queue için, alpine image.
4. depends_on ile başlatma sırası: db → app.

## Kısıtlar
- Compose dosyası v3.8+ syntax kullanmalı.
- Secret bilgiler compose dosyasına gömülmemeli — .env dosyasından okusun.
- Tüm servisler tek bir bridge network'te.
- Veritabanı verisi container silinince kaybolmamalı (named volume zorunlu).

## Kabul kriterleri
1. docker compose up -d ile tüm servisler ayağa kalkıyor.
2. Uygulama localhost:3000 (veya ilgili port) üzerinden erişilebilir.
3. docker compose down && docker compose up -d sonrası veritabanı verisi korunuyor.
4. docker compose logs ile tüm servislerin logları okunabiliyor.

## Çıktı formatı
- compose.yaml dosyasının tam içeriği.
- Dockerfile (yoksa yeni, varsa güncellenmiş).
- .env.example dosyası.
- Kullanım: kurulum + başlatma + durdurma komutları.
```

---

### gold_024 | target: claude-code | lang: tr
**Input:**
```
api rate limiting ekle
```
**Output:**
```
<task>
API'ye rate limiting ekle — kötüye kullanımı önlemek için istek sayısını sınırla.
</task>

<context>
- Backend framework: Express, Fastify, Django, FastAPI, Spring? Proje dosyalarından tespit et.
- Mevcut middleware zinciri: auth, CORS, body parser — rate limiter bunların arasına girecek.
- Deployment: tek sunucu mu, çoklu instance mı? Çoklu ise Redis tabanlı store gerekir.
</context>

<constraints>
- Varsayılan limit: IP başına 100 istek / 15 dakika pencere.
- Auth gerektiren endpoint'lerde user ID bazlı limit (IP değil).
- Rate limit aşılınca: 429 Too Many Requests + Retry-After header + JSON hata body.
- Login/register endpoint'leri için daha sıkı limit: 10 istek / 15 dakika (brute force koruması).
- Mevcut testler kırılmasın.
</constraints>

<acceptance>
- Aynı IP'den 101. istek 429 dönüyor.
- Login endpoint'ine 11. istek 429 dönüyor.
- Retry-After header doğru süreyi gösteriyor.
- Rate limit penceresi geçtikten sonra istekler tekrar kabul ediliyor.
- Birim testi: limit aşımı senaryosu test ediliyor.
</acceptance>

<output_format>
- Yeni/değişen dosyalar.
- Kullanılan rate limit kütüphanesi ve neden seçildiği (1 cümle).
- Test komutu.
</output_format>
```

---

### gold_025 | target: chatgpt | lang: en
**Input:**
```
write me a cover letter
```
**Output:**
```
## Goal
Draft a professional, concise cover letter tailored to a specific job application.

## Context
- Role: if not specified, assume a mid-level software engineer position.
- Company: if not specified, leave [Company Name] as a placeholder.
- Applicant profile: generalize as a developer with 3-5 years of experience (customize if more info is given).

## Constraints
- Length: 250-350 words, one page max.
- Structure: (1) Opening — role applied for, how you found it, one hook sentence. (2) Body — 2-3 concrete achievements with metrics where possible. (3) Closing — call to action for an interview, contact info.
- Tone: confident but not arrogant; specific, not generic.
- No cliches: "passionate team player", "results-driven individual", "excited to leverage my skills" are banned.
- No lies or fabricated metrics — use plausible placeholder brackets [X users, Y% improvement] if real numbers are unknown.

## Acceptance criteria
1. The letter clearly states what role and why this person is a strong fit.
2. At least two quantified achievements.
3. Reads naturally — not obviously AI-generated.
4. Fits on one page when pasted into a standard document.

## Output format
- Plain text, paragraph format.
- Date + recipient header block at top.
- Signature block at bottom.
```

---

### gold_026 | target: cursor | lang: tr
**Input:**
```
bu kodda memory leak var
```
**Output:**
```
Find and fix memory leaks in the selected code:

1. Check for event listeners added but never removed (addEventListener without removeEventListener in cleanup).
2. Check for setInterval/setTimeout without clearInterval/clearTimeout in unmount/cleanup.
3. Check for subscriptions (WebSocket, Observable, EventEmitter) not unsubscribed on component unmount.
4. Check for closures holding references to large objects or DOM nodes that prevent garbage collection.
5. If React: verify useEffect cleanup functions exist for every side effect; check for stale closure patterns.
6. Add the fix and verify with a before/after heap snapshot comparison note.

Do not: refactor unrelated code, add new dependencies for leak detection, or change the component's external behavior.
```

---

### gold_027 | target: generic | lang: en
**Input:**
```
optimize my SQL query its taking too long
```
**Output:**
```
## Goal
Analyze and optimize the slow SQL query to reduce execution time significantly.

## Context
- Which database engine? (PostgreSQL, MySQL, SQLite, SQL Server — optimization techniques differ.)
- The slow query: paste the full SQL, or describe what it does.
- Current execution time and target (e.g., "takes 12 seconds, need it under 1 second").
- Table sizes: approximate row counts for the tables involved.

## Optimization checklist
1. Run EXPLAIN ANALYZE (PostgreSQL) or EXPLAIN (MySQL) and share the output.
2. Check for missing indexes on columns in WHERE, JOIN ON, and ORDER BY clauses.
3. Look for sequential scans on large tables that should use index scans.
4. Check for N+1 patterns: a loop running individual queries that should be a single JOIN.
5. Evaluate if the query can be simplified: remove unnecessary subqueries, replace IN (SELECT ...) with EXISTS or JOIN.
6. Consider pagination if the result set is large (LIMIT + OFFSET or keyset pagination).
7. For aggregation queries: check if a materialized view or summary table would help.

## Acceptance criteria
1. The optimized query returns the same results as the original.
2. Execution time is reduced by at least 50% (measure with EXPLAIN ANALYZE before and after).
3. Any new indexes are justified — not adding indexes blindly.
4. The optimization does not degrade write performance unacceptably.

## Output format
- The original query + EXPLAIN output.
- The optimized query with comments explaining each change.
- New CREATE INDEX statements if applicable.
- Before/after execution time comparison.
```

---

### gold_028 | target: claude-code | lang: en
**Input:**
```
refactor this god class its too big
```
**Output:**
```
<task>
Break up the oversized class into smaller, single-responsibility classes while preserving all existing behavior.
</task>

<context>
- Identify the class: look for files over 500 lines or classes with more than 10 public methods.
- Map the class's responsibilities: group methods by what domain concept they serve.
- Check what depends on this class: search for imports/usages across the codebase.
</context>

<constraints>
- Each new class has a single, clear responsibility — name it after what it does (OrderValidator, not OrderHelper).
- Keep the original class as a thin facade if external callers depend on it — delegate to the new classes internally.
- Move methods and their private helpers together — do not orphan private methods.
- One refactoring step at a time: extract one class, verify tests pass, then extract the next.
- No behavior changes — this is a pure structural refactor.
</constraints>

<acceptance>
- All existing tests pass without modification (except import path changes).
- No class exceeds 200 lines after the refactor.
- Each new class has at most 5-7 public methods.
- The original class's public API still works (via delegation or re-export).
- Run the linter — no new warnings.
</acceptance>

<output_format>
- New files created (full content).
- Modified files (diffs).
- A dependency diagram: which new class calls which.
- Summary: what was extracted and why.
</output_format>
```

---

### gold_029 | target: chatgpt | lang: tr
**Input:**
```
sunum hazırla yapay zeka hakkında
```
**Output:**
```
## Hedef
"Yapay Zeka" konusunda 15-20 slaytlık bir sunum taslağı hazırla.

## Bağlam
- Hedef kitle bilinmiyorsa varsayım: teknik olmayan iş profesyonelleri.
- Sunum amacı: AI'ın ne olduğunu, güncel uygulama alanlarını ve iş dünyasına etkisini anlatmak.
- Süre: yaklaşık 20-30 dakika.

## Kısıtlar
- Her slayt: başlık + 3-5 madde (tam cümle değil, anahtar ifadeler) + konuşmacı notu (2-3 cümle).
- En az 3 somut örnek/vaka çalışması (gerçek şirketler ve sonuçlar).
- En az 2 görsel/diyagram önerisi (hangi slayta, ne tür görsel).
- Son slayt: özet + tartışma soruları.
- AI hype yapmadan gerçekçi bir ton: hem fırsatları hem sınırlılıkları ele al.
- Türkçe.

## Kabul kriterleri
1. 15-20 slayt arasında.
2. Akış: Giriş → Tanım → Tarihçe (kısa) → Türleri → Uygulama alanları → İş etkisi → Riskler → Gelecek → Özet.
3. Her slaytın konuşmacı notu var.
4. En az bir "izleyiciyi dahil etme" anı (soru, anket, demo önerisi).

## Çıktı formatı
- Markdown: her slayt ## başlığıyla.
- Her slaytın altında "Konuşmacı notu:" bölümü.
- En sonda: önerilen görsel listesi ve kaynaklar.
```

---

### gold_030 | target: cursor | lang: en
**Input:**
```
add error handling to this function
```
**Output:**
```
Add proper error handling to the selected function:

1. Identify all operations that can fail: network requests, file I/O, JSON parsing, database queries, division, array access.
2. Wrap each in try/catch (or the language's equivalent) with specific error types — not a single catch-all.
3. For recoverable errors: retry with backoff, use a fallback value, or return a Result/Either type.
4. For unrecoverable errors: throw/propagate with a descriptive message including the failed operation and input context.
5. Log errors with severity level (warn for recoverable, error for unrecoverable) including the original error's stack trace.
6. Return appropriate HTTP status codes if this is an API handler (400 for bad input, 404 for not found, 500 for unexpected).

Do not: swallow errors silently (empty catch blocks), use generic "Something went wrong" messages, or add error handling to pure computation that cannot fail.
```

---

### gold_031 | target: generic | lang: tr
**Input:**
```
nginx reverse proxy ayarla
```
**Output:**
```
## Hedef
Nginx'i reverse proxy olarak yapılandır: gelen HTTP/HTTPS trafiğini arkadaki uygulama sunucusuna yönlendir.

## Bağlam
- Uygulama hangi portta çalışıyor? (Varsayım: localhost:3000)
- Domain adı var mı? (Varsayım: var, example.com)
- SSL gerekli mi? (Varsayım: evet, Let's Encrypt ile.)
- İşletim sistemi: Ubuntu/Debian mı, CentOS/RHEL mi?

## Yapılandırma adımları
1. Nginx kurulumu (apt/yum).
2. Site config dosyası: /etc/nginx/sites-available/example.com.
3. Proxy ayarları: proxy_pass, proxy_set_header (Host, X-Real-IP, X-Forwarded-For, X-Forwarded-Proto).
4. WebSocket desteği (gerekiyorsa): proxy_http_version 1.1, Upgrade ve Connection header'ları.
5. SSL: certbot ile sertifika al, HTTP→HTTPS redirect.
6. Güvenlik header'ları: X-Frame-Options, X-Content-Type-Options, Strict-Transport-Security.
7. Rate limiting (opsiyonel): limit_req_zone.

## Kabul kriterleri
1. http://example.com → https://example.com redirect çalışıyor.
2. https://example.com → localhost:3000 proxy çalışıyor.
3. SSL sertifikası geçerli (curl -vI ile kontrol).
4. nginx -t syntax testi geçiyor.
5. Uygulama loglarında client IP doğru görünüyor (X-Real-IP üzerinden).

## Çıktı formatı
- Nginx config dosyasının tam içeriği.
- Adım adım kurulum komutları.
- Certbot komutu.
- Test komutları.
```

---

### gold_032 | target: claude-code | lang: tr
**Input:**
```
proje çok yavaş açılıyor hızlandır
```
**Output:**
```
<task>
Uygulamanın başlangıç süresini analiz et ve önemli ölçüde kısalt.
</task>

<context>
- Uygulama türü: web frontend mi (Webpack/Vite bundle), backend mi (Node.js/Spring boot time), masaüstü mü?
- Mevcut başlangıç süresi: tarayıcı DevTools Performance tab veya time node index.js ile ölç.
- Bundle analyzer varsa çalıştır (webpack-bundle-analyzer, vite-plugin-visualizer): en büyük chunk'ları bul.
</context>

<constraints>
- Önce ölç, sonra optimize et — tahmine dayalı optimizasyon yapma.
- Frontend ise: code splitting (lazy routes), tree shaking, büyük bağımlılıkları (moment→dayjs, lodash→lodash-es) değiştir, resim optimizasyonu.
- Backend ise: lazy initialization, gereksiz startup import'ları ertele, bağlantı pool'ları async başlat.
- Mevcut fonksiyonaliteyi bozma — sadece yükleme sırasını ve boyutunu optimize et.
</constraints>

<acceptance>
- Başlangıç süresi en az %30 kısaldı (ölçümle kanıtla).
- Lighthouse Performance skoru düşmedi (frontend ise).
- Mevcut testler geçiyor.
- Kullanıcı deneyimi aynı — lazy load edilen özellikler ilk kullanımda gözle görülür gecikme yapmıyor.
</acceptance>

<output_format>
- Öncesi/sonrası ölçüm sonuçları.
- Değişen dosyalar + açıklama.
- Bundle size karşılaştırması (frontend ise).
</output_format>
```

---

### gold_033 | target: chatgpt | lang: en
**Input:**
```
help me prepare for a job interview
```
**Output:**
```
## Goal
Create a structured interview preparation guide tailored to the candidate's target role.

## Context
- Role: if not specified, assume mid-level software engineer at a tech company.
- Interview type: assume a mix of behavioral, technical (coding), and system design rounds.
- Timeline: if not specified, assume 1 week of preparation time.

## Constraints
- Organize by interview round type, not by day.
- For each round type, provide: what to expect, how to prepare, 5 practice questions, and common mistakes to avoid.
- Include the STAR method explanation for behavioral questions, with one worked example.
- Technical section: focus on data structures, algorithms, and the candidate's primary language.
- System design section: provide a step-by-step framework (requirements → estimation → API → data model → architecture → trade-offs).
- Keep actionable — "practice X for 30 minutes daily" is better than "get comfortable with X."

## Acceptance criteria
1. Covers at least 3 round types: behavioral, coding, system design.
2. At least 15 practice questions total.
3. One complete worked example per round type.
4. Time allocation suggestion for 1-week prep.

## Output format
- Markdown with ## sections per round type.
- Practice questions as numbered lists.
- Worked examples in blockquotes or separate subsections.
```

---

### gold_034 | target: cursor | lang: tr
**Input:**
```
responsive yap bu sayfayı
```
**Output:**
```
Make the current page fully responsive across mobile, tablet, and desktop breakpoints:

1. Replace fixed widths (px) with relative units (%, vw, rem) or max-width constraints.
2. Convert rigid layouts to CSS Grid or Flexbox with flex-wrap.
3. Add media queries: mobile-first base styles, then @media (min-width: 768px) for tablet, @media (min-width: 1024px) for desktop.
4. Make images and media responsive: max-width: 100%, height: auto.
5. Ensure touch targets are at least 44x44px on mobile.
6. Hide or reorganize navigation into a hamburger menu on mobile if it overflows.
7. Test: no horizontal scrollbar at any viewport width from 320px to 1920px.

Do not: use !important, add a CSS framework (Bootstrap, Tailwind) if one is not already in use, or change the desktop design — only adapt it for smaller screens.
```

---

### gold_035 | target: generic | lang: en
**Input:**
```
set up a monorepo with multiple packages
```
**Output:**
```
## Goal
Convert the project into a monorepo structure with shared packages, unified tooling, and efficient dependency management.

## Context
- Current state: is this a single repo being split, or multiple repos being merged?
- Language/ecosystem: Node.js (npm/pnpm/yarn workspaces), Python (uv workspaces), Go (multi-module), Java (Maven multi-module)?
- How many packages/apps will exist? What are their names and relationships?

## Recommended structure
```
monorepo/
├── apps/
│   ├── web/          # frontend application
│   └── api/          # backend application
├── packages/
│   ├── shared/       # shared types, utilities
│   ├── ui/           # shared UI components
│   └── config/       # shared ESLint, TSConfig, etc.
├── package.json      # root workspace config
├── pnpm-workspace.yaml (or equivalent)
└── turbo.json / nx.json (optional: build orchestration)
```

## Key decisions
1. Package manager: pnpm workspaces (recommended for Node.js — strict, fast, disk-efficient).
2. Build orchestration: Turborepo or Nx for task caching and dependency-aware builds.
3. Versioning: independent per-package (Changesets) or fixed (Lerna).
4. Shared config: ESLint, TypeScript, and Prettier configs as internal packages.

## Acceptance criteria
1. pnpm install at root installs all dependencies for all packages.
2. Changes in packages/shared trigger rebuilds only in apps that depend on it.
3. Each package can be built, tested, and linted independently.
4. CI pipeline runs only affected packages on PR (not the entire monorepo).
5. A new package can be added by creating a folder + package.json, no other config changes.

## Output format
- Complete directory structure with key file contents.
- Root package.json / workspace config.
- Build orchestration config.
- CI pipeline config (GitHub Actions or equivalent).
- A short guide: "how to add a new package."
```

---

### gold_036 | target: claude-code | lang: en
**Input:**
```
add caching to make things faster
```
**Output:**
```
<task>
Add a caching layer to reduce redundant computation or data fetching and improve response times.
</task>

<context>
- What is slow? Identify the specific endpoints, queries, or computations that need caching.
- Current architecture: is there already a Redis/Memcached instance? Check docker-compose.yaml, .env, or config files.
- Data freshness requirements: how stale can cached data be? (seconds, minutes, hours)
</context>

<constraints>
- Cache strategy: use the simplest approach that works:
  - In-memory (Map/LRU) for single-instance, small data.
  - Redis for multi-instance or data > 100MB.
  - HTTP cache headers (ETag, Cache-Control) for client-side caching.
- Cache key: deterministic and collision-free — include all varying parameters.
- TTL: set explicit expiration — no infinite caches. Default 5 minutes unless the data changes less frequently.
- Invalidation: invalidate on write — when the underlying data changes, delete or update the cached entry.
- Cache stampede protection: use a lock or stale-while-revalidate pattern for high-traffic keys.
</constraints>

<acceptance>
- Cached responses are at least 5x faster than uncached (measure with a benchmark).
- Cache miss returns the same result as before caching was added.
- Writing new data invalidates the relevant cache entries.
- Cache can be fully cleared without restarting the application.
- No stale data served after a write (within the invalidation window).
- Existing tests pass; add a test for cache hit and cache invalidation.
</acceptance>

<output_format>
- New/modified files.
- Cache architecture decision (in-memory vs Redis) with one-sentence justification.
- Before/after latency measurements.
</output_format>
```

---

### gold_037 | target: chatgpt | lang: tr
**Input:**
```
regex yaz email doğrulama için
```
**Output:**
```
## Hedef
E-posta adresi doğrulama için regex pattern yaz ve açıkla.

## Bağlam
- Kullanım yeri: form doğrulama (frontend JS, backend Python/Java, veya her ikisi).
- Hassasiyet seviyesi: RFC 5322'nin tam uyumluluğu pratikte gereksiz — yaygın e-posta formatlarını kabul eden, bariz geçersizleri reddeden bir denge.

## Kısıtlar
- Kabul etmeli: user@example.com, user.name@example.co.uk, user+tag@domain.org, user@sub.domain.com.
- Reddetmeli: @domain.com, user@, user@@domain.com, user@.com, user@domain, boşluk içeren adresler.
- Pattern'i parça parça açıkla: local part, @, domain part, TLD.
- Hem JavaScript hem Python syntax'ında ver.
- Uyarı ekle: regex tek başına e-posta doğrulamaya yetmez — asıl doğrulama onay e-postası göndermektir.

## Kabul kriterleri
1. Yukarıdaki kabul/red listesinin tamamını doğru handle ediyor.
2. Pattern okunabilir — aşırı karmaşık tek satırlık regex yerine, named groups veya açıklamalı parçalama tercih et.
3. ReDoS (catastrophic backtracking) riski yok.

## Çıktı formatı
- Regex pattern (JS ve Python).
- Her parçanın açıklaması.
- Test örnekleri tablosu: girdi → beklenen sonuç (match/no match).
- Güvenlik notu.
```

---

### gold_038 | target: cursor | lang: en
**Input:**
```
refactor this to use hooks instead of class
```
**Output:**
```
Convert the selected React class component to a functional component with hooks:

1. Replace class declaration with a function component (const Component = () => {...}).
2. Convert this.state and this.setState to useState hooks — one useState per independent state variable.
3. Convert componentDidMount to useEffect with empty dependency array [].
4. Convert componentDidUpdate to useEffect with specific dependencies.
5. Convert componentWillUnmount to useEffect cleanup function (return () => {...}).
6. Replace this.props with destructured function parameters.
7. Convert class methods to const functions; wrap handlers in useCallback if passed as props.
8. Move context consumers to useContext.
9. Verify the component renders identically before and after conversion.

Do not: change prop names, modify the component's external behavior, split into multiple components during this refactor, or remove TypeScript types.
```

---

### gold_039 | target: generic | lang: tr
**Input:**
```
jwt authentication nasıl eklenir
```
**Output:**
```
## Hedef
Projeye JWT tabanlı kimlik doğrulama sistemi ekle: kayıt, giriş, token yenileme ve korumalı route'lar.

## Bağlam
- Backend framework: Express, FastAPI, Django, Spring Boot — projedeki mevcut yapıyı kullan.
- Kullanıcı verisi nerede saklanıyor? Veritabanı türü (PostgreSQL, MongoDB, vs.) ve mevcut User modeli.
- Şifre hashlemede mevcut bir çözüm var mı? (bcrypt, argon2, vb.)

## Bileşenler
1. **Kayıt (POST /auth/register):** e-posta + şifre al, şifreyi hashle (bcrypt, cost 12), veritabanına kaydet, access + refresh token dön.
2. **Giriş (POST /auth/login):** e-posta + şifre doğrula, access token (15dk TTL) + refresh token (7gün TTL) dön.
3. **Token yenileme (POST /auth/refresh):** refresh token ile yeni access token üret; eski refresh token'ı rotate et.
4. **Middleware/guard:** korumalı endpoint'lerde Authorization: Bearer <token> header'ını doğrula; geçersizse 401 dön.
5. **Çıkış (POST /auth/logout):** refresh token'ı geçersiz kıl (blacklist veya DB'den sil).

## Kısıtlar
- Access token kısa ömürlü (15 dakika), refresh token uzun ömürlü (7 gün).
- JWT secret .env'de saklanır, koda gömülmez.
- Refresh token'lar veritabanında saklanır (in-memory değil — sunucu yeniden başlayınca geçersiz olmasın).
- Şifre plain text saklanmaz, loglanmaz, response'ta dönmez.
- Rate limiting: login endpoint'inde brute force koruması.

## Kabul kriterleri
1. Kayıt → giriş → korumalı endpoint erişimi akışı çalışıyor.
2. Süresi dolmuş access token 401 dönüyor.
3. Refresh token ile yeni access token alınabiliyor.
4. Geçersiz/expired refresh token 401 dönüyor.
5. Logout sonrası refresh token kullanılamıyor.

## Çıktı formatı
- Tüm auth dosyalarının tam kodu.
- .env.example'a eklenen JWT_SECRET ve JWT_REFRESH_SECRET.
- API endpoint tablosu (method, path, body, response).
- Test komutları veya curl örnekleri.
```

---

### gold_040 | target: claude-code | lang: tr
**Input:**
```
logları düzgün yap her yerde console.log var
```
**Output:**
```
<task>
Dağınık console.log çağrılarını yapılandırılmış bir loglama sistemiyle değiştir.
</task>

<context>
- Proje dili/framework'ü: Node.js ise winston veya pino; Python ise stdlib logging; Java ise SLF4J + Logback.
- Mevcut console.log kullanım sayısı: grep -r "console.log" src/ ile say.
- Hangi log seviyeleri anlamlı: debug (geliştirme), info (normal akış), warn (beklenmeyen ama kurtarılabilir), error (hata).
</context>

<constraints>
- Tek bir logger instance oluştur: src/lib/logger veya src/utils/logger.
- Log formatı: JSON (production) + pretty-print (development). Timestamp, seviye, mesaj, context alanları zorunlu.
- Her console.log'u uygun seviyeye dönüştür:
  - Debugging amaçlı → logger.debug (veya tamamen sil).
  - Bilgi amaçlı (istek geldi, işlem tamamlandı) → logger.info.
  - Uyarı (deprecated kullanım, yavaş sorgu) → logger.warn.
  - Hata yakalama → logger.error (error objesini de geç).
- Hassas veri loglanmasın: şifre, token, kişisel bilgi.
- Log seviyesi ortam değişkeniyle ayarlanabilir olsun (LOG_LEVEL=debug|info|warn|error).
</constraints>

<acceptance>
- Projede console.log kalmadı (console.error hariç — o da logger.error'a dönüştü).
- LOG_LEVEL=info ile debug logları görünmüyor.
- LOG_LEVEL=debug ile tüm loglar görünüyor.
- Production'da JSON formatında loglar üretiliyor.
- Mevcut testler geçiyor.
</acceptance>

<output_format>
- Logger modülü tam kodu.
- Dönüştürülen dosyaların diff'leri.
- Kullanılan kütüphane ve neden seçildiği (1 cümle).
</output_format>
```

---

### gold_041 | target: chatgpt | lang: en
**Input:**
```
summarize this research paper
```
**Output:**
```
## Goal
Provide a structured summary of the given research paper, extracting key findings and their significance.

## Context
- The paper should be provided (pasted text, title for lookup, or PDF content).
- If no paper is specified, ask which paper to summarize.
- Target audience: someone in the field who wants the essence without reading the full paper.

## Constraints
- Summary structure:
  1. **One-sentence takeaway** — the single most important finding.
  2. **Problem** — what gap or question does the paper address? (2-3 sentences)
  3. **Method** — how did they investigate it? (3-4 sentences)
  4. **Key findings** — numbered list, 3-5 items, each one sentence.
  5. **Limitations** — what the authors acknowledge or what you notice. (2-3 items)
  6. **Significance** — why does this matter for the field? (2-3 sentences)
- Total length: 300-500 words.
- Use the paper's own terminology but define niche terms in parentheses.
- Do not editorialize — report what the authors found, not what you think about it.
- Cite specific numbers/metrics from the paper where relevant.

## Acceptance criteria
1. Someone who reads only this summary understands the paper's contribution.
2. No information is fabricated — everything traces back to the paper.
3. Limitations section is honest, not just repeating the authors' disclaimers.

## Output format
- Markdown with the 6 sections above as ### headings.
- Paper citation at the top (authors, title, year, venue if known).
```

---

### gold_042 | target: cursor | lang: en
**Input:**
```
write unit tests for this file
```
**Output:**
```
Write unit tests for every public function and exported member in the current file:

1. Identify all public functions, classes, and exported constants.
2. For each function, write tests covering: normal input, edge cases (empty, null, boundary values), and error cases (invalid input, exceptions).
3. Use the project's existing test framework (detect from package.json or config). If none, use the language default (Jest for JS/TS, pytest for Python, JUnit for Java).
4. Mock external dependencies (API calls, database, file system) — test the unit's logic in isolation.
5. Use descriptive test names: "returns empty array when input is null", not "test1".
6. Aim for at least 90% line coverage of the file under test.
7. Place the test file next to the source file or in the matching __tests__/ directory, following existing convention.

Do not: test private/internal functions directly, add snapshot tests unless the output is a serializable data structure, or modify the source file.
```

---

### gold_043 | target: generic | lang: tr
**Input:**
```
redis cache nasıl kullanılır
```
**Output:**
```
## Hedef
Redis'i projede cache katmanı olarak kullanmak için kurulum, bağlantı, temel işlemler ve yaygın pattern'leri açıkla.

## Bağlam
- Hedef kitle: Redis'i daha önce kullanmamış ama veritabanı ve API kavramlarını bilen bir geliştirici.
- Proje ortamı: Docker ile Redis container veya yerel kurulum.
- Uygulama dili: Node.js (ioredis), Python (redis-py), veya Go (go-redis) — proje diline göre uyarla.

## İçerik yapısı
1. **Kurulum:** Docker ile tek komutla Redis başlatma (docker run), bağlantı testi (redis-cli PING).
2. **Bağlantı:** uygulama kodundan Redis'e bağlanma, connection pool ayarları.
3. **Temel işlemler:** SET/GET (string), HSET/HGET (hash), LPUSH/LRANGE (list), EXPIRE (TTL).
4. **Cache pattern'leri:**
   - Cache-aside (lazy loading): önce cache'e bak, yoksa DB'den çek ve cache'e yaz.
   - Write-through: DB'ye yazarken aynı anda cache'i güncelle.
   - Cache invalidation: veri değişince ilgili key'i sil.
5. **TTL stratejisi:** hangi veri ne kadar cache'lenir (oturum: 30dk, ürün listesi: 5dk, statik config: 1 saat).
6. **Hata yönetimi:** Redis çökerse uygulama çalışmaya devam etmeli — cache miss fallback.

## Kısıtlar
- Kod örnekleri çalıştırılabilir olsun (copy-paste ready).
- Güvenlik: Redis AUTH şifresi .env'de, default port dışarıya açık olmasın.
- Monitoring: MONITOR komutu dev'de debug için, INFO STATS production'da metrik için.

## Kabul kriterleri
1. Örneklerdeki kod çalıştırılınca Redis'e veri yazıp okuyabiliyor.
2. TTL süresi dolunca key otomatik siliniyor.
3. Cache miss durumunda DB'den veri çekilip cache'e yazılıyor.

## Çıktı formatı
- Markdown, bölüm başlıklı.
- Her bölümde kod bloğu.
- Docker komutu + uygulama kodu + redis-cli test komutu.
```

---

### gold_044 | target: claude-code | lang: en
**Input:**
```
migrate the database to the new schema
```
**Output:**
```
<task>
Write and execute database migration(s) to move from the current schema to the new target schema without data loss.
</task>

<context>
- Migration tool: detect from the project (Prisma Migrate, Alembic, Flyway, Knex, Django, TypeORM migrations).
- Current schema: inspect the database or read the latest migration files.
- Target schema: check if a new schema definition exists (Prisma schema, models.py, entity files) or if the user describes the changes.
- Data volume: estimate row counts in affected tables to gauge migration duration.
</context>

<constraints>
- Every migration must be reversible (include a down/rollback function).
- No data loss: if dropping a column, migrate data to the new location first.
- Rename columns with a multi-step approach: add new → copy data → drop old (not a direct rename, which some ORMs handle differently).
- Add NOT NULL columns with a default value to avoid breaking existing rows.
- Large table migrations: consider batching updates if > 1M rows.
- Test the migration on a copy of production data before applying to production.
</constraints>

<acceptance>
- Migration runs without errors: migrate up succeeds.
- Rollback works: migrate down returns to the previous state.
- Round-trip test: up → down → up produces the same result.
- Existing application code works with the new schema (no broken queries).
- No orphaned data or broken foreign key relationships.
</acceptance>

<output_format>
- Migration file(s) with full content.
- SQL preview (what the migration actually runs).
- Data migration script if columns are moved/merged.
- Rollback instructions.
</output_format>
```

---

### gold_045 | target: chatgpt | lang: tr
**Input:**
```
instagram post fikirleri ver
```
**Output:**
```
## Hedef
Bir Instagram hesabı için 10 günlük içerik planı ve post fikirleri hazırla.

## Bağlam
- Hesap türü belirtilmedi — varsayım: kişisel marka / yazılım geliştirici profili.
- Platform: Instagram (görsel ağırlıklı, kısa metin, carousel ve reels önemli).
- Hedef: takipçi etkileşimini artırmak ve uzmanlık alanını göstermek.

## Kısıtlar
- Her gün için: post türü (carousel, single image, reel, story) + konu + kısa açıklama + caption taslağı + hashtag önerisi (5-10 adet).
- İçerik karışımı: %40 eğitici (coding tips, tool reviews), %30 kişisel (behind the scenes, daily routine), %30 etkileşim (soru, anket, meme).
- Caption: 150-300 karakter, hook cümlesiyle başla, CTA ile bitir ("kaydet", "yorum yaz", "arkadaşını etiketle").
- Hashtag: niş + genel karışımı (#developer #coding + #tech #daily).
- Reels süresi: 30-60 saniye.
- Türkçe.

## Kabul kriterleri
1. 10 günlük plan, her gün farklı konu.
2. En az 3 farklı post formatı kullanılmış.
3. Her post'un caption taslağı var.
4. Tekrar eden konu yok.

## Çıktı formatı
- Tablo: Gün | Format | Konu | Caption | Hashtag'ler.
- Her gün için 1-2 cümle görsel açıklaması.
```

---

### gold_046 | target: cursor | lang: tr
**Input:**
```
bu formu doğrulama ekle
```
**Output:**
```
Add client-side validation to the selected form:

1. Mark required fields — show a red asterisk (*) next to the label.
2. Validate on blur (per field) and on submit (all fields):
   - Required fields: non-empty check.
   - Email: valid email format.
   - Password: minimum 8 chars, at least one letter and one digit.
   - Confirm password: matches password field.
   - Phone (if present): digits only, 10-15 chars.
3. Show inline error messages below each invalid field in red text.
4. Disable the submit button while any field is invalid.
5. On submit, prevent default if validation fails; show a summary at the top listing all errors.
6. Clear field error when the user starts typing in that field.
7. Use the existing form library if one is present (React Hook Form, Formik, Zod). If none, use native HTML5 validation attributes + minimal JS.

Do not: add server-side validation here (that belongs in the API handler), change form layout or styling beyond error states, or add CAPTCHA.
```

---

### gold_047 | target: generic | lang: en
**Input:**
```
explain how to use git branches properly
```
**Output:**
```
## Goal
Explain a practical Git branching strategy suitable for a small-to-medium team, with clear rules for when to create, merge, and delete branches.

## Context
- Audience: developers who know basic Git (commit, push, pull) but struggle with branch management.
- Team size assumption: 2-8 developers working on the same repo.

## Branching strategy
1. **main** — always deployable. Direct commits are blocked; changes enter only via pull request.
2. **Feature branches** — one per task/ticket. Naming: feature/short-description or feat/JIRA-123-short-description.
3. **Bugfix branches** — same as feature, but prefixed: fix/short-description.
4. **Release branches** (optional, for teams with formal releases): release/v1.2.0, branched from main, receives only bug fixes.

## Workflow rules
1. Create a branch from main for every piece of work — never commit directly to main.
2. Keep branches short-lived: merge within 1-3 days. Long-lived branches cause painful merge conflicts.
3. Pull main into your branch daily (or rebase) to stay current.
4. Open a pull request when ready — at least one reviewer approves before merge.
5. Squash-merge or rebase-merge to keep main's history clean (no merge commit clutter).
6. Delete the branch after merge — it served its purpose.
7. Never force-push to main or shared branches.

## Common mistakes
- "I'll just commit to main quickly" — even a one-line fix deserves a branch + PR.
- Branch lives for 2 weeks — by the time you merge, half the codebase changed underneath.
- Naming chaos — feat/johns-thing tells no one what it does.

## Output format
- Markdown with ## sections.
- One ASCII diagram showing the branch/merge flow.
- A cheat sheet: 5-6 most common commands with one-line explanations.
```

---

### gold_048 | target: claude-code | lang: tr
**Input:**
```
env dosyasını düzenle güvenli hale getir
```
**Output:**
```
<task>
Projenin environment variable yönetimini güvenli hale getir: sızıntı riski olan noktaları kapat, yapılandırmayı standartlaştır.
</task>

<context>
- Mevcut .env dosyası var mı? İçinde neler var? (git log -- .env ile geçmişte commit edilip edilmediğini kontrol et.)
- .gitignore'da .env tanımlı mı?
- Hangi değişkenler var: API key'leri, veritabanı bağlantısı, JWT secret, üçüncü parti servis token'ları?
- Uygulama bu değişkenleri nasıl okuyor: dotenv, vite env, next.config, os.environ?
</context>

<constraints>
- .env dosyası .gitignore'a eklenmiş olmalı. Git geçmişinde .env varsa uyarı ver (key rotation gerekir).
- .env.example dosyası oluştur: tüm değişken isimleri + açıklayıcı placeholder değerler (gerçek secret yok).
- Validation: uygulama başlarken tüm zorunlu env değişkenlerinin varlığını kontrol et — eksikse net hata mesajıyla çık.
- Farklı ortamlar: .env.development, .env.production, .env.test ayrımı (framework destekliyorsa).
- Client-side koda secret sızmamış mı kontrol et (VITE_*, NEXT_PUBLIC_* prefix'leri yalnızca public değerler için).
</constraints>

<acceptance>
- .env .gitignore'da.
- .env.example tüm değişkenleri listeler, gerçek değer içermez.
- Uygulama eksik env değişkeniyle başlatılınca anlamlı hata mesajı veriyor.
- git log -- .env geçmişte commit gösteriyorsa uyarı raporlanmış.
- Client bundle'da secret yok (build edip bundle içinde grep ile kontrol).
</acceptance>

<output_format>
- .gitignore değişikliği.
- .env.example tam içeriği.
- Env validation kodu.
- Güvenlik raporu: bulunan sorunlar ve düzeltmeler.
</output_format>
```

---

### gold_049 | target: chatgpt | lang: en
**Input:**
```
debug this error message for me
```
**Output:**
```
## Goal
Diagnose and resolve the error based on the provided error message, stack trace, or description.

## Context
- The error message or stack trace must be provided. If not given, ask for it.
- Include: the full error text, the language/framework, what action triggered it, and whether it's reproducible.

## Constraints
- Diagnosis structure:
  1. **What the error means** — translate the error message into plain English in one sentence.
  2. **Most likely cause** — based on the error type and stack trace, identify the probable root cause (not a list of 10 possibilities — pick the most likely one).
  3. **How to verify** — a specific command or check to confirm the diagnosis.
  4. **Fix** — the exact code change, config edit, or command to resolve it.
  5. **Prevention** — one sentence on how to avoid this in the future (linter rule, type check, test).
- If the error is ambiguous and could have multiple causes, present the top 2 with a differentiating check for each.
- Do not guess wildly — if the error message is too vague without more context, list exactly what additional information is needed.

## Acceptance criteria
1. The diagnosis is specific to this error, not a generic troubleshooting guide.
2. The fix is actionable — copy-pasteable command or code change.
3. The explanation is understandable to someone who encountered this error for the first time.

## Output format
- Five numbered sections as listed above.
- Code blocks for commands and fixes.
- Keep total length under 400 words.
```

---

### gold_050 | target: cursor | lang: en
**Input:**
```
make this accessible
```
**Output:**
```
Improve the accessibility of the selected component to meet WCAG 2.1 AA standards:

1. Add semantic HTML: replace generic divs with appropriate elements (button, nav, main, article, section, aside, header, footer).
2. Add ARIA attributes where semantic HTML is insufficient: aria-label for icon-only buttons, aria-expanded for toggles, aria-live for dynamic content, role for custom widgets.
3. Ensure all images have descriptive alt text (or alt="" for decorative images).
4. Check color contrast: text must have at least 4.5:1 ratio against its background (3:1 for large text). Use the existing color system; adjust shades if needed.
5. Ensure keyboard navigation: all interactive elements are focusable and operable with Enter/Space. Add visible focus indicators (:focus-visible outline).
6. Add skip-to-content link if this is a page-level component.
7. Form inputs must have associated labels (htmlFor/id pairing or aria-label).
8. Verify with a screen reader mental walkthrough: read through the component top-to-bottom — does the order make sense? Is any content invisible to assistive tech?

Do not: remove existing functionality, change visual design unless needed for contrast, or add aria-label to elements that already have visible text labels.
```
