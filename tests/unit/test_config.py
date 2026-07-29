"""ClarifyConfig testleri — torch gerektirmeden calisir.

training.model.__init__ torch'a bagli oldugu icin, config parametreleri
burada bagimsiz olarak dogrudan test ediliyor.
"""

from __future__ import annotations


def auto_hidden_dim(dim: int) -> int:
    raw = int(dim * 8 / 3)
    return raw + (64 - raw % 64) if raw % 64 else raw


PRESETS = {
    "SMALL": {
        "vocab_size": 12_000,
        "max_seq_len": 1024,
        "dim": 512,
        "n_layers": 8,
        "n_heads": 8,
        "n_kv_heads": 4,
        "dropout": 0.1,
    },
    "BASE": {
        "vocab_size": 12_000,
        "max_seq_len": 1024,
        "dim": 768,
        "n_layers": 12,
        "n_heads": 12,
        "n_kv_heads": 4,
        "dropout": 0.05,
    },
    "LARGE": {
        "vocab_size": 12_000,
        "max_seq_len": 1024,
        "dim": 1024,
        "n_layers": 16,
        "n_heads": 16,
        "n_kv_heads": 4,
        "dropout": 0.05,
    },
    "XLARGE": {
        "vocab_size": 12_000,
        "max_seq_len": 1024,
        "dim": 1280,
        "n_layers": 20,
        "n_heads": 20,
        "n_kv_heads": 4,
        "dropout": 0.05,
    },
}


class TestHiddenDim:
    def test_auto_alignment_512(self):
        assert auto_hidden_dim(512) % 64 == 0

    def test_auto_alignment_768(self):
        assert auto_hidden_dim(768) % 64 == 0

    def test_auto_alignment_1024(self):
        assert auto_hidden_dim(1024) % 64 == 0

    def test_value_for_768(self):
        assert auto_hidden_dim(768) == 2048

    def test_value_for_1024(self):
        result = auto_hidden_dim(1024)
        raw = int(1024 * 8 / 3)
        assert result >= raw
        assert result % 64 == 0

    def test_auto_alignment_1280(self):
        result = auto_hidden_dim(1280)
        assert result % 64 == 0
        assert result >= int(1280 * 8 / 3)


class TestPresets:
    def test_all_use_12k_vocab(self):
        for name, cfg in PRESETS.items():
            assert cfg["vocab_size"] == 12_000, name

    def test_all_max_seq_1024(self):
        for name, cfg in PRESETS.items():
            assert cfg["max_seq_len"] == 1024, name

    def test_small_dimensions(self):
        s = PRESETS["SMALL"]
        assert s["dim"] == 512
        assert s["n_layers"] == 8
        assert s["n_heads"] == 8

    def test_base_dimensions(self):
        b = PRESETS["BASE"]
        assert b["dim"] == 768
        assert b["n_layers"] == 12
        assert b["n_heads"] == 12

    def test_large_dimensions(self):
        large_config = PRESETS["LARGE"]
        assert large_config["dim"] == 1024
        assert large_config["n_layers"] == 16
        assert large_config["n_heads"] == 16
        assert large_config["n_kv_heads"] == 4

    def test_kv_heads_divide_n_heads(self):
        for name, cfg in PRESETS.items():
            assert cfg["n_heads"] % cfg["n_kv_heads"] == 0, name

    def test_head_dim_consistency(self):
        for name, cfg in PRESETS.items():
            assert cfg["dim"] % cfg["n_heads"] == 0, name
            head_dim = cfg["dim"] // cfg["n_heads"]
            assert head_dim == 64, f"{name}: head_dim={head_dim}"

    def test_xlarge_dimensions(self):
        xl = PRESETS["XLARGE"]
        assert xl["dim"] == 1280
        assert xl["n_layers"] == 20
        assert xl["n_heads"] == 20
        assert xl["n_kv_heads"] == 4

    def test_dim_increases_with_preset_size(self):
        assert (
            PRESETS["SMALL"]["dim"]
            < PRESETS["BASE"]["dim"]
            < PRESETS["LARGE"]["dim"]
            < PRESETS["XLARGE"]["dim"]
        )

    def test_layers_increase_with_preset_size(self):
        assert (
            PRESETS["SMALL"]["n_layers"]
            < PRESETS["BASE"]["n_layers"]
            < PRESETS["LARGE"]["n_layers"]
            < PRESETS["XLARGE"]["n_layers"]
        )
