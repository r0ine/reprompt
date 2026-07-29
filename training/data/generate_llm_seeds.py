"""NVIDIA NIM (DeepSeek) ile yuksek kaliteli egitim seed'leri ureten betik.

DeepSeek'e meta-prompt gondererek gercekci (raw_prompt, optimized_prompt)
ciftleri uretir. Her batch cagrisi 5-10 ornek dondurur.

Kullanim:
    python -m training.data.generate_llm_seeds --count 500 --lang tr,en
    python -m training.data.generate_llm_seeds --count 5000 --category direct_enhance,question_first
    python -m training.data.generate_llm_seeds --target claude-code --lang tr --count 200
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import click
import requests

SECRETS_PATH = Path(r"C:\Users\Kemal\Desktop\Workspace\secrets\.env")
OUT_PATH = Path("training/datasets/raw/llm_seeds.jsonl")

NIM_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-ai/deepseek-v4-flash"

CATEGORIES = [
    "direct_enhance",
    "question_first",
    "context_aware",
    "system_integrated",
    "ambiguity_resolve",
    "multi_step",
]

TARGETS = ["claude-code", "chatgpt", "cursor", "generic"]

LANGS = ["tr", "en", "de", "fr", "es", "pt", "ru", "ja", "zh", "ko"]

LANG_NAMES = {
    "tr": "Turkish", "en": "English", "de": "German", "fr": "French",
    "es": "Spanish", "pt": "Portuguese", "ru": "Russian",
    "ja": "Japanese", "zh": "Chinese", "ko": "Korean",
}

MAX_RPS = 5
BATCH_SIZE_PER_CALL = 5
MAX_RETRIES = 4
RETRY_BASE_DELAY = 3.0

DOMAINS = {
    "code": [
        "React dashboard", "REST API endpoint", "database migration",
        "WebSocket chat", "authentication flow", "CI/CD pipeline",
        "GraphQL schema", "microservice", "cron scheduler", "search indexer",
        "payment integration", "file upload handler", "rate limiter",
        "notification service", "caching layer", "state management",
        "error boundary", "logging middleware", "test suite", "CLI tool",
        "browser extension", "mobile app screen", "Docker setup",
        "reverse proxy config", "queue consumer", "event bus",
        "PDF generator", "email template engine", "analytics tracker",
    ],
    "writing": [
        "blog post", "technical documentation", "API reference",
        "bug report", "presentation slides", "email draft",
        "product description", "meeting summary", "project brief",
        "test plan", "release notes", "performance report",
        "security assessment", "cost analysis", "user guide",
        "changelog entry", "code review feedback", "RFC document",
        "onboarding guide", "troubleshooting doc", "architecture decision record",
    ],
    "data": [
        "ETL pipeline", "data cleaning script", "SQL query optimization",
        "Pandas analysis", "chart/visualization", "CSV parser",
        "data validation", "feature engineering", "model evaluation",
        "A/B test analysis", "time series forecast", "anomaly detection",
    ],
    "devops": [
        "Kubernetes deployment", "Terraform module", "GitHub Actions workflow",
        "monitoring dashboard", "alerting rules", "backup strategy",
        "load testing setup", "SSL certificate renewal", "DNS configuration",
        "container orchestration", "secrets management", "rollback procedure",
    ],
}

META_PROMPTS: dict[str, str] = {
    "direct_enhance": """Generate {n} DIVERSE training examples for a prompt-engineering AI.
Each example is a pair: (raw_prompt, optimized_prompt).

Category: DIRECT ENHANCE — take a lazy/incomplete developer prompt and rewrite it into a rich, structured prompt.

Language: {lang_name}
Target LLM profile: {target}

Domain hints (pick from these OR invent related ones): {domains}

Rules for the RAW prompt:
- Short, sloppy, realistic — typos OK, slang OK, missing context OK
- Between 5 and 40 words
- Some should be commands ("fix X"), some questions ("how do I X"), some complaints ("X is broken")
- Mix skill levels: junior dev, senior dev, PM, designer

