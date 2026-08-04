"""Shared event schema for trigger-router-action flows.

The schema is intentionally small for the first ChatRSS minor-version slice.
Trigger connectors normalize external updates into :class:`TriggerEvent`; routers
produce :class:`RouteDecision`; planners produce :class:`ActionJob`; executors
return :class:`ActionResult` and append all steps to a durable ledger.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


JsonDict = dict[str, Any]


@dataclass(frozen=True)
class EventActor:
    """Who caused the event, when the connector can identify them."""

    type: str = "unknown"
    id: str = "unknown"
    display_name: str = "unknown"


@dataclass(frozen=True)
class EventSubject:
    """The object the event is about: a repo, issue, PR, thread, etc."""

    type: str = "unknown"
    repo: str = ""
    number: str = ""


@dataclass(frozen=True)
class TriggerEvent:
    """Normalized event envelope passed from trigger connectors to routers."""

    event_id: str
    source: str
    connector: str
    event_type: str
    title: str
    url: str
    content: str = ""
    published_at: str = ""
    actor: EventActor = field(default_factory=EventActor)
    subject: EventSubject = field(default_factory=EventSubject)
    raw: JsonDict = field(default_factory=dict)

    def to_dict(self) -> JsonDict:
        return asdict(self)


@dataclass(frozen=True)
class RouteDecision:
    """Router output: whether to act, archive, ignore, or ask for review."""

    event_id: str
    decision: str
    route: str
    reason: str
    action_hints: list[str] = field(default_factory=list)
    context: JsonDict = field(default_factory=dict)

    def to_dict(self) -> JsonDict:
        return asdict(self)


@dataclass(frozen=True)
class ActionJob:
    """Concrete action request produced by the action planner."""

    action_id: str
    event_id: str
    type: str
    mode: str
    target: JsonDict = field(default_factory=dict)
    input: JsonDict = field(default_factory=dict)
    idempotency_key: str = ""
    requires_approval: bool = False

    def to_dict(self) -> JsonDict:
        return asdict(self)


@dataclass(frozen=True)
class ActionResult:
    """Executor result for an action job."""

    action_id: str
    status: str
    message: str
    receipt: JsonDict = field(default_factory=dict)
    verified: bool = False

    def to_dict(self) -> JsonDict:
        return asdict(self)
