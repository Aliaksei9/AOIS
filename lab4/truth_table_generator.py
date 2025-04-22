from node import *
class TruthTableGenerator:
    def __init__(self, tree, variables):
        self.tree = tree
        self.variables = variables
        self.subexpressions = self.get_subexpressions(tree)

    def get_subexpressions(self, node):
        subs = []
        if node is None:
            return subs
        if node.var is not None:
            return subs  # переменная не является подвыражением
        if node.op == "!":
            subs.extend(self.get_subexpressions(node.child))
        else:
            subs.extend(self.get_subexpressions(node.left))
            subs.extend(self.get_subexpressions(node.right))
        subs.append(node.expr)
        return subs

    def evaluate_tree(self, node, assignment, sub_values):
        if node.var is not None:
            return bool(assignment[node.var])
        if node.op == "!":
            child_val = self.evaluate_tree(node.child, assignment, sub_values)
            val = not child_val
            sub_values[node.expr] = str(int(val))
            return val
        left_val = self.evaluate_tree(node.left, assignment, sub_values)
        right_val = self.evaluate_tree(node.right, assignment, sub_values)
        if node.op == "&":
            val = left_val and right_val
        elif node.op == "|":
            val = left_val or right_val
        elif node.op == "->":
            val = (not left_val) or right_val
        elif node.op == "<->":
            val = (left_val == right_val)
        else:
            raise ValueError("Неизвестный оператор")
        sub_values[node.expr] = str(int(val))
        return val

    def generate(self, lit):
        headers = self.variables + [lit]
        data = [headers]
        sdnf_terms = []  # Минтермы для СДНФ
        sknf_terms = []  # Макстермы для СКНФ
    
        for i in range(2 ** len(self.variables)):
            assignment = {var: (i >> (len(self.variables) - 1 - idx)) & 1
                          for idx, var in enumerate(self.variables)}
            sub_values = {}
            result = self.evaluate_tree(self.tree, assignment, sub_values)
    
            # Строка: значения переменных + результат
            row = [str(assignment[var]) for var in self.variables] + [str(int(result))]
    
            if result:
                term = "/\\".join(f"{var}" if assignment[var] else f"!{var}" for var in self.variables)
                sdnf_terms.append(f"({term})")
            else:
                term = "\\/".join(f"{var}" if not assignment[var] else f"!{var}" for var in self.variables)
                sknf_terms.append(f"({term})")
            data.append(row)
    
        # Вычисляем ширину для каждого столбца
        col_widths = [max(len(str(row[j])) for row in data) for j in range(len(headers))]
    
        # Функция форматирования строки
        def format_row(row):
            return " | ".join(str(cell).center(col_widths[idx]) for idx, cell in enumerate(row))
    
        # Печатаем таблицу
        print(format_row(data[0]))
        print("-" * (sum(col_widths) + 3 * (len(headers) - 1)))
        for row in data[1:]:
            print(format_row(row))
    
        return " \\/ ".join(sdnf_terms) if sdnf_terms else "Нет SDNF"
