# Класс для парсинга выражения в дерево разбора
from node import *
class Parser:
    def __init__(self, expression):
        self.tokens = self.tokenize(expression)
        self.pos = 0

    def tokenize(self, expression):
        tokens = []
        i = 0
        while i < len(expression):
            if expression[i].isspace():
                i += 1
                continue
            if expression[i].isalnum():
                var = ""
                while i < len(expression) and expression[i].isalnum():
                    var += expression[i]
                    i += 1
                tokens.append(var)
                continue
            if expression[i] in "!&|()":
                tokens.append(expression[i])
            elif expression[i] == '-' and i+1 < len(expression) and expression[i+1] == '>':
                tokens.append("->")
                i += 1
            elif expression[i] == '<' and i+2 < len(expression) and expression[i+1] == '-' and expression[i+2] == '>':
                tokens.append("<->")
                i += 2
            else:
                raise ValueError(f"Недопустимый символ: {expression[i]}")
            i += 1
        return tokens

    def parse(self):
        node = self.parse_expression()
        if self.pos != len(self.tokens):
            raise ValueError("Обнаружены лишние токены после разбора!")
        return node

    def parse_expression(self):
        node = self.parse_implication()
        while self.pos < len(self.tokens) and self.tokens[self.pos] == "<->":
            op = self.tokens[self.pos]
            self.pos += 1
            right = self.parse_implication()
            node = Node(op=op, left=node, right=right, explicit=False)
        return node

    def parse_implication(self):
        node = self.parse_or()
        while self.pos < len(self.tokens) and self.tokens[self.pos] == "->":
            op = self.tokens[self.pos]
            self.pos += 1
            right = self.parse_or()
            node = Node(op=op, left=node, right=right, explicit=False)
        return node

    def parse_or(self):
        node = self.parse_and()
        while self.pos < len(self.tokens) and self.tokens[self.pos] == "|":
            op = self.tokens[self.pos]
            self.pos += 1
            right = self.parse_and()
            node = Node(op=op, left=node, right=right, explicit=False)
        return node

    def parse_and(self):
        node = self.parse_not()
        while self.pos < len(self.tokens) and self.tokens[self.pos] == "&":
            op = self.tokens[self.pos]
            self.pos += 1
            right = self.parse_not()
            node = Node(op=op, left=node, right=right, explicit=False)
        return node

    def parse_not(self):
        if self.pos < len(self.tokens) and self.tokens[self.pos] == "!":
            self.pos += 1
            child = self.parse_not()
            return Node(op="!", child=child, explicit=False)
        else:
            return self.parse_primary()

    def parse_primary(self):
    # Если текущий токен — закрывающая скобка, то это ошибка
        if self.tokens[self.pos] == ")":
            raise ValueError("Неожиданная закрывающая скобка: ')' без соответствующей открывающей скобки")
        if self.tokens[self.pos] == "(":
            self.pos += 1  # пропускаем '('
            node = self.parse_expression()
            if self.pos >= len(self.tokens) or self.tokens[self.pos] != ")":
                raise ValueError("Ожидалась ')'!")
            self.pos += 1  # пропускаем ')'
            node.explicit = True
            return node
        else:
            var = self.tokens[self.pos]
            # Если токен не является алфавитно-цифровым, сообщаем об ошибке
            if not var.isalnum():
                raise ValueError(f"Ожидалась переменная или '(', получен: '{var}'")
            self.pos += 1
            return Node(var=var)

