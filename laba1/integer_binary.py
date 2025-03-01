from transfers import *
class integer_binary:    
    def decimal(code:str, minus:bool=False):
        decimal_num=0
        point_position=0
        for place in range(0,len(code)):
            decimal_num+=int(code[place])*2**(len(code)-1-place)
        if minus:
            return -decimal_num
        return decimal_num
    def __init__(self, value):
        self.binary=""
        self.binary_module=""
        minus=False
        if type(value)==int:
            if(value<0):
                value=-value
                minus=True
            self.binary=int_to_bin(value)
            if(len(self.binary)>31):
                raise OverflowError("Переполнение в классе integer_binary")
            # Вставить обработку ошибок
            while len(self.binary)!=32:
                self.binary=str(0)+self.binary
            self.binary_module=self.binary
            if minus:
                self.binary=(integer_binary(dop_reverse(self.binary_module))+integer_binary(1)).binary
        elif type(value)==str:
            self.binary=value
            if len(value)!=32:
                raise ValueError("Нужно строка с 32 символами")
            if(self.binary[0]=="1"):
                self.binary_module=(integer_binary(dop_reverse(self.binary))+integer_binary(1)).binary
            else:
                self.binary_module=self.binary
        else:
            raise TypeError("Неправильный аргумент в создании класса integer_binary")
    def show(self):          
        if self.binary[0]==str(1):
            print("Прямой код: ",str(1)+self.binary_module[1:])
            print("Обратный код: ", dop_reverse(self.binary_module))
            print("Дополнительный код: ", self.binary)
            print("В десятичной системе счисления:", integer_binary.decimal(self.binary_module, True))
        else:
            print("Прямой код: ",self.binary_module)
            print("Обратный код: ", self.binary_module)
            print("Дополнительный код: ", self.binary)  
            print("В десятичной системе счисления:", integer_binary.decimal(self.binary_module))
    def __add__(self, n):
        if isinstance(n,integer_binary):
            second_term=list(n.binary)[::-1]
            first_term=list(self.binary)[::-1]
            transportable_value=0
            result=list()
            for i in range(0,32):
                a=int(first_term[i])+int(second_term[i])+transportable_value
                if a>=2:
                    result.append(str(a-2))
                    transportable_value=1
                else:
                    result.append(str(a))
                    transportable_value=0
            return integer_binary("".join(result[::-1]))
        else:
            raise TypeError("Второе слагаемое должно быть классом integer_binary")        
    def __neg__(self):
        binary=(integer_binary(dop_reverse(self.binary))+integer_binary(1)).binary
        return binary
    def __sub__(self, n):
        if isinstance(n, integer_binary):
            return self+integer_binary((-n))
        else:
            raise TypeError
    def __mul__(self, n):
        if isinstance(n,integer_binary):
            intermediate_number=str(0)*31
            first_multiplier=self.binary_module[1:]
            second_multiplier=n.binary_module[1:]
            for bit in range(0,31):
                if second_multiplier[30-bit]=="1":
                    summable_num=first_multiplier[bit:]
                    summable_num+=str(0)*bit
                    second_term=list(intermediate_number[::-1])
                    first_term=list(summable_num[::-1])
                    transportable_value=0
                    result=list()
                    for i in range(0,31):
                        a=int(first_term[i])+int(second_term[i])+transportable_value
                        if a>=2:
                            result.append(str(a-2))
                            transportable_value=1
                        else:
                            result.append(str(a))
                            transportable_value=0
                    intermediate_number="".join(result[::-1])
                    result.clear()
            if (n.binary[0]==str(1) and self.binary[0]==str(1)) or (n.binary[0]==str(0) and self.binary[0]==str(0)):
                return integer_binary(str(0)+intermediate_number)
            else:
                return integer_binary(dop_reverse(str(0)+intermediate_number))+integer_binary(1)
        else:
            raise TypeError("Второй множитель должен быть классом integer_binary")    
    def __truediv__(self, n):
        if not isinstance(n, integer_binary):
            raise TypeError("Деление возможно только между объектами integer_binary")
        sign = "0" if (((self.binary[0] == '1') and (n.binary[0] == '1')) or ((self.binary[0] == '0') and (n.binary[0] == '0'))) else "1"
        dividend = self.binary_module.lstrip('0') or '0'
        divisor = n.binary_module.lstrip('0') or '0'
        if divisor == '0':
            raise ZeroDivisionError("Деление на ноль")
        def bin_sub(a, b):
            max_len = max(len(a), len(b))
            a = a.zfill(max_len)
            b = b.zfill(max_len)
            result = ""
            borrow = 0
            for i in range(max_len - 1, -1, -1):
                bit_a = int(a[i])
                bit_b = int(b[i])
                diff = bit_a - bit_b - borrow
                if diff < 0:
                    diff += 2
                    borrow = 1
                else:
                    borrow = 0
                result = str(diff) + result
            return result.lstrip('0') or '0'
        # Деление в столбик для целой части
        quotient = ""
        remainder = ""
        for bit in dividend:
            remainder = remainder + bit
            remainder = remainder.lstrip('0') or '0'
            if bin_ge(remainder, divisor):
                remainder = bin_sub(remainder, divisor)
                quotient += '1'
            else:
                quotient += '0'
        quotient = quotient.lstrip('0') or '0'
        fraction = ""
        for _ in range(5):
            remainder = remainder + '0'  # умножение остатка на 2
            remainder = remainder.lstrip('0') or '0'
            if bin_ge(remainder, divisor):
                remainder = bin_sub(remainder, divisor)
                fraction += '1'
            else:
                fraction += '0'
        result = sign+(quotient + '.' + fraction).rjust(32,"0")
        return result   