from integer_binary import *
class float_binary:
    def decimal(code:str):
        mantissa=code[9:]
        exponenta_code=code[1:9]
        num=1
        count=-1
        for place in range(0,len(mantissa)):
            num+=int(mantissa[place])*2**(-1-place)
        exponenta=integer_binary.decimal(exponenta_code)
        if(code[0]=="0"):
            return num*(2**(exponenta-127))
        else:
            return -num*(2**(exponenta-127))
    def show(self):
        print(self.binary)
        print(float_binary.decimal(self.binary))
    def __init__(self, value):
        if type(value)==float:
            integer_part_value=int(abs(value))
            integer_part_code=int_to_bin(integer_part_value)
            float_part=abs(value)-integer_part_value
            float_part_code=""
            count=0
            while float_part > 0 and count < 33:
                float_part*= 2
                bit = int(float_part)
                float_part_code += str(bit)
                float_part -= bit
                count += 1
            exponent, mantissa=0,0
            if integer_part_value != 0:
                exponent = len(integer_part_code) - 1
                mantissa = integer_part_code[1:]+float_part_code  # Убираем ведущую 1
            else:
                first_one = float_part_code.find("1")
                exponent = -first_one - 1
                mantissa = float_part_code[first_one + 1:]  # Убираем ведущую 1
            biased_exponent = exponent + 127
            exponent_bin = int_to_bin(biased_exponent).rjust(8, "0")
            mantissa = mantissa[:23].ljust(23, "0")
            if value>0:
                self.binary="0"+exponent_bin+mantissa
            else:
                self.binary="1"+exponent_bin+mantissa
        elif type(value)==str:
            if len(value)!=32:
                raise ValueError("Нужно строка с 32 символами")
            self.binary=value
        else:
            raise TypeError("Неправильный аргумент в создании класса float_binary")
    def __add__(self, n):
        if isinstance(n, float_binary):
            if self.binary[0] == "0" and n.binary[0] == "0":
                exp1 = integer_binary(self.binary[1:9].rjust(32, "0"))
                exp2 = integer_binary(n.binary[1:9].rjust(32, "0"))
                M1_aligned = "1" + self.binary[9:]
                M2_aligned = "1" + n.binary[9:]
                E_max = 0
                if bin_ge(exp1.binary, exp2.binary):
                    E_max = integer_binary.decimal(exp1.binary)
                    M2_aligned = ("0" * (integer_binary.decimal((exp1 - exp2).binary)) + M2_aligned)[:24]
                else:
                    E_max = integer_binary.decimal(exp2.binary)
                    M1_aligned = ("0" * (integer_binary.decimal((exp2 - exp1).binary)) + M1_aligned)[:24]
                # Побитовое сложение 24-битных значимых (в виде строк)
                first_term = list(M1_aligned)[::-1]
                second_term = list(M2_aligned)[::-1]
                transportable_value = 0
                result = list()
                for i in range(0, 24):
                    a = int(first_term[i]) + int(second_term[i]) + transportable_value
                    if a >= 2:
                        result.append(str(a - 2))
                        transportable_value = 1
                    else:
                        result.append(str(a))
                        transportable_value = 0     
                sum_bits = "".join(result[::-1])
                if transportable_value == 1:
                    E_max += 1
                    sum_bits = ("1" + sum_bits)[:-1]
                else:
                    sum_bits = sum_bits.zfill(24)
                # Удаляем неявную единицу: оставляем 23 бита (начиная со второго бита)
                mantissa = sum_bits[1:]
                result_bin = "0" + int_to_bin(E_max).rjust(8, "0") + mantissa
                return float_binary(result_bin)
            else:
                raise ValueError("Числа должны быть положительными")
        else:
            raise TypeError("Второе слогаемое должно быть класса float_binary")
        
