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
    # --- Метод минимизации с использованием табличного метода на основе карт Карно ---
    def evaluate_formula(self, assignment):
        """
        Вычисление значения всей функции по таблице истинности.
        Для СДНФ функция равна 1, если хотя бы один импликант удовлетворён.
        Для СКНФ функция равна 0, если хотя бы одна клауза принимает 0.
        """
        if self.form_type == 1:
            return any(self.eval_implicant(term, assignment) for term in self.terms)
        else:
            return all(self.eval_clause(term, assignment) for term in self.terms)
        
    def candidate_covers(self, candidate, minterm):
        """
        Проверка, что кандидат для СКНФ (клауза) 
        обнуляется (то есть принимает значение 0)
        при заданном назначении (minterm).
        
        Для СДНФ: кандидат покрывает минтерм, если для каждого литерала,
        заданного в кандидате, назначение удовлетворяет этому литералу.
        Для СКНФ: кандидат (клауза) ложна, если ни один из её литералов не удовлетворён.
        
        """
        if self.form_type == 1:
            for i, lit in enumerate(candidate):
                if lit == '-':
                    continue
                if lit.startswith('!'):
                    if minterm[i] is not False:
                        return False
                else:
                    if minterm[i] is not True:
                        return False
            return True
        else:
            # Исправленная логика для СКНФ:
            for i, lit in enumerate(candidate):
                if lit == '-':
                    continue
                if lit.startswith('!'):
                    # Для !X, чтобы литерал был ложным, X должно быть True
                    if minterm[i] is not True:
                        return False
                else:
                    # Для X, чтобы литерал был ложным, X должно быть False
                    if minterm[i] is not False:
                        return False
            return True       
    
    def get_assignment_from_cell(self, layer, r, c, gray_order):
        """
        Восстанавливает назначение переменных для ячейки карты.
        Для строк (первые 2 переменные) используется код Грея из gray_order,
        аналогично для столбцов (следующие 2 переменные).
        Переменная для слоя (пятая) принимает значение True, если layer==1, иначе False.
        """
        bits_row = format(gray_order[r], '02b')
        bits_col = format(gray_order[c], '02b')
        assign = {}
        assign[self.variables[0]] = (bits_row[0] == '1')
        assign[self.variables[1]] = (bits_row[1] == '1')
        assign[self.variables[2]] = (bits_col[0] == '1')
        assign[self.variables[3]] = (bits_col[1] == '1')
        assign[self.variables[4]] = (layer == 1)
        return assign    
    
    def print_karnaugh_map_table(self, karnaugh_table):
        cd_order = ['00', '01', '11', '10']
        # Жёстко заданный порядок для вывода столбцов:
        # Каждая пара: ("L", i) означает, что берём i-ю ячейку левого слоя (E=0),
        # а ("R", i) – с правого слоя (E=1)
        desired_cols = [("L", 0), ("R", 0), ("R", 1), ("L", 1),
                            ("L", 2), ("R", 2), ("R", 3), ("L", 3)]
        # Формируем заголовок столбцов, добавляя E
        header_cols = []
        for layer, idx in desired_cols:
            if layer == "L":
                header_cols.append(cd_order[idx] + "0")
            else:
                header_cols.append(cd_order[idx] + "1")
        header = "AB \\ CDE".ljust(10) + "\t" + "\t".join(header_cols)
        print(header)
        # Для строк используем Gray порядок для 2 бит (AB):
        row_labels = ['00', '01', '11', '10']
        for r in range(4):
            cells = []
            for layer, idx in desired_cols:
                if layer == "L":
                    val = '1' if karnaugh_table[0][r][idx] else '0'
                else:
                    val = '1' if karnaugh_table[1][r][idx] else '0'
                cells.append(val)
            print(row_labels[r].ljust(10) + "\t" + "\t".join(cells))
        
    def candidate_cells(self, karnaugh_table, layer, start_r, start_c, l_size, r_size, c_size):
        """
        Генерирует множество ячеек (cells) для заданного прямоугольного блока
        на карте Карно, исходя из начальных координат, размера по слоям (l_size),
        строкам (r_size) и столбцам (c_size). При этом проверяется, что все ячейки 
        в блоке имеют требуемое значение (desired), зависящее от типа формы.
        Если хотя бы одна ячейка не удовлетворяет условию, возвращается None.
        """
        cells = set()
        desired = True if self.form_type == 1 else False
        for dl in range(l_size):
            current_layer = layer + dl
            for dr in range(r_size):
                r = (start_r + dr) % 4
                for dc in range(c_size):
                    c = (start_c + dc) % 4
                    cells.add((current_layer, r, c))
                    if karnaugh_table[current_layer][r][c] != desired:
                        return None  # Блок невалиден, если найдено несоответствие
        return cells

    def build_implicant_from_cells(self, cells, gray_order):
        """
        Строит импликанту (список литералов) по заданному множеству ячеек.
        Для каждой переменной берётся значение из назначений ячеек, если оно одинаково,
        иначе ставится '-' (т.е. переменная не зависит от группы).
        Также применяются корректировки, если блок покрывает все строки/столбцы или слои.
        """
        # Собираем назначения для всех ячеек группы
        group_assignments = []
        for (lay, r, c) in cells:
            assignment = self.get_assignment_from_cell(lay, r, c, gray_order)
            group_assignments.append([assignment[var] for var in self.variables])
        
        implicant = []
        for i in range(len(self.variables)):
            vals = {assign[i] for assign in group_assignments}
            if len(vals) == 1:
                val = next(iter(vals))
                if self.form_type == 1:
                    literal = self.variables[i] if val else f"!{self.variables[i]}"
                else:
                    # Для СКНФ правило обратное: 
                    literal = self.variables[i] if not val else f"!{self.variables[i]}"
                implicant.append(literal)
            else:
                implicant.append('-')
        return implicant

    def adjust_implicant(self, implicant, r_size, c_size, l_size):
        """
        Применяет корректировку импликанты: 
         - Если блок покрывает все строки (r_size == 4) → пропускаем переменные A и B.
         - Если блок покрывает все столбцы (c_size == 4) → пропускаем переменные C и D.
         - Если блок покрывает оба слоя (l_size == 2) → пропускаем переменную E.
        """
        if r_size == 4:
            implicant[0] = '-'
            implicant[1] = '-'
        if c_size == 4:
            implicant[2] = '-'
            implicant[3] = '-'
        if l_size == 2:
            implicant[4] = '-'
        return implicant

    def compute_raw_candidates(self, karnaugh_table, gray_order):
        """
        Перебирает все возможные прямоугольные блоки на карте Карно и 
        собирает валидных кандидатов в виде пар (импликанта, cell_set).
        """
        raw_candidates = []
        # Перебор размеров блока по слоям (l_size)
        for l_size in [1, 2]:
            for layer in range(2):
                # Если берём два слоя, обрабатываем только с layer 0
                if l_size == 2 and layer != 0:
                    continue
                # Перебор размеров блока по строкам
                for r_size in [1, 2, 4]:
                    for start_r in range(4):
                        # Перебор размеров блока по столбцам
                        for c_size in [1, 2, 4]:
                            for start_c in range(4):
                                cells = self.candidate_cells(karnaugh_table, layer, start_r, start_c, l_size, r_size, c_size)
                                if cells is None:
                                    continue
                                # Формируем импликанту по найденной группе ячеек
                                implicant = self.build_implicant_from_cells(cells, gray_order)
                                implicant = self.adjust_implicant(implicant, r_size, c_size, l_size)
                                raw_candidates.append((implicant, cells))
        return raw_candidates

    def minimize_karnaugh_table_5_var(self):
        """
        Минимизация СДНФ/СКНФ для пяти переменных с использованием табличного метода на основе карты Карно,
        с учётом двух 4×4 карт (x5 = 0 и x5 = 1) и циклической смежности.
        """
        print("\nМинимизация методом карты Карно:")
        gray_order = [0, 1, 3, 2]
        # Построение карты Карно: создаём две 4×4 таблицы
        karnaugh_table = [[[False for _ in range(4)] for _ in range(4)] for _ in range(2)]
        minterms = []
        for layer in range(2):
            for r in range(4):
                for c in range(4):
                    assign = self.get_assignment_from_cell(layer, r, c, gray_order)
                    val = self.evaluate_formula(assign)
                    karnaugh_table[layer][r][c] = val
                    if (self.form_type == 1 and val) or (self.form_type == 2 and not val):
                        mt = tuple(assign[var] for var in self.variables)
                        if mt not in minterms:
                            minterms.append(mt)
        print("Множество минтермов:")
        for mt in minterms:
            print(mt)

        print("\nКарта Карно:")
        self.print_karnaugh_map_table(karnaugh_table)

        # Получение «сырых» кандидатов-импликант
        raw_candidates = self.compute_raw_candidates(karnaugh_table, gray_order)
        print("\nНайденные кандидаты-импликанты (до фильтрации):")
        print(self.implicants_to_string([cand for cand, _ in raw_candidates]))

        # Далее – фильтрация кандидатов по максимальности, построение таблицы покрытия 
        # и жадный выбор минимального покрытия. (Эта часть не изменилась.)
        filtered_candidates = []
        for i, (cand_i, cells_i) in enumerate(raw_candidates):
            maximal = True
            for j, (cand_j, cells_j) in enumerate(raw_candidates):
                if i != j and cells_i.issubset(cells_j):
                    if cells_j != cells_i:
                        maximal = False
                        break
            if maximal and cand_i not in filtered_candidates:
                filtered_candidates.append(cand_i)
        print("\nНайденные кандидаты-импликанты (после фильтрации по максимальности):")
        print(self.implicants_to_string(filtered_candidates))

        # Формирование таблицы покрытия
        coverage_table = {}
        for i, candidate in enumerate(filtered_candidates):
            coverage_table[i] = [self.candidate_covers(candidate, mt) for mt in minterms]
        # Жадное покрытие
        essential = []
        covered = set()
        for col in range(len(minterms)):
            covering = [i for i, row in coverage_table.items() if row[col]]
            if len(covering) == 1:
                imp_idx = covering[0]
                if imp_idx not in essential:
                    essential.append(imp_idx)
                    covered.update(j for j, val in enumerate(coverage_table[imp_idx]) if val)
        remaining = set(range(len(minterms))) - covered
        while remaining:
            best_candidate = max(
                ((i, sum(coverage_table[i][j] for j in remaining))
                 for i in range(len(filtered_candidates)) if i not in essential),
                key=lambda x: x[1], default=None
            )
            if not best_candidate or best_candidate[1] == 0:
                break
            imp_idx = best_candidate[0]
            essential.append(imp_idx)
            covered.update(j for j, val in enumerate(coverage_table[imp_idx]) if val)
            remaining = set(range(len(minterms))) - covered

        minimal_cover = [filtered_candidates[i] for i in essential]
        print("\nМинимальная форма (выбранные кандидаты):")
        print(self.implicants_to_string(minimal_cover))
        return minimal_cover

    
    def build_kmap(self):
        """Построение линейной карты Карно (в виде списка) с использованием кода Грея.
           Для СДНФ по умолчанию ячейки инициализируются 0, а для СКНФ – 1."""
        num_vars = len(self.variables)
        size = 1 << num_vars
        kmap = [0] * size if self.form_type == 1 else [1] * size
        gray = self.gray_code(num_vars)
        
        for const in self.terms:
            binary = ''
            for var in self.variables:
                # Для СКНФ: мы ищем комбинацию, при которой весь дизъюнкт ложен
                if self.form_type == 1:
                    # СДНФ: ищем значение, при котором конъюнкт истинен
                    if f"!{var}" in const:
                        binary += '0'
                    elif var in const:
                        binary += '1'
                else:
                    # СКНФ: находим комбинацию, при которой дизъюнкт ложен
                    if f"!{var}" in const:
                        binary += '1'  # !A ложен, когда A = 1
                    elif var in const:
                        binary += '0'  # A ложен, когда A = 0
                    else:
                        binary += '-'  # Если переменной нет — она не влияет (не фиксируется)
            if '-' in binary:
                # Дизъюнкт не фиксирует значение — значит он не обнуляет ни одну ячейку
                continue
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
            if len(self.variables)==5:
                return self.minimize_karnaugh_table_5_var()
            else:
                return self.minimize_karnaugh()
        else:
            raise ValueError("Неизвестный метод минимизации.")