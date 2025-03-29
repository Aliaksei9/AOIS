import unittest
from node import *
class TestNode(unittest.TestCase):
    def test_node_creation(self):
        var_node = Node(var="A")
        self.assertEqual(var_node.var, "A")
        self.assertEqual(var_node.expr, "A")

        not_node = Node(op="!", child=var_node)
        self.assertEqual(not_node.op, "!")
        self.assertEqual(not_node.expr, "!A")

        and_node = Node(op="&", left=var_node, right=not_node)
        self.assertEqual(and_node.op, "&")
        self.assertEqual(and_node.expr, "(A & !A)")
if __name__ == '__main__':  
    unittest.main()