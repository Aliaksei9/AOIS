from bucket import *
class HashTable:
    def __init__(self, initial_size=20, q=2):
        self.size = initial_size
        self.q = q
        self.count = 0
        self.buckets = [Bucket() for _ in range(self.size)]
        letters = [
            'А','Б','В','Г','Д','Е','Ё','Ж','З','И','Й','К','Л','М','Н','О','П',
            'Р','С','Т','У','Ф','Х','Ц','Ч','Ш','Щ','Ъ','Ы','Ь','Э','Ю','Я'
        ]
        self.char_to_num = {ch: i for i, ch in enumerate(letters)}

    def _compute_V(self, key):
        k = key.upper()
        a = self.char_to_num.get(k[0], 0)
        b = self.char_to_num.get(k[1], 0) if len(k) > 1 else 0
        return a * 33 + b

    def _hash(self, V):
        return V % self.size

    def _resize(self):
        old_buckets = self.buckets
        self.size *= 2
        self.buckets = [Bucket() for _ in range(self.size)]
        self.count = 0
        for bucket in old_buckets:
            if bucket.U == 1 and bucket.D == 0:
                self.insert(bucket.key, bucket.value)

    def insert(self, key, specialization):
        if self.search(key) is not None:
            raise KeyError(f"Ключ '{key}' уже существует в таблице")
        V = self._compute_V(key)
        h0 = self._hash(V)
        if self.buckets[h0].U == 0:
            b = self.buckets[h0]
            b.key = key; b.value = specialization; b.V = V; b.h = h0
            b.U = 1; b.D = 0; b.C = 0; b.T = 1; b.Po = None
            self.count += 1
            return
        for i in range(1, self.size):
            idx = (h0 + i * self.q) % self.size
            if self.buckets[idx].U == 0:
                head = self.buckets[h0]
                if head.C == 0:
                    head.C = 1; head.T = 0; head.Po = idx
                else:
                    cur = h0
                    while not self.buckets[cur].T:
                        cur = self.buckets[cur].Po
                    tail = self.buckets[cur]
                    tail.T = 0; tail.Po = idx
                nb = self.buckets[idx]
                nb.key = key; nb.value = specialization; nb.V = V; nb.h = h0
                nb.U = 1; nb.D = 0; nb.C = 0; nb.T = 1; nb.Po = None
                self.count += 1
                return
        self._resize()
        self.insert(key, specialization)

    def search(self, key):
        V = self._compute_V(key); h0 = self._hash(V)
        b = self.buckets[h0]
        if b.U == 0:
            return None
        if b.key == key and b.D == 0:
            return b.value
        if b.C == 1:
            cur = b.Po
            while cur is not None:
                nb = self.buckets[cur]
                if nb.key == key and nb.D == 0:
                    return nb.value
                if nb.T == 1:
                    break
                cur = nb.Po
        return None

    def delete(self, key):
        V = self._compute_V(key); h0 = self._hash(V)
        b = self.buckets[h0]
        idx = None
        if b.U == 1 and b.D == 0 and b.key == key:
            idx = h0
        elif b.C == 1:
            cur = b.Po
            while cur is not None:
                nb = self.buckets[cur]
                if nb.U == 1 and nb.D == 0 and nb.key == key:
                    idx = cur; break
                if nb.T == 1:
                    break
                cur = nb.Po
        if idx is None:
            raise KeyError(f"Ключ '{key}' не найден")
        node = self.buckets[idx]; node.D = 1
        if node.C == 0 and node.T == 1:
            node.U = 0
        elif node.T == 1:
            prev = h0
            while self.buckets[prev].Po != idx:
                prev = self.buckets[prev].Po
            self.buckets[prev].T = 1; self.buckets[prev].Po = None
            node.U = 0
        elif node.C == 0:
            nxt = self.buckets[node.Po]
            node.key = nxt.key; node.value = nxt.value; node.V = nxt.V; node.h = nxt.h
            node.U = 1; node.D = nxt.D; node.C = nxt.C; node.T = nxt.T; node.Po = nxt.Po
            nxt.U = 0
        else:
            nxt = self.buckets[node.Po]
            node.key, node.value = nxt.key, nxt.value; node.V, node.h = nxt.V, nxt.h
            node.D, node.C, node.T, node.Po = nxt.D, nxt.C, nxt.T, nxt.Po
            nxt.U = 0
        self.count -= 1

    def load_factor(self):
        return self.count / self.size

    def display(self):
        cols = ["Idx","Key","V","h","C","U","T","D","Po","Spec"]
        rows = []
        for i, b in enumerate(self.buckets):
            po_str = str(b.Po) if b.Po is not None else '-'
            rows.append([
                str(i), b.key or '-', str(b.V or '-'), str(b.h or '-'),
                str(b.C), str(b.U), str(b.T), str(b.D), po_str, b.value or '-'
            ])
        widths = [max(len(r[j]) for r in [cols]+rows) for j in range(len(cols))]
        def fmt(r): return " | ".join(r[j].ljust(widths[j]) for j in range(len(cols)))
        print(fmt(cols)); print("-" * (sum(widths) + 3*(len(cols)-1)))
        for r in rows:
            print(fmt(r))

