from __future__ import annotations


class TriageNode:
    """A question (internal node) or a final verdict (leaf)."""

    def __init__(self, node_id: str, text: str, severity: str | None = None, action: str | None = None):
        self.id = node_id
        self.text = text
        self.severity = severity
        self.action = action
        self.yes: TriageNode | None = None
        self.no: TriageNode | None = None

    @property
    def is_leaf(self) -> bool:
        return self.yes is None and self.no is None

    def child(self, answer: bool) -> TriageNode | None:
        return self.yes if answer else self.no

    def set_child(self, answer: bool, node: TriageNode) -> None:
        setattr(self, "yes" if answer else "no", node)

    def to_dict(self, deep: bool = True) -> dict:
        data = {"id": self.id, "text": self.text, "severity": self.severity,
                "action": self.action, "leaf": self.is_leaf}
        if deep:
            data["yes"] = self.yes.to_dict() if self.yes else None
            data["no"] = self.no.to_dict() if self.no else None
        return data
