def pkr(value):
    try: return f"Rs. {float(value):,.0f}"
    except (TypeError, ValueError): return "—"

def badge(level: str) -> str:
    return {"GREEN":"🟢", "YELLOW":"🟡", "RED":"🔴", "HIGH":"●●●", "MODERATE":"●●○", "LOW":"●○○"}.get(level, "•")
