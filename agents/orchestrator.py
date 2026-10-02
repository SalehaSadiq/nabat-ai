from agents import intake,plant_health,nutrition,biotech,skeptic,evidence,safety,finance,accessibility,planner
from services.citation_engine import references

def first_round(profile):
    case=intake.run(profile); ph=plant_health.run(case); nu=nutrition.run(case); bt=biotech.run(case,ph); sk=skeptic.run(case,ph); ev=evidence.run(case,ph,sk); sf=safety.run(case,ph,ev)
    return {"structured_case":case,"plant_health":ph,"nutrition":nu,"biotechnology":bt,"skeptic":sk,"evidence":ev,"safety":sf,"references":references([str(case.get('crop','')), 'soil','diagnostics'])[:4]}

def second_round(profile, confirmed, before):
    case=before.get("structured_case") or intake.run(profile); ph=plant_health.run(case,confirmed); nu=nutrition.run(case,confirmed); bt=biotech.run(case,ph); sk=skeptic.run(case,ph); ev=evidence.run(case,ph,sk); sf=safety.run(case,ph,ev)
    return {"structured_case":case,"plant_health":ph,"nutrition":nu,"biotechnology":bt,"skeptic":sk,"evidence":ev,"safety":sf,"change_explanation":"The assessment was re-run using only values you confirmed. Differences reflect the new evidence; the system may reverse its earlier hypothesis.","references":references([str(case.get('crop','')), 'soil','diagnostics'])[:4]}

def build_options(profile, assessment, budget_override=None):
    tests=assessment.get("evidence",{}).get("tests",[]); out=finance.run(profile,tests,budget_override); out["pathways"]=accessibility.run(out["pathways"],profile); return out

def build_plan(profile, options): return planner.run(profile,options)
