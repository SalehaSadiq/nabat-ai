def run(case,assessment,tests):
    serious=any(x in str(assessment).lower() for x in ["viral","destroy","chemical","pcr","elisa"])
    budget=float(case.get("budget") or 0)
    level="RED" if serious else "YELLOW"
    reasons=["Human review is required before high-impact or uncertain actions."] if level=="RED" else ["Collect recommended evidence before spending on specific treatment."]
    return {"level":level,"reasons":reasons,"requires_expert":level=="RED","budget_context_pkr":budget}
