from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

Confidence = Literal["LOW", "MODERATE", "HIGH"]
SafetyLevel = Literal["GREEN", "YELLOW", "RED"]

class Hypothesis(BaseModel):
    name: str
    category: str = "uncertain"
    confidence: Confidence = "LOW"
    rationale: str = ""
    supporting_evidence: List[str] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)

class TestRecommendation(BaseModel):
    name: str
    priority: str = "Medium"
    why_needed: str = ""
    decision_change: str = ""
    estimated_cost_pkr: float = 0
    essential: bool = False
    evidence_strength: Confidence = "MODERATE"

class SafetyDecision(BaseModel):
    level: SafetyLevel = "YELLOW"
    reasons: List[str] = Field(default_factory=list)
    requires_expert: bool = False

class Pathway(BaseModel):
    name: str
    estimated_cost_pkr: float = 0
    effectiveness: Confidence = "MODERATE"
    evidence_strength: Confidence = "MODERATE"
    tradeoff: str = ""
    actions: List[str] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)

class CaseState(BaseModel):
    profile: Dict[str, Any] = Field(default_factory=dict)
    structured_case: Dict[str, Any] = Field(default_factory=dict)
    first_assessment: Dict[str, Any] = Field(default_factory=dict)
    requested_tests: List[Dict[str, Any]] = Field(default_factory=list)
    report_extraction: Dict[str, Any] = Field(default_factory=dict)
    confirmed_values: Dict[str, Any] = Field(default_factory=dict)
    second_assessment: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    budget: Dict[str, Any] = Field(default_factory=dict)
    plan: Dict[str, Any] = Field(default_factory=dict)
    expert_review: Dict[str, Any] = Field(default_factory=dict)