Rules for the OPTIMIZED prompt:
{target_rules}
- Always richer than the raw: add goal, context, constraints, acceptance criteria
- Each optimized prompt should feel DIFFERENT in structure and wording — avoid formula
- Between 80 and 500 words

Return ONLY a JSON array of objects. Each object:
{{"raw": "...", "optimized": "...", "complexity": "low|medium|high"}}

No markdown fences, no explanation. Just the JSON array.""",

    "question_first": """Generate {n} DIVERSE training examples for a prompt-engineering AI.

Category: QUESTION FIRST — the AI should first ask 2-4 clarifying questions, then provide the structured prompt based on assumed answers.

Language: {lang_name}
Target LLM profile: {target}

Domain hints: {domains}

Rules for the RAW prompt:
- Deliberately vague or underspecified — multiple valid interpretations
- Between 5 and 30 words

Rules for the OPTIMIZED output:
- Start with "## Clarifying Questions" section listing 2-4 questions
- Then "## Assumed Answers" with reasonable defaults
- Then the full structured prompt based on those assumptions
{target_rules}
- Between 120 and 600 words total

Return ONLY a JSON array:
{{"raw": "...", "optimized": "...", "complexity": "low|medium|high"}}""",

    "context_aware": """Generate {n} DIVERSE training examples for a prompt-engineering AI.

Category: CONTEXT AWARE — the input includes both a raw prompt AND project context (tech stack, existing code patterns, team conventions). The output should be tailored to that context.

Language: {lang_name}
Target LLM profile: {target}

Domain hints: {domains}

Rules for the RAW prompt:
- Include a [Context] block with 2-5 bullet points about the project
- Then a short request (5-30 words)
- Example context: "Stack: Next.js 14 + Prisma + PostgreSQL, Monorepo with turborepo, Team uses conventional commits"

Rules for the OPTIMIZED prompt:
{target_rules}
- Must reference and leverage the provided context
- Should mention specific files/patterns from context where relevant
- Between 100 and 500 words

Return ONLY a JSON array:
{{"raw": "...", "optimized": "...", "complexity": "medium|high"}}""",

    "system_integrated": """Generate {n} DIVERSE training examples for a prompt-engineering AI.

Category: SYSTEM INTEGRATED — the input includes a raw prompt plus system-level instructions (role, persona, rules). The output weaves both into a coherent enhanced prompt.

Language: {lang_name}
Target LLM profile: {target}

Domain hints: {domains}

Rules for the RAW prompt:
- Include a [System] block with 1-3 rules (e.g., "Always use TypeScript", "Follow SOLID principles", "Respond in formal tone")
- Then a short request

Rules for the OPTIMIZED prompt:
{target_rules}
- Embed system rules naturally — don't just copy them
- Between 100 and 500 words

Return ONLY a JSON array:
{{"raw": "...", "optimized": "...", "complexity": "medium|high"}}""",

    "ambiguity_resolve": """Generate {n} DIVERSE training examples for a prompt-engineering AI.

Category: AMBIGUITY RESOLVE — the input is extremely vague. The output should state explicit assumptions and then produce the best possible prompt.

Language: {lang_name}
Target LLM profile: {target}

Domain hints: {domains}

Rules for the RAW prompt:
- Maximum 15 words, intentionally ambiguous
- Could mean multiple things (e.g., "make it better", "fix the thing", "add auth")

Rules for the OPTIMIZED output:
- Start with "## Assumptions" listing 3-5 assumptions made
- Then the full structured prompt
{target_rules}
- Between 100 and 500 words

Return ONLY a JSON array:
{{"raw": "...", "optimized": "...", "complexity": "low|medium|high"}}""",

    "multi_step": """Generate {n} DIVERSE training examples for a prompt-engineering AI.

Category: MULTI-STEP — the input is a complex request that should be broken into phased, prioritized steps.

Language: {lang_name}
Target LLM profile: {target}

Domain hints: {domains}

Rules for the RAW prompt:
- Longer than usual: 20-60 words
- Covers multiple concerns (e.g., "rebuild the auth, add 2FA, migrate the DB, and update the docs")

