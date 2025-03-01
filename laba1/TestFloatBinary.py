import unittest
from float_binary import *
class TestTransfer(unittest.TestCase):
    def test_PosValues(self):
        A=float_binary(0.25)
        self.assertEqual(A.binary,"00111110100000000000000000000000")
        self.assertEqual(0.25, float_binary.decimal(A.binary))
    def test_NegValues(self):
        A=float_binary(-0.25)
        self.assertEqual(A.binary,"10111110100000000000000000000000")
        self.assertEqual(-0.25, float_binary.decimal(A.binary))
    def test_Exceptions(self):
        with self.assertRaises(TypeError):
            C=float_binary([1,2,3])
        with self.assertRaises(ValueError):
            C=float_binary("11") 
class TestAdd(unittest.TestCase):
    def test_Add(self):
        A=float_binary(0.25)
        B=float_binary(0.5)
        C=A+B
        self.assertEqual(0.75, float_binary.decimal(C.binary))  
    def test_Exceprions(self):
        with self.assertRaises(ValueError):
            C=float_binary(-0.25)+float_binary(-0.5)
        with self.assertRaises(ValueError):
            C=float_binary(-0.25)+float_binary(0.5)
        with self.assertRaises(ValueError):
            C=float_binary(0.25)+float_binary(-0.5)
        with self.assertRaises(TypeError):
            C=float_binary(0.25)+3
if __name__ == '__main__':  
    unittest.main()