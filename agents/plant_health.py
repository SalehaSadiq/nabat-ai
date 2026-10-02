from services.llm import LLMService

def _fallback(case):
    text=" ".join(case.get("symptoms",[])).lower(); crop=str(case.get("crop","")).lower()
    hs=[]
    if "yellow" in text or "peel" in text: hs += [{"name":"Nutrient availability problem","category":"nutrient deficiency","confidence":"MODERATE","rationale":"Yellowing and poor growth can be consistent with nutrient availability issues, but are not specific.","missing_evidence":["soil pH/EC and nutrient status"]},{"name":"Root-zone or irrigation stress","category":"water stress","confidence":"LOW","rationale":"Root-zone stress can produce similar symptoms.","missing_evidence":["soil moisture and root condition"]}]
    if "curl" in text or "whitefly" in text: hs += [{"name":"Whitefly-associated viral disease","category":"disease","confidence":"MODERATE","rationale":"Leaf curl plus whitefly observation warrants viral disease consideration.","missing_evidence":["expert inspection or diagnostic confirmation"]}]
    if crop=="potato": hs += [{"name":"Seed-borne disease carryover","category":"disease","confidence":"MODERATE","rationale":"Repeated disease history can justify checking planting-material health.","missing_evidence":["seed source and diagnostic history"]}]
    if not hs: hs=[{"name":"Multiple causes remain plausible","category":"uncertain","confidence":"LOW","rationale":"Symptoms alone are insufficient for a reliable conclusion.","missing_evidence":["field observations or testing"]}]
    return {"hypotheses":hs[:4],"uncertainty":"Preliminary assessment; symptoms may overlap across causes."}

def run(case, evidence=None):
    payload={"case":case,"confirmed_evidence":evidence or {}}
    return LLMService().json_call("You are the Plant Health Agent. Generate 2-4 competing hypotheses, qualitative confidence LOW/MODERATE/HIGH, rationale and missing evidence. Never claim certainty. Return JSON.",payload,_fallback(case))
