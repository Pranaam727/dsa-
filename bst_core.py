"""
bst_core.py - Core Binary Search Tree Module
Student Index Recovery System

Provides core data structures and pure functions for BST validation,
traversal, inspection, and visualization without external tree libraries.
"""

from typing import Optional, List, Tuple, Any


class Node:
    """
    A binary tree node representing a student index record.

    Attributes:
        id (int): Student index number (BST key).
        left (Optional[Node]): Pointer to left child.
        right (Optional[Node]): Pointer to right child.
        data (Any): Optional payload (e.g., student name or details).
    """

    def __init__(
        self,
        id: int,
        left: Optional["Node"] = None,
        right: Optional["Node"] = None,
        data: Any = None,
    ):
        self.id: int = id
        self.left: Optional["Node"] = left
        self.right: Optional["Node"] = right
        self.data: Any = data

    def is_leaf(self) -> bool:
        """Returns True if the node has no children (left is None and right is None)."""
        return self.left is None and self.right is None

    def __repr__(self) -> str:
        return f"Node(id={self.id})"


# ============================================================================
# Leaf and ID Collection Helpers
# ============================================================================

def collect_leaf_nodes(root: Optional[Node]) -> List[Node]:
    """
    Collects all leaf nodes (nodes where left is None and right is None)
    in the tree in left-to-right order.
    """
    leaves: List[Node] = []

    def _traverse(node: Optional[Node]) -> None:
        if node is None:
            return
        if node.left is None and node.right is None:
            leaves.append(node)
            return
        if node.left is not None:
            _traverse(node.left)
        if node.right is not None:
            _traverse(node.right)

    _traverse(root)
    return leaves


# Alias for flexible importing
get_leaf_nodes = collect_leaf_nodes


def collect_leaf_ids(root: Optional[Node]) -> List[int]:
    """
    Collects IDs of all leaf nodes (left is None and right is None).
    """
    return [node.id for node in collect_leaf_nodes(root)]


# Alias for flexible importing
get_leaf_ids = collect_leaf_ids


def collect_all_node_ids(root: Optional[Node]) -> List[int]:
    """
    Collects all node IDs present in the tree in ascending (inorder) sequence.
    """
    return inorder_traversal(root)


# Alias for flexible importing
get_all_node_ids = collect_all_node_ids


# ============================================================================
# BST Validation
# ============================================================================

def is_valid_bst(
    root: Optional[Node],
    min_val: float = float("-inf"),
    max_val: float = float("inf"),
) -> Tuple[bool, Optional[str]]:
    """
    Validates strict global BST ordering across every subtree using min/max bounds.
    Every node must strictly satisfy: min_val < node.id < max_val.

    Args:
        root: The root node of the tree or subtree.
        min_val: Strict lower bound for the current subtree.
        max_val: Strict upper bound for the current subtree.

    Returns:
        (True, None) if the tree is a valid BST.
        (False, clear_conflict_reason) detailing the exact node ID and bounds violated.
    """
    if root is None:
        return True, None

    # Strict BST check: min_val < root.id < max_val
    if not (min_val < root.id < max_val):
        bound_low = "-∞" if min_val == float("-inf") else str(min_val)
        bound_high = "+∞" if max_val == float("inf") else str(max_val)
        reason = (
            f"BST ordering violation at Node ID {root.id}: "
            f"Value must strictly satisfy {bound_low} < ID < {bound_high}."
        )
        return False, reason

    # Recursively check left subtree: all IDs must be strictly < root.id
    left_valid, left_reason = is_valid_bst(root.left, min_val, root.id)
    if not left_valid:
        return False, left_reason

    # Recursively check right subtree: all IDs must be strictly > root.id
    right_valid, right_reason = is_valid_bst(root.right, root.id, max_val)
    if not right_valid:
        return False, right_reason

    return True, None


# ============================================================================
# Traversal
# ============================================================================

def inorder_traversal(root: Optional[Node]) -> List[int]:
    """
    Performs an inorder traversal (Left, Root, Right) of the tree.

    Returns:
        A list of integer IDs in inorder sequence.
    """
    result: List[int] = []

    def _inorder(node: Optional[Node]) -> None:
        if node is None:
            return
        _inorder(node.left)
        result.append(node.id)
        _inorder(node.right)

    _inorder(root)
    return result


# ============================================================================
# Tree Visualization & Formatting
# ============================================================================

def format_tree(root: Optional[Node]) -> str:
    """
    Generates a clear visual string representation of the tree, displaying
    the Root ID, node hierarchy, branch directions (L/R), and leaf indicators.

    Args:
        root: Root node of the tree.

    Returns:
        Multi-line string representation of the tree and its root ID.
    """
    if root is None:
        return "Root ID: None\n(Empty Tree)"

    lines: List[str] = [f"Root ID: {root.id}"]

    def _render(
        node: Optional[Node],
        prefix: str = "",
        is_last: bool = True,
        branch_label: str = "",
    ) -> None:
        if node is None:
            return

        connector = "└── " if is_last else "├── "
        label = f"[{branch_label}] " if branch_label else ""
        leaf_tag = " (leaf)" if node.is_leaf() else ""
        lines.append(f"{prefix}{connector}{label}ID: {node.id}{leaf_tag}")

        child_prefix = prefix + ("    " if is_last else "│   ")

        # Determine existing children to render proper branches
        children = []
        if node.left is not None:
            children.append((node.left, "L"))
        if node.right is not None:
            children.append((node.right, "R"))

        for i, (child, direction) in enumerate(children):
            is_child_last = (i == len(children) - 1)
            _render(child, child_prefix, is_child_last, direction)

    # Render root and its children
    root_tag = " (leaf)" if root.is_leaf() else ""
    lines.append(f"Tree Structure:\nID: {root.id}{root_tag}")
    
    children = []
    if root.left is not None:
        children.append((root.left, "L"))
    if root.right is not None:
        children.append((root.right, "R"))

    for i, (child, direction) in enumerate(children):
        is_child_last = (i == len(children) - 1)
        _render(child, "", is_child_last, direction)

    return "\n".join(lines)


def print_tree(root: Optional[Node]) -> None:
    """Convenience helper to format and print the tree to stdout."""
    print(format_tree(root))


# ============================================================================
# Additional Utility Helpers (Useful for merger and index recovery)
# ============================================================================

def insert_node(root: Optional[Node], id: int, data: Any = None) -> Node:
    """
    Inserts a new ID into the BST according to BST rules.
    If tree is empty, returns new Node as root.
    """
    if root is None:
        return Node(id=id, data=data)

    if id < root.id:
        root.left = insert_node(root.left, id, data)
    elif id > root.id:
        root.right = insert_node(root.right, id, data)
    # If id == root.id, duplicate key is ignored or updated with data
    elif data is not None:
        root.data = data

    return root


def build_balanced_bst_from_sorted(sorted_ids: List[int]) -> Optional[Node]:
    """
    Constructs a height-balanced BST from a strictly sorted list of unique IDs.
    """
    if not sorted_ids:
        return None

    mid = len(sorted_ids) // 2
    root = Node(id=sorted_ids[mid])
    root.left = build_balanced_bst_from_sorted(sorted_ids[:mid])
    root.right = build_balanced_bst_from_sorted(sorted_ids[mid + 1:])
    return root
