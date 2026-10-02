from services.llm import LLMService

def run(profile):
    fallback={"crop":profile.get("crop"),"variety":profile.get("variety"),"growth_stage":profile.get("growth_stage"),"symptoms":[profile.get("problem_description","")],"duration":"not stated","severity":"not stated","location":profile.get("location"),"area":{"value":profile.get("area"),"unit":profile.get("area_unit")},"budget":profile.get("budget"),"previous_treatments":[profile.get("previous_fertilizer",""),profile.get("previous_pesticide","")],"irrigation":profile.get("irrigation"),"available_evidence":[]}
    return LLMService().json_call("You are the Intake Agent. Structure farmer input only. Do not diagnose. Return concise JSON.", profile, fallback)
