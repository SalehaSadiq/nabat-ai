import json,streamlit as st
from utils.formatting import pkr,badge
st.title("2 · Initial assessment")
a=st.session_state.get("first_assessment")
if not a: st.warning("Create a case first."); st.stop()
st.warning("Preliminary assessment only — collect evidence before high-impact spending or treatment.")
st.subheader("Possible causes")
for h in a["plant_health"].get("hypotheses",[]):
    with st.container(border=True): st.markdown(f"**{h.get('name')}** · {badge(h.get('confidence'))} {h.get('confidence')}"); st.write(h.get("rationale","")); st.caption("Missing: "+", ".join(h.get("missing_evidence",[])))
st.subheader("What we still don't know")
st.write(a["skeptic"].get("challenge")); st.caption("Competing explanations: "+", ".join(a["skeptic"].get("competing_explanations",[])))
st.subheader("Recommended evidence")
for t in a["evidence"].get("tests",[]):
    with st.container(border=True): st.markdown(f"**{t.get('name')}** — {pkr(t.get('estimated_cost_pkr'))} *(editable demo estimate)*"); st.write(t.get("why_needed")); st.caption("Could change: "+t.get("decision_change",""))
st.error("💸 **Don't Spend Yet** — avoid random micronutrient mixtures, unnecessary fertilizer, or expensive treatment until the key uncertainty is reduced.")
s=a["safety"]; st.markdown(f"### Safety gate: {badge(s['level'])} {s['level']}"); st.write(" ".join(s.get("reasons",[])))
with st.expander("See how the AI team worked"):
    st.write("✅ Intake Agent — case structured\n\n✅ Plant Agent — competing hypotheses evaluated\n\n✅ Nutrition Agent — evidence threshold checked\n\n✅ Biotechnology Agent — relevance screened\n\n✅ Skeptic Agent — assumptions challenged\n\n✅ Evidence Agent — minimum useful evidence selected\n\n✅ Safety Agent — risk gate applied")
with st.expander("Research references"):
    for r in a.get("references",[]): st.markdown(f"**{r['title']}** — {r['organization']} ({r['year']}) · Tier {r['evidence_tier']}\n\n{r['relevance']} [Source]({r['url']})\n\n*Limitation: {r['limitation']}*")
if st.button("Add lab / field evidence",type="primary",use_container_width=True): st.switch_page("pages/3_upload_report.py")
