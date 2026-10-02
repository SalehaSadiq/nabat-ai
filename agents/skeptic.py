from services.llm import LLMService

def run(case,assessment):
    fallback={"challenge":"The current leading explanation is not confirmed.","competing_explanations":["environmental/root-zone stress","management or irrigation issue"],"unsupported_assumptions":["symptoms are specific to one cause"],"contradictions":[],"confidence_reduction_reason":"Overlapping symptoms require evidence before treatment."}
    return LLMService().json_call("You are the Skeptic Agent. Try to prove the current diagnosis wrong. Identify competing explanations, missing evidence, unsupported assumptions and contradictions. Return JSON.",{"case":case,"assessment":assessment},fallback)