Rules for the OPTIMIZED prompt:
{target_rules}
- Must organize into numbered phases with priorities
- Each phase should have its own acceptance criteria
- Between 150 and 700 words

Return ONLY a JSON array:
{{"raw": "...", "optimized": "...", "complexity": "high"}}""",
}

TARGET_RULES: dict[str, str] = {
    "claude-code": """- Use XML tags: <task>, <context>, <constraints>, <acceptance>, <output_format>
- Concise, imperative style
- Include verification commands where appropriate (e.g., "run tests", "check build")""",
    "chatgpt": """- Use Markdown headings: ## Goal, ## Context, ## Constraints, ## Acceptance criteria, ## Output format
- Conversational but precise tone
- Explicitly state what NOT to do""",
    "cursor": """- Numbered step list format, IDE-aware
- Reference file patterns (e.g., "find files matching src/**/*.ts")
- Include "Do not" guardrails at the end
- Keep it scannable — no long paragraphs""",
    "generic": """- Use Markdown headings: ## Goal, ## Context, ## Steps, ## Acceptance criteria, ## Output format
- Profile-agnostic — should work with any LLM
- Clear, structured, no assumptions about tool access""",
}


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def load_env_keys() -> dict[str, str]:
    keys = {}
    for line in SECRETS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        keys[k.strip()] = v.strip().strip('"').strip("'")
    return keys


def seed_id(raw: str, target: str, cat: str) -> str:
    blob = f"{raw}|{target}|{cat}".encode()
    return f"llmseed_{hashlib.md5(blob).hexdigest()[:12]}"


def pick_domains(rng: random.Random, n: int = 6) -> str:
    pool = []
    for group in DOMAINS.values():
        pool.extend(group)
    return ", ".join(rng.sample(pool, min(n, len(pool))))


def api_call(session: requests.Session, api_key: str, prompt: str, attempt: int = 0) -> str | None:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "You are a training data generator. Return ONLY valid JSON arrays. No markdown, no explanation."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.9,
        "max_tokens": 4096,
        "top_p": 0.95,
    }

    try:
        resp = session.post(NIM_ENDPOINT, json=payload, headers=headers, timeout=300)
    except (requests.Timeout, requests.ConnectionError, requests.exceptions.ChunkedEncodingError) as exc:
        if attempt < MAX_RETRIES:
            delay = RETRY_BASE_DELAY * (2 ** attempt) + random.uniform(0, 1)
            log(f"  [RETRY] Baglanti hatasi, {delay:.1f}s bekleyip tekrar ({attempt+1}/{MAX_RETRIES})...")
            time.sleep(delay)
            return api_call(session, api_key, prompt, attempt + 1)
        log(f"  [FAIL] API erisim hatasi: {exc}")
        return None

    if resp.status_code == 429:
        if attempt < MAX_RETRIES:
            delay = RETRY_BASE_DELAY * (2 ** attempt) + random.uniform(0, 2)
            log(f"  [RETRY] Rate limit, {delay:.1f}s bekleniyor...")
            time.sleep(delay)
            return api_call(session, api_key, prompt, attempt + 1)
        log("  [FAIL] Rate limit asimi.")
        return None

    if resp.status_code != 200:
        if attempt < MAX_RETRIES and resp.status_code >= 500:
            delay = RETRY_BASE_DELAY * (2 ** attempt)
            log(f"  [RETRY] Server error {resp.status_code}...")
            time.sleep(delay)
            return api_call(session, api_key, prompt, attempt + 1)
        log(f"  [FAIL] HTTP {resp.status_code}: {resp.text[:200]}")
        return None

    try:
        data = resp.json()
    except ValueError:
        log(f"  [FAIL] JSON decode hatasi, yanit: {resp.text[:200]}")
        return None

    choices = data.get("choices", [])
    if not choices:
        return None

    content = choices[0].get("message", {}).get("content", "")
    return content.strip()


def parse_batch_response(raw_json: str) -> list[dict]:
    text = raw_json.strip()

    # <think>...</think> bloklarini temizle (reasoning modelleri)
    if "<think>" in text:
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    # Markdown fences temizle (```json ... ```)
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)

    # Disarida kalan metinleri at, ilk [ ile son ] arasini al
    start = text.find("[")
    end = text.rfind("]")
    if start < 0 or end <= start:
        return []
    text = text[start:end + 1]

    try:
        arr = json.loads(text)
    except json.JSONDecodeError:
        # Bazen trailing comma gibi sorunlar olabiliyor, temizle
        cleaned = re.sub(r",\s*([}\]])", r"\1", text)
        try:
            arr = json.loads(cleaned)
        except json.JSONDecodeError:
            return []

    if not isinstance(arr, list):
        return []

    valid = []
    for item in arr:
        if not isinstance(item, dict):
            continue
        raw = item.get("raw", "").strip()
        opt = item.get("optimized", "").strip()
        if len(raw) < 5 or len(opt) < 40:
            continue
        valid.append(item)
    return valid


def build_meta_prompt(category: str, lang: str, target: str, batch_size: int, rng: random.Random) -> str:
    template = META_PROMPTS[category]
    return template.format(
        n=batch_size,
        lang_name=LANG_NAMES.get(lang, lang),
        target=target,
        domains=pick_domains(rng),
        target_rules=TARGET_RULES[target],
    )


def make_plan(
    total: int,
    langs: list[str],
    targets: list[str],
    categories: list[str],
    rng: random.Random,
) -> list[tuple[str, str, str]]:
    combos = [(cat, lang, tgt) for cat in categories for lang in langs for tgt in targets]
    rng.shuffle(combos)

    batches_needed = (total + BATCH_SIZE_PER_CALL - 1) // BATCH_SIZE_PER_CALL
    plan = []
    idx = 0
    for _ in range(batches_needed):
        plan.append(combos[idx % len(combos)])
        idx += 1
    return plan


@click.command()
@click.option("--count", "-n", default=5000, help="Hedef ornek sayisi")
@click.option("--lang", "-l", default=None, help="Virgul-ayirli dil filtreleri (tr,en,de...)")
@click.option("--target", "-t", default=None, help="Virgul-ayirli hedef profiller (claude-code,chatgpt...)")
@click.option("--category", "-c", default=None, help="Virgul-ayirli kategoriler (direct_enhance,question_first...)")
@click.option("--seed", "-s", default=42, help="Rastgelelik tohumu")
@click.option("--append/--overwrite", default=True, help="Mevcut dosyaya ekle veya sifirdan yaz")
@click.option("--dry-run", is_flag=True, help="Plan goster, API cagirma")
def main(count: int, lang: str | None, target: str | None, category: str | None,
         seed: int, append: bool, dry_run: bool) -> None:

    rng = random.Random(seed)

    sel_langs = [l.strip() for l in lang.split(",")] if lang else LANGS
    sel_targets = [t.strip() for t in target.split(",")] if target else TARGETS
    sel_categories = [c.strip() for c in category.split(",")] if category else CATEGORIES

    for l in sel_langs:
        if l not in LANGS:
            raise click.BadParameter(f"Bilinmeyen dil: {l}. Gecerli: {', '.join(LANGS)}")
    for t in sel_targets:
        if t not in TARGETS:
            raise click.BadParameter(f"Bilinmeyen hedef: {t}. Gecerli: {', '.join(TARGETS)}")
    for c in sel_categories:
        if c not in CATEGORIES:
            raise click.BadParameter(f"Bilinmeyen kategori: {c}. Gecerli: {', '.join(CATEGORIES)}")

    plan = make_plan(count, sel_langs, sel_targets, sel_categories, rng)

    log("LLM Seed Uretici")
    log(f"  Hedef: {count} ornek")
    log(f"  Diller: {', '.join(sel_langs)}")
    log(f"  Hedefler: {', '.join(sel_targets)}")
    log(f"  Kategoriler: {', '.join(sel_categories)}")
    log(f"  Tahmini batch sayisi: {len(plan)}")
    log(f"  Model: {DEEPSEEK_MODEL}")

    if dry_run:
        log("Dry-run -- API cagrisi yapilmadi.")
        return

    env_keys = load_env_keys()
    api_key = env_keys.get("NVIDIA_DEEPSEEK_KEY")
    if not api_key:
        raise click.ClickException(f"NVIDIA_DEEPSEEK_KEY bulunamadi: {SECRETS_PATH}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    existing_ids: set[str] = set()
    if append and OUT_PATH.exists():
        for line in OUT_PATH.read_text(encoding="utf-8").splitlines():
            try:
                existing_ids.add(json.loads(line)["id"])
            except (json.JSONDecodeError, KeyError):
                pass
        log(f"  Mevcut kayit: {len(existing_ids)}")

    mode = "a" if append else "w"
    written = 0
    failed_batches = 0
    cat_counts: dict[str, int] = {}
    lang_counts: dict[str, int] = {}
    last_call_time = 0.0

    session = requests.Session()

    try:
        with OUT_PATH.open(mode, encoding="utf-8") as fh:
            for batch_idx, (cat, lng, tgt) in enumerate(plan):
                if written >= count:
                    break

                remaining = count - written
                batch_n = min(BATCH_SIZE_PER_CALL, remaining)

                elapsed = time.monotonic() - last_call_time
                min_interval = 1.0 / MAX_RPS
                if elapsed < min_interval:
                    time.sleep(min_interval - elapsed)

                prompt = build_meta_prompt(cat, lng, tgt, batch_n, rng)
                last_call_time = time.monotonic()
                log(f"  Batch {batch_idx+1}/{len(plan)}: {cat}/{lng}/{tgt} (n={batch_n})...")

                raw_response = api_call(session, api_key, prompt)
                if not raw_response:
                    failed_batches += 1
                    log("    -> bos yanit")
                    continue

                examples = parse_batch_response(raw_response)
                if not examples:
                    failed_batches += 1
                    log(f"    -> parse hatasi ({len(raw_response)} kar). Ilk 200: {raw_response[:200]}")
                    continue

                batch_written = 0
                for ex in examples:
                    if written >= count:
                        break

                    raw_text = ex["raw"]
                    opt_text = ex["optimized"]
                    complexity = ex.get("complexity", "medium")

                    rid = seed_id(raw_text, tgt, cat)
                    if rid in existing_ids:
                        continue
                    existing_ids.add(rid)

                    has_questions = "?" in opt_text and cat in ("question_first", "ambiguity_resolve")
                    has_system = "[System]" in raw_text or "[system]" in raw_text
                    has_context = "[Context]" in raw_text or "[context]" in raw_text

                    record = {
                        "id": rid,
                        "source": "llm_seed",
                        "target": tgt,
                        "lang": lng,
                        "input": raw_text,
                        "output": opt_text,
                        "category": cat,
                        "has_questions": has_questions,
                        "has_system_prompt": has_system,
                        "has_context": has_context,
                        "complexity": complexity,
                        "meta": {
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "teacher": DEEPSEEK_MODEL,
                            "notes": f"batch_{batch_idx}",
                        },
                    }
                    fh.write(json.dumps(record, ensure_ascii=False) + "\n")
                    written += 1
                    batch_written += 1

                    cat_counts[cat] = cat_counts.get(cat, 0) + 1
                    lang_counts[lng] = lang_counts.get(lng, 0) + 1

                fh.flush()
                log(f"    -> +{batch_written} (toplam: {written}/{count})")

    finally:
        session.close()

    log("")
    log(f"{written:,} seed yazildi -> {OUT_PATH}")
    if failed_batches:
        log(f"Basarisiz batch: {failed_batches}")

    if cat_counts:
        log("  Kategori dagilimi:")
        for cat in sorted(cat_counts, key=cat_counts.get, reverse=True):
            log(f"    {cat}: {cat_counts[cat]:,}")

    if lang_counts:
        log("  Dil dagilimi:")
        for lng in sorted(lang_counts, key=lang_counts.get, reverse=True):
            log(f"    {lng}: {lang_counts[lng]:,}")


if __name__ == "__main__":
    main()
