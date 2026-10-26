from node import TriageNode
from tree import DecisionTree


class TreeBuilder:
    """Builds the default cybersecurity triage tree using only insert()."""

    @staticmethod
    def question(node_id: str, text: str) -> TriageNode:
        return TriageNode(node_id, text)

    @staticmethod
    def verdict(node_id: str, severity: str, action: str) -> TriageNode:
        return TriageNode(node_id, f"{severity} incident", severity, action)

    @classmethod
    def default(cls) -> DecisionTree:
        q, v = cls.question, cls.verdict
        tree = DecisionTree(q("Q1", "Is there confirmed data exfiltration or ransomware activity?"))
        branches = [
            ("Q1", True, q("Q2", "Are production systems affected?")),
            ("Q1", False, q("Q3", "Is a privileged account involved?")),
            ("Q2", True, v("R1", "CRITICAL", "Isolate the network segment, activate the IR team and notify legal.")),
            ("Q2", False, v("R2", "HIGH", "Contain the affected host, preserve forensic evidence and alert the CISO.")),
            ("Q3", True, q("Q4", "Does the activity come from an unknown device or location?")),
            ("Q3", False, q("Q5", "Does the alert match a known malware signature?")),
            ("Q4", True, v("R3", "HIGH", "Revoke active sessions, reset credentials and review MFA enrollment.")),
            ("Q4", False, v("R4", "MEDIUM", "Audit recent logs and confirm the activity with the account owner.")),
            ("Q5", True, v("R5", "MEDIUM", "Quarantine the file, scan connected endpoints and update signatures.")),
            ("Q5", False, q("Q6", "Is it a repeated failed-login pattern?")),
            ("Q6", True, v("R6", "LOW", "Rate-limit the source, block the IP and keep monitoring.")),
            ("Q6", False, v("R7", "INFO", "Log the event and close it as a false positive.")),
        ]
        for parent_id, answer, node in branches:
            tree.insert(parent_id, answer, node)
        return tree
