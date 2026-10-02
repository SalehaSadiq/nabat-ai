import json,streamlit as st
from utils.formatting import pkr
st.title("5 · CropCare plan")
plan=st.session_state.get("plan")
if not plan: st.warning("Build options first."); st.stop()
for period in ["Today","Next 7 Days","Next 30 Days","Next Crop Stage","Harvest / End of Season","Next Season"]:
    st.subheader(period)
    for x in plan.get(period,[]):
        with st.container(border=True): st.write(f"**{x['action']}**"); st.caption(f"Estimated cost: {pkr(x['cost_pkr'])} · Priority: {x['priority']} · Follow-up: {x['checkpoint']}")
st.metric("Estimated selected-plan cost",pkr(plan.get("estimated_plan_cost_pkr",0)))
st.info("Laboratory results, weather, field conditions and crop response may change this plan. Re-evaluate when new evidence appears.")
case={k:st.session_state.get(k) for k in ["profile","first_assessment","report_extraction","confirmed_values","second_assessment","options","plan","expert_review"]}
st.download_button("Download nabat_case.json",json.dumps(case,ensure_ascii=False,indent=2,default=str),file_name="nabat_case.json",mime="application/json",use_container_width=True)
