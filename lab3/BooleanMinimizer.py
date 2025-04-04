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
        print("\nМинимизация расчетным методом:")
        implicants = self.terms.copy()
        stage = 1
        while True:
            print(f"\nСтадия {stage} склеивания:")
            print(self.implicants_to_string(implicants))
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
        print("\nТупиковая форма после удаления лишних импликант:")
        print(self.implicants_to_string(essential))
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

    # --- Расчетно-табличный метод ---

    def covers(self, implicant, term):
        for i, lit in enumerate(implicant):
            if lit != '-' and lit != term[i]:
                return False
        return True

    def build_coverage_table(self, implicants):
        """Построение таблицы покрытия."""
        table = {}
        for i, imp in enumerate(implicants):
            table[i] = [self.covers(imp, const) for const in self.terms]
        return table

    def print_table(self, table, implicants):
        print("\nТаблица покрытия:")
        col_width = 15  # Фиксированная ширина для каждого столбца
        # Формируем заголовок: столбец для "Импликанта" и для каждого конституента
        header_constituents = " | ".join(f"{self.term_to_string(c):^{col_width}}" for c in self.terms)
        header = f"{'Импликанта':^{col_width}} | " + header_constituents
        print(header)
        print("-" * len(header))
        # Вывод строк таблицы
        for i, row in table.items():
            imp_str = f"{self.term_to_string(implicants[i]):^{col_width}}"
            row_values = " | ".join(f"{'X' if x else ' ':^{col_width}}" for x in row)
            print(f"{imp_str} | " + row_values)


    def find_minimal_cover(self, table, implicants):
        """Нахождение минимального покрытия."""
        essential = []
        covered = set()
        # Сначала добавляем необходимые импликанты (покрывающие уникальные конституенты)
        for col in range(len(self.terms)):
            covering_imps = [i for i, row in table.items() if row[col]]
            if len(covering_imps) == 1:
                imp_idx = covering_imps[0]
                if imp_idx not in essential:
                    essential.append(imp_idx)
                    covered.update(j for j, val in enumerate(table[imp_idx]) if val)
        # Покрываем оставшиеся конституенты
        remaining = set(range(len(self.terms))) - covered
        while remaining:
            best_imp = max(
                ((i, sum(row[j] for j in remaining)) for i, row in table.items() if i not in essential),
                key=lambda x: x[1], default=None
            )
            if not best_imp:
                break
            imp_idx = best_imp[0]
            essential.append(imp_idx)
            covered.update(j for j, val in enumerate(table[imp_idx]) if val)
            remaining -= covered
        return [implicants[i] for i in essential]

    def minimize_calculative_tabular(self):
        """Минимизация расчетно-табличным методом."""
        print("\nМинимизация расчетно-табличным методом:")
        implicants = self.terms.copy()
        stage = 1
        while True:
            print(f"\nСтадия {stage} склеивания:")
            print(self.implicants_to_string(implicants))
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
        # Таблица покрытия
        table = self.build_coverage_table(implicants)
        self.print_table(table, implicants)
        # Минимальное покрытие
        minimal = self.find_minimal_cover(table, implicants)
        print("\nМинимальная форма:")
        print(self.implicants_to_string(minimal))
        return minimal

        # Вывод таблицы покрытия для наглядности (при необходимости)
        table = self.build_coverage_table(implicants)
        self.print_table(table, implicants)

        # Применяем новый метод удаления лишних импликант, который подставляет критическое назначение
        minimal = self.remove_redundant(implicants)

        print("\nМинимальная форма после удаления лишних импликант:")
        print(self.implicants_to_string(minimal))
        return minimal


    # --- Табличный метод (Карта Карно) ---

    def build_kmap(self):
        """Построение линейной карты Карно (в виде списка) с использованием кода Грея.
           Для СДНФ по умолчанию ячейки инициализируются 0, а для СКНФ – 1."""
        num_vars = len(self.variables)
        size = 1 << num_vars
        if self.form_type == 1:
            kmap = [0] * size
        else:  # Для СКНФ функция истинна, если не выполнен макситерм, поэтому по умолчанию 1.
            kmap = [1] * size
        gray = self.gray_code(num_vars)
        for const in self.terms:
            binary = ''
            for var in self.variables:
                if f"!{var}" in const:
                    binary += '0'
                elif var in const:
                    binary += '1'
            idx = gray.index(binary)
            if self.form_type == 1:
                kmap[idx] = 1
            else:
                kmap[idx] = 0
        return kmap, gray

    def gray_code(self, n):
        """Генерация кода Грея."""
        if n <= 0:
            return ['']
        prev = self.gray_code(n - 1)
        return ['0' + code for code in prev] + ['1' + code for code in prev[::-1]]

    def get_grid_dimensions(self, n):
        """Определение размеров карты и разбиения переменных на оси."""
        if n == 1:
            return (1, 2, [''], [self.gray_code(1)[0], self.gray_code(1)[1]])
        elif n == 2:
            return (2, 2, self.gray_code(1), self.gray_code(1))
        elif n == 3:
            # Для 3 переменных: 1 переменная по оси Y, 2 переменные по оси X (Gray: ['00','01','11','10'])
            return (2, 4, self.gray_code(1), self.gray_code(2))
        elif n == 4:
            # Для 4 переменных: 2 переменные по оси Y и 2 по оси X (Gray: ['00','01','11','10'])
            return (4, 4, self.gray_code(2), self.gray_code(2))
        else:
            raise ValueError("Карты Карно поддерживаются только до 4 переменных.")

    def print_kmap(self, grid, row_codes, col_codes):
        """Вывод карты Карно с осями и указанием переменных."""
        num_vars = len(self.variables)
        # Определяем какие переменные отображаются по строкам и столбцам
        if num_vars == 1:
            row_vars = []
            col_vars = [self.variables[0]]
        elif num_vars == 2:
            row_vars = [self.variables[0]]
            col_vars = [self.variables[1]]
        elif num_vars == 3:
            row_vars = [self.variables[0]]
            col_vars = self.variables[1:3]
        else:  # n==4
            row_vars = self.variables[:2]
            col_vars = self.variables[2:]

        # Вывод заголовка столбцов
        col_header = " " * 10
        for j, code in enumerate(col_codes):
            col_header += f"{code:>6}"
        print("\nКарта Карно:")
        print("Столбцы (", ", ".join(col_vars), ")")
        print(col_header)
        # Вывод строк с указанием row_codes
        for i, row in enumerate(grid):
            line = f"{row_codes[i]:>8} |"
            for val in row:
                line += f"{val:>6}"
            print(line)
        print("Строки (", ", ".join(row_vars), ")")

    def enumerate_groups(self, grid, num_rows, num_cols, target):
        """Перебор всех возможных групп с учётом циклического (wrap-around) соединения.
           Возвращает список кортежей (covered, implicant) где covered – набор координат, а implicant – список символов ('1','0','-')."""
        groups = []
        # Возможные размеры групп – степени двойки, не превышающие размеры карты.
        possible_heights = [h for h in [1,2,4] if h <= num_rows]
        possible_widths = [w for w in [1,2,4] if w <= num_cols]
        for h in possible_heights:
            for w in possible_widths:
                # Перебор всех возможных позиций (начало группы)
                for r in range(num_rows):
                    for c in range(num_cols):
                        # Собираем координаты с учетом wrap-around
                        cells = [((r + dr) % num_rows, (c + dc) % num_cols) for dr in range(h) for dc in range(w)]
                        # Проверяем, что все клетки имеют значение target
                        if all(grid[i][j] == target for i, j in cells):
                            # Вычисляем implicant группы: для каждой переменной определяется, фиксирован ли бит
                            bin_codes = []
                            # Определяем число бит для строк и столбцов:
                            if num_rows * num_cols == 2**len(self.variables):
                                if len(self.variables) == 1:
                                    row_bits = ['']
                                    col_bits = self.gray_code(1)
                                elif len(self.variables) == 2:
                                    row_bits = self.gray_code(1)
                                    col_bits = self.gray_code(1)
                                elif len(self.variables) == 3:
                                    row_bits = self.gray_code(1)
                                    col_bits = self.gray_code(2)
                                else:  # n==4
                                    row_bits = self.gray_code(2)
                                    col_bits = self.gray_code(2)
                            else:
                                row_bits = ['']*num_rows
                                col_bits = ['']*num_cols
                            for i, j in cells:
                                code = row_bits[i] + col_bits[j]
                                bin_codes.append(code)
                            # Для каждого разряда определяем, одинаков ли он во всех клетках
                            implicant = []
                            for bit in range(len(self.variables)):
                                bits = [code[bit] for code in bin_codes]
                                if all(b == bits[0] for b in bits):
                                    implicant.append(bits[0])
                                else:
                                    implicant.append('-')
                            groups.append((set(cells), implicant))
        # Убираем дубликаты (одинаковые по покрытию и implicant)
        unique = {}
        for covered, imp in groups:
            key = (frozenset(covered), tuple(imp))
            unique[key] = (covered, imp)
        return list(unique.values())

    def select_groups(self, groups, grid, num_rows, num_cols, target):
        """Жадный выбор групп, покрывающих все клетки с target."""
        # Собираем все минотермы: координаты клеток со значением target
        minterms = {(i, j) for i in range(num_rows) for j in range(num_cols) if grid[i][j] == target}
        # Сортируем группы по размеру (убывание)
        groups = sorted(groups, key=lambda x: len(x[0]), reverse=True)
        selected = []
        uncovered = set(minterms)
        for covered, imp in groups:
            if uncovered & covered:
                selected.append((covered, imp))
                uncovered -= covered
            if not uncovered:
                break
        return selected

    def implicant_to_term(self, implicant):
        """Преобразует implicant (список символов '1','0','-') в список литералов."""
        term = []
        for i, bit in enumerate(implicant):
            if bit == '-':
                continue
            elif bit == '1':
                term.append(self.variables[i])
            elif bit == '0':
                term.append("!"+self.variables[i])
        # Если term пуст – для СДНФ это 1, а для СКНФ – 1 (так как 1 является нейтральным элементом для конъюнкции)
        if not term:
            term = ['1']
        return term

    def minimize_karnaugh(self):
        """Минимизация с помощью карт Карно для СДНФ и СКНФ (до 4 переменных)."""
        print("\nМинимизация табличным методом (Карта Карно):")
        num_vars = len(self.variables)
        if num_vars > 4:
            raise ValueError("Карты Карно для более чем 4 переменных не поддерживаются.")
        # Получаем линейную карту и полный код Грея
        full_kmap, full_gray = self.build_kmap()
        full_map = {code: full_kmap[i] for i, code in enumerate(full_gray)}
        # Определяем размеры карты и осевые коды
        num_rows, num_cols, row_codes, col_codes = self.get_grid_dimensions(num_vars)
        # Строим 2D сетку карты
        grid = [[0 for _ in range(num_cols)] for _ in range(num_rows)]
        for i in range(num_rows):
            for j in range(num_cols):
                binary = row_codes[i] + col_codes[j]
                grid[i][j] = full_map.get(binary, 0)
        # Вывод карты с осями и указанием переменных
        self.print_kmap(grid, row_codes, col_codes)
        # Целевое значение: для СДНФ – группируем единицы, для СКНФ – нули
        target = 1 if self.form_type == 1 else 0
        # Находим все возможные группы
        groups = self.enumerate_groups(grid, num_rows, num_cols, target)
        # Выбираем группы для покрытия всех минотермов
        selected_groups = self.select_groups(groups, grid, num_rows, num_cols, target)
        # Преобразуем выбранные группы в список импликант
        implicants = [self.implicant_to_term(imp) for _, imp in selected_groups]
        print("\nМинимизирующая форма:")
        print(self.implicants_to_string(implicants))
        return implicants

    def run(self, method):
        """Запуск указанного метода минимизации."""
        if method == 'calculative':
            return self.minimize_calculative()
        elif method == 'calculative_tabular':
            return self.minimize_calculative_tabular()
        elif method == 'karnaugh':
            return self.minimize_karnaugh()
        else:
            raise ValueError("Неизвестный метод минимизации.")