from services.llm import LLMService

def run(case,evidence=None):
    ev=evidence or {}; fallback={"assessment":"Nutrition status cannot be confirmed from symptoms alone.","concerns":["pH/EC may alter nutrient availability"],"exact_dose_allowed":False,"next_step":"Use confirmed soil/tissue evidence before exact fertilizer dosing."}
    if ev: fallback={"assessment":"Confirmed laboratory values should be interpreted against crop, stage and local lab reference ranges.","concerns":[],"exact_dose_allowed":False,"next_step":"Use a qualified local agronomist for exact dosage where material financial/crop risk exists."}
    return LLMService().json_call("You are the Nutrition Agent. Evaluate pH, EC, OM, N/P/K, micronutrients, history and stage. No exact fertilizer dosage without sufficient validated evidence. Return JSON.",{"case":case,"evidence":ev},fallback)
