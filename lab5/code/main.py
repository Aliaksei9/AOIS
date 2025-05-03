from boolean_minimizer import BooleanMinimizer
# 1) Построение таблицы переходов и сигналов h
def build_transition_table(n_bits=4):
    bits = [1]*n_bits
    table = []  # [([q4*,q3*,q2*,q1*,V], [h4,h3,h2,h1])]
    for _ in range(2**n_bits):
        q_star = bits[:]
        V = 1
        # Вычисляем T-входы
        T = [0]*n_bits
        T[0] = V
        for i in range(1, n_bits):
            if V==1 and all(q_star[j]==0 for j in range(i)):
                T[i] = 1
        # Новые биты и h-сигналы
        new = [q_star[i] ^ T[i] for i in range(n_bits)]
        h = [1 if q_star[i]!=new[i] else 0 for i in range(n_bits)]
        table.append((list(reversed(q_star))+[V], list(reversed(h))))
        bits = new
    return table

# 2) Функция для построения SDNF (сырой полная ДНФ)
def build_sdnf(table, index, inputs):
    terms = []
    for inp, h_vals in table:
        if h_vals[index]==1:
            lits = [var if val==1 else f"!{var}" for var,val in zip(inputs, inp)]
            terms.append("(" + "/\\".join(lits) + ")")
    return "\\/".join(terms) if terms else "0"

# Основное
inputs = ["q4s","q3s","q2s","q1s","V"]
table = build_transition_table(4)

# Печать таблицы переходов
header = ["№"] + inputs + ["h4","h3","h2","h1"]
print(" ".join(f"{h:>4}" for h in header))
for i,(inp,hv) in enumerate(table):
    row = [i] + inp + hv
    print(" ".join(f"{str(x):>4}" for x in row))
print()

# Маппинг для минимизатора: A…E
var_map = {'A':'q4s','B':'q3s','C':'q2s','D':'q1s','E':'V'}
inv_map = {v:k for k,v in var_map.items()}

# Для каждого h:
for idx,h in enumerate(["h4","h3","h2","h1"]):
    # 1) SDNF
    raw = build_sdnf(table, idx, inputs)
    print(f"{h} SDNF = {raw}")
    # 2) подготовки для минимизатора: заменить на A..E
    raw_A = raw
    for orig, one in inv_map.items():
        raw_A = raw_A.replace(orig, one)
    # 3) минимизация
    bm = BooleanMinimizer(raw_A, form_type=1)
    essential = bm.minimize_calculative()
    dnf_A = bm.implicants_to_string(essential).replace(" \\/ ","\\/").replace(" /\\ ","/\\")
    # 4) вернуть исходные имена
    for one, orig in var_map.items():
        dnf_A = dnf_A.replace(one, orig)
    print(f"{h} DNF  = {dnf_A}")
    print()