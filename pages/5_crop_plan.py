from services.pdf_report import generate_case_pdf
case_export = {
    "profile": st.session_state.get("profile", {}),
    "problem_description": st.session_state.get(
        "problem_description", ""
    ),
    "first_assessment": st.session_state.get(
        "first_assessment", {}
    ),
    "requested_tests": st.session_state.get(
        "requested_tests", []
    ),
    "uploaded_results": st.session_state.get(
        "uploaded_results", {}
    ),
    "confirmed_values": st.session_state.get(
        "confirmed_values", {}
    ),
    "second_assessment": st.session_state.get(
        "second_assessment", {}
    ),
    "options": st.session_state.get(
        "options", {}
    ),
    "recommendations": st.session_state.get(
        "recommendations", {}
    ),
    "financial_summary": st.session_state.get(
        "financial_summary", {}
    ),
    "plan": st.session_state.get(
        "crop_plan", {}
    ),
    "references": st.session_state.get(
        "references", []
    ),
    "expert_review": st.session_state.get(
        "expert_review", {}
    ),
}
import json

json_bytes = json.dumps(
    case_export,
    indent=2,
    ensure_ascii=False,
).encode("utf-8")
try:
    pdf_bytes = generate_case_pdf(case_export)
except Exception as exc:
    pdf_bytes = None
    st.error(f"Could not generate PDF report: {exc}")
st.subheader("📥 Export Your Case")

col1, col2 = st.columns(2)

with col1:
    st.download_button(
        label="📄 Download Full PDF Report",
        data=pdf_bytes,
        file_name="NabatAI_Crop_Report.pdf",
        mime="application/pdf",
        use_container_width=True,
        disabled=pdf_bytes is None,
    )

with col2:
    st.download_button(
        label="💾 Download Case JSON",
        data=json_bytes,
        file_name="nabat_case.json",
        mime="application/json",
        use_container_width=True,
    )
