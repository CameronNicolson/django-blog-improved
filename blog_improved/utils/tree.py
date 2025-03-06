from __future__ import annotations
from typing import Optional, Callable

class Node:
    def __init__(self, value=None, children=None):
        self.value = value
        self.children = list(children) if children else []

    def add_child(self, value) -> None:
        self.children.append(Node(value=value))
   
    def search(self, match_fn: Callable[[dict], bool]) -> Optional[Node]:
        if match_fn(self.value):
            return self
        for child in self.children:
            result = child.search(match_fn)
            if result is not None:
                return result
        return None  # If no match is found

    def __repr__(self):
        return f"Node({self.value})"

class DfsIterator:
    def __init__(self, root):
        self.stack = [root] if root else []  # Stack for DFS Preorder

    def __iter__(self):
        return self  # This makes it an iterable object

    def __next__(self):
        if not self.stack:
            raise StopIteration  # Standard Python iteration behavior

        current = self.stack.pop()
        self.stack.extend(reversed(current.children))  # Push children in reverse order

        return current.value  # Return the current node's string value

class DFSIterator:
    def __init__(self, root):
        self.stack = [root] if root else []  # Start with the root node

    def __iter__(self):
        return self

    def __next__(self):
        if not self.stack:
            raise StopIteration  # End iteration when stack is empty
        
        # Last In, First Out ordering
        # Get the next node 
        current = self.stack.pop()

        # Add children to stack in **reverse order** (to process leftmost first)
        self.stack.extend(reversed(current.children))

        return current.value  # Return the node's value

# Since a tree is fundamentally a node (with children), 
# aliasing from tree to node.
Tree = Node 
