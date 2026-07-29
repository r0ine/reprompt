"""Model parametrelerini hesapla — torch gerekmeden.

Kullanim:
    python -m training.model.count_params
"""

from training.model.config import ClarifyConfig, SMALL, BASE, LARGE


def count_params(cfg: ClarifyConfig) -> dict[str, int]:
    d = cfg.dim
    h = cfg.hidden_dim
    n = cfg.n_layers
    v = cfg.vocab_size
    hd = cfg.head_dim
    nh = cfg.n_heads
    nkv = cfg.n_kv_heads

    tok_emb = v * d
    per_layer_attn = d * nh * hd + d * nkv * hd + d * nkv * hd + nh * hd * d
    per_layer_ffn = d * h + h * d + d * h
    per_layer_norm = d * 2
    total_layers = n * (per_layer_attn + per_layer_ffn + per_layer_norm)
    final_norm = d
    lm_head = 0 if cfg.tie_embeddings else v * d

    total = tok_emb + total_layers + final_norm + lm_head
    return {
        "tok_emb": tok_emb,
        "per_layer": per_layer_attn + per_layer_ffn + per_layer_norm,
        "layers_total": total_layers,
        "final_norm": final_norm,
        "lm_head": lm_head,
        "total": total,
    }


def format_m(n: int) -> str:
    return f"{n / 1_000_000:.1f}M"


if __name__ == "__main__":
    for name, cfg in [("SMALL", SMALL), ("BASE", BASE), ("LARGE", LARGE)]:
        p = count_params(cfg)
        print(f"{name}: {format_m(p['total'])} parametre")
        print(f"  Embedding: {format_m(p['tok_emb'])}")
        print(f"  Katman basina: {format_m(p['per_layer'])} x {cfg.n_layers}")
        print(f"  dim={cfg.dim}, n_layers={cfg.n_layers}, n_heads={cfg.n_heads}, "
              f"hidden_dim={cfg.hidden_dim}")
        fp16_gb = p["total"] * 2 / (1024 ** 3)
        train_gb = p["total"] * 2 * 4 / (1024 ** 3)
        print(f"  FP16 boyut: {fp16_gb:.2f} GB | Egitim tahmini: {train_gb:.2f} GB")
        print()
