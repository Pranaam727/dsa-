# Student Index Recovery System (BST Reconstruction)

An algorithmic framework designed to recover corrupted student index records by merging independent Binary Search Tree (BST) fragments into a globally valid, unified BST.

---

## 1. System Overview & Architecture

When student index records are split into fragmented subtrees (1-node, 2-node, or 3-node fragments), this system reconstructs the entire tree hierarchy or proves that recovery is `IMPOSSIBLE` due to structural or ordering violations.

```
                  Input Fragments:
     [2, 1]          [3, 2, 5]          [5, 4]
       2                 3                 5
      /                 / \               /
     1                 2   5             4
                       │   │
                       └───┴── Grafting onto Leaves
                                │
                                ▼
                       Unified BST Root: 3
                                3
                              /   \
                             2     5
                            /     /
                           1     4
             Inorder Traversal: [1, 2, 3, 4, 5]
```

### Module Structure

| File | Purpose |
| :--- | :--- |
| `bst_core.py` | Scratch-built `Node` class, leaf & ID collectors, global BST bounds validator, inorder traversal, and visual tree formatter. |
| `merger.py` | Core merge algorithm: root identification, leaf grafting, cycle detection, component connectivity, and `MergeResult` wrapper. |
| `app.py` | Interactive CLI menu and command-line runner with preset validation demos. |
| `test_suite.py` | Comprehensive verification test suite for valid merges, ancestor bounds conflicts, and disconnected components. |

---

## 2. Setup & Requirements

- **Python Version**: Python 3.8+
- **External Dependencies**: None (Standard Library only: `typing`, `unittest`, `ast`, `copy`).

No `pip install` is needed. Clone or extract the repository and run directly:
```bash
python --version
```

---

## 3. How to Run

### Running the Verification Test Suite
Execute the comprehensive test cases verifying all functional requirements:
```bash
python -m unittest test_suite.py -v
```
Or directly:
```bash
python test_suite.py
```

### Running the Application (`app.py`)
Launch the interactive CLI:
```bash
python app.py
```

Or run dedicated command-line demos:
```bash
# 1. Run the illustrative valid merge demo ([2,1], [3,2,5], [5,4])
python app.py --demo

# 2. Run the global ancestor bound conflict demo ([5,2,8], [2,1,6])
python app.py --conflict

# 3. Run the disconnected fragments demo ([3,2,5], [10,8,12])
python app.py --disconnected

# 4. Supply custom fragments directly as a string
python app.py "[[2, 1], [3, 2, 5], [5, 4]]"
```

---

## 4. Team Member Module Ownership

| Member | Primary Ownership | Files Owned | Key Deliverables |
| :--- | :--- | :--- | :--- |
| **Member 1** | **Core Tree Structures & Validation** | `bst_core.py` | `Node` class, `is_valid_bst`, `inorder_traversal`, `collect_leaf_nodes`, `format_tree`. |
| **Member 2** | **Merge Engine & Algorithm** | `merger.py` | `merge_fragments`, `fragment_to_node`, `MergeResult`, candidate root discovery, leaf grafting. |
| **Member 3** | **Application, CLI & Verification** | `app.py`, `test_suite.py` | CLI interface, input parsing, end-to-end edge case test suite, documentation. |

---

## 5. Evaluation Guide: Explaining Your Code

Use the talking points below during lab evaluations or code reviews.

### Member 1: Core Tree Structures & Validation (`bst_core.py`)
- **Key Question: "Why can't you just check if `left.id < root.id < right.id` locally?"**
  - *Answer*: "Local checks miss ancestor bound violations. In a BST, every node in a left subtree must be less than *all* its ancestors. In `is_valid_bst(root, min_val, max_val)`, we pass down strict bounds $(-\infty, +\infty)$ and narrow them recursively: the left child must be strictly within `(min_val, root.id)` and the right child within `(root.id, max_val)` in $O(N)$ time."
- **Key Question: "How does `format_tree` ensure directional clarity?"**
  - *Answer*: "It inspects each node's children and prefixes them with `[L]` or `[R]` markers and `(leaf)` tags. This immediately distinguishes whether a single child is a left or right branch."

### Member 2: Fragment Merging Algorithm (`merger.py`)
- **Key Question: "How do you determine which fragment is the overall root?"**
  - *Answer*: "We build a directed child-to-parent graph. Every fragment attached to a leaf has in-degree 1 (its root matches a leaf of another fragment). The overall root is the unique fragment whose root ID has in-degree 0 (does not appear as a child in any other fragment). If there are 0 candidates, a cycle exists; if there are $>1$, the fragments are disconnected."
- **Key Question: "Why can a fragment only attach to a leaf node?"**
  - *Answer*: "If a fragment root $X$ attempted to attach to a non-leaf node $X$, node $X$ would receive duplicate left or right children, violating the binary tree definition and corrupting index integrity."

### Member 3: System Integration & Test Suite (`app.py`, `test_suite.py`)
- **Key Question: "What edge cases does `test_suite.py` cover?"**
  - *Answer*:
    1. **Illustrative Valid Merge**: `[2,1], [3,2,5], [5,4]` produces root 3 and inorder `[1,2,3,4,5]`.
    2. **Multi-Fragment Merges**: 1-node, 2-node, 3-node combinations up to 7-fragment moderate trees.
    3. **Ancestor Inversions**: Where a fragment like `[2, 1, 6]` is locally valid, but its right child 6 violates ancestor bound $< 5$ when grafted into `[5, 2, 8]`.
    4. **Structural Failures**: Disconnected components, missing attachment points, cyclic fragments, and duplicate roots returning `IMPOSSIBLE` with exact diagnostics.
- **Key Question: "How does `app.py` handle user interaction without crashes?"**
  - *Answer*: "Inputs are parsed safely with `ast.literal_eval`, converted through `fragment_to_node`, and returned as a resilient `MergeResult` object supporting attribute inspection, boolean checks, and tuple unpacking."
