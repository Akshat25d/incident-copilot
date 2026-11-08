import json
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, model_validator

GOLDEN_DIR = Path(__file__).resolve().parent / "golden_set"


class Scenario(BaseModel):
    type: Literal["scripted", "synthetic"]
    command: str | None = None


class Remediation(BaseModel):
    action: Literal["rollback", "restart", "other", "none"]
    service: str | None = None
    detail: str


class Incident(BaseModel):
    id: str
    split: Literal["dev", "test"]
    fault: str
    difficulty: Literal["easy", "medium", "hard"]
    answerable: bool = True
    title: str
    scenario: Scenario
    alert: str
    query: str
    root_cause: str
    root_cause_service: str | None = None
    remediation: Remediation
    expected_docs: list[str] = []
    also_relevant: list[str] = []
    distractors: list[str] = []
    evidence: list[str]

    @model_validator(mode="after")
    def check_consistency(self) -> Self:
        if self.scenario.type == "scripted" and not self.scenario.command:
            raise ValueError(f"{self.id}: scripted scenarios need a command")
        if self.answerable and not self.expected_docs:
            raise ValueError(f"{self.id}: answerable incidents need expected_docs")
        if not self.answerable and (self.expected_docs or self.remediation.action != "none"):
            raise ValueError(f"{self.id}: unanswerable incidents have no docs and no action")
        return self


def load_golden(directory: Path = GOLDEN_DIR) -> list[Incident]:
    paths = sorted(directory.glob("G-*.json"))
    return [Incident.model_validate(json.loads(path.read_text())) for path in paths]
