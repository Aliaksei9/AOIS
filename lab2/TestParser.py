import unittest
from parser import *
class TestParser(unittest.TestCase):
    def test_tokenize(self):
        parser = Parser("(A & B) -> C")
        self.assertEqual(parser.tokenize("(A & B) -> C"), ["(", "A", "&", "B", ")", "->", "C"])
        
    def test_parse_complex_expression(self):
        parser = Parser("A -> (!B | C)")
        tree = parser.parse()
        self.assertEqual(tree.op, "->")
        self.assertEqual(tree.left.var, "A")
        self.assertEqual(tree.right.op, "|")
        self.assertEqual(tree.right.left.op, "!")
        self.assertEqual(tree.right.left.child.var, "B")
        self.assertEqual(tree.right.right.var, "C")
        
    def test_parser_errors(self):
        with self.assertRaises(ValueError):
            parser = Parser("A - (!B | C)")
        with self.assertRaises(ValueError):
            parser = Parser("A -> )(!B | C)")
            parser.parse()
        with self.assertRaises(ValueError):
            parser = Parser("A -> (!B | C) D")
            parser.parse()            
if __name__ == '__main__':  
    unittest.main()

