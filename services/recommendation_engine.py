import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name): return json.loads((ROOT/f"data/{name}.json").read_text(encoding="utf-8"))
def recommendations_for(crop): return [x for x in load("recommendations") if crop.lower() in [c.lower() for c in x.get("crops",[])]]
