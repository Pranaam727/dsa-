"""
test_suite.py - Verification Test Suite
Student Index Recovery System

Verifies:
1. Illustrative valid merge ([2,1], [3,2,5], [5,4]) producing root 3 and inorder [1,2,3,4,5].
2. Multi-fragment merges with 1-node, 2-node, and 3-node fragments up to moderate counts.
3. Ordering conflicts (local violations and global ancestor bound violations) returning IMPOSSIBLE with clear reasons.
4. Unused or disconnected fragments returning IMPOSSIBLE with clear reasons.
"""

import unittest
from bst_core import Node, inorder_traversal, format_tree, is_valid_bst, collect_leaf_ids
from merger import merge_fragments, MergeResult


class TestStudentIndexRecovery(unittest.TestCase):

    # ========================================================================
    # 1. Illustrative Valid Merge
    # ========================================================================
    def test_01_illustrative_valid_merge(self):
        """
        Verify: [2,1], [3,2,5], [5,4]
        Produces merged tree with root ID 3 and inorder traversal [1, 2, 3, 4, 5].
        """
        fragments = [[2, 1], [3, 2, 5], [5, 4]]
        result = merge_fragments(fragments)

        # Result status checks
        self.assertEqual(result.status, "SUCCESS")
        self.assertTrue(result.is_success)
        self.assertIsNotNone(result.root)

        # Root verification
        self.assertEqual(result.root.id, 3)

        # Inorder traversal verification
        traversal = inorder_traversal(result.root)
        self.assertEqual(traversal, [1, 2, 3, 4, 5])
        self.assertEqual(result.inorder, [1, 2, 3, 4, 5])

        # Global BST validation check
        is_valid, reason = is_valid_bst(result.root)
        self.assertTrue(is_valid)
        self.assertIsNone(reason)

        # Leaf nodes check: leaves must be 1 and 4
        self.assertEqual(collect_leaf_ids(result.root), [1, 4])

    # ========================================================================
    # 2. Additional Valid Multi-Fragment Merges
    # ========================================================================
    def test_02_single_node_fragment_merge(self):
        """Test merge involving 1-node fragments attaching to leaves."""
        # [20, 10, 30] where leaves 10 and 30 are expanded by single node fragments or 2-node fragments
        fragments = [
            [20, 10, 30],
            [10, 5],       # 2-node
            [30, 40],      # 2-node
            [5],           # 1-node
        ]
        result = merge_fragments(fragments)
        self.assertTrue(result.is_success)
        self.assertEqual(result.root.id, 20)
        self.assertEqual(result.inorder, [5, 10, 20, 30, 40])

    def test_03_moderate_count_multi_fragment_merge(self):
        r"""
        Test a 7-fragment merge representing a complete recovery of student indexes:
        Tree structure:
                    50
                 /      \
               25        75
              /  \      /  \
            15    35   65   85
           /  \
          10  18
        """
        fragments = [
            [50, 25, 75],     # Root fragment
            [25, 15, 35],     # Left child of 50
            [75, 65, 85],     # Right child of 50
            [15, 10, 18],     # Left child of 25
            [35],             # 1-node leaf
            [65],             # 1-node leaf
            [85],             # 1-node leaf
        ]
        result = merge_fragments(fragments)
        self.assertTrue(result.is_success)
        self.assertEqual(result.root.id, 50)
        expected_inorder = [10, 15, 18, 25, 35, 50, 65, 75, 85]
        self.assertEqual(result.inorder, expected_inorder)

        # Unpacking syntax support verification
        root, err = result
        self.assertEqual(root.id, 50)
        self.assertIsNone(err)

    def test_04_chain_growth_merge(self):
        """Test deep chain growth of fragments."""
        # [10, 8] -> [8, 6] -> [6, 4] -> [4, 2]
        fragments = [
            [10, 8],
            [8, 6],
            [6, 4],
            [4, 2],
        ]
        result = merge_fragments(fragments)
        self.assertTrue(result.is_success)
        self.assertEqual(result.root.id, 10)
        self.assertEqual(result.inorder, [2, 4, 6, 8, 10])

    # ========================================================================
    # 3. Ordering Conflicts (Local & Global Ancestor Bounds)
    # ========================================================================
    def test_05_global_ancestor_bound_conflict(self):
        """
        Subtree [2, 1, 6] is locally valid (1 < 2 < 6),
        but attaching to leaf 2 of [5, 2, 8] violates ancestor bound (6 > 5 in left subtree).
        Must return IMPOSSIBLE with a clear reason.
        """
        fragments = [
            [5, 2, 8],
            [2, 1, 6],  # Locally valid BST, but 6 violates global upper bound of 5!
        ]
        result = merge_fragments(fragments)
        self.assertEqual(result.status, "IMPOSSIBLE")
        self.assertEqual(result, "IMPOSSIBLE")
        self.assertFalse(result.is_success)
        self.assertIn("BST ordering violation", result.reason)
        self.assertIn("Node ID 6", result.reason)

        # Verify tuple unpacking behavior on failure
        status, reason = result
        self.assertEqual(status, "IMPOSSIBLE")
        self.assertIn("Node ID 6", reason)

    def test_06_local_ordering_conflict_in_fragment(self):
        """Fragment contains direct local BST inversion (left >= root or right <= root)."""
        # Fragment with left child greater than root
        fragments = [
            [10, 15],  # 15 < 10 is False; left child 15 is invalid
        ]
        # In our fragment_to_node: 15 > 10 creates a right child by default for 2-element list.
        # So test with explicit 3-element inversion [10, 15, 5]:
        result = merge_fragments([[10, 15, 5]])
        self.assertEqual(result.status, "IMPOSSIBLE")
        self.assertIn("Fragment #1", result.reason)

    def test_07_duplicate_key_conflict_across_fragments(self):
        """Multiple fragments introduce duplicate keys, violating strict BST ordering or tree properties."""
        # Case A: Duplicate child ID claimed by two different parent fragments
        fragments_multi_parent = [
            [50, 20, 80],
            [20, 10, 30],
            [80, 30, 90],  # 30 is claimed as child of both 20 and 80
        ]
        result_a = merge_fragments(fragments_multi_parent)
        self.assertEqual(result_a.status, "IMPOSSIBLE")
        self.assertIn("multiple parents", result_a.reason.lower())

        # Case B: Duplicate key in subtree causing BST strict inequality violation
        # [50, 20, 70] merged with [20, 10, 50] (duplicate 50 inside subtree)
        fragments_dup_val = [
            [50, 20, 70],
            [20, 10, 50],
        ]
        result_b = merge_fragments(fragments_dup_val)
        self.assertEqual(result_b.status, "IMPOSSIBLE")

    # ========================================================================
    # 4. Unused or Disconnected Fragments
    # ========================================================================
    def test_08_disconnected_separate_components(self):
        """Two disjoint trees that do not share any attachment points."""
        fragments = [
            [3, 2, 5],
            [10, 8, 12],
        ]
        result = merge_fragments(fragments)
        self.assertEqual(result.status, "IMPOSSIBLE")
        self.assertIn("Disconnected fragments", result.reason)
        self.assertIn("Multiple independent tree roots found", result.reason)

    def test_09_unused_fragment_cannot_attach_to_leaf(self):
        """
        Fragment tries to attach to an ID that is NOT a leaf,
        or fragment root does not match any leaf.
        """
        fragments = [
            [10, 5, 15],
            [5, 2],
            [99, 90],  # Root 99 is nowhere in the tree
        ]
        result = merge_fragments(fragments)
        self.assertEqual(result.status, "IMPOSSIBLE")
        self.assertIn("Disconnected fragments", result.reason)
        self.assertIn("99", result.reason)

    def test_10_cyclic_fragment_dependencies(self):
        """Fragments forming a cycle where no root candidate has in-degree 0."""
        fragments = [
            [5, 2],
            [2, 5],
        ]
        result = merge_fragments(fragments)
        self.assertEqual(result.status, "IMPOSSIBLE")
        self.assertIn("Cyclic dependency", result.reason)

    def test_11_duplicate_root_fragments(self):
        """Two fragments specify competing definitions for the same root ID."""
        fragments = [
            [5, 2],
            [5, 8],
        ]
        result = merge_fragments(fragments)
        self.assertEqual(result.status, "IMPOSSIBLE")
        self.assertIn("Duplicate fragment roots detected", result.reason)


if __name__ == "__main__":
    unittest.main(verbosity=2)
