import unittest
from BooleanMinimizer import BooleanMinimizer

class TestBooleanMinimizer(unittest.TestCase):
    def test_extract_variables(self):
        formula = "A /\\ B \\/ C"
        minimizer = BooleanMinimizer(formula, 1)
        self.assertEqual(minimizer.variables, ['A', 'B', 'C'])

    def test_parse_formula_dnf(self):
        formula = "(A /\\ B) \\/ (C /\\ D)"
        minimizer = BooleanMinimizer(formula, 1)
        self.assertEqual(minimizer.terms, [['A', 'B', '-', '-'], ['C', 'D', '-', '-']])

    def test_parse_formula_cnf(self):
        formula = "(A \\/ B) /\\ (C \\/ D)"
        minimizer = BooleanMinimizer(formula, 2)
        self.assertEqual(minimizer.terms, [['A', 'B', '-', '-'], ['C', 'D', '-', '-']])

    def test_term_to_string_dnf(self):
        minimizer = BooleanMinimizer("A /\\ B", 1)
        self.assertEqual(minimizer.term_to_string(['A', 'B']), 'A/\\B')

    def test_term_to_string_cnf(self):
        minimizer = BooleanMinimizer("A \\/ B", 2)
        self.assertEqual(minimizer.term_to_string(['A', 'B']), 'A\\/B')

    def test_glue_terms(self):
        minimizer = BooleanMinimizer("A /\\ B", 1)
        term1 = ['A', 'B']
        term2 = ['A', '!B']
        glued = minimizer.glue(term1, term2)
        self.assertEqual(glued, ['A', '-'])

    def test_remove_redundant_dnf(self):
        formula = "(A /\\ B) \\/ (A /\\ !B) \\/ (A /\\ C)"
        minimizer = BooleanMinimizer(formula, 1)
        # Исправленные импликанты: 3 элемента (A, B, C)
        implicants = [['A', '-', '-'], ['A', '-', 'C']]  # A ∧ (B ∨ ¬B) и A ∧ C
        essential = minimizer.remove_redundant(implicants)
        self.assertEqual(essential, [['A', '-', '-']])

    def test_coverage_table(self):
        formula = "A /\\ B \\/ A /\\ !B"
        minimizer = BooleanMinimizer(formula, 1)
        implicants = [['A', '-']]
        table = minimizer.build_coverage_table(implicants)
        self.assertTrue(all(table[0]))

    def test_karnaugh_map_2vars(self):
        formula = "(!A /\\ !B) \\/ (!A /\\ B) \\/ (A /\\ B)"
        minimizer = BooleanMinimizer(formula, 1)
        result = minimizer.minimize_karnaugh()
        # Ожидаемые термы: ['!A'] и ['B']
        self.assertEqual(result, [['!A'], ['B']])

    def test_calculative_method_dnf(self):
        formula = "A /\\ B \\/ A /\\ !B \\/ !A /\\ B"
        minimizer = BooleanMinimizer(formula, 1)
        result = minimizer.minimize_calculative()
        self.assertEqual(result,[['A', '-'], ['-', 'B']])

    def test_calculative_tabular_method(self):
        formula = "(A /\\ B) \\/ (A /\\ !B) \\/ (!A /\\ B)"
        minimizer = BooleanMinimizer(formula, 1)
        result = minimizer.minimize_calculative_tabular()
        self.assertEqual(result, [['A', '-'], ['-', 'B']])

    def test_single_variable(self):
        formula = "A"
        minimizer = BooleanMinimizer(formula, 1)
        result = minimizer.minimize_calculative()
        self.assertEqual(result, [['A']])

    def test_all_terms_covered(self):
        formula = "(A /\\ B) \\/ (A /\\ B)"
        minimizer = BooleanMinimizer(formula, 1)
        result = minimizer.minimize_calculative()
        self.assertEqual(result, [['A', 'B']])

if __name__ == '__main__':
    unittest.main()