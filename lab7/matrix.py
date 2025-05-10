from integer_binary import *
class Matrix16:
    def __init__(self):
        self.size = 16
        # инициализируем матрицу нулями
        self.mat = [[0]*16 for _ in range(16)]

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

    def find_words_in_range(self, top: int, bottom: int) -> None:
        if not ((top>=0 and top<=65535) and (bottom>=0 and bottom<=65535)):
            raise ValueError("В поск переданы неправильные аргументы")
        top=integer_binary(top).binary_module[16:]
        bottom=integer_binary(bottom).binary_module[16:]
        found_words = []
        for i in range(16):
            current_word = self.get_word(i)
            top_cmp = self.compare([int(s) for s in list(top)], current_word)
            bottom_cmp = self.compare([int(s) for s in list(bottom)], current_word)
            if top_cmp >= 0 and bottom_cmp <= 0:
                found_words.append(current_word)
        print("Найденные слова:")
        for word in found_words:
            print(word)



    def sum_ab_for_v(self, v_key_bits: list[int]) -> list[tuple[str, str]]:
        """
        Для всех слов, где V == v_key_bits:
        - вычислить A + B
        - записать результат (5 бит) в поле S (биты 11–15)
        Возвращает список: (индекс, A, B, записанное S)
        """
        results = []
        for idx in range(self.size):
            w = self.get_word(idx)

            v = w[0:3]
            if v != v_key_bits:
                continue
            a_word=''.join(str(b) for b in w[3:7])
            b_word=''.join(str(b) for b in w[7:11])

            a_val=integer_binary(a_word.zfill(32))
            b_val=integer_binary(b_word.zfill(32))
            s_val = (a_val + b_val)

            s_bits =s_val.binary_module[27:]
            new_word = w[:11] + [int(s) for s in s_bits]
            self.set_word(idx, new_word)

            results.append((''.join(str(b) for b in w), ''.join(str(b) for b in new_word)))
        return results