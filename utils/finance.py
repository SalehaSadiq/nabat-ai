from typing import Optional

def area_to_acres(area: float, unit: str) -> Optional[float]:
    if unit == "acre": return area
    if unit == "kanal": return area / 8
    if unit == "marla": return area / 160
    return None

def financial_summary(cost: float, budget: float, crop_value: float | None, area: float, unit: str) -> dict:
    acres = area_to_acres(area, unit)
    return {
        "total_cost": round(cost, 2),
        "remaining_budget": round(budget - cost, 2),
        "cost_per_acre": round(cost / acres, 2) if acres else None,
        "cost_per_kanal": round(cost / (acres * 8), 2) if acres else None,
        "cost_pct_crop_value": round(cost / crop_value * 100, 2) if crop_value else None,
        "break_even_value": round(cost, 2),
    }
