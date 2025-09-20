from datetime import date, timedelta
from typing import List, Literal

import pandas as pd
from fastapi import FastAPI, Query

app = FastAPI(title="PlanoPy API")

@app.get("/")
def root():
    return {"msg": "PlanoPy API online!"}

@app.get("/metrics")
def metrics(
    days: int = Query(30, ge=1, le=365, description="Quantidade de dias históricos"),
    scenario: Literal["base", "otimista", "pessimista"] = "base",
    variation: float = Query(1.0, ge=0.1, le=5.0, description="Fator multiplicador"),
) -> List[dict]:
    """
    Gera uma série temporal sintética de exemplo.
    """
    end = date.today()
    start = end - timedelta(days=days - 1)

    dates = pd.date_range(start, end, freq="D").date
    drift = {"base": 0.2, "otimista": 0.5, "pessimista": -0.1}[scenario]

    values = []
    val = 100.0
    for _ in dates:
        val = max(0, val + drift)
        values.append(val * variation)

    return [
        {"date": d.isoformat(), "value": float(v), "scenario": scenario}
        for d, v in zip(dates, values)
    ]
