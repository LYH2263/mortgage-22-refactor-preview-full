def equal_payment_schedule(principal: float, annual_rate: float, months: int) -> dict:
    P = float(principal)
    n = int(months)
    r = float(annual_rate) / 12.0 / 100.0
    if n <= 0:
        raise ValueError("months")
    if r == 0:
        pay = P / n
    else:
        pay = P * r * (1 + r) ** n / ((1 + r) ** n - 1)
    rows = []
    bal = P
    interest_sum = 0.0
    for i in range(1, n + 1):
        interest = bal * r
        principal_part = pay - interest
        if i == n:
            principal_part = bal
            pay_i = principal_part + interest
        else:
            pay_i = pay
        bal = max(0.0, bal - principal_part)
        interest_sum += interest
        rows.append({
            "period": i,
            "payment": round(pay_i, 2),
            "principal": round(principal_part, 2),
            "interest": round(interest, 2),
            "balance": round(bal, 2),
        })
    return {
        "monthly_payment": round(pay if n else 0, 2),
        "total_interest": round(interest_sum, 2),
        "total_payment": round(sum(x["payment"] for x in rows), 2),
        "rows": rows,
    }


def truncate_rows(rows: list, preview_rows: int) -> list:
    """截取全表前 preview_rows 行作为预览。

    纯截断：只对全表做切片，不重算、不改写全表的余额序列。
    """
    return list(rows[:preview_rows])


def schedule_response(full: dict, preview_rows: int) -> dict:
    """由全表组装 schedule 回包：汇总值 + 截断预览 + 总期数。"""
    return {
        "monthly_payment": full["monthly_payment"],
        "total_interest": full["total_interest"],
        "total_payment": full["total_payment"],
        "preview": truncate_rows(full["rows"], preview_rows),
        "row_count": len(full["rows"]),
    }
