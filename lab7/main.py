from matrix import *
if __name__ == '__main__':
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
    try:
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
                    for past_word, new_word in matches:
                        print(f"Было:{past_word}, Стало:{new_word}")
                else:
                    print("Нет слов с таким ключом V.")
            elif cmd == '8':
                g = int(input("g (целое число от 0 до 65535(верхняя граница)): "))
                l = int(input("l (целое число от 0 до 65535(нижняя граница)): "))

                M.find_words_in_range(g,l)
            else:
                print("Неверная опция, попробуйте ещё раз.")
    except Exception as e:
        print(e)
