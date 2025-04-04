# Основная программа
from BooleanMinimizer import BooleanMinimizer
def main():
    form_type = int(input("Введите тип формы 1, если формула является СДНФ; 2, если СКНФ: "))
    formula = input("Введите формулу (например, (A/\\B/\\C)\\/(!A/\\B/\\C) для СДНФ): ").strip()
    minimizer = BooleanMinimizer(formula, form_type)

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