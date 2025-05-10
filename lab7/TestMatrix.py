# test_matrix16.py
import unittest
import io
import sys

from integer_binary import *
from matrix import *
class TestMatrix16(unittest.TestCase):
    def setUp(self):
        self.M = Matrix16()

    def test_set_get_word(self):
        self.assertEqual(self.M.get_word(0), [0]*16)
        bits = [i % 2 for i in range(16)]
        self.M.set_word(5, bits)
        self.assertEqual(self.M.get_word(5), bits)

    def test_set_get_address(self):
        addr = [1, 0, 1]
        self.M.set_address(2, addr)
        self.assertEqual(self.M.get_address(2, length=3), addr)
        full = self.M.get_address(2)
        self.assertEqual(full[:3], addr)
        self.assertEqual(full[3:], [0]*13)

    def test_logic_functions(self):
        w1 = [i % 2 for i in range(16)]
        w2 = [1 - (i % 2) for i in range(16)]
        self.M.set_word(0, w1)
        self.M.set_word(1, w2)
        self.assertEqual(self.M.f2(0,1), w1)
        self.assertEqual(self.M.f7(0,1), [1]*16)
        self.assertEqual(self.M.f8(0,1), [0]*16)
        self.assertEqual(self.M.f13(0,1), [1 - b for b in w1])

    def test_find_words_in_range_prints_correct(self):
        for i in range(16):
            bits = [int(b) for b in f"{i:016b}"]
            self.M.set_word(i, bits)

        buf = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buf
        try:
            self.M.find_words_in_range(top=5, bottom=3)
        finally:
            sys.stdout = sys_stdout

        output = buf.getvalue().strip().splitlines()
        self.assertTrue(output[0].startswith("Найденные слова:"))
        printed = [line.strip() for line in output[1:]]
        expected_repr = [str([int(c) for c in f"{i:016b}"]) for i in range(3,6)]
        self.assertEqual(printed, expected_repr)

    def test_sum_ab_for_v_updates_S(self):
        word = [1,0,1] + [0,0,1,1] + [0,1,0,1] + [0]*5
        self.M.set_word(7, word.copy())
        res = self.M.sum_ab_for_v([1,0,1])
        self.assertEqual(len(res), 1)
        before_str, after_str = res[0]
        self.assertEqual(before_str, ''.join(str(b) for b in word))

        after_bits = [int(ch) for ch in after_str]
        matching_cols = [i for i in range(16) if self.M.get_word(i) == after_bits]
        self.assertEqual(len(matching_cols), 1)
        updated = after_bits
        self.assertEqual(updated[11:], [0,1,0,0,0])

    def test_compare(self):
        cmp = self.M.compare
        self.assertEqual(cmp([1,0,1], [1,0,1]), 0)
        self.assertEqual(cmp([1,1,0], [1,0,1]), 1)
        self.assertEqual(cmp([0,0,0], [0,0,1]), -1)

if __name__ == '__main__':
    unittest.main()
