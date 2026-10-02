import base64
from services.llm import LLMService

def extract_report(uploaded_file):
    raw=uploaded_file.getvalue(); mime=getattr(uploaded_file,"type","") or "application/octet-stream"
    fallback={"laboratory_name":"", "test_date":"", "pH":None,"EC":None,"organic_matter":None,"nitrogen":None,"phosphorus":None,"potassium":None,"micronutrients":"","pathogen_test":"","ELISA_result":"","PCR_result":"","water_quality":"", "note":"AI extraction unavailable or incomplete; please enter values manually."}
    if mime == "application/pdf":
        try:
            import fitz
            text="\n".join(p.get_text() for p in fitz.open(stream=raw,filetype="pdf"))[:12000]
            return LLMService().json_call("Extract agricultural lab report fields. Return JSON only; use null for unknown values.", {"report_text":text}, fallback)
        except Exception: return fallback
    data_url=f"data:{mime};base64,{base64.b64encode(raw).decode()}"
    return LLMService().json_call("Extract agricultural lab report fields from this image. Return JSON only; never invent unreadable values.", {"task":"report extraction"}, fallback, data_url)
