import json
from pathlib import Path

from fastapi import FastAPI, HTTPException

DATA = Path(__file__).resolve().parent.parent / "data" / "payer_mock_data"
app = FastAPI(title="MedCore Mock Payer System")


def _load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


@app.get("/eligibility/{member_id}")
def eligibility(member_id: str):
    rec = _load("eligibility.json").get(member_id)
    if rec is None:
        raise HTTPException(404, "Member not found")
    return {"member_id": member_id, **rec}


@app.get("/prior-claims/{patient_id}")
def prior_claims(patient_id: str):
    return {"patient_id": patient_id, "claims": _load("prior_claims.json").get(patient_id, [])}


@app.get("/provider-verification/{npi}")
def provider(npi: str):
    rec = _load("provider_verification.json").get(npi)
    if rec is None:
        return {"npi": npi, "name": None, "verified": False, "sanctioned": False}
    return {"npi": npi, **rec}


@app.get("/procedure-cost/{code}")
def procedure_cost(code: str):
    rec = _load("procedure_costs.json").get(code)
    if rec is None:
        raise HTTPException(404, "Unknown procedure code")
    return {"code": code, **rec}