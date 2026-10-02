import json

def validate_case_json(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict): raise ValueError("Case file must contain a JSON object.")
    return data

def clean_number(value, default=0.0):
    try: return float(value)
    except (TypeError, ValueError): return default
