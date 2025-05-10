import unittest
from integer_binary import *
class TestOperationPositiveValues(unittest.TestCase):
    def setUp(self):
        self.A=integer_binary(2)
        self.B=integer_binary(3)
    def test_PosAdd(self):
        C=self.A+self.B
        self.assertEqual(5,integer_binary.decimal(C.binary))
    def test_PosDifference(self):
        C=self.A-self.B
        minus=False
        if C.binary[0]=="1":
            minus=True
        self.assertEqual(-1,integer_binary.decimal(C.binary_module, minus))  
    def test_PosMul(self):
        C=self.A*self.B
        self.assertEqual(6,integer_binary.decimal(C.binary))
    def test_PosDiv(self):
        C=self.A/self.B
        self.assertEqual(C,"000000000000000000000000000.10101")
class TestOperationNegativeValues(unittest.TestCase):
    def setUp(self):
        self.A=integer_binary(-2)
        self.B=integer_binary(-3)
    def test_NegAdd(self):        
        C=self.A+self.B
        minus=False
        if C.binary[0]=="1":
            minus=True        
        self.assertEqual(-5,integer_binary.decimal(C.binary_module,minus))
    def test_NegDifference(self):
        C=self.A-self.B
        minus=False
        if C.binary[0]=="1":
            minus=True
        self.assertEqual(1,integer_binary.decimal(C.binary_module, minus))  
    def test_NegMul(self):
        C=self.A*self.B
        self.assertEqual(6,integer_binary.decimal(C.binary))
    def test_NegDiv(self):
        C=self.A/self.B
        self.assertEqual(C,"000000000000000000000000000.10101")   
class TestOperationDifferentValues(unittest.TestCase):
    def setUp(self):
        self.A=integer_binary(2)
        self.B=integer_binary(-3)
    def test_DiffAdd(self):        
        C=self.A+self.B
        minus=False
        if C.binary[0]=="1":
            minus=True        
        self.assertEqual(-1,integer_binary.decimal(C.binary_module,minus))
    def test_DiffDifference(self):
        C=self.A-self.B
        minus=False
        if C.binary[0]=="1":
            minus=True
        self.assertEqual(5,integer_binary.decimal(C.binary_module, minus))  
    def test_DiffMul(self):
        C=self.A*self.B
        minus=False
        if C.binary[0]=="1":
            minus=True        
        self.assertEqual(-6,integer_binary.decimal(C.binary_module, minus))
    def test_DiffDiv(self):
        C=self.A/self.B       
        self.assertEqual(C,"100000000000000000000000000.10101")
class TestExceprions(unittest.TestCase):
    def setUp(self):
        self.A=integer_binary(2)
    def test_InitErors(self):
        with self.assertRaises(TypeError):
            B=integer_binary([1,2,3])
        with self.assertRaises(OverflowError):
            B=integer_binary(999999999999999999999999999999999999999999999999999)
        with self.assertRaises(ValueError):
            B=integer_binary("11")
    def test_AddErrors(self):
        with self.assertRaises(TypeError):
            B=self.A+12
    def test_DifferenceErrors(self):
        with self.assertRaises(TypeError):
            B=self.A-12
    def test_MulErrors(self):
        with self.assertRaises(TypeError):
            B=self.A*12  
    def test_DivErrors(self):
        with self.assertRaises(TypeError):
            B=self.A/12
        with self.assertRaises(ZeroDivisionError):
            B=self.A/integer_binary(0)
if __name__ == '__main__':  
    unittest.main()
    