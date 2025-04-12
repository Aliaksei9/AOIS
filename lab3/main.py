from boolean_minimizer import BooleanMinimizer
from parser import *
from truth_table_generator import *
def main():
    expr=input("Введите логическое выражение")
    parser = Parser(expr)
    tree = parser.parse()
    generator = TruthTableGenerator(tree, sorted(set(token for token in parser.tokens if token.isalnum())))    
    formulaSDNF, formulaSKNF = generator.generate() 
    minimizerSDNF = BooleanMinimizer(formulaSDNF, 1)
    minimizerSKNF = BooleanMinimizer(formulaSKNF, 2)
    print("Расчётный:")
    print("\n СДНФ:")
    minimizerSDNF.minimize_calculative()
    print("\n СКНФ:")
    minimizerSKNF.minimize_calculative()
    print("Расчётно-табличный:")
    print("\n СДНФ:")
    minimizerSDNF.minimize_calculative_tabular()
    print("\n СКНФ:")
    minimizerSKNF.minimize_calculative_tabular()  
    print("Табличный")
    if len(minimizerSDNF.variables)==5:
        print("\n СДНФ:")
        minimizerSDNF.minimize_karnaugh_table_5_var()
        print("\n СКНФ:")
        minimizerSKNF.minimize_karnaugh_table_5_var()
    else:
        print("\n СДНФ:")
        minimizerSDNF.minimize_karnaugh()
        print("\n СКНФ:")
        minimizerSKNF.minimize_karnaugh()  
if __name__ == "__main__":
    main()