from typing import List
from pydantic import BaseModel, Field

class DuplicateCandidate(BaseModel):
    case_id: str = Field(description="OnPoint case ID")
    reason: str = Field(description="Similarity rationale")
    confidence: float = Field(ge=0.0, le=1.0, description="Match confidence between 0.0 and 1.0")

class IntakeOutputContract(BaseModel):
    request_id: str
    request_type: str
    business_problem_as_stated: str
    target_population: str
    requested_date: str
    urgency_score: int = Field(ge=1, le=5)
    business_impact_score: int = Field(ge=1, le=5)
    duplicate_case_flag: bool
    duplicate_candidates: List[DuplicateCandidate]
    routing_decision: str
    missing_information: List[str]
    discovery_ready: bool
    evidence: List[str]
    confidence: float = Field(ge=0.0, le=1.0)
    routing_rationale: str
