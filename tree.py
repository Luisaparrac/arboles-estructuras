from __future__ import annotations

from collections import deque
from typing import Iterator

from node import TriageNode


class DecisionTree:
    """Binary decision tree: every question has a YES and a NO branch."""

    def __init__(self, root: TriageNode):
        self.root = root

    # ---- construction -------------------------------------------------
    def insert(self, parent_id: str, answer: bool, node: TriageNode) -> TriageNode:
        parent = self.find(parent_id)
        if parent is None:
            raise KeyError(f"unknown parent: {parent_id}")
        if parent.child(answer) is not None:
            raise ValueError(f"{parent_id} already has a {'YES' if answer else 'NO'} branch")
        parent.set_child(answer, node)
        return node

    # ---- traversals ---------------------------------------------------
    def preorder(self, node: TriageNode | None = None) -> Iterator[TriageNode]:
        node = node or self.root
        yield node
        for child in (node.yes, node.no):
            if child:
                yield from self.preorder(child)

    def postorder(self, node: TriageNode | None = None) -> Iterator[TriageNode]:
        node = node or self.root
        for child in (node.yes, node.no):
            if child:
                yield from self.postorder(child)
        yield node

    def bfs(self) -> Iterator[TriageNode]:
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            yield node
            queue.extend(c for c in (node.yes, node.no) if c)

    def traverse(self, mode: str) -> Iterator[TriageNode]:
        return {"bfs": self.bfs, "preorder": self.preorder, "postorder": self.postorder}[mode]()

    # ---- queries ------------------------------------------------------
    def find(self, node_id: str) -> TriageNode | None:
        return next((n for n in self.preorder() if n.id == node_id), None)

    def step(self, node_id: str, answer: bool) -> TriageNode:
        node = self.find(node_id)
        child = node.child(answer) if node else None
        if child is None:
            raise ValueError(f"cannot answer from '{node_id}'")
        return child

    def walk(self, answers: list[bool]) -> list[TriageNode]:
        """Follow a list of answers from the root and return the visited path."""
        path = [self.root]
        for answer in answers:
            path.append(self.step(path[-1].id, answer))
        return path

    def height(self, node: TriageNode | None = None) -> int:
        node = node or self.root
        return 1 + max((self.height(c) for c in (node.yes, node.no) if c), default=-1)

    def leaves(self) -> list[TriageNode]:
        return [n for n in self.bfs() if n.is_leaf]

    def stats(self) -> dict:
        nodes = list(self.bfs())
        leaves = self.leaves()
        return {"nodes": len(nodes), "questions": len(nodes) - len(leaves),
                "leaves": len(leaves), "height": self.height()}
