import json
from pathlib import Path
from services.llm import LLMService
ROOT=Path(__file__).resolve().parents[1]
def run(case,assessment,skeptic):
    crop=str(case.get("crop","")).lower(); symptom=" ".join(case.get("symptoms",[])).lower(); tests=json.loads((ROOT/"data/test_catalog.json").read_text())
    chosen=[]
    if "yellow" in symptom or "poor growth" in symptom: chosen=[tests[0]]
    elif "curl" in symptom or "whitefly" in symptom: chosen=[tests[2],tests[3]]
    elif crop=="potato": chosen=[tests[3]]
    else: chosen=[tests[4]]
    fallback={"tests":chosen[:2],"principle":"Recommend the minimum evidence likely to change the decision."}
    return LLMService().json_call("You are the Evidence/Test Agent. Recommend the MINIMUM useful additional evidence. Include priority, why, decision change, editable estimated PKR cost, essential/optional, evidence strength. Return JSON.",{"case":case,"assessment":assessment,"skeptic":skeptic,"catalog":tests},fallback)
