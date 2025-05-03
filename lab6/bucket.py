class Bucket:
    def __init__(self):
        # Поля строки хеш-таблицы
        self.key = None       # ID (название)
        self.value = None     # Pi (специализация)
        self.V = None         # числовое значение ключа
        self.h = None         # хеш-адрес
        self.C = 0            # флаг коллизии
        self.U = 0            # флаг занятости
        self.T = 0            # терминальный флаг
        self.D = 0            # флаг удаления
        self.Po = None        # указатель на следующую запись цепочки