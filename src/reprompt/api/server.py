"""REST API server — self-hostable prompt rewriting service.

    reprompt serve --model ~/models/clarify.gguf --port 8741
    curl -X POST http://localhost:8741/v1/rewrite \
         -H 'Content-Type: application/json' \
         -d '{"prompt": "login sayfası yap", "target": "claude-code"}'
"""

from __future__ import annotations

import os
import time
from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from reprompt import __version__
from reprompt.config.schema import BackendName
from reprompt.prompts.types import (
    DETAIL_LEVELS,
    TARGET_PROFILES,
    TASK_PROFILES,
    DetailLevel,
    TargetProfile,
    TaskProfile,
)
from reprompt.sdk import RepromptEngine

_engine: RepromptEngine | None = None


def _get_engine() -> RepromptEngine:
    global _engine
    if _engine is None:
        model_path = os.environ.get("REPROMPT_MODEL_PATH")
        backend_value = os.environ.get("REPROMPT_BACKEND", "llama")
        if backend_value not in ("llama", "llama-py"):
            raise RuntimeError(f"unsupported inference backend: {backend_value}")
        backend = cast(BackendName, backend_value)
        gpu_layers = int(os.environ.get("REPROMPT_GPU_LAYERS", "33"))
        ctx = int(os.environ.get("REPROMPT_CTX_SIZE", "8192"))
        _engine = RepromptEngine(
            model=model_path,
            backend=backend,
            n_gpu_layers=gpu_layers,
            ctx_size=ctx,
        )
    return _engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    _get_engine()
    yield


app = FastAPI(
    title="reprompt",
    version=__version__,
    description="Prompt rewriting API — turns raw inputs into structured, optimized prompts.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class RewriteRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10_000)
    target: TargetProfile = "generic"
    task: TaskProfile = "auto"
    detail: DetailLevel = "balanced"
    explain: bool = False
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1, le=4096)


class RewriteResponse(BaseModel):
    rewritten_prompt: str
    target: str
    task: str
    detail: str
    model: str | None
    elapsed_ms: int


class BatchRequest(BaseModel):
    prompts: list[str] = Field(..., min_length=1, max_length=50)
    target: TargetProfile = "generic"
    task: TaskProfile = "auto"
    detail: DetailLevel = "balanced"


class BatchResponse(BaseModel):
    results: list[RewriteResponse]
    total_elapsed_ms: int


class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        version=__version__,
        model_loaded=_engine is not None,
    )


@app.get("/v1/targets")
def list_targets():
    return {"targets": list(TARGET_PROFILES)}


@app.get("/v1/profiles")
def list_profiles():
    return {
        "targets": list(TARGET_PROFILES),
        "tasks": list(TASK_PROFILES),
        "detail_levels": list(DETAIL_LEVELS),
    }


@app.post("/v1/rewrite", response_model=RewriteResponse)
def rewrite(req: RewriteRequest):
    engine = _get_engine()
    t0 = time.perf_counter()
    try:
        result = engine.rewrite(
            prompt=req.prompt,
            target=req.target,
            explain=req.explain,
            task=req.task,
            detail=req.detail,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    elapsed = int((time.perf_counter() - t0) * 1000)
    return RewriteResponse(
        rewritten_prompt=result.text,
        target=result.target,
        task=result.task,
        detail=result.detail,
        model=result.model_path,
        elapsed_ms=elapsed,
    )


@app.post("/v1/batch", response_model=BatchResponse)
def batch_rewrite(req: BatchRequest):
    engine = _get_engine()
    t0 = time.perf_counter()
    results = []
    for prompt_text in req.prompts:
        step_t0 = time.perf_counter()
        try:
            rewrite_result = engine.rewrite(
                prompt=prompt_text,
                target=req.target,
                task=req.task,
                detail=req.detail,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        step_ms = int((time.perf_counter() - step_t0) * 1000)
        results.append(
            RewriteResponse(
                rewritten_prompt=rewrite_result.text,
                target=rewrite_result.target,
                task=rewrite_result.task,
                detail=rewrite_result.detail,
                model=rewrite_result.model_path,
                elapsed_ms=step_ms,
            )
        )
    total = int((time.perf_counter() - t0) * 1000)
    return BatchResponse(results=results, total_elapsed_ms=total)


@app.post("/v1/chat/completions")
def openai_compat(body: dict):
    """OpenAI-compatible endpoint so tools expecting the ChatCompletions API
    can talk to reprompt without code changes."""
    messages = body.get("messages", [])
    user_msg = ""
    target: TargetProfile = "generic"

    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "user":
            user_msg = content
        elif role == "system" and "claude" in content.lower():
            target = "claude-code"
        elif role == "system" and "chatgpt" in content.lower():
            target = "chatgpt"
        elif role == "system" and "cursor" in content.lower():
            target = "cursor"

    if not user_msg:
        raise HTTPException(400, "no user message found")

    engine = _get_engine()
    result = engine.rewrite(prompt=user_msg, target=target)

    return {
        "id": "clarify-0",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": result.text},
                "finish_reason": "stop",
            }
        ],
        "model": "reprompt",
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }
