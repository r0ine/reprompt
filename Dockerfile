FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential cmake && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE ./
COPY src/ src/

RUN pip install --no-cache-dir ".[all]"

ENV CLARIFY_PROMPT_MODEL_PATH=/models/clarify-prompt.gguf
EXPOSE 8741

ENTRYPOINT ["clarify-prompt"]
CMD ["serve", "--host", "0.0.0.0", "--port", "8741"]
