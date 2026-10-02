import os,streamlit as st
st.title("6 · Expert Mode")
try: secret=st.secrets.get("EXPERT_PASSWORD",os.getenv("EXPERT_PASSWORD",""))
except Exception: secret=os.getenv("EXPERT_PASSWORD","")
if not secret: st.warning("Set EXPERT_PASSWORD in Streamlit secrets or environment variables to enable Expert Mode."); st.stop()
pw=st.text_input("Expert password",type="password")
if pw!=secret: st.info("Enter the configured expert password."); st.stop()
a=st.session_state.get("second_assessment") or st.session_state.get("first_assessment")
if not a: st.warning("No active case."); st.stop()
st.success("Expert access enabled for this session.")
st.json({"profile":st.session_state.get("profile"),"assessment":a,"confirmed_values":st.session_state.get("confirmed_values",{})})
decision=st.radio("Decision",["Approve","Modify","Reject","Request additional evidence"]); note=st.text_area("Expert note")
if st.button("Save expert review",type="primary"):
    st.session_state.expert_review={"decision":decision,"note":note}; st.success("Saved in this session only.")
if decision == "Modify":

    modified_recommendation = st.text_area(
        "Revised recommendation",
        value=current_recommendation,
    )

    additional_test = st.text_input(
        "Additional evidence/test required"
    )

    revised_cost = st.number_input(
        "Revised estimated cost (PKR)",
        min_value=0,
    )
st.session_state["expert_review"] = {
    "decision": decision,
    "note": expert_note,
    "modified_recommendation": modified_recommendation,
    "additional_test": additional_test,
    "revised_cost_pkr": revised_cost,
}    
