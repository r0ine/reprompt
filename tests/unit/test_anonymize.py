from __future__ import annotations

import pytest


def test_anonymize_strips_email_and_ip_and_token() -> None:
    pytest.importorskip("training.data.anonymize", reason="training package not on path in CI")
    from training.data.anonymize import anonymize
    fake_key = "sk-" + "FAKE" + "0123456789ABCDEFGHIJ"
    text = f"reach me at user@example.org from 10.0.0.5 with {fake_key}"
    out = anonymize(text)
    assert "@" not in out
    assert "10.0.0.5" not in out
    assert fake_key not in out
    assert "<EMAIL>" in out
    assert "<IP>" in out
    assert "<API_KEY>" in out
