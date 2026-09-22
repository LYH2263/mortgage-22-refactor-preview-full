import pytest
from app.engines.amortization import equal_payment_schedule, truncate_preview

def test_monthly_payment():
    s = equal_payment_schedule(1_000_000, 3.5, 360)
    assert s["monthly_payment"] == 4490.45

def test_first_period_interest():
    s = equal_payment_schedule(1_000_000, 3.5, 360)
    assert s["rows"][0]["interest"] == 2916.67
    assert s["rows"][0]["period"] == 1

def test_zero_rate():
    s = equal_payment_schedule(120000, 0, 12)
    assert s["monthly_payment"] == 10000.0

def test_bad_months():
    with pytest.raises(ValueError):
        equal_payment_schedule(100, 3, 0)

def test_truncate_default_preview_and_row_count():
    full = equal_payment_schedule(1_000_000, 3.5, 360)
    payload = truncate_preview(full)
    assert payload["row_count"] == 360
    assert len(payload["preview"]) == 12
    assert payload["preview"][0]["interest"] == 2916.67

def test_truncate_preview_rows_equals_total():
    full = equal_payment_schedule(1_000_000, 3.5, 360)
    payload = truncate_preview(full, 360)
    assert len(payload["preview"]) == 360
    assert payload["row_count"] == 360
    assert payload["preview"][-1]["period"] == 360
    assert payload["preview"][-1]["balance"] == 0.0

def test_truncate_does_not_rewrite_full_balances():
    full = equal_payment_schedule(1_000_000, 3.5, 360)
    balances_before = [r["balance"] for r in full["rows"]]
    truncate_preview(full, 12)
    assert [r["balance"] for r in full["rows"]] == balances_before
    assert len(full["rows"]) == 360
