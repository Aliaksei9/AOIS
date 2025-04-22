import re
import itertools

class BooleanMinimizer:
    def __init__(self, formula, form_type):
        self.formula = formula
        self.form_type = form_type  
        self.variables = self.extract_variables()
        self.terms = self.parse_formula()

    def extract_variables(self):
        """Извлечение уникальных переменных из формулы."""
        return sorted(set(re.findall(r'[A-Za-z]', self.formula)))

    def parse_formula(self):
        """Парсинг формулы в список термов."""
        if self.form_type == 1:
            terms = re.split(r'\s*\\/\s*', self.formula)
            terms = [term.strip('() ') for term in terms]
            term_lists = [re.split(r'\s*/\\\s*', term) for term in terms]
        elif self.form_type == 2:
            terms = re.split(r'\s*/\\\s*', self.formula)
            terms = [term.strip('() ') for term in terms]
            term_lists = [re.split(r'\s*\\/\s*', term) for term in terms]
        # Дополнить каждый терм символами '-' до длины равной количеству переменных
        for term in term_lists:
            while len(term) < len(self.variables):
                term.append('-')
        return term_lists

        

    def term_to_string(self, term):
        """Преобразование терма в строковый вид."""
        if self.form_type == 1:
            return '/\\'.join(term)
        return '\\/'.join(term)

    def implicants_to_string(self, implicants):
        """Преобразование списка импликант в строку."""
        if self.form_type == 1:
            return ' \\/ '.join([self.term_to_string(imp) for imp in implicants])
        return ' /\\ '.join([self.term_to_string(imp) for imp in implicants])

    # --- Расчетный метод ---

    def get_diff(self, term1, term2):
        """Подсчет различий между двумя термами."""
        diff = 0
        for lit1, lit2 in zip(term1, term2):
            if lit1 != lit2:
                diff += 1
        return diff

    def glue(self, term1, term2):
        """Склеивание двух термов."""
        new_term = []
        for lit1, lit2 in zip(term1, term2):
            if lit1 == lit2:
                new_term.append(lit1)
            else:
                new_term.append('-')
        return new_term

    def minimize_calculative(self):
        """Минимизация расчетным методом с выводом стадий склеивания."""
        implicants = self.terms.copy()
        stage = 1
        while True:
            new_implicants = []
            used = set()
            for i, j in itertools.combinations(range(len(implicants)), 2):
                if self.get_diff(implicants[i], implicants[j]) == 1:
                    new_term = self.glue(implicants[i], implicants[j])
                    new_implicants.append(new_term)
                    used.add(i)
                    used.add(j)
            if not new_implicants:
                break
            implicants = [implicants[i] for i in range(len(implicants)) if i not in used] + new_implicants
            stage += 1
        # Удаление лишних импликант
        essential = self.remove_redundant(implicants)
        return essential

    def assignments_for_implicant(self, implicant):
        """
        Генерирует все возможные назначения (assignment) для импликанты,
        учитывая, что в позициях с '-' переменная может принимать любое значение.
        Для фиксированных позиций назначение уже задано критическим назначением.
        """
        fixed = {}
        free_vars = []
        for i, var in enumerate(self.variables):
            lit = implicant[i]
            if lit == '-':
                free_vars.append(var)
            elif lit.startswith('!'):
                fixed[var] = False
            else:
                fixed[var] = True
        assignments = []
        for bits in itertools.product([False, True], repeat=len(free_vars)):
            assign = fixed.copy()
            for var, val in zip(free_vars, bits):
                assign[var] = val
            assignments.append(assign)
        return assignments

    def eval_implicant(self, implicant, assignment):
        """
        Оценивает импликанту для ДНФ (конъюнкция литералов) при заданном назначении.
        Возвращает True, если для всех позиций, где implicant задаёт конкретное значение,
        оно совпадает с соответствующим значением в assignment.
        """
        for i, var in enumerate(self.variables):
            lit = implicant[i]
            if lit == '-':
                continue
            elif lit.startswith('!'):
                if assignment[var] is not False:
                    return False
            else:
                if assignment[var] is not True:
                    return False
        return True

    def eval_clause(self, clause, assignment):
        """
        Оценивает импликанту для КНФ (дизъюнкция литералов) при заданном назначении.
        Возвращает True, если хотя бы один литерал удовлетворён (то есть дизъюнкция равна 1).
        """
        for i, var in enumerate(self.variables):
            lit = clause[i]
            if lit == '-':
                return True
            elif lit.startswith('!'):
                if assignment[var] is False:
                    return True
            else:
                if assignment[var] is True:
                    return True
        return False

    def remove_redundant(self, implicants):
        """
        Удаляет лишние импликанты по следующей логике:

        Для СДНФ:
          Для каждой импликанты imp генерируются все назначения, удовлетворяющие imp.
          Для каждого такого назначения вычисляется значение оставшегося выражения –
          логическое ИЛИ (OR) всех остальных импликант, оценённых через eval_implicant.
          Если для каждого такого назначения значение OR равно 1, то удаление imp не изменяет функцию.

        Для СКНФ (аналогично, но с конъюнкцией и проверкой на 0).
        """
        new_implicants = implicants.copy()
        for imp in implicants:
            others = [other for other in new_implicants if other != imp]
            redundant = True
            if self.form_type == 1:
                # Для каждой возможной комбинации свободных переменных, удовлетворяющей imp:
                for assign in self.assignments_for_implicant(imp):
                    # Оцениваем оставшееся выражение как OR всех других импликант
                    overall = any(self.eval_implicant(other, assign) for other in others)
                    if not overall:
                        redundant = False
                        break
            else:  # для 'cnf'
                for assign in self.assignments_for_implicant(imp):
                    # Для КНФ считаем, что оставшееся выражение – это AND всех других клауз,
                    # а функция равна 0, если хотя бы одна клаузa равна 0.
                    overall = all(self.eval_clause(other, assign) for other in others) if others else True
                    if overall:  # если выражение принимает 1, а imp должна дать 0, то imp не лишняя
                        redundant = False
                        break
            if redundant and imp in new_implicants:
                new_implicants.remove(imp)
        # Удаляем дубликаты, если они есть:
        unique_implicants = []
        for imp in new_implicants:
            if imp not in unique_implicants:
                unique_implicants.append(imp)
        return unique_implicants