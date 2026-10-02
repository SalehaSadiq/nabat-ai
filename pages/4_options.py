import streamlit as st
from agents.orchestrator import build_options
from utils.formatting import pkr
st.title("4 · Compare options")
profile=st.session_state.get("profile"); assessment=st.session_state.get("second_assessment") or st.session_state.get("first_assessment")
if not profile or not assessment: st.warning("Create and assess a case first."); st.stop()
if "options" not in st.session_state: st.session_state.options=build_options(profile,assessment)
o=st.session_state.options
for p in o["pathways"]:
    label="⭐ BEST VALUE" if p["name"]=="Best Value" else p["name"].upper()
    with st.container(border=True):
        st.subheader(label); st.metric("Estimated cost",pkr(p["estimated_cost_pkr"])); st.write(f"**Expected effectiveness:** {p['effectiveness']}  |  **Evidence strength:** {p['evidence_strength']}"); st.write(p["tradeoff"]); st.write("**Actions:** "+" · ".join(p["actions"])); st.caption(p["accessibility"]); st.write("Affordable within entered budget: "+("Yes" if p["affordable"] else "No")); f=p["finance"]; st.caption(f"Remaining budget: {pkr(f['remaining_budget'])} · Break-even direct value: {pkr(f['break_even_value'])}")
st.caption("Costs are editable demo estimates, not current market quotations. No unsupported yield or ROI claim is made.")
with st.expander("I can't afford this"):
    b=st.number_input("What can you afford right now? (PKR)",min_value=0.0,value=float(profile.get("budget",0)),step=500.0)
    if st.button("Rebuild within this budget"):
        st.session_state.options=build_options(profile,assessment,b); st.rerun()
if st.button("Build CropCare plan",type="primary",use_container_width=True):
    from agents.orchestrator import build_plan
    st.session_state.plan=build_plan(profile,st.session_state.options); st.switch_page("pages/5_crop_plan.py")
