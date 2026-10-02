from utils.finance import financial_summary

def run(case, tests, budget_override=None):
    budget=float(budget_override if budget_override is not None else case.get("budget") or 0)
    test_cost=sum(float(t.get("estimated_cost_pkr",0) or 0) for t in tests if t.get("essential"))
    base=max(test_cost,500)
    pathways=[
      {"name":"Minimum Cost","estimated_cost_pkr":base,"effectiveness":"MODERATE","evidence_strength":"MODERATE","tradeoff":"Focuses on essential evidence and low-cost observation first.","actions":["Complete essential evidence","Avoid unconfirmed input purchases"]},
      {"name":"Best Value","estimated_cost_pkr":base+1500,"effectiveness":"MODERATE","evidence_strength":"MODERATE","tradeoff":"Balances confirmation, practical intervention and prevention.","actions":["Complete essential evidence","Use targeted action only after confirmation","Schedule follow-up"]},
      {"name":"Comprehensive","estimated_cost_pkr":base+4000,"effectiveness":"MODERATE","evidence_strength":"MODERATE","tradeoff":"Adds optional confirmation/follow-up; incremental benefit may be limited.","actions":["Complete evidence","Targeted intervention","Optional follow-up testing","Next-season prevention"]}]
    for p in pathways:
        p["affordable"]=p["estimated_cost_pkr"]<=budget
        p["finance"]=financial_summary(p["estimated_cost_pkr"],budget,case.get("expected_crop_value"),float(case.get("area",1) or 1),case.get("area_unit","acre"))
    affordable=[p for p in pathways if p["affordable"]]
    return {"budget":budget,"pathways":pathways,"best_value_note":"Best Value is a balance label, not a guarantee of superior biological outcome.","reduced_plan": affordable[-1] if affordable else pathways[0]}
