import streamlit as st
from services.report_parser import extract_report
st.title("3 · Add evidence")
if not st.session_state.get("first_assessment"): st.warning("Run the initial assessment first."); st.stop()
f=st.file_uploader("Upload report (PDF, PNG, JPG, JPEG)",type=["pdf","png","jpg","jpeg"])
if f and st.button("Extract values"):
    with st.spinner("Reading report..."): st.session_state.report_extraction=extract_report(f)
ex=st.session_state.get("report_extraction",{})
if ex:
    st.subheader("Confirm Extracted Values")
    st.info("Mandatory human-in-the-loop step: edit anything incorrect. Values are not used until you confirm them.")
    fields=["laboratory_name","test_date","pH","EC","organic_matter","nitrogen","phosphorus","potassium","micronutrients","pathogen_test","ELISA_result","PCR_result","water_quality"]
    confirmed={}
    with st.form("confirm"):
        for k in fields: confirmed[k]=st.text_input(k.replace("_"," ").title(),"" if ex.get(k) is None else str(ex.get(k)))
        c1,c2=st.columns(2); ok=c1.form_submit_button("Confirm and re-evaluate",type="primary",use_container_width=True); reject=c2.form_submit_button("Reject extraction",use_container_width=True)
    if reject: st.session_state.report_extraction={}; st.rerun()
    if ok:
        st.session_state.confirmed_values=confirmed
        from agents.orchestrator import second_round
        with st.spinner("Re-evaluating from confirmed evidence..."): st.session_state.second_assessment=second_round(st.session_state.profile,confirmed,st.session_state.first_assessment)
        st.rerun()
if st.session_state.get("second_assessment"):
    b=st.session_state.first_assessment; a=st.session_state.second_assessment
    st.divider(); st.subheader("Before test vs after test")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("**BEFORE TEST**"); [st.write(f"• {x.get('name')} — {x.get('confidence')}") for x in b["plant_health"].get("hypotheses",[])]
    with c2:
        st.markdown("**AFTER TEST**"); [st.write(f"• {x.get('name')} — {x.get('confidence')}") for x in a["plant_health"].get("hypotheses",[])]
    st.info("**Why did our assessment change?** "+a.get("change_explanation",""))
    if st.button("Compare affordable options",type="primary",use_container_width=True): st.switch_page("pages/4_options.py")
else:
    st.caption("No report? You can still continue with the preliminary assessment, but uncertainty remains.")
    if st.button("Compare preliminary options anyway"): st.switch_page("pages/4_options.py")
