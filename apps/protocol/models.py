"""Data models for the collaboration protocol system."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


class DecisionPoint(BaseModel):
    id: str  # e.g. "ID-001"
    description: str
    status: Literal["active", "paused", "completed"] = "active"
    tier: Literal["critical", "adaptable", "flexible"] = "flexible"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    paused_at: Optional[datetime] = None
    resumed_at: Optional[datetime] = None
    last_completed_step: Optional[int] = None


class Constraints(BaseModel):
    net: str = "stable"
    time: str = "normal"
    tools: list[str] = Field(default_factory=list)
    extras: dict[str, str] = Field(default_factory=dict)


class ChecklistStep(BaseModel):
    text: str
    required: bool = True


class ChecklistDef(BaseModel):
    name: str
    intent: str
    preflight: list[ChecklistStep] = Field(default_factory=list)
    run: list[ChecklistStep] = Field(default_factory=list)
    verify: list[ChecklistStep] = Field(default_factory=list)
    fallback: list[str] = Field(default_factory=list)


class ChecklistRun(BaseModel):
    checklist_name: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    phase_results: dict[str, list[bool]] = Field(default_factory=dict)
    status: Literal["passed", "failed", "aborted"] = "passed"


class SessionState(BaseModel):
    sid: str
    seq: int = 0
    ctx: str = ""
    decision_points: dict[str, DecisionPoint] = Field(default_factory=dict)
    active_id: Optional[str] = None
    constraints: Constraints = Field(default_factory=Constraints)
    roles: dict[str, str] = Field(default_factory=lambda: {
        "A": "operator", "B": "helper", "AI": "planner",
    })
    risks: list[str] = Field(default_factory=list)
    fallback: Optional[str] = None
    sync_interval_min: int = 30
    sync_every_msgs: int = 10
    confidence: float = 0.5
    tag: Literal["provisional", "confirmed"] = "provisional"
    recheck_days: int = 7
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_sync_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    checklist_runs: list[ChecklistRun] = Field(default_factory=list)
