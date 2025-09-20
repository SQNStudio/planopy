from datetime import date, timedelta
from typing import List, Literal

import pandas as pd
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/")
def root():
    return {"msg": "PlanoPy API online!"}

@app.get("/metrics")
def metrics(
    days: int = Query(30, ge=1, le=365),
    scenario: Literal["base", "otimista", "pessimista"] = "base",
    variation: float = Query(1.0, ge=0.1, le=5.0),
) -> List[dict]:
    """
    Gera uma série temporal fake para demonstração.
    - days: quantos dias para trás
    - scenario: base/otimista/pessimista
    - variation: fator multiplicador
    """
    end = date.today()
    start = end - timedelta(days=days - 1)
    dates = pd.date_range(start, end, freq="D")

    base = 100.0
    drift = {"base": 0.2, "otimista": 0.5, "pessimista": -0.1}[scenario]

    values = []
    val = base
    for _ in dates:
        val = max(0, val + drift)  # passo simples
        values.append(val * variation)

    df = pd.DataFrame({"date": dates.date, "value": values})
    return [
        {"date": d.isoformat(), "value": float(v), "scenario": scenario}
        for d, v in zip(df["date"], df["value"])
    ]
