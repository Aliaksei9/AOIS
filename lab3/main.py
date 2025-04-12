# Основная программа
from boolean_minimizer import BooleanMinimizer
from parser import *
from truth_table_generator import *
def main():
    expr=input("Введите логическое выражение")
    parser = Parser(expr)
    tree = parser.parse()
    generator = TruthTableGenerator(tree, sorted(set(token for token in parser.tokens if token.isalnum())))    
    formulaSDNF, formulaSKNF = generator.generate() 
    print(formulaSKNF)
    form_type = int(input("Введите тип формы 1, если формула является СДНФ; 2, если СКНФ: "))
    if form_type==1:
        minimizer = BooleanMinimizer(formulaSDNF, form_type)
    else:
        minimizer = BooleanMinimizer(formulaSKNF, form_type)
    result = minimizer.minimize_karnaugh_table_5_var()
    print(result)
    print("\nВыберите метод минимизации:")
    print("1. Расчетный метод")
    print("2. Расчетно-табличный метод")
    print("3. Табличный метод (Карта Карно)")
    choice = input("Введите номер метода (1-3): ").strip()

    methods = {'1': 'calculative', '2': 'calculative_tabular', '3': 'karnaugh'}
    if choice in methods:
        minimizer.run(methods[choice])
    else:
        print("Неверный выбор метода.")

if __name__ == "__main__":
    main()