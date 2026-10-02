import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def references(tags=None):
    data = json.loads((ROOT/"data/reference_library.json").read_text(encoding="utf-8"))
    if not tags: return data
    tags = {str(t).lower() for t in tags}
    return [r for r in data if tags.intersection({x.lower() for x in r.get("tags", [])})]
