from parser import *
from truth_table_generator import *
expr=input("Введите логическое выражение")
parser = Parser(expr)
tree = parser.parse()
generator = TruthTableGenerator(tree, sorted(set(token for token in parser.tokens if token.isalnum())))
generator.generate()