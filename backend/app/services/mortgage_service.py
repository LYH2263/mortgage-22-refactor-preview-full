from app.db import connect
from app.engines.amortization import equal_payment_schedule, truncate_preview
from app.repositories import loans, runs, settings

class MortgageService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_loans(self): return loans.list_all(self._c)
    def loan(self, lid): return loans.get(self._c, lid)
    def settings(self): return settings.get_map(self._c)
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def full_schedule(self, principal, annual_rate, months):
        """第一段：生成完整摊还表（含全表余额序列），不做任何截断。"""
        return equal_payment_schedule(principal, annual_rate, months)
    def preview_payload(self, full, preview_rows=12):
        """第二段：基于全表只读截断出 preview，不改写全表余额序列，row_count 仍为总期数。"""
        return truncate_preview(full, preview_rows)
    def schedule(self, principal, annual_rate, months, loan_id, persist, preview_rows=12):
        full = self.full_schedule(principal, annual_rate, months)
        out = self.preview_payload(full, preview_rows)
        rid = None
        if persist:
            rid = runs.insert(self._c, "schedule", {"principal": principal, "annual_rate": annual_rate, "months": months}, out, loan_id)
        return {"run_id": rid, **out}
    def dashboard(self):
        items = loans.list_all(self._c)
        return {"loan_count": len(items), "clean": len([x for x in items if "种子" not in x["name"]]), "dirty": len([x for x in items if "种子" in x["name"]])}
