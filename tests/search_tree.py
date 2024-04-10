from __future__ import annotations

from typing import Generic, Optional, Protocol, TypeVar


class SelfComparable(Protocol):
    def __lt__(self: T, other: T) -> bool: ...


T = TypeVar("T", bound=SelfComparable)


class SearchTree(Generic[T]):
    def __init__(self) -> None:
        self.root: Optional[Node[T]] = None

    def insert(self, value: T) -> None:
        if self.root is None:
            self.root = Node(value=value)
            return
        node = self.root
        while True:
            if value < node.value:
                if node.left is None:
                    node.left = Node(value=value)
                    break
                else:
                    node = node.left
            else:
                if node.right is None:
                    node.right = Node(value=value)
                    break
                else:
                    node = node.right

    def last(self) -> Optional[T]:
        if self.root is None:
            return None
        else:
            node = self.root
            while node.right is not None:
                node = node.right
            return node.value


class Node(Generic[T]):
    def __init__(
        self,
        value: T,
        left: Optional[Node[T]] = None,
        right: Optional[Node[T]] = None,
    ) -> None:
        self.value = value
        self.left = left
        self.right = right
