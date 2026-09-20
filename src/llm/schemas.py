from typing import TypedDict, List


class EvidenceItem(TypedDict):
    signal: str
    observation: str


class AccountIntelligence(TypedDict):
    account: str
    summary: str
    why_relevant: str
    evidence: List[EvidenceItem]
    security_conversation: str
    recommended_angle: str
    confidence: str