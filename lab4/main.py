from boolean_minimizer import *
from parser import *
from truth_table_generator import *
from integer_binary import *

print("Перенос:")
trunser_formula="(A&B)|(A&PO)|(B&PO)"
parser_trunsfer = Parser(trunser_formula)
tree_trunsfer = parser_trunsfer.parse()
generator_trunsfer = TruthTableGenerator(tree_trunsfer, sorted(set(token for token in parser_trunsfer.tokens if token.isalnum())))    
formulaSDNF_trunsfer = generator_trunsfer.generate('P') 
minimizerSDNF_trunfer = BooleanMinimizer(formulaSDNF_trunsfer, 1)
print("Минимизированная ДНФ, которая представляет формулу переноса:\n" + minimizerSDNF_trunfer.implicants_to_string(minimizerSDNF_trunfer.minimize_calculative()))

print("Сумма:")
sum_formula="(!A&!B&PO)|(!A&B&!PO)|(A&!B&!PO)|(A&B&PO)"
parser_sum = Parser(sum_formula)
tree_sum = parser_sum.parse()
generator_sum = TruthTableGenerator(tree_sum, sorted(set(token for token in parser_sum.tokens if token.isalnum())))    
formulaSDNF_sum = generator_sum.generate('S') 
minimizerSDNF_sum = BooleanMinimizer(formulaSDNF_sum, 1)
print("Минимизированная ДНФ, которая представляет формулу суммы:\n" + minimizerSDNF_sum.implicants_to_string(minimizerSDNF_sum.minimize_calculative()))

print("Таблица 1. Д8421")
number=integer_binary(0)
for i in range(0,12):
    print("|"+number.binary[-4]+"|"+number.binary[-3]+"|"+number.binary[-2]+"|"+number.binary[-1]+"|")
    number=number+integer_binary(1)
    if(integer_binary.decimal(number.binary)>9):
        number=integer_binary(0)
print("Таблица 1. Д8421+2")
number=integer_binary(2)
for i in range(0,12):
    print("|"+number.binary[-4]+"|"+number.binary[-3]+"|"+number.binary[-2]+"|"+number.binary[-1]+"|")
    number=number+integer_binary(1)
    if(integer_binary.decimal(number.binary)>9):
        number=integer_binary(0)

minimizerBIT0 = BooleanMinimizer("(!A /\\ !B /\\ !C /\\ D) \\/(!A /\\ !B /\\ C /\\ D) \\/(!A /\\ B /\\ !C /\\ D) \\/(!A /\\ B /\\ C /\\ D) \\/(A /\\ !B /\\ !C /\\ D)", 1)
print("МИН ДНФ для первого бита:\n" + minimizerBIT0.implicants_to_string(minimizerBIT0.minimize_calculative()))
 
minimizerBIT1 = BooleanMinimizer("(!A /\\ !B /\\ !C /\\ !D) \\/(!A /\\ !B /\\ !C /\\ D) \\/(!A /\\ B /\\ !C /\\ !D) \\/(!A /\\ B /\\ !C /\\ D)", 1)
print("МИН ДНФ для второго бита:\n" + minimizerBIT1.implicants_to_string(minimizerBIT1.minimize_calculative()))

minimizerBIT2 = BooleanMinimizer("(!A /\\ !B /\\ C /\\ !D) \\/(!A /\\ !B /\\ C /\\ D) \\/(!A /\\ B /\\ !C /\\ !D) \\/(!A /\\ B /\\ !C /\\ D)", 1)
print("МИН ДНФ для третьго бита:\n" + minimizerBIT2.implicants_to_string(minimizerBIT2.minimize_calculative()))

minimizerBIT3 = BooleanMinimizer("(!A /\\ B /\\ C /\\ !D) \\/(!A /\\ B /\\ C /\\ D)", 1)
print("МИН ДНФ для четвёртого бита:\n" + minimizerBIT3.implicants_to_string(minimizerBIT3.minimize_calculative()))

input_num=int(input("Введите число"))
num=integer_binary(input_num%10)
print("В Д8421:" + num.binary[-4:])
print("В Д8421+2:" + (num+integer_binary(2)).binary[-4:])
