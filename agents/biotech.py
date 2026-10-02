from services.llm import LLMService

def run(case,assessment):
    crop=str(case.get("crop","")).lower(); text=str(assessment).lower(); opts=[]
    if "viral" in text or crop=="potato": opts.append({"pathway":"Virus diagnostics / clean planting material","relevance":"Potentially relevant where viral or seed-borne disease is plausible.","action":"Consider diagnostic confirmation and certified disease-free planting material for future cycles."})
    if crop=="potato": opts.append({"pathway":"Tissue-culture-derived clean seed systems","relevance":"Relevant to disease-free potato seed multiplication systems.","action":"Explore certified clean seed sources rather than on-farm tissue culture."})
    fallback={"relevant":bool(opts),"options":opts,"note":"Biotechnology is suggested only when it changes a practical decision."}
    return LLMService().json_call("You are the Biotechnology Agent. Suggest biotech only when genuinely relevant: diagnostics, clean material, resistant varieties, biocontrol etc. Avoid forcing biotech. Return JSON.",{"case":case,"assessment":assessment},fallback)
