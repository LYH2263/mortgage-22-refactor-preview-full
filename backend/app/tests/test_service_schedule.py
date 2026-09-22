from app.services.mortgage_service import MortgageService
from app.repositories import runs

def _service():
    s = MortgageService()
    s._c.execute("""
    CREATE TABLE IF NOT EXISTS calc_runs(id INTEGER PRIMARY KEY, kind TEXT, loan_id INTEGER,
        input_json TEXT, result_json TEXT, created_at TEXT)
    """)
    return s

def test_schedule_default_preview_rows_is_twelve():
    with _service() as s:
        out = s.schedule(1_000_000, 3.5, 360, None, False)
    assert out["row_count"] == 360
    assert len(out["preview"]) == 12
    assert out["preview"][0]["interest"] == 2916.67
    assert out["run_id"] is None

def test_schedule_preview_rows_equals_total():
    with _service() as s:
        out = s.schedule(1_000_000, 3.5, 360, None, False, preview_rows=360)
    assert len(out["preview"]) == 360
    assert out["row_count"] == 360

def test_stages_independently_callable_and_full_unaffected():
    with _service() as s:
        full = s.full_schedule(1_000_000, 3.5, 360)
        assert len(full["rows"]) == 360
        payload = s.preview_payload(full, preview_rows=12)
    assert len(payload["preview"]) == 12
    assert payload["row_count"] == 360
    assert len(full["rows"]) == 360

def test_persist_false_writes_nothing():
    with _service() as s:
        before = len(runs.list_recent(s._c, 1000))
        out = s.schedule(1_000_000, 3.5, 360, None, False)
        after = runs.list_recent(s._c, 1000)
    assert out["run_id"] is None
    assert len(after) == before

def test_persist_true_writes_run_and_returns_id():
    with _service() as s:
        before = len(runs.list_recent(s._c, 1000))
        out = s.schedule(1_000_000, 3.5, 360, None, True)
        after = runs.list_recent(s._c, 1000)
    assert isinstance(out["run_id"], int)
    assert len(after) == before + 1
    assert after[0]["kind"] == "schedule"
