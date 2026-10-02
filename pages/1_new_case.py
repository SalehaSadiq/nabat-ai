import json,streamlit as st
from pathlib import Path
from utils.validators import validate_case_json
ROOT=Path(__file__).resolve().parents[1]
st.title("1 · Tell us the problem")
if "profile" not in st.session_state: st.session_state.profile={}
demos=json.loads((ROOT/"data/demo_cases.json").read_text())
choice=st.selectbox("Optional demo case",["Start blank"]+[d["name"] for d in demos])
if st.button("Load selected demo") and choice!="Start blank":
    st.session_state.profile=next(d["profile"] for d in demos if d["name"]==choice); st.rerun()
upload=st.file_uploader("Continue a saved NabatAI case (.json)",type=["json"])
if upload and st.button("Import case"):
    try:
        data=validate_case_json(upload.getvalue()); st.session_state.update(data); st.success("Case imported.")
    except Exception as e:
        st.error(f"Could not import: {e}")
p=st.session_state.profile
with st.form("intake"):
    c1,c2=st.columns(2)
    user_type=c1.selectbox("User type",["Farmer","Commercial Grower","Home Grower"],index=["Farmer","Commercial Grower","Home Grower"].index(p.get("user_type","Farmer")))
    language=c2.selectbox("Language",["English","Urdu","Roman Urdu"],index=["English","Urdu","Roman Urdu"].index(p.get("language","English")))
    crop=c1.selectbox("Crop",["Wheat","Tomato","Potato","Chilli","Citrus"],index=["Wheat","Tomato","Potato","Chilli","Citrus"].index(p.get("crop","Wheat")))
    variety=c2.text_input("Variety (optional)",p.get("variety","")); location=c1.text_input("District / location",p.get("location","")); area=c2.number_input("Area",min_value=0.0,value=float(p.get("area",1)))
    area_unit=c1.selectbox("Area unit",["acre","kanal","marla","pots"],index=["acre","kanal","marla","pots"].index(p.get("area_unit","acre")))
    crop_age=c2.text_input("Crop age",p.get("crop_age","")); growth_stage=c1.text_input("Growth stage",p.get("growth_stage","")); purpose=c2.selectbox("Purpose",["commercial","home consumption"],index=0 if p.get("purpose","commercial")=="commercial" else 1)
    budget=c1.number_input("Available budget (PKR)",min_value=0.0,value=float(p.get("budget",0)),step=500.0); expected=c2.number_input("Expected crop value (PKR, optional)",min_value=0.0,value=float(p.get("expected_crop_value",0) or 0),step=1000.0)
    irrigation=c1.selectbox("Irrigation source",["canal","tube well","rain","tap","other"],index=["canal","tube well","rain","tap","other"].index(p.get("irrigation","canal")))
    soil=c2.selectbox("Known soil test?",["no","yes"],index=1 if p.get("known_soil_test")=="yes" else 0); water=c1.selectbox("Known water test?",["no","yes"],index=1 if p.get("known_water_test")=="yes" else 0)
    fert=st.text_input("Previous fertilizer applications (optional)",p.get("previous_fertilizer","")); pest=st.text_input("Previous pesticide applications (optional)",p.get("previous_pesticide","")); problem=st.text_area("Describe the problem — English, Urdu or Roman Urdu",p.get("problem_description",""),height=120)
    photo=st.file_uploader("Plant photo (optional)",type=["png","jpg","jpeg"])
    submitted=st.form_submit_button("Run initial assessment",type="primary",use_container_width=True)
if submitted:
    if not problem.strip(): st.error("Please describe the crop problem.")
    else:
        st.session_state.profile={"user_type":user_type,"language":language,"crop":crop,"variety":variety,"location":location,"area":area,"area_unit":area_unit,"crop_age":crop_age,"growth_stage":growth_stage,"purpose":purpose,"budget":budget,"expected_crop_value":expected or None,"irrigation":irrigation,"known_soil_test":soil,"known_water_test":water,"previous_fertilizer":fert,"previous_pesticide":pest,"problem_description":problem,"photo_metadata":{"name":photo.name,"type":photo.type} if photo else None}
        from agents.orchestrator import first_round
        with st.spinner("AI team is evaluating competing explanations and missing evidence..."): st.session_state.first_assessment=first_round(st.session_state.profile)
        st.switch_page("pages/2_assessment.py")
