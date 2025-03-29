import unittest
import io
import contextlib
from parser import *
from truth_table_generator import *
class TestTruthTableGenerator(unittest.TestCase):
    def test_simple_expression_A_and_B(self):
        # Проверяем выражение "A & B"
        expr = "A & B"
        parser = Parser(expr)
        tree = parser.parse()
        # Для теста берем переменные в отсортированном порядке
        variables = sorted(set(token for token in parser.tokens if token.isalnum()))
        generator = TruthTableGenerator(tree, variables)
        
        # Захватываем вывод generate()
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            generator.generate()
        output = f.getvalue()
        
        # Проверяем, что вывод содержит корректные заголовки переменных и подвыражений
        self.assertIn("A", output)
        self.assertIn("B", output)
        # Проверяем, что столбец "Результат" отсутствует
        self.assertNotIn("Результат", output)
        
        # Для "A & B" таблица истинности (с учетом переменных A и B):
        # Комбинации:
        # 0: A=0, B=0 => 0
        # 1: A=0, B=1 => 0
        # 2: A=1, B=0 => 0
        # 3: A=1, B=1 => 1
        # Ожидаем индексную форму:
        # СДНФ: (3) |
        # СКНФ: (0,1,2) &
        self.assertIn("(3) |", output)
        self.assertIn("(0,1,2) &", output)