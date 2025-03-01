def dop_reverse(bin):
    result=""
    for b in bin:
        if b=="0":
            result+="1"
        else:
            result+="0"
    return result
def int_to_bin(integer_part_value):
    integer_part_code=""
    while integer_part_value-2>-1:
        integer_part_code+=str(integer_part_value%2)
        integer_part_value//=2         
    integer_part_code+=str(integer_part_value%2)
    return integer_part_code[::-1]
def bin_ge(a:str, b:str):
    if len(a) != len(b):
        return len(a) > len(b)
    return a >= b