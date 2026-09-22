import pytest
from app.engines.amortization import equal_payment_schedule, schedule_response, truncate_rows

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

def test_response_row_count_and_first_interest():
    out = schedule_response(equal_payment_schedule(1_000_000, 3.5, 360), 12)
    assert out["row_count"] == 360
    assert out["preview"][0]["interest"] == 2916.67

def test_response_default_preview_length():
    out = schedule_response(equal_payment_schedule(1_000_000, 3.5, 360), 12)
    assert len(out["preview"]) == 12
    assert out["row_count"] == 360

def test_response_preview_rows_equals_total():
    out = schedule_response(equal_payment_schedule(1_000_000, 3.5, 360), 360)
    assert len(out["preview"]) == 360
    assert out["row_count"] == 360

def test_truncate_keeps_full_table_balances():
    full = equal_payment_schedule(1_000_000, 3.5, 360)
    before = [dict(r) for r in full["rows"]]
    preview = truncate_rows(full["rows"], 12)
    assert preview == before[:12]
    assert full["rows"] == before
