#!/bin/env python3
w = "0001000000100001"

a = "01100101011001000110111101001110001100011100111101111111111111111"

w_n = len(w)
# dodajemy zera do a
a = a + "0" * w_n
print("Extended a {}".format(a))
a_n = len(a)

# powiekszamy w
w = "1" + w
print("Extended w {}".format(w))
w_n = len(w)


a_int = int(a,2)
w_int = int(w,2)

if 1:
    # valid for CRC16
    init_val = 0xFFFF;
    len_init_val = 16; # how many bits have init val - can be precalculated
    last_bit_pos = len(a); # include zeros at the begining
    print("last bit pos" , last_bit_pos)
    init_val = init_val << last_bit_pos - len_init_val
    print("AO {0:088b}".format(a_int))
    print("I  {0:088b}".format(init_val))
    a_int = a_int ^ init_val;
    print("AX {0:088b}".format(a_int))

while True:
    print("-----------------");
    print("a {0:088b}".format(a_int))
    last_set_bit_pos = len("{0:b}".format(a_int));
    d = w_int << last_set_bit_pos - w_n
    print("w {0:>88b}".format(d))
    o = a_int ^ d
    print("o {0:088b}".format(o))
    a_int = o
    last_set_bit_pos = len("{0:b}".format(a_int));
    if last_set_bit_pos < w_n:
        print("End of calculation")
        print("Result: {}".format(hex(a_int)))
        break

