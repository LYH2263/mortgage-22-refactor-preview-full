def truncate_preview(schedule: dict, preview_rows: int = 12) -> dict:
    """从已生成的全表结果中按 preview_rows 切片，只做只读截断。

    不重新计算、不修改全表的余额序列；row_count 始终为全表总期数。
    preview_rows 大于等于总期数时 preview 即为全表。
    """
    rows = schedule["rows"]
    return {
        "monthly_payment": schedule["monthly_payment"],
        "total_interest": schedule["total_interest"],
        "total_payment": schedule["total_payment"],
        "preview": rows[:preview_rows],
        "row_count": len(rows),
    }

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
