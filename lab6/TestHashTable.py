import unittest
import io
import sys
from hash_table import *

class TestHashTableCoverage(unittest.TestCase):
    def setUp(self):
        self.ht = HashTable(initial_size=5, q=1)
        # создаем несколько записей
        self.entries = [
            ('Ангина', 'Отоларинголог'),
            ('Бронхит', 'Пульмонолог'),
            ('Грипп', 'Терапевт'),
            ('Диабет', 'Эндокринолог'),
        ]
        for k, v in self.entries:
            self.ht.insert(k, v)

    def test_display_format(self):
        # Перехват вывода display
        buffer = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buffer
        try:
            self.ht.display()
        finally:
            sys.stdout = sys_stdout
        out = buffer.getvalue()
        # Должны содержать заголовок и одну из специализаций
        self.assertIn('Idx', out)
        self.assertIn('Отоларинголог', out)
        # Проверяем, что прочерки отображаются
        self.assertIn('- |', out)

    def test_insert_after_delete_reuse_slot(self):
        # Удаляем 'Грипп'
        self.ht.delete('Грипп')
        V = self.ht._compute_V('Грипп')
        h = self.ht._hash(V)
        # Вставляем новый на то же место
        self.ht.insert('Грипп', 'НовыйТерапевт')
        # Проверяем, что новая специализация корректна
        self.assertEqual(self.ht.search('Грипп'), 'НовыйТерапевт')
        # Проверяем, что старый tombstone сброшен
        bucket = self.ht.buckets[h]
        self.assertEqual(bucket.D, 0)

    def test_resize_and_preserve(self):
        old_size = self.ht.size
        # Заполняем до хэд рост >70%
        extras = [('Язва', 'Гастроэнтеролог'), ('Астма', 'Аллерголог')]
        for k, v in extras:
            self.ht.insert(k, v)
        # После вставок должен быть ресайз
        self.assertGreater(self.ht.size, old_size)
        # Все записи сохраняются
        for k, v in self.entries + extras:
            self.assertEqual(self.ht.search(k), v)

    def test_search_stops_at_empty(self):
        # Ищем в пустом слоте
        self.assertIsNone(self.ht.search('НеСуществует'))

    def test_delete_raises(self):
        with self.assertRaises(KeyError):
            self.ht.delete('НеТакое')

    def test_insert_raises_duplicate(self):
        with self.assertRaises(KeyError):
            self.ht.insert('Ангина', 'КтоУгодно')

    def test_load_factor_bounds(self):
        lf = self.ht.load_factor()
        self.assertTrue(0 < lf <= 1)
        # После удаления
        self.ht.delete('Диабет')
        new_lf = self.ht.load_factor()
        self.assertTrue(new_lf < lf)

    def test_chain_structure_pointers(self):
        # Создаем коллизию
        ht2 = HashTable(initial_size=3, q=1)
        ht2.insert('АА', 'D1')
        ht2.insert('ААА', 'D2')
        V = ht2._compute_V('АА')
        h = ht2._hash(V)
        head = ht2.buckets[h]
        self.assertEqual(head.C, 1)
        self.assertEqual(head.Po is not None, True)
        tail = ht2.buckets[head.Po]
        self.assertEqual(tail.T, 1)
        self.assertIsNone(tail.Po)

    def test_delete_middle_and_head_and_tail(self):
        # Цепочка из трех
        ht3 = HashTable(initial_size=5, q=1)
        keys = ['АА','ААА','АААА']
        for i,k in enumerate(keys): ht3.insert(k, f'D{i}')
        # Удаление среднего
        ht3.delete('ААА')
        self.assertIsNone(ht3.search('ААА'))
        # Удаление головы
        ht3.delete('АА')
        self.assertIsNone(ht3.search('АА'))
        # Удаление хвоста
        ht3.delete('АААА')
        self.assertIsNone(ht3.search('АААА'))
        # После всех удалений load_factor = 0
        self.assertEqual(ht3.load_factor(), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)