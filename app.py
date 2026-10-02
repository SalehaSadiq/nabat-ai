import json, streamlit as st
from pathlib import Path
st.set_page_config(page_title="NabatAI",page_icon="🌱",layout="wide")
ROOT=Path(__file__).parent
st.markdown("""<style>.block-container{max-width:1100px;padding-top:2rem}.hero{padding:2rem;border-radius:20px;background:#eef5ea}.small{color:#52645a}.stButton button{border-radius:10px;font-weight:600}</style>""",unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🌱 NabatAI</h1><h3>Evidence-Based Plant Biotechnology & Crop Decision Support for Pakistan</h3><p>Don’t guess. Identify uncertainty. Ask for evidence. Re-evaluate. Escalate risky decisions. Then build a practical plan.</p></div>',unsafe_allow_html=True)
st.write("")
st.info("NabatAI provides decision support, not guaranteed diagnosis. Critical agricultural and financial decisions should be confirmed with qualified local professionals.")
st.subheader("How it works")
st.write("**1. Tell us the problem → 2. Initial assessment → 3. Add evidence → 4. Re-evaluation → 5. Compare options → 6. Crop plan**")
st.subheader("Start")
if st.button("Create / open a crop case",type="primary",use_container_width=True): st.switch_page("pages/1_new_case.py")
st.caption("No account or persistent database is required. Export your case as JSON and upload it later to continue.")
