#Определяем класс для узлов дерева разбора
class Node:
    def __init__(self, op=None, left=None, right=None, child=None, var=None, explicit=False):
        self.op = op      
        self.left = left  
        self.right = right  
        self.child = child  
        self.var = var      
        self.explicit = explicit  
        if var is not None:
            self.expr = var
        elif op == '!':
            if child and child.op in {"&", "|", "->", "<->"}:
                self.expr = f"!({child.expr})"
            else:
                self.expr = f"!{child.expr}"
        elif op in {"&", "|", "->", "<->"}:
            self.expr = f"({left.expr} {op} {right.expr})"