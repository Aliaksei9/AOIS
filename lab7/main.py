class Matrix16:
    def __init__(self, size=16):
        self.size = size
        # инициализируем матрицу нулями
        self.mat = [[0]*size for _ in range(size)]

    def __str__(self):
        # красивая печать всей матрицы
        lines = []
        for row in self.mat:
            lines.append(' '.join(str(bit) for bit in row))
        return '\n'.join(lines)

    def print_word(self, index):
        w = self.get_word(index)
        print(f"Word #{index}: {''.join(str(bit) for bit in w)}")

    def get_word(self, index: int) -> list[int]:
        # список номеров строк в нужном порядке
        rows = list(range(index, self.size)) + list(range(0, index))
        # забираем бит из каждой строки в столбце index
        return [self.mat[r][index] for r in rows]

    def set_word(self, index: int, bits: list[int]) -> None:
        """
        Записывает слово `bits` (длина должна быть = size) в столбец `index`,
        начиная с строки `index` и вниз до конца, затем с начала до строки index-1.
        """
        if len(bits) != self.size:
            raise ValueError(f"Длина списка bits должна быть {self.size}, а получена {len(bits)}")
        rows = list(range(index, self.size)) + list(range(0, index))
        for r, b in zip(rows, bits):
            self.mat[r][index] = b

    # чтение слова номер index:
    # берём столбец index, начиная с строки index, wrap-around по модулю size
    def get_address(self, index: int, length: int = None) -> list[int]:
        """
        Считывает address #index как диагональ,
        начинающуюся в (row=index, col=0),
        затем (index+1,1), (index+2,2)... с wrap-around по строкам.
        """
        if length is None:
            length = self.size
        return [
            self.mat[(index + j) % self.size][j]
            for j in range(length)
        ]

    def set_address(self, index: int, bits: list[int]) -> None:
        """
        Записывает bits вдоль диагонали #index,
        начиная в (row=index, col=0), затем (index+1,1)...
        bits может быть длины до size.
        """
        for j, b in enumerate(bits):
            r = (index + j) % self.size
            c = j
            self.mat[r][c] = b

    # логические функции – остаются без изменений
    def f2(self, col1, col2):
        w1 = self.get_word(col1)
        w2 = self.get_word(col2)
        return [1 if (a == 1 and b == 0) else 0 for a, b in zip(w1, w2)]

    def f7(self, col1, col2):
        w1 = self.get_word(col1)
        w2 = self.get_word(col2)
        return [1 if (a == 1 or b == 1) else 0 for a, b in zip(w1, w2)]

    def f8(self, col1, col2):
        w1 = self.get_word(col1)
        w2 = self.get_word(col2)
        return [1 if (a == 0 and b == 0) else 0 for a, b in zip(w1, w2)]

    def f13(self, col1, col2):
        w1 = self.get_word(col1)
        w2 = self.get_word(col2)
        return [1 if not (a == 1 and b == 0) else 0 for a, b in zip(w1, w2)]

    # поиск всех слов, значение которых (при интерпретации как число) лежит в [g, l]
    def compare(self, value1: list[int], value2: list[int]) -> int:
        for a, b in zip(value1, value2):
            if a > b:
                return 1
            elif a < b:
                return -1
        return 0

    def find_words_in_range(self, matrix, top: list[int], bottom: list[int]) -> list[bool]:
        flags = []
        size = len(matrix)  # предполагаем, что matrix — квадратная матрица
        for i in range(size):
            current_word = self.get_word(matrix, i)
            top_cmp = self.compare(top, current_word)
            bottom_cmp = self.compare(bottom, current_word)
            flags.append(top_cmp >= 0 and bottom_cmp <= 0)
        return flags

    # суммирование полей A и B в словах S для тех слов, у которых ключ V == заданный ключ
    # допущение: в каждом слове S есть два полу-слова A (биты 0..7) и B (8..15), а V – ещё одна маска
    def sum_ab_for_v(self, v_key_bits: list[int]) -> list[tuple[int, int, int, int]]:
        """
        Для всех слов, где V == v_key_bits:
        - вычислить A + B
        - записать результат (5 бит) в поле S (биты 11–15)
        Возвращает список: (индекс, A, B, записанное S)
        """
        results = []
        for idx in range(self.size):
            w = self.get_word(idx)
            if len(w) < 16:
                continue

            v = w[0:3]
            if v != v_key_bits:
                continue

            a_val = int(''.join(str(bit) for bit in w[3:7]), 2)
            b_val = int(''.join(str(bit) for bit in w[7:11]), 2)
            s_val = (a_val + b_val) & 0b11111  # только 5 бит

            s_bits = [int(bit) for bit in f'{s_val:05b}']
            new_word = w[:11] + s_bits
            self.set_word(idx, new_word)

            results.append((idx, a_val, b_val, s_val))
        return results


M = Matrix16()
menu = """
    1) Добавить слово
    2) Добавить адрес
    3) f2 (A AND NOT B)
    4) f7 (A OR B)
    5) f8 (NOT A AND NOT B)
    6) f13 (NOT (A AND NOT B))
    7) Сумма
    8) Поиск слов по диапазону [g, l]
    0) Выход
    """
while True:
    print("Текущая матрица:")
    print(M)  # __str__ печатает всю матрицу
    print(menu)
    cmd = input("Выберите опцию: ").strip()
    if cmd == '0':
        break
    elif cmd == '1':
        col = int(input("Столбец (0–15): "))
        bits = list(map(int, input("16 бит через пробел: ").split()))
        M.set_word(col, bits)
        print("Слово записано.")
    elif cmd == '2':
        idx = int(input("Номер адреса (0–15): "))
        bits = list(map(int, input("Биты адреса через пробел: ").split()))
        if len(bits) > M.size:
            print(f"Можно задать не более {M.size} бит.")
        else:
            M.set_address(idx, bits)
            print(f"Адрес на диагонали {idx} записан.")
    elif cmd in ('3', '4', '5', '6'):
        funcs = {'3': M.f2, '4': M.f7, '5': M.f8, '6': M.f13}
        c1 = int(input("col1 (0–15): "))
        c2 = int(input("col2 (0–15): "))
        res = funcs[cmd](c1, c2)
        print("Результат:", ''.join(str(b) for b in res))
    elif cmd == '7':
        vk = list(map(int, input("Ключ V (3 бита через пробел): ").split()))
        matches = M.sum_ab_for_v(vk)
        if matches:
            print("Обновлённые слова:")
            for i, a, b, s in matches:
                print(f"col={i}: A={a}, B={b}, S={s}")
        else:
            print("Нет слов с таким ключом V.")
    elif cmd == '8':
        g = int(input("g (целое число от 0 до 65535): "))
        l = int(input("l (целое число от 0 до 65535): "))

        top_bits = [int(b) for b in f'{l:016b}']
        bottom_bits = [int(b) for b in f'{g:016b}']

        flags = M.find_words_in_range(top_bits, bottom_bits)
        found_any = False

        for i, match in enumerate(flags):
            if match:
                word_bits = M.get_word(i)
                word_value = int(''.join(str(b) for b in word_bits), 2)
                print(f"col={i}: word={''.join(str(b) for b in word_bits)}, value={word_value}")
                found_any = True

        if not found_any:
            print("Нет слов в заданном диапазоне.")

    else:
        print("Неверная опция, попробуйте ещё раз.")
    print(M)
