from hash_table import *

ht = HashTable()
diseases = [
            ('Ангина', 'Отоларинголог'),
            ('Бронхит', 'Пульмонолог'),
            ('Грипп', 'Терапевт'),
            ('Диабет', 'Эндокринолог'),
            ('Язва', 'Гастроэнтеролог'),
            ('Астма', 'Аллерголог'),
            ('Кариес', 'Стоматолог'),
            ('Отит', 'Отоларинголог'),
            ('Рак', 'Онколог'),
            ('Туберкулёз', 'Фтизиатр'),
        ]
for name, spec in diseases:
            ht.insert(name, spec)
while True:
    ht.display()
    print("\nМеню:")
    print("1. Добавить запись")
    print("2. Удалить запись")
    print("3. Обновить запись")
    print("0. Выход")
    choice = input("Выберите действие: ")
    try:
        if choice == '1':
            k = input("Введите название заболевания: ")
            v = input("Введите специализацию врача: ")
            ht.insert(k, v)
            print("Добавлено.")
        elif choice == '2':
            k = input("Введите название заболевания для удаления: ")
            ht.delete(k)
            print("Удалено.")
        elif choice == '3':
            k = input("Введите название заболевания для обновления: ")
            v = input("Введите новую специализацию: ")
            ht.update(k, v)
            print("Обновлено.")
        elif choice == '0':
            print("Выход.")
            break
        else:
            print("Неверный выбор.")
    except KeyError as e:
        print(e)

